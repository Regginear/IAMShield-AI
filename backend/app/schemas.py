from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator("password")
    def validate_password(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Role Schemas
class RoleBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Authentication Schemas
class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    scopes: List[str] = []


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


# Policy Schemas
class PolicyBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    policy_type: str
    resource_type: str


class PolicyCreate(PolicyBase):
    policy_document: dict


class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    policy_document: Optional[dict] = None
    status: Optional[str] = None


class Policy(PolicyBase):
    id: int
    policy_document: dict
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    activated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Access Pattern Schemas
class AccessPatternBase(BaseModel):
    resource: str
    action: str


class AccessPatternCreate(AccessPatternBase):
    user_id: Optional[int] = None
    source_ip: Optional[str] = None


class AccessPattern(AccessPatternBase):
    id: int
    access_count: int
    first_accessed: datetime
    last_accessed: datetime
    status: str

    class Config:
        from_attributes = True


# Audit Log Schemas
class AuditLogBase(BaseModel):
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[str] = None


class AuditLog(AuditLogBase):
    id: int
    user_id: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Policy Synthesis Schemas
class PolicyAnalysisRequest(BaseModel):
    user_id: Optional[int] = None
    timeframe_days: int = Field(default=30, ge=1, le=365)
    resource_type: Optional[str] = None


class AnalyzedPermission(BaseModel):
    resource: str
    action: str
    frequency: int
    first_seen: datetime
    last_seen: datetime
    required: bool = True


class PolicySynthesisResponse(BaseModel):
    policy_name: str
    policy_document: dict
    permissions: List[AnalyzedPermission]
    recommendations: List[str]
    confidence_score: float = Field(..., ge=0, le=1)


class PolicyValidationRequest(BaseModel):
    policy_document: dict
    policy_type: str


class PolicyValidationResponse(BaseModel):
    is_valid: bool
    warnings: List[str]
    errors: List[str]
    recommendations: List[str]
