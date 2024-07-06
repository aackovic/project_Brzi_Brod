CREATE SCHEMA IF NOT EXISTS `Projekat`;

USE `Projekat`;

DROP TABLE IF EXISTS `Odgovor`
;

DROP TABLE IF EXISTS `Tema`
;

DROP TABLE IF EXISTS `Kategorija`
;

DROP TABLE IF EXISTS `Recenzija`
;

DROP TABLE IF EXISTS `AktivnaTabla`
;

DROP TABLE IF EXISTS `Obuhvatanje`
;

DROP TABLE IF EXISTS `Obrok`
;

DROP TABLE IF EXISTS `Moderator`
;

DROP TABLE IF EXISTS `Menza`
;

DROP TABLE IF EXISTS `Meni`
;

DROP TABLE IF EXISTS `Student`
;

DROP TABLE IF EXISTS `VerifikacioniPIN`
;

DROP TABLE IF EXISTS `Korisnik`
;

CREATE TABLE `AktivnaTabla`
(
    `IdMnz`              integer primary key NOT NULL,
	`Aktivna`            integer NULL,
	`TipObroka`          varchar(1) NULL
)
;

CREATE TABLE `Kategorija`
( 
	`IdKat`              integer AUTO_INCREMENT primary key NOT NULL ,
	`Naziv`              varchar(100) NOT NULL 
)
;

CREATE TABLE `Korisnik`
( 
	`IdKor`              integer primary key NOT NULL ,
	`ProfilnaSlika`      varchar(100) NOT NULL ,
    `Adresa`             varchar(500) NOT NULL ,
	`DatumRodjenja`      date NULL default NULL,
	`BrojTel`            varchar(15) NULL			 
)
;

CREATE TABLE `Meni`
( 
	`IdMen`              integer AUTO_INCREMENT primary key  NOT NULL 
)
;

CREATE TABLE `Menza`
( 
	`IdMnz`              integer AUTO_INCREMENT primary key NOT NULL ,
	`Naziv`              varchar(20) NOT NULL ,
	`Kapacitet`          integer NOT NULL 
	CONSTRAINT `KapacitetVeceIliJednakoNula`
		CHECK  ( Kapacitet >= 0 ),
	`Adresa`             varchar(500) NOT NULL ,
	`Slika`              blob NOT NULL ,
	`IdMen`              integer NOT NULL ,
	`RadnoVremeDor`      varchar(11) NOT NULL ,
	`RadnoVremeRuc`      varchar(11) NOT NULL ,
	`RadnoVremeVec`      varchar(11) NOT NULL ,
    `Link`				 varchar(500) NOT NULL
)
;

CREATE TABLE `Moderator`
( 
	`IdMod`              integer NOT NULL primary key,
	`IdMnz`              integer NOT NULL
)
;

CREATE TABLE `Obrok`
( 
	`IdObr`              integer AUTO_INCREMENT primary key NOT NULL ,
	`Naziv`              varchar(20) NOT NULL 
)
;

CREATE TABLE `Obuhvatanje`
( 
	`IdObu`				 integer AUTO_INCREMENT primary key NOT NULL ,
	`IdMen`              integer NOT NULL ,
	`IdObr`              integer NOT NULL ,
	`DanUNedelji`        char(3) NOT NULL 
	CONSTRAINT `DanUNedeljiDanUNed`
		CHECK  ( `DanUNedelji`='PON' OR `DanUNedelji`='UTO' OR `DanUNedelji`='SRE' OR `DanUNedelji`='CET' OR `DanUNedelji`='PET' OR `DanUNedelji`='SUB' OR `DanUNedelji`='NED' ),
	`Tip`                char(1) NOT NULL 
	CONSTRAINT `TipTipObrokaMeni`
		CHECK  ( `Tip`='D' OR `Tip`='R' OR `Tip`='V' )
)
;

CREATE TABLE `Odgovor`
( 
	`IdOdg`              integer AUTO_INCREMENT primary key NOT NULL ,
	`Naslov`             varchar(100) NOT NULL ,
	`DatumVreme`         datetime NOT NULL ,
	`Komentar`           varchar(1000) NOT NULL ,
	`Slika`              varchar(100)  NULL ,
	`IdTem`              integer NOT NULL ,
	`IdKor`              integer NOT NULL 
)
;

CREATE TABLE `Recenzija`
( 
	`IdRec`				 integer AUTO_INCREMENT primary key NOT NULL ,
	`Opis`               varchar(200) NOT NULL ,
	`Tekst`              varchar(500) NULL ,
	`DatumVreme`         datetime NOT NULL ,
	`Ocena`              integer NOT NULL 
	CONSTRAINT `OcenaVeceIliJednakoJedanManjeIliJednakoPet`
		CHECK  ( Ocena BETWEEN 1 AND 5 ),
	`IdStu`              integer NOT NULL ,
	`IdMnz`              integer NOT NULL
)
;

CREATE TABLE `Student`
( 
	`StanjeRacuna`       decimal(20,2) NOT NULL 
	CONSTRAINT `StanjeRacunaVeceIliJednakoNula`
		CHECK  ( StanjeRacuna >= 0 ),
	`Dorucak`            integer NOT NULL DEFAULT  0
	CONSTRAINT `DorucakVeceIliJednakoNula`
		CHECK  ( Dorucak >= 0 ),
	`Rucak`              integer NOT NULL DEFAULT  0
	CONSTRAINT `RucakVeceIliJednakoNula`
		CHECK  ( Rucak >= 0 ),
	`Vecera`             integer NOT NULL DEFAULT  0
	CONSTRAINT `VeceraVeceIliJednakoNula`
		CHECK  ( Vecera >= 0 ),
	`Zeton`              integer NOT NULL DEFAULT  0,
	`IdStu`              integer primary key  NOT NULL ,
	`BrojStudKartice`    varchar(20)  NOT NULL 
)
;

CREATE TABLE `Tema`
( 
	`IdTem`              integer  AUTO_INCREMENT primary key  NOT NULL ,
	`Naziv`              varchar(100)  NOT NULL ,
	`Opis`               varchar(200)  NOT NULL ,
	`IdKat`              integer  NOT NULL 
)
;

CREATE TABLE `VerifikacioniPIN`
( 
	`PIN`                char(20)  NOT NULL ,
	`BrojStudKartice`    varchar(20) primary key  NOT NULL 
)
;

ALTER TABLE `Menza`
	ADD CONSTRAINT `XAK1Menza` UNIQUE (`Naziv`  ASC)
;

ALTER TABLE `Obrok`
	ADD CONSTRAINT `XAK1Obrok` UNIQUE (`Naziv`  ASC)
;

ALTER TABLE `Obuhvatanje`
	ADD CONSTRAINT `XAK1Obuhvatanje` UNIQUE (`IdMen` ASC, `IdObr` ASC, `DanUNedelji` ASC, `Tip` ASC)
;

ALTER TABLE `Recenzija`
	ADD CONSTRAINT `XAK1Recenzija` UNIQUE (`IdStu` ASC, `IdMnz` ASC)
;

ALTER TABLE `Student`
	ADD CONSTRAINT `XAK1Student` UNIQUE (`BrojStudKartice`  ASC)
;

ALTER TABLE `VerifikacioniPIN`
	ADD CONSTRAINT `XAK1VerifikacioniPIN` UNIQUE (`PIN`  ASC)
;


ALTER TABLE `AktivnaTabla`
	ADD CONSTRAINT FOREIGN KEY (`IdMnz`) REFERENCES `Menza`(`IdMnz`)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;


ALTER TABLE `Korisnik`
	ADD CONSTRAINT FOREIGN KEY (`IdKor`) REFERENCES `auth_user`(`id`)
		ON DELETE CASCADE
        ON UPDATE CASCADE
;


ALTER TABLE `Menza`
	ADD CONSTRAINT FOREIGN KEY (`IdMen`) REFERENCES `Meni`(`IdMen`)
		ON UPDATE CASCADE
;


ALTER TABLE `Moderator`
	ADD CONSTRAINT FOREIGN KEY (`IdMod`) REFERENCES `Korisnik`(`IdKor`)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;

ALTER TABLE `Moderator`
	ADD CONSTRAINT FOREIGN KEY (`IdMnz`) REFERENCES `Menza`(`IdMnz`)
		ON UPDATE CASCADE
;


ALTER TABLE `Obuhvatanje`
	ADD CONSTRAINT FOREIGN KEY (`IdMen`) REFERENCES `Meni`(`IdMen`)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;

ALTER TABLE `Obuhvatanje`
	ADD CONSTRAINT FOREIGN KEY (`IdObr`) REFERENCES `Obrok`(`IdObr`)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;


ALTER TABLE `Odgovor`
	ADD CONSTRAINT FOREIGN KEY (`IdTem`) REFERENCES `Tema`(`IdTem`)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;

ALTER TABLE `Odgovor`
	ADD CONSTRAINT FOREIGN KEY (`IdKor`) REFERENCES `Korisnik`(`IdKor`)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;


ALTER TABLE `Recenzija`
	ADD CONSTRAINT FOREIGN KEY (`IdStu`) REFERENCES `Student`(`IdStu`)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;

ALTER TABLE `Recenzija`
	ADD CONSTRAINT FOREIGN KEY (`IdMnz`) REFERENCES `Menza`(`IdMnz`)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;


ALTER TABLE `Student`
	ADD CONSTRAINT FOREIGN KEY (`IdStu`) REFERENCES `Korisnik`(`IdKor`)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;

ALTER TABLE `Student`
	ADD CONSTRAINT FOREIGN KEY (`BrojStudKartice`) REFERENCES `VerifikacioniPIN`(`BrojStudKartice`)
		ON UPDATE CASCADE
;


ALTER TABLE `Tema`
	ADD CONSTRAINT FOREIGN KEY (`IdKat`) REFERENCES `Kategorija`(`IdKat`)
		ON DELETE CASCADE
		ON UPDATE CASCADE
;


INSERT INTO `projekat`.`obrok`
(`Naziv`)
VALUES
('Burek sa mesom'),
('Burek sa sirom'),
('Prženice'),
('Kajgana'),
('Viršle'),
('Kiflice sa džemom'),
('Bečka šnicla'),
('Pohovano pileće belo'),
('Pljeskavica'),
('Spanać'),
('Brokoli'),
('Musaka'),
('Pastrimka'),
('Rižoto'),
('Pire krompir'),
('Pomfrit'),
('Ćufte'),
('Lazanje'),
('Kupus'),
('Kukuruz'),
('Karfiol');

INSERT INTO `projekat`.`meni`() values();
INSERT INTO `projekat`.`meni`() values();
INSERT INTO `projekat`.`meni`() values();
INSERT INTO `projekat`.`meni`() values();
INSERT INTO `projekat`.`meni`() values();

INSERT INTO `projekat`.`menza`
(`Naziv`,
`Kapacitet`,
`Adresa`,
`Slika`,
`IdMen`,
`RadnoVremeDor`,
`RadnoVremeRuc`,
`RadnoVremeVec`,
`Link`)
VALUES
('Karaburma', 300, 'Mije Kovačevića 7b', '', 1, '07:00-09:00', '12:00-15:00', '17:00-20:00','Karaburma+Student+Dormitory'),
('Studentski grad', 500, 'Tošin bunar', '', 2, '06:00-09:00', '12:00-15:00', '17:00-21:00', 'Studentski+grad'),
('Patris Lumumba', 100, 'Cocina 22', '', 3, '07:00-09:00', '12:00-15:00', '17:00-20:00', 'Patris+Lumumba'),
('Kralj Aleksandar I', 250, 'Bulevar kralja Aleksandra 75', '', 4, '07:30-09:30', '12:30-15:00', '17:00-20:30', 'studentski+dom+kralj+aleksandar+i'),
('Rifat Burdžević', 150, 'Milana Rakića 77', '', 5, '07:00-09:00', '12:00-15:00', '17:00-20:00', 'Restoran+"Rifat+Burdžović"');

INSERT INTO `projekat`.`aktivnatabla`
(`IdMnz`,
`Aktivna`)
VALUES
(1,false),
(2,false),
(3,false),
(4,false),
(5,false);

INSERT INTO projekat.verifikacionipin() VALUES('46672610005135886247', '1111-2222-3333-5555');
INSERT INTO projekat.verifikacionipin() VALUES('65609302608326031065', '1111-2222-3333-4444');
INSERT INTO projekat.verifikacionipin() VALUES('83548824865525527627', '2222-4444-6666-8888');

INSERT INTO `projekat`.`kategorija`
(
`Naziv`)
VALUES
('Hrana'),
('Usluga'),
('Cena');

INSERT INTO `projekat`.`tema`
(
`Naziv`,
`Opis`,
`IdKat`)
VALUES
('Kvalitet hrane', 'Mesto za diskusiju kvaliteta hrane u studentskim menzama',1),
('Raznovrsnost jelovnika', 'Predlozi i kritike na izbor jela',1),
('Dostupnost hrane', 'Dostupnost, odnosno nedostupnost određenih jela u menzama',1),
('Kvalitet usluge', 'Diskusija o ponašanju zaposlenih i odnosu prema studentima',2),
('Radno vreme', 'Predlozi i kritike na radno vreme',2),
('Odnos cene i kvaliteta','Komentari na odnos cene i pruženih usluga',3)
;

update Menza 
set slika=LOAD_FILE("C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/karaburma.jpg")
where idmnz=1;

update Menza 
set slika=LOAD_FILE("C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/studenjak.jpg")
where idmnz=2;

update Menza 
set slika=LOAD_FILE("C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/patris.jpg")
where idmnz=3;

update Menza 
set slika=LOAD_FILE("C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/lola.jpg")
where idmnz=4;

update Menza 
set slika=LOAD_FILE("C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/rifat.jpg")
where idmnz=5;

INSERT INTO projekat.obuhvatanje
(IdMen,
IdObr,
DanUNedelji,
Tip)
VALUES
(1,1,'PON','D'),
(1,7,'PON','R'),
(1,8,'PON','V'),
(1,2,'UTO','D'),
(1,9,'UTO','R'),
(1,10,'UTO','V'),
(1,3,'SRE','D'),
(1,11,'SRE','R'),
(1,12,'SRE','V'),
(1,4,'CET','D'),
(1,13,'CET','R'),
(1,14,'CET','V'),
(1,5,'PET','D'),
(1,15,'PET','R'),
(1,16,'PET','V'),
(1,6,'SUB','D'),
(1,17,'SUB','R'),
(1,18,'SUB','V'),
(1,4,'NED','D'),
(1,19,'NED','R'),
(1,20,'NED','V'),

(2,2,'PON','D'),
(2,9,'PON','R'),
(2,12,'PON','V'),
(2,3,'UTO','D'),
(2,8,'UTO','R'),
(2,15,'UTO','V'),
(2,1,'SRE','D'),
(2,16,'SRE','R'),
(2,18,'SRE','V'),
(2,4,'CET','D'),
(2,10,'CET','R'),
(2,14,'CET','V'),
(2,5,'PET','D'),
(2,9,'PET','R'),
(2,18,'PET','V'),
(2,6,'SUB','D'),
(2,19,'SUB','R'),
(2,20,'SUB','V'),
(2,4,'NED','D'),
(2,21,'NED','R'),
(2,20,'NED','V')
;

INSERT INTO projekat.obuhvatanje
(IdMen,
IdObr,
DanUNedelji,
Tip)
VALUES
(3,2,'PON','D'),
(3,9,'PON','R'),
(3,10,'PON','V'),
(3,1,'UTO','D'),
(3,11,'UTO','R'),
(3,16,'UTO','V'),
(3,3,'SRE','D'),
(3,18,'SRE','R'),
(3,12,'SRE','V'),
(3,4,'CET','D'),
(3,14,'CET','R'),
(3,21,'CET','V'),
(3,6,'PET','D'),
(3,15,'PET','R'),
(3,14,'PET','V'),
(3,5,'SUB','D'),
(3,13,'SUB','R'),
(3,18,'SUB','V'),
(3,2,'NED','D'),
(3,19,'NED','R'),
(3,9,'NED','V'),

(4,5,'PON','D'),
(4,9,'PON','R'),
(4,12,'PON','V'),
(4,1,'UTO','D'),
(4,8,'UTO','R'),
(4,11,'UTO','V'),
(4,4,'SRE','D'),
(4,16,'SRE','R'),
(4,18,'SRE','V'),
(4,4,'CET','D'),
(4,10,'CET','R'),
(4,14,'CET','V'),
(4,5,'PET','D'),
(4,8,'PET','R'),
(4,12,'PET','V'),
(4,6,'SUB','D'),
(4,19,'SUB','R'),
(4,16,'SUB','V'),
(4,4,'NED','D'),
(4,21,'NED','R'),
(4,20,'NED','V'),

(5,2,'PON','D'),
(5,19,'PON','R'),
(5,21,'PON','V'),
(5,3,'UTO','D'),
(5,18,'UTO','R'),
(5,12,'UTO','V'),
(5,4,'SRE','D'),
(5,14,'SRE','R'),
(5,15,'SRE','V'),
(5,1,'CET','D'),
(5,10,'CET','R'),
(5,16,'CET','V'),
(5,5,'PET','D'),
(5,8,'PET','R'),
(5,12,'PET','V'),
(5,6,'SUB','D'),
(5,18,'SUB','R'),
(5,19,'SUB','V'),
(5,4,'NED','D'),
(5,19,'NED','R'),
(5,20,'NED','V')
;

INSERT INTO projekat.verifikacionipin() VALUES('32172610003125886247', '1234-1234-1234-1234');
INSERT INTO projekat.verifikacionipin() VALUES('65656702608326031065', '2222-2222-3333-3333');
INSERT INTO projekat.verifikacionipin() VALUES('83548824812345527627', '5555-4444-6666-7777');

INSERT INTO projekat.verifikacionipin() VALUES('12342610005135886247', '9876-4532-9876-4532');
INSERT INTO projekat.verifikacionipin() VALUES('22209302602222031065', '1212-1212-1212-1212');
INSERT INTO projekat.verifikacionipin() VALUES('83533334865544447627', '2121-2121-2121-2121');

INSERT INTO projekat.verifikacionipin() VALUES('88972610005135886247', '7778-7778-8887-8887');
INSERT INTO projekat.verifikacionipin() VALUES('66609302608222031065', '5511-2222-3333-5511');
INSERT INTO projekat.verifikacionipin() VALUES('55548824865525527627', '1234-4321-4321-1234');

INSERT INTO projekat.verifikacionipin() VALUES('54544610005123456247', '4455-4455-5555-5555');
INSERT INTO projekat.verifikacionipin() VALUES('11119302608326031065', '3434-2222-3434-4444');
INSERT INTO projekat.verifikacionipin() VALUES('99999999865525527627', '3434-1144-6666-4422');