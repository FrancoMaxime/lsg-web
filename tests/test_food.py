import pytest
from lsg_web.db import get_db


def test_listing(client, auth):

    auth.login(mail="alice@user.be")
    response = client.get('/food/list')
    assert b'Foods' in response.data
    assert b'Alice' in response.data
    assert b'Add a new food' in response.data
    assert b'Super-Water' in response.data
    auth.logout()

    auth.login(mail="simple@user.be")
    response = client.get('/food/list')
    assert b'Foods' in response.data
    assert b'Simple User' in response.data
    assert b'Super-Water' in response.data
    assert b'Add a new food' not in response.data


@pytest.mark.parametrize("path", ("/food/1/update", "/food/create"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_security_required(client, auth):
    assert client.get('/food/list').status_code == 302
    # simple user can't modify or create a food
    auth.login(mail="simple@user.be")
    assert client.post('/food/create').status_code == 403
    assert client.post('/food/1/update').status_code == 403

    # simple user doesn't see edit link
    assert b'href="/food/1/update"' not in client.get("/food/list").data


def test_exists_required(client, auth):
    auth.login()
    assert client.post("/food/25/update").status_code == 404


def test_create(client, auth, app):
    auth.login(mail="alice@user.be")
    assert client.get("/food/create").status_code == 200
    client.post("/food/create", data={"name": "created", "category": 1, "information": "created information"})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id_food) FROM food").fetchone()[0]
        assert count == 6
        food = db.execute("SELECT * FROM food WHERE id_food = 6").fetchone()
        assert food["name"] == "created"
        assert food["id_category"] == 1
        assert food["information"] == "created information"
        assert food["id_person"] == 3


def test_update(client, auth, app):
    auth.login(mail="alice@user.be")
    assert client.get('/food/1/update').status_code == 200
    client.post('/food/1/update', data={"name": "updated", "category": 4, "information": 'information updated'})

    with app.app_context():
        db = get_db()
        food = db.execute('SELECT * FROM food WHERE id_food = 1').fetchone()
        assert food['name'] == 'updated'
        assert food['information'] == 'information updated'
        assert food['id_category'] == 4
        assert food['id_person'] == 3


@pytest.mark.parametrize("path", ("/food/create", "/food/1/update"))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"name": "", "category": "", "information": ""})
    assert b"You must enter a name." in response.data
    response = client.post(path, data={"name": "Created", "category": "", "information": ""})
    assert b"You must enter a category." in response.data
    response = client.post(path, data={"name": "Created", "category": "1", "information": ""})
    assert b"You must enter some information." in response.data
    response = client.post(path, data={"name": "Created", "category": "25", "information": "250"})
    assert b"You must select a valid category." in response.data