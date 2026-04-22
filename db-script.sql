DROP DATABASE IF EXISTS AD;
CREATE DATABASE AD;
USE AD;

CREATE TABLE aduser_status (
    id_pk INT AUTO_INCREMENT PRIMARY KEY,
    bezeichnung VARCHAR(20) NOT NULL
);
CREATE TABLE adou (
    id_pk INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    beschreibung TEXT
);
CREATE TABLE aduser (
    id_pk INT AUTO_INCREMENT PRIMARY KEY,
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    username VARCHAR(20),
    email VARCHAR(100),
    phone VARCHAR(20),
    ou VARCHAR(100),
    street VARCHAR(100),
	city VARCHAR(100),
	city_code VARCHAR(5),
	postalcode VARCHAR(20),
    status_id_fk INT, FOREIGN KEY (status_id_fk) REFERENCES aduser_status(id_pk),
    ou_id_fk INT, FOREIGN KEY (ou_id_fk) REFERENCES adou(id_pk),
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified DATETIME DEFAULT CURRENT_TIMESTAMP);

INSERT INTO aduser_status (id_pk, bezeichnung) VALUES
(1, 'aktiv'),
(2, 'inaktiv'),
(3, 'abgelehnt');


INSERT INTO `adou` (`id_pk`, `name`, `beschreibung`) VALUES
(1, 'BuHa12A', 'Buchhaltung Klasse 12A'),
(2, 'BuHa12B', 'Buchhaltung Klasse 12B'),
(3, 'BuHa13A', 'Buchhaltung Klasse 13A'),
(4, 'BuHa13B', 'Buchhaltung Klasse 13B'),
(5, 'IT14A', 'Informatik Klasse 14A'),
(6, 'IT14B', 'Informatik Klasse 14B'),
(7, 'IT15A', 'Informatik Klasse 15A'),
(8, 'IT15B', 'Informatik Klasse 15B');

DROP VIEW IF EXISTS view_aduser_details;

CREATE
SQL SECURITY INVOKER 
VIEW view_aduser_details 
AS
SELECT
    u.id_pk AS user_id,
    u.firstname AS "Vorname",
    u.lastname AS "Nachname",
    u.phone AS "Telefon",
    u.ou AS "ou",
    u.street AS "Strasse",
    u.city AS "Ort",
    u.city_code AS "Kürzel",
    u.postalcode AS "PLZ",
    u.status_id_fk AS "Status_code",
	s.bezeichnung AS status,
	u.ou_id_fk AS "Kurs_Code",
    o.name AS "Kurs",
    o.beschreibung AS "Kursbezeichnung",
    CONVERT_TZ(u.created,  '+00:00', '+02:00') AS "Erstellt am",
	CONVERT_TZ(u.modified, '+00:00', '+02:00') AS "Verändert am"
FROM
    aduser u
LEFT JOIN
    aduser_status s ON u.status_id_fk = s.id_pk
LEFT JOIN
    adou o ON u.ou_id_fk = o.id_pk;

