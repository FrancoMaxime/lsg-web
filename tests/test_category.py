import pytest
from lsg_web.db import get_db


def test_listing(client, auth):

    auth.login()
    response = client.get('/category/list')
    assert b'Categories' in response.data
    assert b'Administrator' in response.data
    assert b'Add a new category' in response.data
    assert b'Drink' in response.data
    auth.logout()

    auth.login(mail="simple@user.be")
    response = client.get('/category/list')
    assert b'Categories' in response.data
    assert b'Simple User' in response.data
    assert b'Add a new category' not in response.data
    assert b'Drink' in response.data


@pytest.mark.parametrize("path", ("/category/1/update", "/category/create"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_security_required(client, auth):
    assert client.get('/category/list').status_code == 302
    # simple user can't modify or create a category
    auth.login(mail="simple@user.be")
    assert client.post('/category/create').status_code == 403
    assert client.post('/category/1/update').status_code == 403

    # simple user doesn't see edit link
    assert b'href="/category/1/update"' not in client.get("/category/list").data


def test_exists_required(client, auth):
    auth.login()
    assert client.post("/category/25/update").status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/category/create").status_code == 200
    client.post("/category/create", data={"name": "created"})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id_category) FROM category").fetchone()[0]
        assert count == 8


def test_update(client, auth, app):
    auth.login()
    assert client.get('/category/1/update').status_code == 200
    client.post('/category/1/update', data={"name": "updated"})

    with app.app_context():
        db = get_db()
        category = db.execute('SELECT * FROM category WHERE id_category = 1').fetchone()
        assert category['name'] == 'updated'


@pytest.mark.parametrize("path", ("/category/create", "/category/1/update"))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"name": ""})
    assert b"You must enter a name." in response.data
    response = client.post(path, data={"name": "Drink"})
    assert b"This category already exists." in response.data
