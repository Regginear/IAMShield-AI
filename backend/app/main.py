import json
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.config import ALLOWED_ORIGINS, APP_NAME, APP_VERSION
from app.core.database import engine, Base, get_db
from app.models import AccessPattern, Policy
from app.schemas import (
    AccessPatternCreate,
    PolicyAnalysisRequest,
    PolicyCreate,
    PolicyValidationRequest,
)
from app.services.synthesis import analyze_patterns, validate_policy

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


@app.post("/api/synthesis/analyze")
def synthesize_policy(payload: PolicyAnalysisRequest, db: Session = Depends(get_db)):
    patterns = db.query(AccessPattern).all()
    if payload.resource_type:
        patterns = [item for item in patterns if payload.resource_type.lower() in item.resource.lower()]
    return analyze_patterns(patterns, payload.timeframe_days)


@app.post("/api/synthesis/validate")
def validate_synthesized_policy(payload: PolicyValidationRequest):
    return validate_policy(payload.policy_document)


@app.post("/api/policies")
def save_policy(payload: PolicyCreate, db: Session = Depends(get_db)):
    policy = Policy(name=payload.name, description=payload.description,
                    policy_type=payload.policy_type, resource_type=payload.resource_type,
                    policy_document=json.dumps(payload.policy_document), status="draft")
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return {"id": policy.id, "name": policy.name, "status": policy.status,
            "policy_document": payload.policy_document}


@app.get("/api/policies")
def list_policies(db: Session = Depends(get_db)):
    policies = db.query(Policy).order_by(Policy.created_at.desc()).all()
    return [{"id": item.id, "name": item.name, "status": item.status,
             "policy_type": item.policy_type, "resource_type": item.resource_type,
             "policy_document": json.loads(item.policy_document)} for item in policies]


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
