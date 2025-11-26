-- Schema for Campus Maintenance and Management System

DROP TABLE IF EXISTS Maintenance;
DROP TABLE IF EXISTS Activity;
DROP TABLE IF EXISTS Location;
DROP TABLE IF EXISTS School;
DROP TABLE IF EXISTS Profile;
DROP TABLE IF EXISTS Person;

CREATE TABLE Person (
    personal_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(10),
    date_of_birth DATE,
    supervisor_id VARCHAR(20),
    FOREIGN KEY (supervisor_id) REFERENCES Person(personal_id)
);

CREATE TABLE Profile (
    profile_id INT AUTO_INCREMENT PRIMARY KEY,
    personal_id VARCHAR(20) NOT NULL,
    job_role VARCHAR(50), -- Academic, Maintenance, Student
    status VARCHAR(20), -- Current, Former
    FOREIGN KEY (personal_id) REFERENCES Person(personal_id),
    UNIQUE (personal_id) -- One-to-one relationship
);

CREATE TABLE School (
    school_name VARCHAR(100) PRIMARY KEY,
    department VARCHAR(100) NOT NULL UNIQUE,
    faculty VARCHAR(100)
);

CREATE TABLE Location (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    room VARCHAR(20),
    floor VARCHAR(10),
    building VARCHAR(50),
    campus VARCHAR(50),
    school_name VARCHAR(100),
    FOREIGN KEY (school_name) REFERENCES School(school_name)
);

CREATE TABLE Activity (
    activity_id VARCHAR(20) PRIMARY KEY,
    type VARCHAR(50), -- Lecture, Event
    time DATETIME,
    organiser_id VARCHAR(20) NOT NULL,
    FOREIGN KEY (organiser_id) REFERENCES Person(personal_id)
);

CREATE TABLE Maintenance (
    maintenance_id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50), -- Repair, Renovation, Security, Cleaning
    frequency VARCHAR(50),
    location_id INT NOT NULL,
    FOREIGN KEY (location_id) REFERENCES Location(location_id)
);

-- Many-to-Many: Person participates in Activity
CREATE TABLE Participation (
    personal_id VARCHAR(20),
    activity_id VARCHAR(20),
    PRIMARY KEY (personal_id, activity_id),
    FOREIGN KEY (personal_id) REFERENCES Person(personal_id),
    FOREIGN KEY (activity_id) REFERENCES Activity(activity_id)
);

-- Many-to-Many: Person affiliated to School
CREATE TABLE Affiliation (
    personal_id VARCHAR(20),
    school_name VARCHAR(100),
    PRIMARY KEY (personal_id, school_name),
    FOREIGN KEY (personal_id) REFERENCES Person(personal_id),
    FOREIGN KEY (school_name) REFERENCES School(school_name)
);
