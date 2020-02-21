DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS meal;
DROP TABLE IF EXISTS tray;
DROP TABLE IF EXISTS food;
DROP TABLE IF EXISTS menu;

CREATE TABLE user (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    mail TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    birthdate DATE NOT NULL,
    gender INTEGER NOT NULL,
    weight REAL NOT NULL
);

CREATE TABLE food(
    id_food INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    informations TEXT NOT NULL
);

CREATE TABLE menu(
    id_menu INTEGER PRIMARY KEY AUTOINCREMENT,
    id_drink INTEGER NOT NULL,
    id_meat INTEGER NOT NULL,
    id_vegetable INTEGER NOT NULL,
    id_starchy INTEGER NOT NULL,
    id_dessert INTEGER NOT NULL,
    id_fish INTEGER NOT NULL,
    FOREIGN KEY (id_drink) REFERENCES food(id_food),
    FOREIGN KEY (id_meat) REFERENCES food(id_food),
    FOREIGN KEY (id_vegetable) REFERENCES food(id_food),
    FOREIGN KEY (id_starchy) REFERENCES food(id_food),
    FOREIGN KEY (id_dessert) REFERENCES food(id_food),
    FOREIGN KEY (id_fish) REFERENCES food(id_food)
);

CREATE TABLE tray(
    id_tray INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    version INTEGER NOT NULL,
    informations TEXT NOT NULL,
    ip TEXT NOT NULL,
    online INTEGER NOT NULL
);

CREATE TABLE meal(
    id_meal INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user INTEGER NOT NULL,
    id_menu INTEGER NOT NULL,
    id_tray INTEGER NOT NULL,
    start DATETIME NOT NULL,
    end DATETIME,
    FOREIGN KEY (id_user) REFERENCES user(id_user),
    FOREIGN KEY (id_menu) REFERENCES menu(id_menu),
    FOREIGN KEY (id_tray) REFERENCES tray(id_tray)
);

INSERT INTO user (name, mail, password, birthdate, gender, weight) VALUES
("Simon Dejaeger", "simon.dejaeger@uliege.be", "pbkdf2:sha256:150000$tqaXMquc$52afb1b6ec7ed791e131aab586e5f7c1d2f584cc23086325617ebd8991b506f3", "1994-10-16", "masculin","62");