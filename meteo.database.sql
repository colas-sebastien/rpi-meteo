CREATE DATABASE meteo;

CREATE USER 'meteo'@'%' IDENTIFIED BY 'meteo';
GRANT ALL PRIVILEGES ON meteo.* TO 'meteo'@'%';
FLUSH PRIVILEGES;

CREATE TABLE meteo.openweathermap (
  date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  temperature decimal(3,1) DEFAULT NULL,
  pressure decimal(6,2) DEFAULT NULL,
  humidity decimal(3,0) DEFAULT NULL,
  icon char(3) DEFAULT NULL,
  PRIMARY KEY (date)
);

CREATE TABLE meteo.sensor_data (
  sensor_id tinyint(3) unsigned NOT NULL,
  date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  temperature decimal(3,1) DEFAULT NULL,
  humidity decimal(3,0) DEFAULT NULL,
  battery decimal(3,0) DEFAULT NULL,
  PRIMARY KEY (sensor_id,date)
);
