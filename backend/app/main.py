import json
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.config import ALLOWED_ORIGINS, APP_NAME, APP_VERSION
from app.core.database import engine, Base, get_db
from app.models import AccessPattern, AuditLog, Policy, PolicyAuditLog, PolicyLifecycle, PolicyVersion, User
from app.schemas import (
    AccessPatternCreate,
    AccessPatternBatchCreate,
    PolicyAnalysisRequest,
    PolicyCreate,
    PolicyStatusUpdate,
    PolicyValidationRequest,
    LoginRequest,
    Token,
    UserCreate,
    RefreshRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    LogoutRequest,
    PolicyLifecycleUpdate,
    PolicyRollbackRequest,
)
from app.services.synthesis import analyze_patterns, validate_policy
from app.auth.security import (
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    get_password_hash,
    revoke_token,
    verify_token,
    verify_password,
)
from collections import defaultdict
import time

_auth_attempts = defaultdict(list)


def enforce_rate_limit(key: str, limit: int = 10, window_seconds: int = 60):
    now = time.time()
    recent = [item for item in _auth_attempts[key] if now - item < window_seconds]
    if len(recent) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests; try again later")
    recent.append(now)
    _auth_attempts[key] = recent

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=APP_NAME,
    description="Autonomous Least-Privilege IAM Policy Synthesizer",
    version=APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_demo_data(db: Session):
    """Seed a small, visible dataset for first-run presentations."""
    if db.query(AccessPattern).count():
        return
    now = datetime.utcnow()
    demo = [
        ("arn:aws:s3:::iamshield-audit/*", "s3:GetObject", 128),
        ("arn:aws:s3:::iamshield-audit", "s3:ListBucket", 42),
        ("arn:aws:ec2:us-east-1:123456789012:instance/*", "ec2:DescribeInstances", 76),
        ("*", "s3:*", 2),
    ]
    for resource, action, count in demo:
        db.add(AccessPattern(resource=resource, action=action, access_count=count,
                             first_accessed=now - timedelta(days=14), last_accessed=now))
    db.commit()


def record_audit(
    db: Session,
    action: str,
    user_id: int | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: str | None = None,
):
    db.add(AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
    ))


@app.on_event("startup")
def startup_seed():
    db = next(get_db())
    try:
        seed_demo_data(db)
    finally:
        db.close()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": APP_NAME, "version": APP_VERSION}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {APP_NAME}",
        "version": APP_VERSION,
        "docs": "/api/docs"
    }


@app.post("/api/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    enforce_rate_limit(f"register:{payload.username}")
    existing = db.query(User).filter(
        (User.username == payload.username) | (User.email == payload.email)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username or email is already registered")
    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email is already registered")
    record_audit(db, "user_registered", user.id, "user", str(user.id), "Account created")
    db.commit()
    token = create_access_token({"sub": user.username, "user_id": user.id})
    return Token(access_token=token, refresh_token=create_refresh_token({"sub": user.username, "user_id": user.id}))


@app.post("/api/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    enforce_rate_limit(f"login:{payload.username}")
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    record_audit(db, "user_login", user.id, "user", str(user.id), "Successful login")
    db.commit()
    token = create_access_token({"sub": user.username, "user_id": user.id})
    return Token(access_token=token, refresh_token=create_refresh_token({"sub": user.username, "user_id": user.id}))


@app.post("/api/auth/refresh", response_model=Token)
def refresh_token(payload: RefreshRequest):
    token_data = verify_token(payload.refresh_token)
    claims = jwt.get_unverified_claims(payload.refresh_token)
    if claims.get("token_type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token required")
    revoke_token(payload.refresh_token)
    return Token(
        access_token=create_access_token({"sub": token_data.username, "user_id": token_data.user_id}),
        refresh_token=create_refresh_token({"sub": token_data.username, "user_id": token_data.user_id}),
    )


@app.post("/api/auth/logout")
def logout(payload: LogoutRequest):
    if payload.refresh_token:
        revoke_token(payload.refresh_token)
    return {"message": "Signed out"}


@app.post("/api/auth/password-reset/request")
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user:
        return {"message": "If the account exists, reset instructions are available."}
    token = create_access_token({"sub": user.username, "user_id": user.id, "token_type": "password_reset"}, timedelta(minutes=15))
    return {"message": "Reset token generated for the development workflow.", "reset_token": token}


@app.post("/api/auth/password-reset/confirm")
def confirm_password_reset(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    token_data = verify_token(payload.token)
    claims = jwt.get_unverified_claims(payload.token)
    if claims.get("token_type") != "password_reset":
        raise HTTPException(status_code=401, detail="Password reset token required")
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = get_password_hash(payload.new_password)
    record_audit(db, "password_reset", user.id, "user", str(user.id), "Password changed")
    db.commit()
    revoke_token(payload.token)
    return {"message": "Password updated"}


@app.get("/api/auth/me")
async def current_user(current_user: User = Depends(get_current_active_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
    }


@app.get("/api/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    patterns = db.query(AccessPattern).all()
    generated = db.query(Policy).count()
    risky = sum(1 for item in patterns if item.resource == "*" or item.action in {"*", "s3:*"})
    return {
        "access_events": sum(item.access_count for item in patterns),
        "unique_permissions": len(patterns),
        "risky_permissions": risky,
        "generated_policies": generated,
        "status": "monitoring",
    }


@app.get("/api/access-patterns")
def list_access_patterns(db: Session = Depends(get_db)):
    return db.query(AccessPattern).order_by(AccessPattern.access_count.desc()).all()


@app.post("/api/access-patterns")
def add_access_pattern(payload: AccessPatternCreate, db: Session = Depends(get_db)):
    pattern = AccessPattern(**payload.model_dump())
    db.add(pattern)
    db.commit()
    db.refresh(pattern)
    return pattern


@app.post("/api/access-patterns/bulk")
def add_access_patterns(payload: AccessPatternBatchCreate, db: Session = Depends(get_db)):
    patterns = [AccessPattern(**event.model_dump()) for event in payload.events]
    db.add_all(patterns)
    db.commit()
    return {"imported": len(patterns)}


@app.post("/api/synthesis/analyze")
def synthesize_policy(payload: PolicyAnalysisRequest, db: Session = Depends(get_db)):
    patterns = db.query(AccessPattern).all()
    if payload.user_id is not None:
        patterns = [item for item in patterns if item.user_id == payload.user_id]
    if payload.resource_type:
        patterns = [item for item in patterns if payload.resource_type.lower() in item.resource.lower()]
    return analyze_patterns(patterns, payload.timeframe_days)


@app.post("/api/synthesis/validate")
def validate_synthesized_policy(payload: PolicyValidationRequest):
    return validate_policy(payload.policy_document)


@app.post("/api/policies")
def save_policy(
    payload: PolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    policy = Policy(name=payload.name, description=payload.description,
                    policy_type=payload.policy_type, resource_type=payload.resource_type,
                    policy_document=json.dumps(payload.policy_document), status="draft",
                    created_by=current_user.id)
    db.add(policy)
    db.commit()
    db.refresh(policy)
    db.add(PolicyVersion(
        policy_id=policy.id,
        version_number=1,
        policy_document=json.dumps(payload.policy_document),
        created_by=current_user.id,
    ))
    db.add(PolicyLifecycle(policy_id=policy.id))
    db.add(PolicyAuditLog(
        policy_id=policy.id,
        change_type="created",
        new_value=json.dumps(payload.policy_document),
        changed_by=current_user.id,
    ))
    record_audit(db, "policy_created", current_user.id, "policy", str(policy.id), policy.name)
    db.commit()
    return {"id": policy.id, "name": policy.name, "status": policy.status,
            "policy_document": payload.policy_document}


@app.get("/api/policies")
def list_policies(db: Session = Depends(get_db)):
    policies = db.query(Policy).order_by(Policy.created_at.desc()).all()
    return [{"id": item.id, "name": item.name, "status": item.status,
             "policy_type": item.policy_type, "resource_type": item.resource_type,
             "policy_document": json.loads(item.policy_document)} for item in policies]


@app.get("/api/policies/{policy_id}")
def get_policy(policy_id: int, db: Session = Depends(get_db)):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    lifecycle = db.query(PolicyLifecycle).filter(PolicyLifecycle.policy_id == policy.id).first()
    return {"id": policy.id, "name": policy.name, "description": policy.description,
            "status": policy.status, "policy_type": policy.policy_type,
            "resource_type": policy.resource_type,
            "policy_document": json.loads(policy.policy_document),
            "expires_at": lifecycle.expires_at if lifecycle else None,
            "created_at": policy.created_at, "updated_at": policy.updated_at,
            "activated_at": policy.activated_at}


@app.patch("/api/policies/{policy_id}/status")
def update_policy_status(
    policy_id: int,
    payload: PolicyStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    old_status = policy.status
    policy.status = payload.status
    if payload.status == "approved":
        policy.activated_at = datetime.utcnow()
    db.add(PolicyAuditLog(
        policy_id=policy.id,
        change_type=payload.status,
        old_value=old_status,
        new_value=payload.reason,
        changed_by=current_user.id,
    ))
    record_audit(
        db, f"policy_{payload.status}", current_user.id, "policy",
        str(policy.id), payload.reason,
    )
    db.commit()
    db.refresh(policy)
    return {"id": policy.id, "status": policy.status, "activated_at": policy.activated_at,
            "reason": payload.reason}


@app.get("/api/audit-logs")
def list_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if limit < 1 or limit > 200:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 200")
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return logs


@app.get("/api/policies/{policy_id}/history")
def policy_history(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not db.query(Policy).filter(Policy.id == policy_id).first():
        raise HTTPException(status_code=404, detail="Policy not found")
    return db.query(PolicyAuditLog).filter(
        PolicyAuditLog.policy_id == policy_id
    ).order_by(PolicyAuditLog.created_at.desc()).all()


@app.get("/api/policies/{policy_id}/versions")
def policy_versions(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not db.query(Policy).filter(Policy.id == policy_id).first():
        raise HTTPException(status_code=404, detail="Policy not found")
    versions = db.query(PolicyVersion).filter(
        PolicyVersion.policy_id == policy_id
    ).order_by(PolicyVersion.version_number.desc()).all()
    return [{"version_number": item.version_number, "policy_document": json.loads(item.policy_document), "created_at": item.created_at} for item in versions]


@app.post("/api/policies/{policy_id}/lifecycle")
def update_policy_lifecycle(
    policy_id: int,
    payload: PolicyLifecycleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    lifecycle = db.query(PolicyLifecycle).filter(PolicyLifecycle.policy_id == policy_id).first()
    if not lifecycle:
        lifecycle = PolicyLifecycle(policy_id=policy_id)
        db.add(lifecycle)
    lifecycle.expires_at = payload.expires_at
    record_audit(db, "policy_lifecycle_updated", current_user.id, "policy", str(policy_id), str(payload.expires_at))
    db.commit()
    return {"policy_id": policy_id, "expires_at": lifecycle.expires_at}


@app.post("/api/policies/{policy_id}/rollback")
def rollback_policy(
    policy_id: int,
    payload: PolicyRollbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    version = db.query(PolicyVersion).filter(
        PolicyVersion.policy_id == policy_id,
        PolicyVersion.version_number == payload.version_number,
    ).first()
    if not policy or not version:
        raise HTTPException(status_code=404, detail="Policy or version not found")
    policy.policy_document = version.policy_document
    lifecycle = db.query(PolicyLifecycle).filter(PolicyLifecycle.policy_id == policy_id).first()
    if lifecycle:
        lifecycle.rollback_version = payload.version_number
    record_audit(db, "policy_rollback", current_user.id, "policy", str(policy_id), f"Version {payload.version_number}")
    db.commit()
    return {"id": policy_id, "rolled_back_to": payload.version_number, "policy_document": json.loads(policy.policy_document)}


@app.get("/api/policies/{policy_id}/export")
def export_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {
        "filename": f"{policy.name}.json",
        "content_type": "application/json",
        "policy_document": json.loads(policy.policy_document),
    }


@app.get("/api/monitoring/summary")
def monitoring_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return {
        "audit_events": db.query(AuditLog).count(),
        "policy_count": db.query(Policy).count(),
        "approved_count": db.query(Policy).filter(Policy.status == "approved").count(),
        "draft_count": db.query(Policy).filter(Policy.status == "draft").count(),
        "service": "healthy",
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
