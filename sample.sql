-- CREATES TABLES

-- DON'T WORRY ABOUT
CREATE TABLE User
(id INTEGER NOT NULL PRIMARY KEY,
 uname VARCHAR(32) NOT NULL UNIQUE
);

-- Do we need a Department ID?
CREATE TABLE Department
(id INTEGER NOT NULL PRIMARY KEY,
 name VARCHAR(256),
 abbr VARCHAR(256))

-- Doesn't seem like there's a way to check if active or visiting
CREATE TABLE Professor
(id INTEGER NOT NULL PRIMARY KEY,
 name VARCHAR(256) NOT NULL,
 dept INTEGER references Department(id),
 active BOOLEAN NOT NULL,
 visiting BOOLEAN NOT NULL
)

-- num not an integer; could be something like 89S
CREATE TABLE Course
(id INTEGER NOT NULL PRIMARY KEY,
 dept INTEGER NOT NULL REFERENCES Department(id),
 num VARCHAR(256) NOT NULL,
 description VARCHAR(256)
 -- Probably should put credits underneath Course, not Class
 -- credits FLOAT NOT NULL
);

-- Primary key should be semester, instead of ID
-- Don't need year
-- This will be only lecture classes
CREATE TABLE Class
(id INTEGER NOT NULL PRIMARY KEY,
 course VARCHAR(256) NOT NULL,
 semester CHAR(8),
 year INTEGER NOT NULL,
 teacher INTEGER NOT NULL REFERENCES User(id),
 teacher2 INTEGER REFERENCES User(id) CHECK (teacher2 IS NOT NULL AND (teacher != teacher2)),
 house BOOLEAN NOT NULL,
 special_topics BOOLEAN NOT NULL,
 credits FLOAT NOT NULL
);

-- DON'T WORRY ABOUT
CREATE TABLE Tag
(id INTEGER NOT NULL PRIMARY KEY,
 name VARCHAR(256) NOT NULL UNIQUE
);

-- DON'T WORRY ABOUT
CREATE TABLE Tag_Reviews
(u_id INTEGER NOT NULL REFERENCES User(id),
 class_id INTEGER NOT NULL REFERENCES Course(id),
 tag VARCHAR(256) NOT NULL REFERENCES Tag(name),
 anonymous BOOLEAN NOT NULL
);

-- DON'T WORRY ABOUT
CREATE TABLE Rating
(id INTEGER NOT NULL PRIMARY KEY,
 name VARCHAR(256) NOT NULL UNIQUE
);

-- DON'T WORRY ABOUT
CREATE TABLE Score_Reviews
(u_id INTEGER NOT NULL REFERENCES User(id),
 class_id INTEGER NOT NULL REFERENCES Course(id),
 rating VARCHAR(256) NOT NULL REFERENCES Tag(name),
 score INTEGER NOT NULL CHECK score>=0 AND score<=10,
 anonymous BOOLEAN NOT NULL
);

CREATE TABLE Attribute
(id INTEGER NOT NULL PRIMARY KEY,
 name VARCHAR(256) NOT NULL UNIQUE
);

CREATE TABLE Course_Attributes
(course_id INTEGER NOT NULL REFERENCES Course(id),
 attribute_id NOT NULL REFERENCES Attribute(id)
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
