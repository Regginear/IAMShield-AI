from app.services.synthesis import validate_policy


def test_validate_policy_accepts_single_statement_object():
    result = validate_policy({
        "Version": "2012-10-17",
        "Statement": {
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::example/*",
        },
    })

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert result["warnings"] == []


def test_validate_policy_reports_malformed_statements_without_raising():
    result = validate_policy({
        "Version": "2012-10-17",
        "Statement": ["not an object", {"Effect": "Allow", "Resource": []}],
    })

    assert result["is_valid"] is False
    assert "Statement 1 must be an object." in result["errors"]
    assert any("Action" in error for error in result["errors"])
    assert any("Resource" in error for error in result["errors"])


def test_validate_policy_warns_about_wildcard_actions_and_resources():
    result = validate_policy({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["s3:*"],
            "Resource": "*",
        }],
    })

    assert result["is_valid"] is True
    assert len(result["warnings"]) == 2


def test_validate_policy_does_not_recommend_wildcard_changes_for_version_warning():
    result = validate_policy({
        "Version": "invalid",
        "Statement": [{
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::example/*",
        }],
    })

    assert result["is_valid"] is True
    assert len(result["warnings"]) == 1
    assert "wildcard" not in result["recommendations"][0].lower()
