import re

from lacommunaute.users.models import User


EMAIL = "alex@honnold.com"


class TestUserModel:
    def test_create_user_without_username(self, db):
        user = User.objects.create_user(email=EMAIL)
        assert re.match(r"^[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}$", user.username)
        assert user.email == EMAIL
