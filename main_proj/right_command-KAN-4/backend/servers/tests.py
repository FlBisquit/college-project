import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Server, ServerMember
from users.models import User


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
def third_user(db):
    return User.objects.create_user(
        username='thirduser',
        email='third@example.com',
        password='thirdpass123',
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def second_auth_client(second_user):
    client = APIClient()
    refresh = RefreshToken.for_user(second_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def third_auth_client(third_user):
    client = APIClient()
    refresh = RefreshToken.for_user(third_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client


@pytest.fixture
def server(db, user):
    s = Server.objects.create(
        name='Test Server',
        description='Test description',
        owner=user,
    )
    ServerMember.objects.create(server=s, user=user, role=ServerMember.Role.OWNER)
    return s


@pytest.fixture
def server_with_member(server, second_user):
    ServerMember.objects.create(server=server, user=second_user, role=ServerMember.Role.MEMBER)
    return server


@pytest.fixture
def list_url():
    return reverse('servers:list')


# ---------------------------------------------------------------------------
# ServerListCreateView
# ---------------------------------------------------------------------------

class TestServerListCreateView:

    def test_list_unauthenticated(self, api_client, list_url):
        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_authenticated(self, auth_client, list_url, server):
        response = auth_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_create_server(self, auth_client, list_url):
        data = {'name': 'New Server', 'description': 'Desc'}
        response = auth_client.post(list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Server'

    def test_create_server_unauthenticated(self, api_client, list_url):
        response = api_client.post(list_url, {'name': 'New Server'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_server_owner_becomes_member(self, auth_client, list_url, user):
        auth_client.post(list_url, {'name': 'New Server'})
        server = Server.objects.get(name='New Server')
        member = ServerMember.objects.get(server=server, user=user)
        assert member.role == ServerMember.Role.OWNER

    @pytest.mark.parametrize('data,expected_status', [
        ({'name': 'Valid Server'}, status.HTTP_201_CREATED),
        ({}, status.HTTP_400_BAD_REQUEST),  # нет name
        ({'name': 'x' * 21}, status.HTTP_400_BAD_REQUEST),  # name > 20 символов
    ])
    def test_create_server_validation(self, auth_client, list_url, data, expected_status, db):
        response = auth_client.post(list_url, data)
        assert response.status_code == expected_status


# ---------------------------------------------------------------------------
# ServerDetailView
# ---------------------------------------------------------------------------

class TestServerDetailView:

    def test_get_server(self, auth_client, server):
        url = reverse('servers:detail', kwargs={'pk': server.pk})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == server.name

    def test_get_server_unauthenticated(self, api_client, server):
        url = reverse('servers:detail', kwargs={'pk': server.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_server_not_found(self, auth_client):
        url = reverse('servers:detail', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_server_by_owner(self, auth_client, server):
        url = reverse('servers:detail', kwargs={'pk': server.pk})
        response = auth_client.patch(url, {'name': 'Updated Name'})
        assert response.status_code == status.HTTP_200_OK
        server.refresh_from_db()
        assert server.name == 'Updated Name'

    def test_update_server_by_non_owner(self, second_auth_client, server):
        url = reverse('servers:detail', kwargs={'pk': server.pk})
        response = second_auth_client.patch(url, {'name': 'Hacked'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_server_by_owner(self, auth_client, server):
        url = reverse('servers:detail', kwargs={'pk': server.pk})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Server.objects.filter(pk=server.pk).exists()

    def test_delete_server_by_non_owner(self, second_auth_client, server):
        url = reverse('servers:detail', kwargs={'pk': server.pk})
        response = second_auth_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# JoinServerView
# ---------------------------------------------------------------------------

class TestJoinServerView:

    def test_join_server(self, second_auth_client, server):
        url = reverse('servers:join', kwargs={'pk': server.pk})
        response = second_auth_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        assert ServerMember.objects.filter(server=server, user__username='otheruser').exists()

    def test_join_server_already_member(self, second_auth_client, server_with_member):
        url = reverse('servers:join', kwargs={'pk': server_with_member.pk})
        response = second_auth_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_join_server_unauthenticated(self, api_client, server):
        url = reverse('servers:join', kwargs={'pk': server.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_join_server_not_found(self, second_auth_client):
        url = reverse('servers:join', kwargs={'pk': '00000000-0000-0000-0000-000000000000'})
        response = second_auth_client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# LeaveServerView
# ---------------------------------------------------------------------------

class TestLeaveServerView:

    def test_leave_server(self, second_auth_client, server_with_member):
        url = reverse('servers:leave', kwargs={'pk': server_with_member.pk})
        response = second_auth_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert not ServerMember.objects.filter(server=server_with_member, user__username='otheruser').exists()

    def test_owner_cannot_leave(self, auth_client, server):
        url = reverse('servers:leave', kwargs={'pk': server.pk})
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_leave_server_unauthenticated(self, api_client, server):
        url = reverse('servers:leave', kwargs={'pk': server.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# ServerMembersView
# ---------------------------------------------------------------------------

class TestServerMembersView:

    def test_get_members(self, auth_client, server_with_member):
        url = reverse('servers:members', kwargs={'pk': server_with_member.pk})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # owner + second_user

    def test_get_members_unauthenticated(self, api_client, server):
        url = reverse('servers:members', kwargs={'pk': server.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# UpdateMemberRoleView
# ---------------------------------------------------------------------------

class TestUpdateMemberRoleView:

    def test_owner_can_set_admin(self, auth_client, server_with_member, second_user):
        url = reverse('servers:member-role', kwargs={'pk': server_with_member.pk, 'user_id': second_user.pk})
        response = auth_client.patch(url, {'role': ServerMember.Role.ADMIN})
        assert response.status_code == status.HTTP_200_OK
        member = ServerMember.objects.get(server=server_with_member, user=second_user)
        assert member.role == ServerMember.Role.ADMIN

    def test_member_cannot_change_role(self, second_auth_client, server_with_member, third_user):
        ServerMember.objects.create(server=server_with_member, user=third_user)
        url = reverse('servers:member-role', kwargs={'pk': server_with_member.pk, 'user_id': third_user.pk})
        response = second_auth_client.patch(url, {'role': ServerMember.Role.ADMIN})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_set_owner_role(self, auth_client, server_with_member, second_user):
        url = reverse('servers:member-role', kwargs={'pk': server_with_member.pk, 'user_id': second_user.pk})
        response = auth_client.patch(url, {'role': ServerMember.Role.OWNER})
        assert response.status_code == status.HTTP_400_BAD_REQUEST