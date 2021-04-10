import pytest
from lsg_web.db import get_db
from datetime import datetime


def test_listing(client, auth):
    path = '/meal/list'
    auth.login()
    response = client.get(path)
    assert b'Meals' in response.data
    assert b'Administrator' in response.data
    assert b'Add a new meal' in response.data
    auth.logout()

    auth.login(mail="simple@user.be")
    response = client.get(path)
    assert b'Meals' in response.data
    assert b'Simple User' in response.data
    assert b'Add a new meal' not in response.data


@pytest.mark.parametrize("path", ("/meal/1/update", "/meal/create"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_security_required(client, auth):
    assert client.get('/meal/list').status_code == 302
    # simple user can't modify or create a category
    auth.login(mail="simple@user.be")
    assert client.post('/meal/create').status_code == 403
    assert client.post('/meal/1/update').status_code == 403

    # simple user doesn't see edit link
    assert b'href="/meal/1/update"' not in client.get("/meal/list").data


def test_exists_required(client, auth):
    auth.login()
    assert client.post("/meal/25/update").status_code == 404
    assert client.get("/meal/25/info").status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/meal/create").status_code == 200
    client.post("/meal/create", data={"menu": "1", "person": "3", "tray": 1, "information": "created information"})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id_meal) FROM meal").fetchone()[0]
        assert count == 2
        meal = db.execute('SELECT * FROM meal WHERE id_meal = 2').fetchone()
        assert meal['information'] == 'created information'
        assert meal['id_menu'] == 1
        assert meal['id_candidate'] == 3


def test_update(client, auth, app):
    auth.login()
    assert client.get('/meal/1/update').status_code == 200
    client.post('/meal/1/update', data={"menu": "1", "person": "4", "information": "information updated"})

    with app.app_context():
        db = get_db()
        meal = db.execute('SELECT * FROM meal WHERE id_meal = 1').fetchone()
        assert meal['information'] == 'information updated'
        assert meal['id_menu'] == 1
        assert meal['id_candidate'] == 4


def test_create_validate(client, auth):
    path = "/meal/create"
    auth.login()
    response = client.post(path, data={"menu": "", "person": "3", "tray": 1, "information": "created information"})
    assert b"You must select a menu." in response.data
    response = client.post(path, data={"menu": "1", "person": "", "tray": 1, "information": "created information"})
    assert b"You must select a user." in response.data
    response = client.post(path, data={"menu": "1", "person": "3", "tray": "", "information": "created information"})
    assert b"You must select a tray." in response.data
    response = client.post(path, data={"menu": "1", "person": "3", "tray": 1, "information": ""})
    assert b"You must enter some information." in response.data

    response = client.post(path, data={"menu": "25", "person": "3", "tray": 1, "information": "created information"})
    assert b"You must select a valid menu." in response.data
    response = client.post(path, data={"menu": "1", "person": "25", "tray": 1, "information": "created information"})
    assert b"You must select a valid user." in response.data
    response = client.post(path, data={"menu": "1", "person": "3", "tray": "25", "information": "created information"})
    assert b"You must select a valid tray." in response.data


def test_create_update(client, auth):
    path = "/meal/1/update"
    auth.login()
    response = client.post(path, data={"menu": "", "person": "3", "information": "created information"})
    assert b"You must select a menu." in response.data
    response = client.post(path, data={"menu": "1", "person": "", "information": "created information"})
    assert b"You must select a user." in response.data
    response = client.post(path, data={"menu": "1", "person": "3",  "information": ""})
    assert b"You must enter some information." in response.data

    response = client.post(path, data={"menu": "25", "person": "3",  "information": "created information"})
    assert b"You must select a valid menu." in response.data
    response = client.post(path, data={"menu": "1", "person": "25",  "information": "created information"})
    assert b"You must select a valid user." in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/meal/1/delete')
    assert response.headers['Location'] == 'http://localhost/meal/list'

    with app.app_context():
        db = get_db()
        meal = db.execute('SELECT * FROM meal WHERE id_meal = 1 ').fetchone()
        assert meal['actif'] == 0


def test_finished(client, auth, app):
    auth.login()
    response = client.post('/meal/1/finished')
    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        meal = db.execute('SELECT * FROM meal WHERE id_meal = 1').fetchone()
        assert now <= meal['end']


def test_meal_info(client, auth):
    auth.login(mail="simple@user.be")
    response = client.get('/meal/1/info')
    assert b'Alice' in response.data
    assert b'Super-Menu' in response.data
    assert b'Administrator' in response.data
    assert b'information about Super-Menu' in response.data
    assert b'information about Super-Meal' in response.data
    assert b'/meal/1/download' in response.data


def test_meal_download(client, auth):
    auth.login(mail="simple@user.be")
    response = client.get('/meal/1/download')
    assert response.status_code == 200

    response = client.get('/meal/25/download')
    assert response.status_code == 404