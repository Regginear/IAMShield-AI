from app.auth.security import create_access_token, get_password_hash, verify_password, verify_token


def test_password_hash_and_token_round_trip():
    password_hash = get_password_hash("ReviewPass1")
    assert password_hash != "ReviewPass1"
    assert verify_password("ReviewPass1", password_hash)

    token = create_access_token({"sub": "reviewer", "user_id": 7})
    claims = verify_token(token)
    assert claims.username == "reviewer"
    assert claims.user_id == 7
