"""Explainable least-privilege policy synthesis for the prototype."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Iterable

from app.models import AccessPattern


def analyze_patterns(patterns: Iterable[AccessPattern], timeframe_days: int = 30) -> dict:
    """Build a minimal AWS-style policy from observed allowed access patterns."""
    cutoff = datetime.utcnow() - timedelta(days=timeframe_days)
    grouped: dict[str, set[str]] = defaultdict(set)
    permissions = []
    recommendations = []

    for pattern in patterns:
        if pattern.status != "allowed" or pattern.last_accessed < cutoff:
            continue
        grouped[pattern.resource].add(pattern.action)
        permissions.append({
            "resource": pattern.resource,
            "action": pattern.action,
            "frequency": pattern.access_count,
            "first_seen": pattern.first_accessed,
            "last_seen": pattern.last_accessed,
            "required": pattern.access_count > 0,
        })
        if pattern.action == "*" or pattern.resource == "*":
            recommendations.append(
                f"Replace wildcard access for {pattern.resource} with a specific resource and action."
            )

    statements = [
        {
            "Effect": "Allow",
            "Action": sorted(actions),
            "Resource": resource,
        }
        for resource, actions in sorted(grouped.items())
    ]
    if not statements:
        recommendations.append("No recent allowed activity was found; review the selected timeframe.")
    if not recommendations:
        recommendations.append("Observed permissions are scoped to the resources used in the selected timeframe.")

    return {
        "policy_name": "iamshield-generated-least-privilege",
        "policy_document": {"Version": "2012-10-17", "Statement": statements},
        "permissions": permissions,
        "recommendations": recommendations,
        "confidence_score": round(min(1.0, 0.7 + (0.05 * len(permissions))), 2) if permissions else 0.0,
    }


def validate_policy(policy_document: dict) -> dict:
    errors = []
    warnings = []
    recommendations = []
    if policy_document.get("Version") != "2012-10-17":
        warnings.append("Policy version is missing or is not the AWS-compatible 2012-10-17 version.")
    statements = policy_document.get("Statement")
    if not isinstance(statements, list) or not statements:
        errors.append("Policy must contain a non-empty Statement list.")
    else:
        for index, statement in enumerate(statements, start=1):
            if statement.get("Effect") not in {"Allow", "Deny"}:
                errors.append(f"Statement {index} must define Effect as Allow or Deny.")
            if statement.get("Action") == "*" or "*" in statement.get("Action", []):
                warnings.append(f"Statement {index} grants wildcard actions.")
            if statement.get("Resource") == "*":
                warnings.append(f"Statement {index} grants access to every resource.")
        if warnings:
            recommendations.append("Replace wildcard permissions with explicit actions and resource ARNs.")
        else:
            recommendations.append("Policy uses explicit actions and resource scopes.")
    return {
        "is_valid": not errors,
        "warnings": warnings,
        "errors": errors,
        "recommendations": recommendations,
    }
