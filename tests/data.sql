INSERT INTO person(name, birthdate, gender, weight, actif) VALUES
("Simple User", "1971-04-08", "masculin", "80", 1),
("Alice", "1985-07-22", "femme", "60", 1),
("Bob", "1971-04-08", "homme", "80", 1),
("Justine", "1990-04-08", "femme", "68", 1),
("Michel", "1990-04-08", "homme", "68", 1);

INSERT INTO user (id_person, mail, password, actif, id_permission, filename) VALUES
(2, "simple@user.be", "pbkdf2:sha256:150000$tqaXMquc$52afb1b6ec7ed791e131aab586e5f7c1d2f584cc23086325617ebd8991b506f3", 1, 2, "2.png"),
(3, "alice@user.be", "pbkdf2:sha256:150000$tqaXMquc$52afb1b6ec7ed791e131aab586e5f7c1d2f584cc23086325617ebd8991b506f3", 1, 1, "1.png");

INSERT INTO food (name, id_category, information, id_person) VALUES
("Super-Water", 1, "information Super-Water", 1),
("Super-Meat", 2, "information Super-Meat", 1),
("Super-Vegetable", 3, "information Super-Vegetable", 1),
("Super-Starchy", 4, "information Super-Starchy", 1),
("Super-Dessert", 5, "information Super-Dessert", 1);

INSERT INTO MENU (name, information, id_person, actif)VALUES
("Super-Menu", "information about Super-Menu", 3, 1);

INSERT INTO composed (id_menu, id_food, quantity) VALUES
(1,1,"150"),
(1,2,"300");

INSERT INTO tray(name, id_version, information, ip, online, actif, on_use, timestamp ) VALUES
("Super-Tray", 1, "information about Super-Tray", "None", 0, 1,0, datetime("now", "-45 seconds")),
("Super-Tray II", 2, "information about Super-Tray II", "None", 0, 1,0, datetime("now", "-45 seconds"));

INSERT INTO bug(title, information, bug_date, corrected) VALUES
("Super-Bug", "information about Super-Bug", "2020-05-25", 0);

INSERT INTO meal(id_user, id_menu, id_tray, id_candidate, start, end, information, actif) VALUES
(1, 1, 1, 3, datetime("now", "-45 seconds"), datetime("now"), "information about Super-Meal", 1);
