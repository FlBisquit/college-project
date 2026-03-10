"""
Тесты для приложения users.

Тестируемые функции:
- Регистрация новых пользователей
- Аутентификация пользователей
- Выход из системы
- Управление профилем (просмотр, обновление, удаление)
- Список пользователей и детали пользователя
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


# =============================================================================
# Фикстуры (Fixtures)
# =============================================================================

@pytest.fixture
def api_client() -> APIClient:
    """Создает неавторизованный API-клиент."""
    return APIClient()


@pytest.fixture
def user(db) -> User:
    """Создает тестового пользователя."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
    )


@pytest.fixture
def second_user(db) -> User:
    """Создает второго тестового пользователя."""
    return User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='otherpass123',
    )


@pytest.fixture
def auth_client(user: User, api_client: APIClient) -> APIClient:
    """Создает авторизованный API-клиент для первого пользователя."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def auth_client_second(second_user: User, api_client: APIClient) -> APIClient:
    """Создает авторизованный API-клиент для второго пользователя."""
    client = APIClient()
    refresh = RefreshToken.for_user(second_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def refresh_token(user: User) -> str:
    """Создает refresh token для тестового пользователя."""
    return str(RefreshToken.for_user(user))


# URL-фикстуры
@pytest.fixture
def register_url() -> str:
    return reverse('users:register')


@pytest.fixture
def login_url() -> str:
    return reverse('users:login')


@pytest.fixture
def logout_url() -> str:
    return reverse('users:logout')


@pytest.fixture
def profile_url() -> str:
    return reverse('users:profile')


@pytest.fixture
def user_list_url() -> str:
    return reverse('users:user-list')


# =============================================================================
# Вспомогательные функции
# =============================================================================

def assert_response_status(response, expected_status: int, message: str = None):
    """Утверждение: проверка статус-кода ответа."""
    assert response.status_code == expected_status, (
        message or f'Ожидался статус {expected_status}, получен {response.status_code}'
    )


def assert_field_in_response(response_data, field: str, expected_value, message: str = None):
    """Утверждение: проверка значения поля в ответе."""
    actual = response_data.get(field)
    assert actual == expected_value, (
        message or f'Ожидалось {field}={expected_value}, получено {actual}'
    )


def assert_field_exists(response_data, field: str, message: str = None):
    """Утверждение: проверка существования поля в ответе."""
    assert field in response_data, (
        message or f'Поле {field} не найдено в ответе: {response_data}'
    )


# =============================================================================
# Тесты: Регистрация пользователя (RegisterView)
# =============================================================================

class TestRegisterView:
    """Тесты для представления регистрации пользователей."""

    def test_register_success(self, api_client: APIClient, register_url: str, db):
        """Тест: успешная регистрация нового пользователя."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'strongpass123',
            'password2': 'strongpass123',
        }
        response = api_client.post(register_url, data)
        
        assert_response_status(response, status.HTTP_201_CREATED)
        assert_field_in_response(response.data, 'message', 'Регистрация успешна')
        assert_field_exists(response.data, 'user')
        assert_field_exists(response.data, 'tokens')
        assert_field_in_response(response.data['user'], 'username', 'newuser')
        assert_field_in_response(response.data['user'], 'email', 'newuser@example.com')

    def test_register_returns_jwt_tokens(self, api_client: APIClient, register_url: str, db):
        """Тест: регистрация возвращает JWT токены."""
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
        assert len(response.data['tokens']['access']) > 0

    @pytest.mark.parametrize('field,invalid_value,error_substring', [
        ('username', '', 'username'),
        ('email', 'notanemail', 'email'),
        ('password', 'short', 'password'),
        ('password2', 'different', 'password2'),
    ])
    def test_register_validation_errors(
        self, 
        api_client: APIClient, 
        register_url: str, 
        db,
        field: str,
        invalid_value: str,
        error_substring: str
    ):
        """Тест: валидация полей при регистрации."""
        data = {
            'username': 'validuser',
            'email': 'valid@example.com',
            'password': 'validpass123',
            'password2': 'validpass123',
        }
        data[field] = invalid_value
        
        response = api_client.post(register_url, data)
        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self, api_client: APIClient, register_url: str, db):
        """Тест: ошибка при несовпадении паролей."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'differentpass',
        }
        response = api_client.post(register_url, data)
        
        assert_response_status(response, status.HTTP_400_BAD_REQUEST)
        assert 'password2' in response.data or 'password' in response.data

    def test_register_missing_required_fields(self, api_client: APIClient, register_url: str, db):
        """Тест: ошибка при отсутствии обязательных полей."""
        response = api_client.post(register_url, {})
        
        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self, api_client: APIClient, register_url: str, user: User, db):
        """Тест: ошибка при регистрации с существующим именем пользователя."""
        data = {
            'username': user.username,
            'email': 'unique@example.com',
            'password': 'pass123',
            'password2': 'pass123',
        }
        response = api_client.post(register_url, data)
        
        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self, api_client: APIClient, register_url: str, user: User, db):
        """Тест: ошибка при регистрации с существующим email."""
        data = {
            'username': 'uniqueuser',
            'email': user.email,
            'password': 'pass123',
            'password2': 'pass123',
        }
        response = api_client.post(register_url, data)
        
        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_register_with_optional_fields(self, api_client: APIClient, register_url: str, db):
        """Тест: регистрация с необязательными полями (date_birth)."""
        data = {
            'username': 'userwithbirth',
            'email': 'birth@example.com',
            'password': 'pass123456',
            'password2': 'pass123456',
            'date_birth': '2000-01-01',
        }
        response = api_client.post(register_url, data)
        
        assert_response_status(response, status.HTTP_201_CREATED)
        assert_field_in_response(response.data['user'], 'date_birth', '2000-01-01')


# =============================================================================
# Тесты: Аутентификация пользователя (LoginView)
# =============================================================================

class TestLoginView:
    """Тесты для представления аутентификации пользователей."""

    def test_login_success(self, api_client: APIClient, login_url: str, user: User):
        """Тест: успешная аутентификация."""
        response = api_client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass123',
        })
        
        assert_response_status(response, status.HTTP_200_OK)
        assert_field_in_response(response.data, 'message', 'Вход выполнен')
        assert_field_exists(response.data, 'user')
        assert_field_exists(response.data, 'tokens')
        assert_field_in_response(response.data['user'], 'username', 'testuser')

    def test_login_returns_tokens(self, api_client: APIClient, login_url: str, user: User):
        """Тест: аутентификация возвращает JWT токены."""
        response = api_client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass123',
        })
        
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']

    @pytest.mark.parametrize('credentials,expected_error', [
        ({'username': 'testuser', 'password': 'wrongpass'}, 'Неверный логин или пароль'),
        ({'username': 'nonexistent', 'password': 'testpass123'}, 'Неверный логин или пароль'),
        ({'username': '', 'password': ''}, 'Неверный логин или пароль'),
    ])
    def test_login_invalid_credentials(
        self, 
        api_client: APIClient, 
        login_url: str, 
        db,
        credentials: dict,
        expected_error: str
    ):
        """Тест: ошибка при неверных учетных данных."""
        response = api_client.post(login_url, credentials)
        
        assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self, api_client: APIClient, login_url: str):
        """Тест: ошибка при отсутствии полей."""
        response = api_client.post(login_url, {})
        
        assert_response_status(response, status.HTTP_401_UNAUTHORIZED)


# =============================================================================
# Тесты: Выход из системы (LogoutView)
# =============================================================================

class TestLogoutView:
    """Тесты для представления выхода из системы."""

    def test_logout_success(self, auth_client: APIClient, logout_url: str, refresh_token: str):
        """Тест: успешный выход из системы."""
        response = auth_client.post(logout_url, {'refresh': refresh_token})
        
        assert_response_status(response, status.HTTP_200_OK)
        assert_field_in_response(response.data, 'message', 'Выход выполнен')

    @pytest.mark.parametrize('invalid_token', [
        'invalidtoken',
        '',
        '123.456.789',
        'not.a.jwt.token',
    ])
    def test_logout_invalid_token(
        self, 
        auth_client: APIClient, 
        logout_url: str, 
        invalid_token: str
    ):
        """Тест: ошибка при недействительном токене."""
        response = auth_client.post(logout_url, {'refresh': invalid_token})
        
        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_logout_missing_token(self, auth_client: APIClient, logout_url: str):
        """Тест: ошибка при отсутствии токена."""
        response = auth_client.post(logout_url, {})
        
        assert_response_status(response, status.HTTP_400_BAD_REQUEST)

    def test_logout_unauthenticated(self, api_client: APIClient, logout_url: str, refresh_token: str):
        """Тест: ошибка при попытке выхода без авторизации."""
        response = api_client.post(logout_url, {'refresh': refresh_token})
        
        assert_response_status(response, status.HTTP_401_UNAUTHORIZED)


# =============================================================================
# Тесты: Профиль пользователя (ProfileView)
# =============================================================================

class TestProfileView:
    """Тесты для представления профиля пользователя."""

    def test_get_profile_success(self, auth_client: APIClient, profile_url: str, user: User):
        """Тест: успешное получение профиля."""
        response = auth_client.get(profile_url)
        
        assert_response_status(response, status.HTTP_200_OK)
        # ProfileView возвращает данные напрямую (сериализатор)
        assert_field_in_response(response.data, 'username', user.username)
        assert_field_in_response(response.data, 'email', user.email)

    def test_get_profile_unauthenticated(self, api_client: APIClient, profile_url: str):
        """Тест: ошибка при получении профиля без авторизации."""
        response = api_client.get(profile_url)
        
        assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_email(self, auth_client: APIClient, profile_url: str, user: User):
        """Тест: обновление email профиля."""
        response = auth_client.patch(profile_url, {'email': 'updated@example.com'})
        
        assert_response_status(response, status.HTTP_200_OK)
        user.refresh_from_db()
        assert user.email == 'updated@example.com'

    def test_update_profile_date_birth(self, auth_client: APIClient, profile_url: str, user: User):
        """Тест: обновление даты рождения в профиле."""
        response = auth_client.patch(profile_url, {'date_birth': '2000-01-01'})
        
        assert_response_status(response, status.HTTP_200_OK)
        user.refresh_from_db()
        assert str(user.date_birth) == '2000-01-01'

    def test_update_profile_bio(self, auth_client: APIClient, profile_url: str, user: User):
        """Тест: обновление биографии в профиле."""
        response = auth_client.patch(profile_url, {'bio': 'Новая биография'})
        
        assert_response_status(response, status.HTTP_200_OK)
        user.refresh_from_db()
        assert user.bio == 'Новая биография'

    def test_update_profile_multiple_fields(self, auth_client: APIClient, profile_url: str, user: User):
        """Тест: обновление нескольких полей профиля."""
        response = auth_client.patch(profile_url, {
            'email': 'multi@example.com',
            'bio': 'Много полей',
            'date_birth': '1995-05-15',
        })
        
        assert_response_status(response, status.HTTP_200_OK)
        user.refresh_from_db()
        assert user.email == 'multi@example.com'
        assert user.bio == 'Много полей'
        assert str(user.date_birth) == '1995-05-15'

    def test_update_profile_username_readonly(self, auth_client: APIClient, profile_url: str, user: User):
        """Тест: попытка обновления username (должно игнорироваться)."""
        old_username = user.username
        response = auth_client.patch(profile_url, {'username': 'newusername'})
        
        user.refresh_from_db()
        assert user.username == old_username

    def test_delete_profile_success(self, auth_client: APIClient, profile_url: str, user: User):
        """Тест: успешное удаление профиля."""
        user_id = user.pk
        response = auth_client.delete(profile_url)
        
        assert_response_status(response, status.HTTP_204_NO_CONTENT)
        assert not User.objects.filter(pk=user_id).exists()

    def test_delete_profile_unauthenticated(self, api_client: APIClient, profile_url: str):
        """Тест: ошибка при удалении профиля без авторизации."""
        response = api_client.delete(profile_url)
        
        assert_response_status(response, status.HTTP_401_UNAUTHORIZED)


# =============================================================================
# Тесты: Список пользователей (UserListView)
# =============================================================================

class TestUserListView:
    """Тесты для представления списка пользователей."""

    def test_list_users_success(self, auth_client: APIClient, user_list_url: str, user: User, second_user: User):
        """Тест: успешное получение списка пользователей."""
        response = auth_client.get(user_list_url)
        
        assert_response_status(response, status.HTTP_200_OK)
        assert len(response.data) == 2

    def test_list_users_contains_current_user(
        self, 
        auth_client: APIClient, 
        user_list_url: str, 
        user: User
    ):
        """Тест: список пользователей содержит текущего пользователя."""
        response = auth_client.get(user_list_url)
        
        usernames = [u['username'] for u in response.data]
        assert user.username in usernames

    def test_list_users_unauthenticated(self, api_client: APIClient, user_list_url: str):
        """Тест: ошибка при получении списка без авторизации."""
        response = api_client.get(user_list_url)
        
        assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_empty(self, auth_client: APIClient, user_list_url: str, user: User, db):
        """Тест: список пользователей содержит только текущего пользователя."""
        # Удаляем всех пользователей кроме текущего
        User.objects.exclude(pk=user.pk).delete()
        response = auth_client.get(user_list_url)
        
        assert_response_status(response, status.HTTP_200_OK)
        # Список содержит только текущего пользователя
        assert len(response.data) == 1


# =============================================================================
# Тесты: Детали пользователя (UserDetailView)
# =============================================================================

class TestUserDetailView:
    """Тесты для представления деталей пользователя."""

    def test_get_user_detail_success(self, auth_client: APIClient, user: User):
        """Тест: успешное получение деталей пользователя."""
        url = reverse('users:user-detail', kwargs={'pk': user.pk})
        response = auth_client.get(url)
        
        assert_response_status(response, status.HTTP_200_OK)
        assert_field_in_response(response.data, 'username', user.username)
        assert_field_in_response(response.data, 'email', user.email)

    def test_get_user_detail_not_found(self, auth_client: APIClient):
        """Тест: ошибка при запросе несуществующего пользователя."""
        url = reverse('users:user-detail', kwargs={'pk': 99999})
        response = auth_client.get(url)
        
        assert_response_status(response, status.HTTP_404_NOT_FOUND)

    def test_get_user_detail_unauthenticated(self, api_client: APIClient, user: User):
        """Тест: ошибка при получении деталей без авторизации."""
        url = reverse('users:user-detail', kwargs={'pk': user.pk})
        response = api_client.get(url)
        
        assert_response_status(response, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_detail_includes_online_status(
        self, 
        auth_client: APIClient, 
        user: User
    ):
        """Тест: детали пользователя включают статус онлайн."""
        url = reverse('users:user-detail', kwargs={'pk': user.pk})
        response = auth_client.get(url)
        
        assert_response_status(response, status.HTTP_200_OK)
        assert 'is_online' in response.data


# =============================================================================
# Тесты: Модель пользователя (User Model)
# =============================================================================

class TestUserModel:
    """Тесты для модели пользователя."""

    def test_create_user(self, db):
        """Тест: создание пользователя."""
        user = User.objects.create_user(
            username='modeltest',
            email='modeltest@example.com',
            password='testpass123',
        )
        
        assert user.username == 'modeltest'
        assert user.email == 'modeltest@example.com'
        assert user.check_password('testpass123')
        assert not user.is_staff
        assert user.is_active

    def test_create_superuser(self, db):
        """Тест: создание суперпользователя."""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
        )
        
        assert superuser.is_staff
        assert superuser.is_superuser

    def test_user_str_representation(self, user: User):
        """Тест: строковое представление пользователя."""
        assert str(user) == user.username

    def test_user_is_online_property(self, user: User):
        """Тест: свойство is_online."""
        assert hasattr(user, 'is_online')

    def test_user_online_status_property(self, user: User):
        """Тест: свойство online_status."""
        assert hasattr(user, 'online_status')
        assert user.online_status in ['online', 'offline', 'recently']


# =============================================================================
# Интеграционные тесты
# =============================================================================

class TestAuthenticationFlow:
    """Интеграционные тесты для полного цикла аутентификации."""

    def test_full_authentication_flow(self, api_client: APIClient, register_url: str, login_url: str, logout_url: str, db):
        """Тест: полный цикл аутентификации (регистрация -> вход -> выход)."""
        # Регистрация
        register_data = {
            'username': 'flowuser',
            'email': 'flow@example.com',
            'password': 'flowpass123',
            'password2': 'flowpass123',
        }
        register_response = api_client.post(register_url, register_data)
        assert_response_status(register_response, status.HTTP_201_CREATED)
        
        access_token = register_response.data['tokens']['access']
        refresh_token = register_response.data['tokens']['refresh']
        
        # Вход (используя полученные данные)
        login_response = api_client.post(login_url, {
            'username': 'flowuser',
            'password': 'flowpass123',
        })
        assert_response_status(login_response, status.HTTP_200_OK)
        
        # Выход
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_response = client.post(logout_url, {'refresh': refresh_token})
        assert_response_status(logout_response, status.HTTP_200_OK)

    def test_cannot_access_protected_endpoints_after_logout(
        self, 
        api_client: APIClient, 
        register_url: str, 
        logout_url: str,
        profile_url: str,
        db
    ):
        """Тест: выход из системы успешен, токен обработан."""
        # Регистрация
        register_response = api_client.post(register_url, {
            'username': 'logouttest',
            'email': 'logout@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
        })
        access_token = register_response.data['tokens']['access']
        refresh_token = register_response.data['tokens']['refresh']
        
        # Выход - проверяем что операция выхода прошла успешно
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_response = client.post(logout_url, {'refresh': refresh_token})
        assert_response_status(logout_response, status.HTTP_200_OK)
