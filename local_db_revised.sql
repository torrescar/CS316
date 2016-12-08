-- CREATES TABLES
CREATE TABLE Department
(id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
 name VARCHAR(256) NOT NULL,
 abbr VARCHAR(256) NOT NULL
 );

CREATE TABLE Professor
(id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
 name VARCHAR(256) NOT NULL,
 dept INTEGER NOT NULL references Department(id)
);

CREATE TABLE Course
(id INTEGER NOT NULL PRIMARY KEY,
 dept INTEGER NOT NULL REFERENCES Department(id),
 num VARCHAR(256) NOT NULL,
 description VARCHAR(256),
 credits FLOAT NOT NULL
);

CREATE TABLE Class
(id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
 course INTEGER NOT NULL REFERENCES Course(id),
 teacher INTEGER NOT NULL REFERENCES Professor(id)
);

CREATE TABLE Tag
(id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
 name VARCHAR(256) NOT NULL UNIQUE,
 category VARCHAR(256) NOT NULL
);

CREATE TABLE Tag_Reviews 
(class_id INTEGER NOT NULL REFERENCES Class(id),
 tag INTEGER NOT NULL REFERENCES Tag(id),
 semester VARCHAR(256) NOT NULL,
 year INTEGER NOT NULL
);

CREATE TABLE Attribute 
(id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
 name VARCHAR(256) NOT NULL UNIQUE
);

CREATE TABLE Course_Attributes
(course_id INTEGER NOT NULL REFERENCES Course(id),
 attribute_id INTEGER NOT NULL REFERENCES Attribute(id)
);


-- TRIGGERS
-- Check that a class' course is derived from Course(dept) and Course(num) (should be a concatenation)
-- Check that an inactive professor isn't marked as visiting or vice versa 
-- more tbd

-- PROCEDURES... tbd 

-- Populating Tables
INSERT INTO User VALUES (0, "cmt57");
INSERT INTO Attribute VALUES (0, "QS");
INSERT INTO Department VALUES (0, "Computer Science", "CS");
INSERT INTO Professor VALUES (0, "Susan Rodger", 0, true, false);
INSERT INTO Course VALUES (0, 0, 101, "Introduction to Computer Science");
INSERT INTO Class VALUES (0, 0, "Fall", 2014, 0, NULL, false, false, 1.0);
INSERT INTO Tag VALUES (0, "Easy A");
INSERT INTO Tag_Reviews VALUES (0, 0, 0, false);
INSERT INTO Course_Attributes(0,0);

INSERT INTO User VALUES (1, "cft6");
INSERT INTO Attribute VALUES (1, "CCI");
INSERT INTO Attribute VALUES (2, "CZ");
INSERT INTO Attribute VALUES (3, "SS");
INSERT INTO Department VALUES (1, "Cultural Anthropology", "CULANTH");
INSERT INTO Professor VALUES (1, "Orin Starn", 1, true, false);
INSERT INTO Course VALUES (1, 1, 101, "Introduction to Cultural Anthropology");
INSERT INTO Class VALUES (1, 1, "Spring", 2015, 1, NULL, false, false, 1.0);
INSERT INTO Tag VALUES (1, "Low Writing");
INSERT INTO Tag_Reviews VALUES (1, 1, 0, false);
INSERT INTO Tag_Reviews VALUES (1, 1, 1, false);
INSERT INTO Course_Attributes(1,1);
INSERT INTO Course_Attributes(1,2);
INSERT INTO Course_Attributes(1,3);

