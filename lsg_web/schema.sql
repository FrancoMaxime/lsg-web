DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS meal;
DROP TABLE IF EXISTS tray;
DROP TABLE IF EXISTS food;
DROP TABLE IF EXISTS menu;
DROP TABLE IF EXISTS permission;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS version;
DROP TABLE IF EXISTS composed;
DROP TABLE IF EXISTS bug;

CREATE TABLE user (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    mail TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    birthdate DATE NOT NULL,
    gender INTEGER NOT NULL,
    weight REAL NOT NULL,
    actif INTEGER NOT NULL,
    id_permission INTEGER NOT NULL,
    filename TEXT NOT NULL,
    FOREIGN KEY (id_permission) REFERENCES permission(id_permission)
);

CREATE TABLE food(
    id_food INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    id_category INTEGER NOT NULL,
    informations TEXT NOT NULL,
    id_user INTEGER NOT NULL,
    FOREIGN KEY (id_user) REFERENCES user(id_user),
    FOREIGN KEY (id_category) REFERENCES food(id_category)
);

CREATE TABLE menu(
    id_menu INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    informations TEXT,
    id_user INTEGER NOT NULL,
    actif INTEGER NOT NULL,
    FOREIGN KEY (id_user) REFERENCES user(id_user)
);

CREATE TABLE tray(
    id_tray INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    id_version INTEGER NOT NULL,
    informations TEXT NOT NULL,
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
    id_client INTEGER NOT NULL,
    start DATETIME NOT NULL,
    end DATETIME,
    informations TEXT NOT NULL,
    FOREIGN KEY (id_user) REFERENCES user(id_user),
    FOREIGN KEY (id_client) REFERENCES user(id_user),
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
    informations TEXT NOT NULL,
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

INSERT INTO user (name, mail, password, birthdate, gender, weight, actif, id_permission, filename) VALUES
("Simon Dejaeger", "simon.dejaeger@uliege.be", "pbkdf2:sha256:150000$tqaXMquc$52afb1b6ec7ed791e131aab586e5f7c1d2f584cc23086325617ebd8991b506f3", "1994-10-16", "masculin", "62", 1, 1, "1.png");

INSERT INTO category (name) VALUES
("Drink"),
("Meat"),
("Vegetable"),
("Starchy"),
("Dessert"),
("Fish");

INSERT INTO version(name, release_date) VALUES
("Alpha 0.1.a", date('2020-02-01'));