--create measurement table
CREATE TABLE measurement (
id INTEGER PRIMARY KEY NOT NULL, 
station TEXT,
date DATE,
prcp FLOAT,
tobs FLOAT
);

--create station table
CREATE TABLE station (
id INTEGER PRIMARY KEY NOT NULL, 
station TEXT, 
name TEXT, 
latitude FLOAT,
longitude FLOAT,
elevation FLOAT
);