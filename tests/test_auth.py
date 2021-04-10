import pytest
from flask import g, session


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['id_user'] == 1
        assert g.user['mail'] == 'admin@admin.be'


@pytest.mark.parametrize(('mail', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('admin@admin.be', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, mail, password, message):
    response = auth.login(mail, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session