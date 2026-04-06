import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def second_user(db) -> User:
    return User.objects.create_user(
        username="otheruser",
        email="other@example.com",
        password="otherpass123",
    )


@pytest.fixture
def auth_client(user: User, api_client: APIClient) -> APIClient:
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def auth_client_second(second_user: User, api_client: APIClient) -> APIClient:
    client = APIClient()
    refresh = RefreshToken.for_user(second_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def refresh_token(user: User) -> str:
    return str(RefreshToken.for_user(user))


@pytest.fixture
def register_url() -> str:
    return reverse("users:register")


@pytest.fixture
def login_url() -> str:
    return reverse("users:login")


@pytest.fixture
def logout_url() -> str:
    return reverse("users:logout")


@pytest.fixture
def profile_url() -> str:
    return reverse("users:profile")


@pytest.fixture
def user_list_url() -> str:
    return reverse("users:user-list")


def assert_response_status(response, expected_status: int):
    assert response.status_code == expected_status


def assert_field_in_response(response_data, field: str, expected_value):
    actual = response_data.get(field)
    assert actual == expected_value


def assert_field_exists(response_data, field: str):
    assert field in response_data


class TestRegisterView:
    def test_register_success(self, api_client: APIClient, register_url: str, db):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "strongpass123",
            "password2": "strongpass123",
        }
        response = api_client.post(register_url, data)

        assert_response_status(response, status.HTTP_201_CREATED)
        assert_field_in_response(response.data, "message", "Регистрация успешна")
        assert_field_exists(response.data, "user")
        assert_field_exists(response.data, "user_id")
        assert_field_exists(response.data, "tokens")
        assert_field_in_response(response.data["user"], "username", "newuser")
        assert_field_in_response(response.data["user"], "email", "newuser@example.com")

    def test_register_returns_jwt_tokens(
        self, api_client: APIClient, register_url: str, db
    ):
        data = {
            "username": "tokenuser",
            "email": "tokenuser@example.com",
            "password": "pass123456",
            "password2": "pass123456",
        }
        response = api_client.post(register_url, data)

        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]
        assert len(response.data["tokens"]["access"]) > 0

    @pytest.mark.parametrize(
        "field,invalid_value",
        [
            ("username", ""),
            ("email", "notanemail"),
            ("password", "short"),
            ("password2", "different"),
        ],
    )
    def test_register_validation_errors(
        self,
        api_client: APIClient,
        register_url: str,
        db,
        field: str,
        invalid_value: str,
    ):
        data = {
            "username": "validuser",
            "email": "valid@example.com",
            "password": "validpass123",
            "password2": "validpass123",
        }
        data[field] = invalid_value

        response = api_client.post(register_url, data)
        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(
        self, api_client: APIClient, register_url: str, db
    ):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "password2": "differentpass",
        }
        response = api_client.post(register_url, data)

        assert_response_status(response, status.HTTP_400_BAD_REQUEST)
        assert "password2" in response.data or "password" in response.data

    def test_register_missing_required_fields(
        self, api_client: APIClient, register_url: str, db
    ):
        response = api_client.post(register_url, {})

        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(
        self, api_client: APIClient, register_url: str, user: User, db
    ):
        data = {
            "username": user.username,
            "email": "unique@example.com",
            "password": "pass123",
            "password2": "pass123",
        }
        response = api_client.post(register_url, data)

        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(
        self, api_client: APIClient, register_url: str, user: User, db
    ):
        data = {
            "username": "uniqueuser",
            "email": user.email,
            "password": "pass123",
            "password2": "pass123",
        }
        response = api_client.post(register_url, data)

        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_register_with_optional_fields(
        self, api_client: APIClient, register_url: str, db
    ):
        data = {
            "username": "userwithbirth",
            "email": "birth@example.com",
            "password": "pass123456",
            "password2": "pass123456",
            "date_birth": "2000-01-01",
        }
        response = api_client.post(register_url, data)

        assert_response_status(response, status.HTTP_201_CREATED)
        assert_field_in_response(response.data["user"], "date_birth", "2000-01-01")


class TestLoginView:
    def test_login_success(self, api_client: APIClient, login_url: str, user: User):
        user.is_verified = True
        user.save()

        response = api_client.post(
            login_url,
            {
                "username": "testuser",
                "password": "testpass123",
            },
        )

        assert_response_status(response, status.HTTP_200_OK)
        assert_field_in_response(response.data, "message", "Вход выполнен")
        assert_field_exists(response.data, "user")
        assert_field_exists(response.data, "tokens")
        assert_field_in_response(response.data["user"], "username", "testuser")

    def test_login_returns_tokens(
        self, api_client: APIClient, login_url: str, user: User
    ):
        user.is_verified = True
        user.save()

        response = api_client.post(
            login_url,
            {
                "username": "testuser",
                "password": "testpass123",
            },
        )

        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]

    def test_login_unverified_email(
        self, api_client: APIClient, login_url: str, user: User
    ):
        response = api_client.post(
            login_url,
            {
                "username": "testuser",
                "password": "testpass123",
            },
        )

        assert_response_status(response, status.HTTP_403_FORBIDDEN)
        assert "detail" in response.data

    @pytest.mark.parametrize(
        "credentials",
        [
            {"username": "testuser", "password": "wrongpass"},
            {"username": "nonexistent", "password": "testpass123"},
            {"username": "", "password": ""},
        ],
    )
    def test_login_invalid_credentials(
        self,
        api_client: APIClient,
        login_url: str,
        db,
        credentials: dict,
    ):
        response = api_client.post(login_url, credentials)

        assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self, api_client: APIClient, login_url: str):
        response = api_client.post(login_url, {})

        assert_response_status(response, status.HTTP_401_UNAUTHORIZED)


class TestLogoutView:
    def test_logout_success(
        self, auth_client: APIClient, logout_url: str, refresh_token: str
    ):
        response = auth_client.post(logout_url, {"refresh": refresh_token})

        assert_response_status(response, status.HTTP_200_OK)
        assert_field_in_response(response.data, "message", "Выход выполнен")

    @pytest.mark.parametrize(
        "invalid_token",
        [
            "invalidtoken",
            "",
            "123.456.789",
            "not.a.jwt.token",
        ],
    )
    def test_logout_invalid_token(
        self, auth_client: APIClient, logout_url: str, invalid_token: str
    ):
        response = auth_client.post(logout_url, {"refresh": invalid_token})

        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_logout_missing_token(self, auth_client: APIClient, logout_url: str):
        response = auth_client.post(logout_url, {})

        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_logout_unauthenticated(
        self, api_client: APIClient, logout_url: str, refresh_token: str
    ):
        response = api_client.post(logout_url, {"refresh": refresh_token})

        assert_response_status(response, status.HTTP_401_UNAUTHORIZED)


class TestProfileView:
    def test_get_profile_success(
        self, auth_client: APIClient, profile_url: str, user: User
    ):
        response = auth_client.get(profile_url)

        assert_response_status(response, status.HTTP_200_OK)
        assert_field_in_response(response.data, "username", user.username)
        assert_field_in_response(response.data, "email", user.email)

    def test_get_profile_unauthenticated(self, api_client: APIClient, profile_url: str):
        response = api_client.get(profile_url)

        assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_email(
        self, auth_client: APIClient, profile_url: str, user: User
    ):
        response = auth_client.patch(profile_url, {"email": "updated@example.com"})

        assert_response_status(response, status.HTTP_200_OK)
        user.refresh_from_db()
        assert user.email == "updated@example.com"

    def test_update_profile_date_birth(
        self, auth_client: APIClient, profile_url: str, user: User
    ):
        response = auth_client.patch(profile_url, {"date_birth": "2000-01-01"})

        assert_response_status(response, status.HTTP_200_OK)
        user.refresh_from_db()
        assert str(user.date_birth) == "2000-01-01"

    def test_update_profile_bio(
        self, auth_client: APIClient, profile_url: str, user: User
    ):
        response = auth_client.patch(profile_url, {"bio": "Новая биография"})

        assert_response_status(response, status.HTTP_200_OK)
        user.refresh_from_db()
        assert user.bio == "Новая биография"

    def test_update_profile_multiple_fields(
        self, auth_client: APIClient, profile_url: str, user: User
    ):
        response = auth_client.patch(
            profile_url,
            {
                "email": "multi@example.com",
                "bio": "Много полей",
                "date_birth": "1995-05-15",
            },
        )

        assert_response_status(response, status.HTTP_200_OK)
        user.refresh_from_db()
        assert user.email == "multi@example.com"
        assert user.bio == "Много полей"
        assert str(user.date_birth) == "1995-05-15"

    def test_update_profile_username_readonly(
        self, auth_client: APIClient, profile_url: str, user: User
    ):
        old_username = user.username
        response = auth_client.patch(profile_url, {"username": "newusername"})

        user.refresh_from_db()
        assert user.username == old_username

    def test_delete_profile_success(
        self, auth_client: APIClient, profile_url: str, user: User
    ):
        user_id = user.pk
        response = auth_client.delete(profile_url)

        assert_response_status(response, status.HTTP_204_NO_CONTENT)
        assert not User.objects.filter(pk=user_id).exists()

    def test_delete_profile_unauthenticated(
        self, api_client: APIClient, profile_url: str
    ):
        response = api_client.delete(profile_url)

        assert_response_status(response, status.HTTP_401_UNAUTHORIZED)


class TestUserViewSet:
    def test_list_users_success(
        self, auth_client: APIClient, user_list_url: str, user: User, second_user: User
    ):
        response = auth_client.get(user_list_url)

        assert_response_status(response, status.HTTP_200_OK)
        assert len(response.data) == 2

    def test_list_users_contains_current_user(
        self, auth_client: APIClient, user_list_url: str, user: User
    ):
        response = auth_client.get(user_list_url)

        usernames = [u["username"] for u in response.data]
        assert user.username in usernames

    def test_list_users_unauthenticated(
        self, api_client: APIClient, user_list_url: str
    ):
        response = api_client.get(user_list_url)

        assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_only_current_user(
        self, auth_client: APIClient, user_list_url: str, user: User, db
    ):
        User.objects.exclude(pk=user.pk).delete()
        response = auth_client.get(user_list_url)

        assert_response_status(response, status.HTTP_200_OK)
        assert len(response.data) == 1

    def test_get_user_detail_success(
        self, auth_client: APIClient, user: User, second_user: User
    ):
        url = reverse("users:user-detail", kwargs={"pk": second_user.pk})
        response = auth_client.get(url)

        assert_response_status(response, status.HTTP_200_OK)
        assert_field_in_response(response.data, "username", second_user.username)
        assert_field_in_response(response.data, "email", second_user.email)

    def test_get_user_detail_not_found(self, auth_client: APIClient):
        url = reverse("users:user-detail", kwargs={"pk": 99999})
        response = auth_client.get(url)

        assert_response_status(response, status.HTTP_404_NOT_FOUND)

    def test_get_user_detail_unauthenticated(self, api_client: APIClient, user: User):
        url = reverse("users:user-detail", kwargs={"pk": user.pk})
        response = api_client.get(url)

        assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_detail_includes_online_status(
        self, auth_client: APIClient, user: User
    ):
        url = reverse("users:user-detail", kwargs={"pk": user.pk})
        response = auth_client.get(url)

        assert_response_status(response, status.HTTP_200_OK)
        assert "is_online" in response.data


class TestUserModel:
    def test_create_user(self, db):
        user = User.objects.create_user(
            username="modeltest",
            email="modeltest@example.com",
            password="testpass123",
        )

        assert user.username == "modeltest"
        assert user.email == "modeltest@example.com"
        assert user.check_password("testpass123")
        assert not user.is_staff
        assert user.is_active

    def test_create_superuser(self, db):
        superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )

        assert superuser.is_staff
        assert superuser.is_superuser

    def test_user_str_representation(self, user: User):
        assert str(user) == user.username

    def test_user_is_online_property(self, user: User):
        assert hasattr(user, "is_online")

    def test_user_online_status_property(self, user: User):
        assert hasattr(user, "online_status")
        assert user.online_status in ["online", "offline", "recently"]

    def test_user_last_seen_display(self, user: User):
        assert hasattr(user, "last_seen_display")

    def test_user_avatar_url(self, user: User):
        assert hasattr(user, "avatar_url")
        assert callable(user.avatar_url)


class TestEmailVerificationModel:
    def test_email_verification_creation(self, db, user: User):
        from .models import EmailVerification

        code = EmailVerification.generate_code()
        verification = EmailVerification.objects.create(user=user, code=code)

        assert verification.user == user
        assert verification.code == code
        assert len(code) == 6

    def test_email_verification_is_expired(self, db, user: User):
        from .models import EmailVerification
        from django.utils import timezone as tz
        import datetime

        verification = EmailVerification.objects.create(user=user, code="123456")

        assert not verification.is_expired()

        verification.created_at = tz.now() - datetime.timedelta(seconds=601)
        assert verification.is_expired()

    def test_email_verification_generate_code(self):
        from .models import EmailVerification

        code = EmailVerification.generate_code()

        assert len(code) == 6
        assert code.isdigit()


class TestVerifyEmailView:
    def test_verify_email_success(self, api_client: APIClient, user: User, db):
        from .models import EmailVerification

        code = EmailVerification.generate_code()
        EmailVerification.objects.create(user=user, code=code)

        url = reverse("users:verify-email")
        response = api_client.post(
            url,
            {
                "user_id": user.id,
                "code": code,
            },
        )

        assert_response_status(response, status.HTTP_200_OK)
        assert_field_in_response(response.data, "message", "Email подтверждён")
        user.refresh_from_db()
        assert user.is_verified

    def test_verify_email_invalid_code(self, api_client: APIClient, user: User, db):
        from .models import EmailVerification

        code = EmailVerification.generate_code()
        EmailVerification.objects.create(user=user, code=code)

        url = reverse("users:verify-email")
        response = api_client.post(
            url,
            {
                "user_id": user.id,
                "code": "000000",
            },
        )

        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_verify_email_missing_fields(self, api_client: APIClient):
        url = reverse("users:verify-email")
        response = api_client.post(url, {})

        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_verify_email_expired_code(self, api_client: APIClient, user: User, db):
        from .models import EmailVerification
        from django.utils import timezone as tz
        import datetime

        code = EmailVerification.generate_code()
        verification = EmailVerification.objects.create(user=user, code=code)
        verification.created_at = tz.now() - datetime.timedelta(seconds=601)
        verification.save()

        url = reverse("users:verify-email")
        response = api_client.post(
            url,
            {
                "user_id": user.id,
                "code": code,
            },
        )

        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_verify_email_nonexistent_user(self, api_client: APIClient):
        url = reverse("users:verify-email")
        response = api_client.post(
            url,
            {
                "user_id": 99999,
                "code": "123456",
            },
        )

        assert_response_status(response, status.HTTP_400_BAD_REQUEST)


class TestAuthenticationFlow:
    def test_full_authentication_flow(
        self,
        api_client: APIClient,
        register_url: str,
        login_url: str,
        logout_url: str,
        db,
    ):
        register_data = {
            "username": "flowuser",
            "email": "flow@example.com",
            "password": "flowpass123",
            "password2": "flowpass123",
        }
        register_response = api_client.post(register_url, register_data)
        assert_response_status(register_response, status.HTTP_201_CREATED)

        access_token = register_response.data["tokens"]["access"]
        refresh_token = register_response.data["tokens"]["refresh"]

        login_response = api_client.post(
            login_url,
            {
                "username": "flowuser",
                "password": "flowpass123",
            },
        )
        assert_response_status(login_response, status.HTTP_200_OK)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        logout_response = client.post(logout_url, {"refresh": refresh_token})
        assert_response_status(logout_response, status.HTTP_200_OK)

    def test_cannot_access_protected_endpoints_after_logout(
        self,
        api_client: APIClient,
        register_url: str,
        logout_url: str,
        profile_url: str,
        db,
    ):
        register_response = api_client.post(
            register_url,
            {
                "username": "logouttest",
                "email": "logout@example.com",
                "password": "testpass123",
                "password2": "testpass123",
            },
        )
        access_token = register_response.data["tokens"]["access"]
        refresh_token = register_response.data["tokens"]["refresh"]

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        logout_response = client.post(logout_url, {"refresh": refresh_token})
        assert_response_status(logout_response, status.HTTP_200_OK)
