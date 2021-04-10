import pytest
from lsg_web.db import get_db
import io


def test_listing(client, auth):
    auth.login()
    response = client.get('/tray/list')
    assert b'Trays' in response.data
    assert b'Administrator' in response.data
    assert b'Add a new tray' in response.data
    assert b'Super-Tray II' in response.data
    assert b'Super-Tray ' in response.data
    auth.logout()


@pytest.mark.parametrize("path", ("/tray/1/update", "/tray/create"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_security_required(client, auth):
    assert client.get('/tray/list').status_code == 302
    assert client.get('/tray/connect').status_code == 405
    # simple user can't modify or create a category
    auth.login(mail="simple@user.be")
    assert client.post('/tray/create').status_code == 403
    assert client.post('/tray/1/update').status_code == 403
    assert client.post('/tray/1/delete').status_code == 403
    assert client.get('/tray/list').status_code == 403


def test_exists_required(client, auth):
    auth.login()
    assert client.post("/tray/25/update").status_code == 404
    assert client.post("/tray/25/delete").status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/tray/create").status_code == 200
    client.post("/tray/create", data={"name": "created", "version": "1", "information": "information created"})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id_tray) FROM tray").fetchone()[0]
        assert count == 3
        tray = db.execute("SELECT * FROM tray WHERE id_tray = 3").fetchone()
        assert tray['name'] == "created"
        assert tray['information'] == "information created"
        assert tray['id_version'] == 1


def test_update(client, auth, app):
    auth.login()
    assert client.get('/tray/1/update').status_code == 200
    client.post('/tray/1/update', data={"name": "updated", "version": "2", "information": "information updated", "actif": 0})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id_tray) FROM tray").fetchone()[0]
        assert count == 2
        tray = db.execute("SELECT * FROM tray WHERE id_tray = 1").fetchone()
        assert tray['name'] == "updated"
        assert tray['information'] == "information updated"
        assert tray['id_version'] == 2
        assert tray['actif'] == 0


@pytest.mark.parametrize("path", ("/tray/create", "/tray/1/update"))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"name": "", "version": "1", "information": "information created"})
    assert b"You must enter a name." in response.data
    response = client.post(path, data={"name": "created", "version": "", "information": "information created"})
    assert b"You must enter a version." in response.data
    response = client.post(path, data={"name": "created", "version": "1", "information": ""})
    assert b"You must enter some information." in response.data
    response = client.post(path, data={"name": "created", "version": "25", "information": "Flibidididi"})
    assert b"You must select a valid version." in response.data
    response = client.post(path, data={"name": "Super-Tray II", "version": "1", "information": "Flibidididi"})
    assert b"Tray Super-Tray II is already registered." in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/tray/2/delete')
    assert response.headers['Location'] == 'http://localhost/tray/list'

    with app.app_context():
        db = get_db()
        tray = db.execute('SELECT * FROM tray WHERE id_tray = 2 ').fetchone()
        assert tray['actif'] == 0


def test_connect(client, app):
    client.post('/tray/connect', data={"name": "Super-Tray II", "ip": "192.168.1.1"})

    with app.app_context():
        db = get_db()
        tray = db.execute('SELECT * FROM tray WHERE id_tray = 2 ').fetchone()
        assert tray['online'] == 1
        assert tray['ip'] == "192.168.1.1"


def test_connect_validate(client):
    response = client.post('/tray/connect', data={"name": "Super-Mag II", "ip": "192.168.1.1"})
    assert response.status_code == 400


def test_data(client, auth, app):
    data = {"name": "Super-Tray II", "ip": "192.168.1.1"}
    data = {key: str(value) for key, value in data.items()}
    data['image'] = (io.BytesIO(b"abcdef"), 'test.jpg')
    data['data'] = (io.BytesIO(b"abcdef"), '1.csv')
    response = client.post('/tray/data', data=data, follow_redirects=True, content_type='multipart/form-data')
    assert response.status_code == 200


def test_data_validate(client):
    data = {"name": "Super-Tray II", "ip": "192.168.1.1"}
    data = {key: str(value) for key, value in data.items()}
    response = client.post('/tray/data', data=data)
    assert response.status_code == 404

    data = {"name": "Super-Tray II", "ip": "192.168.1.1"}
    data = {key: str(value) for key, value in data.items()}
    data['image'] = (io.BytesIO(b"abcdef"), 'test.jpg')
    response = client.post('/tray/data', data=data, follow_redirects=True, content_type='multipart/form-data')
    assert response.status_code == 404

    data = {"name": "Super-Tray II", "ip": "192.168.1.1"}
    data = {key: str(value) for key, value in data.items()}
    data['data'] = (io.BytesIO(b"abcdef"), '1.csv')
    response = client.post('/tray/data', data=data, follow_redirects=True, content_type='multipart/form-data')
    assert response.status_code == 404

    data = {"name": "Super-Tray II", "ip": "192.168.1.1"}
    data = {key: str(value) for key, value in data.items()}
    data['image'] = (io.BytesIO(b"abcdef"), '')
    data['data'] = (io.BytesIO(b"abcdef"), '1.csv')
    response = client.post('/tray/data', data=data, follow_redirects=True, content_type='multipart/form-data')
    assert response.status_code == 404

    data = {"name": "Super-Tray II", "ip": "192.168.1.1"}
    data = {key: str(value) for key, value in data.items()}
    data['image'] = (io.BytesIO(b"abcdef"), 'test.jpg')
    data['data'] = (io.BytesIO(b"abcdef"), '')
    response = client.post('/tray/data', data=data, follow_redirects=True, content_type='multipart/form-data')
    assert response.status_code == 404

    data = {"name": "Super-Tray II", "ip": "192.168.1.1"}
    data = {key: str(value) for key, value in data.items()}
    data['image'] = (io.BytesIO(b"abcdef"), 'test.zc')
    data['data'] = (io.BytesIO(b"abcdef"), '1.csv')
    response = client.post('/tray/data', data=data, follow_redirects=True, content_type='multipart/form-data')
    assert response.status_code == 404

    data = {"name": "Super-Tray II", "ip": "192.168.1.1"}
    data = {key: str(value) for key, value in data.items()}
    data['image'] = (io.BytesIO(b"abcdef"), 'test.jpg')
    data['data'] = (io.BytesIO(b"abcdef"), '1.zc')
    response = client.post('/tray/data', data=data, follow_redirects=True, content_type='multipart/form-data')
    assert response.status_code == 404
