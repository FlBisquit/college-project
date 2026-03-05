import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


# ---------------------------------------------------------------------------
# Фикстуры
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
    )


@pytest.fixture
def second_user(db):
    return User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='otherpass123',
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def refresh_token(user):
    return str(RefreshToken.for_user(user))


@pytest.fixture
def register_url():
    return reverse('users:register')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def profile_url():
    return reverse('users:profile')


@pytest.fixture
def list_url():
    return reverse('users:user-list')  # роутер генерирует 'user-list'


# ---------------------------------------------------------------------------
# RegisterView
# ---------------------------------------------------------------------------

class TestRegisterView:

    @pytest.mark.parametrize('data,expected_status', [
        (
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'strongpass123',
                'password2': 'strongpass123',
            },
            status.HTTP_201_CREATED,
        ),
        (
            # несовпадение паролей
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'strongpass123',
                'password2': 'wrongpass',
            },
            status.HTTP_400_BAD_REQUEST,
        ),
        (
            # нет обязательных полей
            {},
            status.HTTP_400_BAD_REQUEST,
        ),
        (
            # невалидный email
            {
                'username': 'newuser',
                'email': 'notanemail',
                'password': 'strongpass123',
                'password2': 'strongpass123',
            },
            status.HTTP_400_BAD_REQUEST,
        ),
    ])
    def test_register(self, api_client, register_url, data, expected_status, db):
        response = api_client.post(register_url, data)
        assert response.status_code == expected_status

    def test_register_returns_tokens(self, api_client, register_url, db):
        data = {
            'username': 'tokenuser',
            'email': 'tokenuser@example.com',
            'password': 'pass123456',
            'password2': 'pass123456',
        }
        response = api_client.post(register_url, data)
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']

    def test_register_duplicate_username(self, api_client, register_url, user):
        data = {
            'username': user.username,
            'email': 'unique@example.com',
            'password': 'pass123',
            'password2': 'pass123',
        }
        response = api_client.post(register_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self, api_client, register_url, user):
        data = {
            'username': 'uniqueuser',
            'email': user.email,
            'password': 'pass123',
            'password2': 'pass123',
        }
        response = api_client.post(register_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# LoginView
# ---------------------------------------------------------------------------

class TestLoginView:

    @pytest.mark.parametrize('credentials,expected_status', [
        ({'username': 'testuser', 'password': 'testpass123'}, status.HTTP_200_OK),
        ({'username': 'testuser', 'password': 'wrongpass'}, status.HTTP_401_UNAUTHORIZED),
        ({'username': 'nouser', 'password': 'testpass123'}, status.HTTP_401_UNAUTHORIZED),
        ({'username': '', 'password': ''}, status.HTTP_401_UNAUTHORIZED),
    ])
    def test_login(self, api_client, login_url, user, credentials, expected_status):
        response = api_client.post(login_url, credentials)
        assert response.status_code == expected_status

    def test_login_returns_tokens(self, api_client, login_url, user):
        response = api_client.post(login_url, {'username': 'testuser', 'password': 'testpass123'})
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']


# ---------------------------------------------------------------------------
# LogoutView
# ---------------------------------------------------------------------------

class TestLogoutView:

    def test_logout_success(self, auth_client, logout_url, refresh_token):
        response = auth_client.post(logout_url, {'refresh': refresh_token})
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize('token', ['invalidtoken', '', '123.456.789'])
    def test_logout_invalid_token(self, auth_client, logout_url, token):
        response = auth_client.post(logout_url, {'refresh': token})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_unauthenticated(self, api_client, logout_url, refresh_token):
        response = api_client.post(logout_url, {'refresh': refresh_token})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# ProfileView
# ---------------------------------------------------------------------------

class TestProfileView:

    def test_get_profile(self, auth_client, profile_url, user):
        response = auth_client.get(profile_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username
        assert response.data['email'] == user.email

    def test_get_profile_unauthenticated(self, api_client, profile_url):
        response = api_client.get(profile_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize('patch_data,field,expected_value', [
        ({'email': 'updated@example.com'}, 'email', 'updated@example.com'),
        ({'date_birth': '2000-01-01'}, 'date_birth', '2000-01-01'),
    ])
    def test_patch_profile(self, auth_client, profile_url, user, patch_data, field, expected_value):
        response = auth_client.patch(profile_url, patch_data)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert str(getattr(user, field)) == expected_value

    def test_delete_profile(self, auth_client, profile_url, user):
        response = auth_client.delete(profile_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(pk=user.pk).exists()

    def test_delete_profile_unauthenticated(self, api_client, profile_url):
        response = api_client.delete(profile_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# UserListView
# ---------------------------------------------------------------------------

class TestUserListView:

    def test_list_returns_all_users(self, auth_client, list_url, user, second_user):
        response = auth_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_list_unauthenticated(self, api_client, list_url):
        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# UserDetailView
# ---------------------------------------------------------------------------

class TestUserDetailView:

    def test_get_user_detail(self, auth_client, user):
        url = reverse('users:user-detail', kwargs={'pk': user.pk})  # роутер генерирует 'user-detail'
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username

    def test_get_user_detail_not_found(self, auth_client):
        url = reverse('users:user-detail', kwargs={'pk': 99999})  # несуществующий int pk
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_user_detail_unauthenticated(self, api_client, user):
        url = reverse('users:user-detail', kwargs={'pk': user.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED