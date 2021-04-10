DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS person;
DROP TABLE IF EXISTS meal;
DROP TABLE IF EXISTS tray;
DROP TABLE IF EXISTS food;
DROP TABLE IF EXISTS menu;
DROP TABLE IF EXISTS permission;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS version;
DROP TABLE IF EXISTS composed;
DROP TABLE IF EXISTS bug;

CREATE TABLE person (
    id_person INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    birthdate DATE NOT NULL,
    gender INTEGER NOT NULL,
    weight REAL NOT NULL,
    actif INTEGER NOT NULL
);

CREATE TABLE user (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    id_person INTEGER NOT NULL,
    mail TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    id_permission INTEGER NOT NULL,
    filename TEXT NOT NULL,
    actif INTEGER NOT NULL,
    FOREIGN KEY (id_permission) REFERENCES permission(id_permission),
    FOREIGN KEY (id_person) REFERENCES person(id_person)
);

CREATE TABLE food(
    id_food INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    id_category INTEGER NOT NULL,
    information TEXT NOT NULL,
    id_person INTEGER NOT NULL,
    FOREIGN KEY (id_person) REFERENCES person(id_person),
    FOREIGN KEY (id_category) REFERENCES food(id_category)
);

CREATE TABLE menu(
    id_menu INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    information TEXT,
    id_person INTEGER NOT NULL,
    actif INTEGER NOT NULL,
    FOREIGN KEY (id_person) REFERENCES person(id_person)
);

CREATE TABLE tray(
    id_tray INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    id_version INTEGER NOT NULL,
    information TEXT NOT NULL,
    ip TEXT NOT NULL,
    online INTEGER NOT NULL,
    actif INTEGER NOT NULL,
    on_use INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (id_version) REFERENCES version(id_version)
);

CREATE TABLE meal(
    id_meal INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user INTEGER NOT NULL,
    id_menu INTEGER NOT NULL,
    id_tray INTEGER NOT NULL,
    id_candidate INTEGER NOT NULL,
    start DATETIME NOT NULL,
    end DATETIME,
    information TEXT NOT NULL,
    actif INTEGER NOT NULL,
    FOREIGN KEY (id_user) REFERENCES person(id_person),
    FOREIGN KEY (id_candidate) REFERENCES person(id_person),
    FOREIGN KEY (id_menu) REFERENCES menu(id_menu),
    FOREIGN KEY (id_tray) REFERENCES tray(id_tray)
);

CREATE TABLE permission(
    id_permission INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE category(
    id_category INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE version(
    id_version INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    release_date DATE NOT NULL
);
CREATE TABLE bug(
    id_bug INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    information TEXT NOT NULL,
    bug_date DATE NOT NULL,
    corrected INTEGER NOT NULL
);

CREATE TABLE composed(
    id_menu INTEGER NOT NULL,
    id_food INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (id_menu) REFERENCES menu(id_menu),
    FOREIGN KEY (id_food) REFERENCES food(id_food)
);

INSERT INTO permission(name) VALUES
("Administrator"),
("Simple User");

INSERT INTO person(name, birthdate, gender, weight, actif) VALUES
("Administrator", "1991-08-27", "homme", "62", 1);

INSERT INTO user (id_person, mail, password, actif, id_permission, filename) VALUES
(1, "admin@admin.be", "pbkdf2:sha256:150000$tqaXMquc$52afb1b6ec7ed791e131aab586e5f7c1d2f584cc23086325617ebd8991b506f3", 1, 1, "administrator.png");

INSERT INTO category (name) VALUES
("Drink"),
("Meat"),
("Vegetable"),
("Starchy"),
("Dessert"),
("Fish"),
("Sauce");

INSERT INTO version(name, release_date) VALUES
("Alpha 0.0.1a", date('2020-02-01')),
("Alpha 0.0.2a", date('2021-02-01'));