
def test_listing(client, auth):
    auth.login()
    response = client.get('/changelog')
    assert b'Changelog 0.0.3' in response.data
    assert b'Administrator' in response.data
    assert b'Changelog 0.0.2' in response.data
    auth.logout()

    auth.login(mail="simple@user.be")
    response = client.get('/changelog')
    assert b'Changelog 0.0.3' in response.data
    assert b'Simple User' in response.data
    assert b'Changelog 0.0.2' in response.data


def test_login_required(client):
    response = client.get("/changelog")
    assert response.headers["Location"] == "http://localhost/auth/login"


