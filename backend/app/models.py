from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles = relationship("Role", secondary="user_roles", back_populates="users")
    policies = relationship("Policy", back_populates="created_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Role(Base):
    """Role model for RBAC."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", secondary="user_roles", back_populates="roles")


class UserRole(Base):
    """Association table for User-Role relationship."""
    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)


class PolicyStatus(str, enum.Enum):
    """Enum for policy status."""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Policy(Base):
    """IAM Policy model."""
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    policy_document = Column(Text, nullable=False)  # JSON policy
    status = Column(String(50), default=PolicyStatus.DRAFT.value)
    policy_type = Column(String(100))  # e.g., "user", "role", "service"
    resource_type = Column(String(100))  # e.g., "s3", "ec2", "iam"
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activated_at = Column(DateTime, nullable=True)

    created_by_user = relationship("User", back_populates="policies")
    audit_logs = relationship("PolicyAuditLog", back_populates="policy")


class AccessPattern(Base):
    """Model for storing access patterns used for policy synthesis."""
    __tablename__ = "access_patterns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resource = Column(String(500), nullable=False)
    action = Column(String(100), nullable=False)
    access_count = Column(Integer, default=1)
    first_accessed = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source_ip = Column(String(50), nullable=True)
    status = Column(String(50), default="allowed")  # allowed, denied


class AuditLog(Base):
    """Audit log for tracking user actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(500), nullable=True)
    details = Column(Text)
    status = Column(String(50), default="success")  # success, failure
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")


class PolicyAuditLog(Base):
    """Specific audit log for policy changes."""
    __tablename__ = "policy_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"))
    change_type = Column(String(50), nullable=False)  # created, updated, activated, deleted
    old_value = Column(Text)
    new_value = Column(Text)
    changed_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    policy = relationship("Policy", back_populates="audit_logs")
