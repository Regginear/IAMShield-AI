from datetime import datetime, timedelta
from types import SimpleNamespace

from app.services.synthesis import analyze_patterns, validate_policy


def pattern(resource, action, count=1, status="allowed", age_days=1):
    seen = datetime.utcnow() - timedelta(days=age_days)
    return SimpleNamespace(
        resource=resource,
        action=action,
        access_count=count,
        status=status,
        first_accessed=seen,
        last_accessed=seen,
    )


def test_synthesis_includes_recent_allowed_events_only():
    result = analyze_patterns([
        pattern("bucket/*", "s3:GetObject", 4),
        pattern("bucket/*", "s3:DeleteObject", 1, status="denied"),
        pattern("old/*", "s3:GetObject", 1, age_days=60),
    ])

    statements = result["policy_document"]["Statement"]
    assert len(statements) == 1
    assert statements[0]["Action"] == ["s3:GetObject"]
    assert result["permissions"][0]["frequency"] == 4


def test_wildcard_action_is_reported():
    result = analyze_patterns([pattern("*", "s3:*", 2)])
    validation = validate_policy(result["policy_document"])

    assert any("wildcard" in item.lower() for item in result["recommendations"])
    assert any("wildcard" in item.lower() for item in validation["warnings"])


def test_empty_policy_is_invalid_for_review():
    result = analyze_patterns([])
    validation = validate_policy(result["policy_document"])

    assert result["policy_document"]["Statement"] == []
    assert validation["is_valid"] is False
    assert validation["errors"]


def test_explicit_policy_is_valid():
    validation = validate_policy({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["s3:GetObject"],
            "Resource": "arn:aws:s3:::bucket/*",
        }],
    })

    assert validation["is_valid"] is True
    assert validation["warnings"] == []
