from lsg_web import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_running(client):
    response = client.get('/running')
    assert response.data == b'Server is running'