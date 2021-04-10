def test_index(client, auth):
    response = client.get('/')
    assert b"Redirecting..." in response.data
    assert b"/auth/login" in response.data

    auth.login()
    response = client.get('/')
    assert b'Active Meals' in response.data
    assert b'Administrator' in response.data
    assert b'Add a new meal' in response.data
    auth.logout()

    auth.login(mail="simple@user.be")
    response = client.get('/')
    assert b'Active Meals' in response.data
    assert b'Simple User' in response.data
    assert b'Add a new meal' not in response.data

