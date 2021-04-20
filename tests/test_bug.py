import pytest
from lsg_web.db import get_db
from datetime import date


def test_listing(client, auth):

    auth.login()
    response = client.get('/bug/list')
    assert b'Bugs/Suggestions' in response.data
    assert b'Administrator' in response.data
    assert b'Add a new bug' in response.data
    assert b'information about Super-Bug' in response.data
    auth.logout()

    auth.login(mail="simple@user.be")
    response = client.get('/bug/list')
    assert b'Bugs/Suggestions' in response.data
    assert b'Simple User' in response.data
    assert b'Add a new bug' in response.data
    assert b'information about Super-Bug' in response.data


def test_login_required(client):
    response = client.post("bug/create")
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_security_required(client, auth):
    assert client.get('/bug/list').status_code == 302
    auth.login(mail="simple@user.be")
    # simple user doesn't see edit link
    assert b'href="/bug/1/delete"' not in client.get("/bug/list").data


def test_exists_required(client, auth):
    auth.login()
    assert client.post("/bug/25/delete").status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/bug/create").status_code == 200
    client.post("/bug/create", data={"title": "created", "information": "information about the bug"})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id_bug) FROM bug").fetchone()[0]
        assert count == 2
        bug = db.execute("SELECT * FROM bug WHERE id_bug = 2").fetchone()
        now = date.today()
        assert bug["title"] == "created"
        assert bug["information"] == "information about the bug"
        assert bug["corrected"] == 0
        assert bug["bug_date"] == now


def test_create_validate(client, auth):
    path = "/bug/create"
    auth.login()
    response = client.post(path, data={"title": "", "information": "information about the bug"})
    assert b"You must enter a title." in response.data
    response = client.post(path, data={"title": "created", "information": ""})
    assert b"You must enter some information." in response.data
    response = client.post(path, data={"title": "Super-Bug", "information": "information about the bug"})
    assert b"This title already exists." in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/bug/1/delete')
    assert response.headers['Location'] == 'http://localhost/bug/list'

    with app.app_context():
        db = get_db()
        bug = db.execute('SELECT * FROM bug WHERE id_bug = 1 ').fetchone()
        assert bug['corrected'] == 1