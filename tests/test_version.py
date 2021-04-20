import pytest
from lsg_web.db import get_db
from datetime import date


def test_listing(client, auth):

    auth.login()
    response = client.get('/version/list')
    assert b'Versions' in response.data
    assert b'Administrator' in response.data
    assert b'Add a new version' in response.data
    assert b'Alpha 0.0.1a' in response.data
    assert b'Alpha 0.0.2a' in response.data
    auth.logout()


def test_login_required(client):
    assert client.get('/version/list').status_code == 302

    response = client.post('/version/create')
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_security_required(client, auth):
    # simple user can't create a version
    auth.login(mail="simple@user.be")
    assert client.post('/version/create').status_code == 403
    assert client.get('/version/list').status_code == 403


def test_create(client, auth, app):
    auth.login()
    assert client.get("/version/create").status_code == 200
    client.post("/version/create", data={"name": "created", "date": "1991-08-27"})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id_version) FROM version").fetchone()[0]
        assert count == 3
        version = db.execute("SELECT * FROM version WHERE id_version = 3").fetchone()
        assert version["name"] == "created"
        r = date(1991, 8, 27)
        assert version["release_date"] == r


def test_create_validate(client, auth):
    auth.login()
    response = client.post("/version/create", data={"name": "", "date": ""})
    assert b"You must enter a name." in response.data
    response = client.post("/version/create", data={"name": "Floup", "date": ""})
    assert b"You must enter a release date." in response.data
    response = client.post("/version/create", data={"name": "Alpha 0.0.1a", "date": "1991-08-27"})
    assert b"This version already exists." in response.data
    response = client.post("/version/create", data={"name": "Floup", "date": "1999991-08-27"})
    assert b"You must enter a valid date." in response.data