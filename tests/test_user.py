import pytest
import io
from lsg_web.db import get_db


def test_listing(client, auth):
    auth.login()
    response = client.get('/user/list')
    assert b'Users' in response.data
    assert b'Administrator' in response.data
    assert b'Add a new user' in response.data
    assert b'admin@admin.be' in response.data
    auth.logout()


@pytest.mark.parametrize("path", ("/user/1/update", "/user/create"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_security_required(client, auth):
    assert client.get('/user/list').status_code == 302
    # simple user can't modify or create a category
    auth.login(mail="simple@user.be")
    assert client.post('/user/create').status_code == 403
    assert client.post('/user/1/update').status_code == 403
    assert client.get('/user/list').status_code == 403


def test_exists_required(client, auth):
    auth.login()
    assert client.post("/user/25/update").status_code == 404
    assert client.post("/user/25/delete").status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/user/create").status_code == 200
    client.post("/user/create", data={"person": "4", "mail": "bob@user.be",
                                      "password1": "admin", "password2": "admin", "permission": "1"})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id_user) FROM user").fetchone()[0]
        assert count == 4
        user = db.execute("SELECT * FROM user WHERE id_user= 4").fetchone()
        assert user['filename'] == "administrator.png"

    client.post("/user/create", data={"person": "5", "mail": "justine@user.be",
                                      "password1": "admin", "password2": "admin", "permission": "2"})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id_user) FROM user").fetchone()[0]
        assert count == 5
        user = db.execute("SELECT * FROM user WHERE id_user= 5").fetchone()
        assert user['filename'] == "simple_user.png"
        assert user['id_permission'] == 2

    data = {"person": "6", "mail": "michel@user.be", "password1": "admin", "password2": "admin", "permission": "1"}
    data = {key: str(value) for key, value in data.items()}
    data['image'] = (io.BytesIO(b"abcdef"), 'test.jpg')
    client.post("/user/create", data=data, follow_redirects=True, content_type='multipart/form-data')
    with app.app_context():
        db = get_db()
        user = db.execute("SELECT * FROM user WHERE id_user= 6").fetchone()
        assert user['filename'] == "6.jpg"
        assert user['id_person'] == 6
        assert user['mail'] == "michel@user.be"
        assert user['id_permission'] == 1


def test_update(client, auth, app):
    auth.login()
    assert client.get('/user/1/update').status_code == 200
    client.post('/user/1/update', data={"person": "4", "mail": "bob@user.be",
                                      "password1": "admin", "password2": "admin", "permission": "1"})

    with app.app_context():
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE id_user = 1').fetchone()
        assert user['mail'] == 'bob@user.be'
        assert user['filename'] == "administrator.png"

    data = {"person": "4", "mail": "bob@user.be",
            "password1": "admin", "password2": "admin", "permission": "1", "actif": "0"}
    data = {key: str(value) for key, value in data.items()}
    data['image'] = (io.BytesIO(b"abcdef"), 'test.jpg')
    client.post('/user/1/update', data=data, follow_redirects=True, content_type='multipart/form-data')
    with app.app_context():
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE id_user = 1').fetchone()
        assert user['actif'] == 0
        assert user['filename'] == "1.jpg"


@pytest.mark.parametrize("path", ("/user/create", "/user/1/update"))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"person": "", "mail": "bob@user.be",
                                       "password1": "admin", "password2": "admin", "permission": "1"})
    assert b"The account should be linked to a person." in response.data

    response = client.post(path, data={"person": "4", "mail": "",
                                       "password1": "admin", "password2": "admin", "permission": "1"})
    assert b"Mail is required." in response.data
    response = client.post(path, data={"person": "4", "mail": "bob@user.be",
                                       "password1": "", "password2": "admin1", "permission": "1"})
    assert b"You must enter a password." in response.data
    response = client.post(path, data={"person": "4", "mail": "bob@user.be",
                                       "password1": "admin", "password2": "admin2", "permission": "1"})
    assert b"The passwords must be the same." in response.data
    response = client.post(path, data={"person": "25", "mail": "bob@user.be",
                                       "password1": "admin", "password2": "admin", "permission": "1"})
    assert b"Person id 25 doesn't exist." in response.data

    response = client.post(path, data={"person": "4", "mail": "simple@user.be",
                                       "password1": "admin", "password2": "admin", "permission": "1"})
    assert b"User simple@user.be already registered." in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/user/2/delete')
    assert response.headers['Location'] == 'http://localhost/user/list'

    with app.app_context():
        db = get_db()
        menu = db.execute('SELECT * FROM user WHERE id_user = 2 ').fetchone()
        assert menu['actif'] == 0
    auth.logout()
    auth.login(mail="simple@user.be")
