-- Copyright (c) Tuukka Norri 2022-2025
-- Licenced under the MIT licence.

PRAGMA foreign_keys = ON;

CREATE TABLE sensor (
	id INTEGER PRIMARY KEY
);

CREATE TABLE sensor_linux_monitoring (
	id INTEGER PRIMARY KEY REFERENCES sensor (id),
	adapter_name VARCHAR NOT NULL,
	prefix VARCHAR NOT NULL,
	addr INTEGER NOT NULL,
	feature VARCHAR NOT NULL,
	UNIQUE (adapter_name, prefix, addr, feature)
);

CREATE TABLE sensor_hdd (
	id INTEGER PRIMARY KEY REFERENCES sensor (id),
	name VARCHAR NOT NULL UNIQUE
);

CREATE TABLE temperature (
	timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	sensor_id INTEGER NOT NULL REFERENCES sensor (id),
	value REAL NOT NULL
);
