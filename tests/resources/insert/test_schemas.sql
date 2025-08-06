PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE schemadescript (
	schema_name VARCHAR(128) NOT NULL, 
	description VARCHAR(1024) NOT NULL, 
	modauthor VARCHAR(128) NOT NULL, 
	loadauthor VARCHAR(128) NOT NULL, 
	moddate DATETIME NOT NULL, 
	loaddate DATETIME NOT NULL, 
	PRIMARY KEY (schema_name)
);
INSERT INTO schemadescript VALUES('Test Schema 1','Schema #1 for testing purposes','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
CREATE TABLE modeldescript (
	model_name VARCHAR(128) NOT NULL, 
	description VARCHAR(1024) NOT NULL, 
	schema_name VARCHAR(128) NOT NULL, 
	modauthor VARCHAR(128) NOT NULL, 
	loadauthor VARCHAR(128) NOT NULL, 
	moddate DATETIME NOT NULL, 
	loaddate DATETIME NOT NULL, 
	PRIMARY KEY (model_name, schema_name)
);
INSERT INTO modeldescript VALUES('model01','Test Model #1','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO modeldescript VALUES('model02','Test Model #2','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO modeldescript VALUES('model03','Test Model #3','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
CREATE TABLE columndescript (
	column_name VARCHAR(128) NOT NULL, 
	column_alias VARCHAR(128) NOT NULL, 
	sa_coltype VARCHAR(128) NOT NULL, 
	"default" VARCHAR(1024) NOT NULL, 
	description VARCHAR(1024) NOT NULL, 
	schema_name VARCHAR(128) NOT NULL, 
	modauthor VARCHAR(128) NOT NULL, 
	loadauthor VARCHAR(128) NOT NULL, 
	moddate DATETIME NOT NULL, 
	loaddate DATETIME NOT NULL, 
	PRIMARY KEY (column_name, schema_name)
);
INSERT INTO columndescript VALUES('column01','-','BigInteger()','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column02','-','Boolean(create_constraint = True, name = ''col02_ck'')','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column03','-','Date()','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column04','-','DateTime(timezone = True)','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column05','-','Double()','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column06','-','Enum(''a'',''b'',''c'',name=''myenum'', create_constraint = True)','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column07','-','Float(precision = 53, asdecimal = True, decimal_return_scale = 3)','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column08','-','Integer()','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column09','-','Interval(False, 2, 1)','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column10','-','LargeBinary(32)','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column11','-','Numeric(precision = 9, scale = 0, asdecimal = False)','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column12','-','PickleType(protocol = 0)','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column13','-','SmallInteger()','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column14','-','String(15, collation = ''utf8'')','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column15','-','Text(length = 15, collation = ''utf8'')','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column16','-','Time()','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column17','-','Unicode(30, collation = ''utf8'')','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column18','-','UnicodeText()','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columndescript VALUES('column19','-','Uuid(as_uuid = True, native_uuid = True)','-','-','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
CREATE TABLE columnassoc (
	model_name VARCHAR(128) NOT NULL, 
	column_name VARCHAR(128) NOT NULL, 
	column_position INTEGER NOT NULL, 
	nullable INTEGER NOT NULL, 
	"autoincrement" VARCHAR(30) NOT NULL, 
	quote VARCHAR(128) NOT NULL, 
	onupdate VARCHAR(128) NOT NULL, 
	schema_name VARCHAR(128) NOT NULL, 
	info VARCHAR(1024) NOT NULL, 
	modauthor VARCHAR(128) NOT NULL, 
	loadauthor VARCHAR(128) NOT NULL, 
	moddate DATETIME NOT NULL, 
	loaddate DATETIME NOT NULL, 
	PRIMARY KEY (column_name, model_name, schema_name)
);
INSERT INTO columnassoc VALUES('model01','column01',0,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model01','column14',1,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model01','column02',2,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model01','column05',3,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model01','column06',4,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model01','column16',5,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model01','column04',6,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model02','column08',0,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model02','column03',1,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model02','column09',2,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model02','column12',3,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model02','column18',4,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model02','column04',5,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model03','column13',0,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model03','column11',1,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model03','column19',2,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model03','column17',3,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model03','column15',4,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model03','column10',5,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model03','column07',6,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO columnassoc VALUES('model03','column04',7,0,'-','-','-','Test Schema 1','-','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
CREATE TABLE constraintdescript (
	constraint_type VARCHAR(2) NOT NULL, 
	columns VARCHAR(1024) NOT NULL, 
	model_name VARCHAR(128) NOT NULL, 
	schema_name VARCHAR(128) NOT NULL, 
	modauthor VARCHAR(128) NOT NULL, 
	loadauthor VARCHAR(128) NOT NULL, 
	moddate DATETIME NOT NULL, 
	loaddate DATETIME NOT NULL, 
	PRIMARY KEY (constraint_type, model_name, schema_name)
);
INSERT INTO constraintdescript VALUES('pk','column01','model01','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO constraintdescript VALUES('uq','column14','model01','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO constraintdescript VALUES('pk','column08, column03','model02','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO constraintdescript VALUES('pk','column19','model03','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
INSERT INTO constraintdescript VALUES('uq','column13, column11, column10','model03','Test Schema 1','bspears-LANL','bspears-LANL','2025-08-06 10:48:00','2025-08-06 10:48:00');
COMMIT;
