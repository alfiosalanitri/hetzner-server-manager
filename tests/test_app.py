import pytest
from unittest.mock import patch, MagicMock
from app import app, get_hcloud_client
from models import Project, Server
from flask import url_for

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF
    with app.test_client() as client:
        yield client

class FakeProject:
    id = 1
    name = "TestProject"
    encrypted_api_token = b"encryptedtoken"

# Mock client Hetzner
class FakeHetznerClient:
    class servers:
        @staticmethod
        def get_all():
            return [
                Server(id=1, name="alpha"),
                Server(id=2, name="beta"),
            ]
        @staticmethod
        def get_by_id(server_id):
            fake_server = MagicMock()
            fake_server.name = f"server-{server_id}"
            fake_server.power_on = MagicMock()
            fake_server.shutdown = MagicMock()
            fake_server.reboot = MagicMock()
            return fake_server

@patch('app.decrypt_token', return_value="fake_token")
@patch('app.db.session.get', return_value=FakeProject())
def test_get_hcloud_client(mock_db_get, mock_decrypt):
    client = get_hcloud_client(1)
    assert client is not None
    mock_decrypt.assert_called_once()

@patch('app.get_hcloud_client', return_value=FakeHetznerClient())
@patch('app.db.session.get', return_value=FakeProject())
def test_project_route_with_servers(mock_db_get, mock_client, client):
    response = client.get('/project/1')
    assert response.status_code == 200
    data = response.get_data(as_text=True)
    assert "alpha" in data
    assert "beta" in data

@patch('app.get_hcloud_client', return_value=FakeHetznerClient())
@patch('app.db.session.get', return_value=FakeProject())
def test_server_action_poweron(mock_db_get, mock_client, client):
    response = client.post('/project/1/server/1/poweron', follow_redirects=True)
    assert response.status_code == 200

@patch('app.get_hcloud_client', return_value=None)
def test_server_action_invalid_client(client):
    response = client.post('/project/1/server/1/poweron', follow_redirects=True)
    assert b"Could not perform action" in response.data
