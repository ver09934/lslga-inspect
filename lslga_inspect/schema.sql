DROP TABLE IF EXISTS user;
-- DROP TABLE IF EXISTS galaxy;
DROP TABLE IF EXISTS inspection;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

/*
CREATE TABLE galaxy (
  lslga_id INTEGER PRIMARY KEY,
  galaxy_name TEXT NOT NULL
);
*/

CREATE TABLE inspection (
  inspection_id INTEGER PRIMARY KEY AUTOINCREMENT,
  lslga_id INTEGER,
  user_id INTEGER,
  quality TEXT NOT NULL,
  feedback TEXT,
  subset TEXT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- FOREIGN KEY (lslga_id) REFERENCES galaxy (lslga_id),
  FOREIGN KEY (user_id) REFERENCES user (id)
);
