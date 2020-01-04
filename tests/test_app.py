from amazons.app import create_app
import pytest


@pytest.fixture
def client():
    app = create_app()
    app.debug = True
    return app.test_client()


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200

