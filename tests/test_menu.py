import pytest
from lsg_web.db import get_db


def test_listing(client, auth):

    auth.login(mail="alice@user.be")
    response = client.get('/menu/list')
    assert b'Menus' in response.data
    assert b'Alice' in response.data
    assert b'Add a new menu' in response.data
    assert b'Super-Menu' in response.data
    assert b'Administrator' in response.data
    assert b'information about Super-Menu' in response.data
    auth.logout()

    auth.login(mail="simple@user.be")
    response = client.get('/menu/list')
    assert b'Menus' in response.data
    assert b'Simple User' in response.data
    assert b'Super-Menu' in response.data
    assert b'information about Super-Menu' in response.data
    assert b'Add a new menu' not in response.data


@pytest.mark.parametrize("path", ("/menu/1/update", "/menu/create", "/menu/1/add", "/menu/1/1/remove", "/menu/1/copy"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_security_required(client, auth):
    # simple user can't modify or create a category
    auth.login(mail="simple@user.be")
    assert client.post('/menu/create').status_code == 403
    assert client.post('/menu/1/update').status_code == 403
    assert client.post('/menu/1/add').status_code == 403
    assert client.post('/menu/1/copy').status_code == 403
    assert client.post('/menu/1/1/remove').status_code == 403

    # simple user doesn't see edit link
    assert b'href="/menu/1/update"' not in client.get("/menu/list").data
    assert b'href="/menu/1/add"' not in client.get("/menu/1/info").data
    assert b'href="/menu/1/copy"' not in client.get("/menu/1/info").data


def test_exists_required(client, auth):
    assert client.get('/menu/list').status_code == 302
    auth.login()
    assert client.post("/menu/25/update").status_code == 404
    assert client.post("/menu/25/add").status_code == 404
    assert client.post("/menu/25/copy").status_code == 404
    assert client.post("/menu/1/25/update").status_code == 404
    assert client.post("/menu/25/1/update").status_code == 404
    assert client.post("/menu/25/25/update").status_code == 404
    assert client.post("/menu/25/delete").status_code == 404
    assert client.get("/menu/25/info").status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/menu/create").status_code == 200
    client.post("/menu/create", data={"name": "created", "information": "information created"})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id_menu) FROM menu").fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get('/menu/1/update').status_code == 200
    client.post('/menu/1/update', data={"name": "updated", "information": "information updated", "actif": 0})
    with app.app_context():
        db = get_db()
        menu = db.execute('SELECT * FROM menu WHERE id_menu = 1').fetchone()
        assert menu['name'] == 'updated'
        assert menu['information'] == 'information updated'
        assert menu['actif'] == 0

    assert client.get('/menu/1/update').status_code == 200
    client.post('/menu/1/update', data={"name": "updated", "information": "information updated", "actif": 1})
    with app.app_context():
        db = get_db()
        category = db.execute('SELECT * FROM menu WHERE id_menu = 1').fetchone()
        assert category['actif'] == 1


@pytest.mark.parametrize("path", ("/menu/create", "/menu/1/update"))
def test_create_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"name": "", "information": ""})
    assert b"You must enter a name." in response.data
    response = client.post(path, data={"name": "Created", "information": ""})
    assert b"You must enter some information." in response.data


def test_listing_composed(client, auth):

    auth.login(mail="alice@user.be")
    response = client.get('/menu/1/info')
    assert b'Alice' in response.data
    assert b'Add a new component' in response.data
    assert b'Super-Menu' in response.data
    assert b'Administrator' in response.data
    assert b'information about Super-Menu' in response.data
    assert b'Super-Water' in response.data
    assert b'Super-Meat' in response.data
    auth.logout()

    auth.login(mail="simple@user.be")
    response = client.get('/menu/1/info')
    assert b'Alice' in response.data
    assert b'Add a new component' not in response.data
    assert b'Super-Menu' in response.data
    assert b'Simple User' in response.data
    assert b'information about Super-Menu' in response.data
    assert b'Super-Water' in response.data
    assert b'Super-Meat' in response.data


def test_create_validate_composed(client, auth):
    auth.login()
    response = client.post("/menu/1/add", data={"food": "", "quantity": ""})
    assert b"You must select a food." in response.data
    response = client.post("/menu/1/add", data={"food": "1", "quantity": ""})
    assert b"You must enter a quantity." in response.data
    response = client.post("/menu/1/add", data={"food": "25", "quantity": "250"})
    assert b"Food does not exist." in response.data
    response = client.post("/menu/1/add", data={"food": "1", "quantity": "100"})
    assert b"Food is already in the menu." in response.data


def test_update_validate_composed(client, auth):
    auth.login()
    assert client.get('/menu/1/1/update').status_code == 200
    response = client.post("/menu/1/1/update", data={"quantity": ""})
    assert b"You must enter a quantity." in response.data
    response = client.post("/menu/1/25/update", data={"quantity": ""})
    assert b"The food 1 doesn't exist for the menu 25." in response.data


def test_update_composed(client, auth, app):
    auth.login()
    assert client.get('/menu/1/1/update').status_code == 200
    client.post('/menu/1/1/update', data={"quantity": "20000"})
    with app.app_context():
        db = get_db()
        composed = db.execute('SELECT * FROM composed WHERE id_menu = 1 AND id_food = 1').fetchone()
        assert composed['quantity'] == 20000


@pytest.mark.parametrize('path', ('/2/update', '/2/delete',))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_delete_composed(client, auth, app):
    auth.login()
    response = client.post('/menu/1/1/remove')
    assert response.headers['Location'] == 'http://localhost/menu/1/info'

    with app.app_context():
        db = get_db()
        composed = db.execute('SELECT * FROM composed WHERE id_menu = 1 AND id_food = 1').fetchone()
        assert composed is None


def test_delete_menu(client, auth, app):
    auth.login()
    response = client.post('/menu/1/delete')
    assert response.headers['Location'] == 'http://localhost/menu/list'

    with app.app_context():
        db = get_db()
        menu = db.execute('SELECT * FROM menu WHERE id_menu = 1 ').fetchone()
        assert menu['actif'] == 0


def test_create_composed(client, auth, app):
    auth.login()
    assert client.get('menu/1/add').status_code == 200
    client.post('menu/1/add', data={"food": "4", "quantity": "250"})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(quantity) FROM composed WHERE id_menu = 1').fetchone()[0]
        assert count == 3


def test_copy_menu(client, auth, app):
    auth.login()
    response = client.post('/menu/1/copy')
    assert response.headers['Location'] == 'http://localhost/menu/2/info'

    with app.app_context():
        db = get_db()
        menu = db.execute('SELECT * FROM menu WHERE id_menu = 2 ').fetchone()
        assert menu['name'] == 'Super-Menu_copy'
        assert menu['information'] == 'information about Super-Menu'
        assert menu['actif'] == 1
        assert menu['id_person'] == 1

        composed = db.execute('SELECT * FROM composed WHERE id_menu = 2').fetchall()
        assert composed[0]["id_food"] == 1
        assert composed[0]["quantity"] == 150
        assert composed[1]["id_food"] == 2
        assert composed[1]["quantity"] == 300
