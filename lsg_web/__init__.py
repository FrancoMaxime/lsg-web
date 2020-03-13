#!/usr/bin/python3.7

import os

from flask import Flask
import paho.mqtt.publish as publish

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'lsg_web.sqlite'),
    )

    app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
    app.config["IMAGE_UPLOADS"] = app.instance_path + "/../lsg_web/static/img/uploads"
    app.config["DATA_UPLOADS"] = app.instance_path + "/../lsg_web/static/data"
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['MQTT_BROKER_URL'] = 'localhost'
    app.config['MQTT_BROKER_PORT'] = 1883
    app.config['MQTT_USERNAME'] = ''
    app.config['MQTT_PASSWORD'] = ''
    app.config['MQTT_KEEPALIVE'] = 5
    app.config['MQTT_TLS_ENABLED'] = False

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    # a simple page that checks if the server is running
    @app.route('/running')
    def running():
        publish.single("lsg/plateau1", "SERVER\tSTART MEAL\t1.csv", hostname=app.config['MQTT_BROKER_URL'])
        return 'Server running'

    @app.route('/close')
    def close():
        publish.single("lsg/plateau1", "SERVER\tEND MEAL\t1.csv", hostname=app.config['MQTT_BROKER_URL'])
        return 'Server end meal'


    @app.context_processor
    def utility_processor():
        def current_meal():
            tmp = db.get_db()
            return tmp.execute(
                'SELECT count(id_meal) FROM meal WHERE end IS NULL'
            ).fetchone()[0]

        return dict(current_meal=current_meal)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import homepage
    app.register_blueprint(homepage.bp)
    app.add_url_rule('/', endpoint='index')

    from . import user
    app.register_blueprint(user.bp)

    from . import food
    app.register_blueprint(food.bp)

    from . import tray
    app.register_blueprint(tray.bp)

    from . import menu
    app.register_blueprint(menu.bp)

    from . import meal
    app.register_blueprint(meal.bp)

    from . import version
    app.register_blueprint(version.bp)

    from . import category
    app.register_blueprint(category.bp)

    from . import bug
    app.register_blueprint(bug.bp)

    from . import changelog
    app.register_blueprint(changelog.bp)

    return app



