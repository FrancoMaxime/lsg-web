import pytest
from lsg_web.db import get_db


def test_listing(client, auth):

    auth.login()
    response = client.get('/person/list')
    assert b'Persons' in response.data
    assert b'Administrator' in response.data
    assert b'Add a new person' in response.data
    assert b'Alice' in response.data
    assert b'Bob' in response.data
    auth.logout()

    auth.login(mail="simple@user.be")
    response = client.get('/person/list')
    assert b'Persons' in response.data
    assert b'Simple User' in response.data
    assert b'Add a new person' not in response.data
    assert b'Alice' in response.data
    assert b'Bob' in response.data


@pytest.mark.parametrize("path", ("/person/1/update", "/person/create"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_security_required(client, auth):
    assert client.get('/person/list').status_code == 302
    # simple user can't modify or create a person
    auth.login(mail="simple@user.be")
    assert client.post('/person/create').status_code == 403
    assert client.post('/person/1/update').status_code == 403

    # simple user doesn't see edit link
    assert b'href="/person/1/update"' not in client.get("/person/list").data
    assert b'href="/meal/1/update"' not in client.get("/person/1/info").data


def test_exists_required(client, auth):
    auth.login()
    assert client.post("/person/25/update").status_code == 404
    assert client.post("/person/25/delete").status_code == 404
    assert client.post('/person/25/update').status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/person/create").status_code == 200
    client.post("/person/create", data={"name": "created", "birthdate": "1991-08-27", "gender": "homme", "weight": "65"})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id_person) FROM person").fetchone()[0]
        assert count == 7


def test_update(client, auth, app):
    auth.login()
    assert client.get('/person/1/update').status_code == 200
    client.post('/person/1/update',
                data={"name": "updated", "birthdate": "1991-08-27", "gender": "homme", "weight": "65", "actif":1})

    with app.app_context():
        db = get_db()
        person = db.execute('SELECT * FROM person WHERE id_person = 1').fetchone()
        assert person['name'] == 'updated'
        assert person['birthdate'].strftime("%Y-%m-%d") == "1991-08-27"
        assert person['gender'] == "homme"
        assert person['actif'] == 1

    assert client.get('/person/1/update').status_code == 200
    client.post('/person/1/update',
                data={"name": "updated", "birthdate": "1991-08-27", "gender": "homme", "weight": "65"})

    with app.app_context():
        db = get_db()
        person = db.execute('SELECT * FROM person WHERE id_person = 1').fetchone()
        assert person['actif'] == 0


@pytest.mark.parametrize("path", ("/person/create", "/person/1/update"))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"name": "", "birthdate": "1991-08-27", "gender": "homme", "weight": "65", "actif": 1})
    assert b"Name is required." in response.data
    response = client.post(path, data={"name": "Flip", "birthdate": "", "gender": "homme", "weight": "65"})
    assert b"You must enter a valid birthdate." in response.data
    response = client.post(path, data={"name": "Flip", "birthdate": "1991-08-27", "gender": "", "weight": "65"})
    assert b"You must select a gender." in response.data
    response = client.post(path, data={"name": "Flip", "birthdate": "1991-08-27", "gender": "homme", "weight": ""})
    assert b"You must enter a weight." in response.data
    response = client.post(path, data={"name": "Flip", "birthdate": "19999991-08-27", "gender": "homme", "weight": "65"})
    assert b"You must enter a valid birthdate." in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/person/2/delete')
    assert response.headers['Location'] == 'http://localhost/person/list'

    with app.app_context():
        db = get_db()
        person = db.execute('SELECT * FROM person WHERE id_person = 2 ').fetchone()
        assert person['actif'] == 0


def test_info(client, auth):
    auth.login(mail="alice@user.be")
    response = client.get('/person/3/info')
    assert b'Alice' in response.data
    assert b'Super-Menu' in response.data
    assert b'Administrator' in response.data
    assert b'information about Super-Menu' in response.data
    assert b'information about Super-Meal' in response.data
    assert b'/meal/1/info' in response.data
