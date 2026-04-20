import pytest

class FakeSettings:
    jwt_secret = "test_secret"
    jwt_alg = "HS256"
    access_token_expire_minutes = 60

@pytest.fixture
def settings():
    return FakeSettings()
