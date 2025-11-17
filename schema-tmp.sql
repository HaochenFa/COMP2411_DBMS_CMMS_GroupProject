-- Always good to set this once per database
SET
    NAMES utf8mb4;

SET
    FOREIGN_KEY_CHECKS = 0;

------------------------------------------------------------
-- 1. SCHOOL and LOCATION
------------------------------------------------------------
CREATE TABLE
    school (
        school_id INT AUTO_INCREMENT PRIMARY KEY,
        faculty VARCHAR(100) NOT NULL,
        department VARCHAR(100) NOT NULL
    ) ENGINE = InnoDB;

CREATE TABLE
    location (
        location_id INT AUTO_INCREMENT PRIMARY KEY,
        school_id INT NOT NULL,
        campus VARCHAR(100) NOT NULL,
        building VARCHAR(100) NOT NULL,
        floor VARCHAR(20) NOT NULL,
        room VARCHAR(50) NOT NULL,
        CONSTRAINT fk_location_school FOREIGN KEY (school_id) REFERENCES school (school_id) ON UPDATE CASCADE ON DELETE RESTRICT
    ) ENGINE = InnoDB;

------------------------------------------------------------
-- 2. PERSON and PROFILE
------------------------------------------------------------
CREATE TABLE
    person (
        -- Key attribute in the E-R model
        personal_id INT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        date_of_birth DATE NOT NULL,
        gender ENUM ('Male', 'Female', 'Other') NOT NULL,
        -- supervisor_id is another person (self-reference)
        supervisor_id INT NULL,
        -- affiliation to exactly one school
        school_id INT NOT NULL,
        CONSTRAINT fk_person_supervisor FOREIGN KEY (supervisor_id) REFERENCES person (personal_id) ON UPDATE CASCADE ON DELETE SET NULL,
        CONSTRAINT fk_person_school FOREIGN KEY (school_id) REFERENCES school (school_id) ON UPDATE CASCADE ON DELETE RESTRICT
        -- AGE is a derived attribute in the E-R diagram, so we do not store
        -- it here; compute it with TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()).
    ) ENGINE = InnoDB;

CREATE TABLE
    profile (
        -- 1 : 1 with PERSON  →  use the same key
        person_id INT PRIMARY KEY,
        job_role ENUM ('Academic', 'Maintenance', 'Student') NOT NULL,
        status ENUM ('Current', 'Former') NOT NULL,
        CONSTRAINT fk_profile_person FOREIGN KEY (person_id) REFERENCES person (personal_id) ON UPDATE CASCADE ON DELETE CASCADE
    ) ENGINE = InnoDB;

------------------------------------------------------------
-- 3. ACTIVITY
------------------------------------------------------------
CREATE TABLE
    activity (
        activity_id INT PRIMARY KEY,
        activity_type ENUM ('Lecture', 'Event') NOT NULL,
        -- "Time" in the diagram – use DATETIME
        scheduled_at DATETIME NOT NULL,
        -- each activity is supervised by exactly one person
        supervisor_id INT NOT NULL,
        CONSTRAINT fk_activity_supervisor FOREIGN KEY (supervisor_id) REFERENCES person (personal_id) ON UPDATE CASCADE ON DELETE RESTRICT
    ) ENGINE = InnoDB;

-- M:N "Organised by" between PERSON and ACTIVITY
CREATE TABLE
    activity_organiser (
        person_id INT NOT NULL,
        activity_id INT NOT NULL,
        PRIMARY KEY (person_id, activity_id),
        CONSTRAINT fk_organiser_person FOREIGN KEY (person_id) REFERENCES person (personal_id) ON UPDATE CASCADE ON DELETE CASCADE,
        CONSTRAINT fk_organiser_activity FOREIGN KEY (activity_id) REFERENCES activity (activity_id) ON UPDATE CASCADE ON DELETE CASCADE
    ) ENGINE = InnoDB;

------------------------------------------------------------
-- 4. MAINTENANCE
------------------------------------------------------------
CREATE TABLE
    maintenance (
        maintenance_id INT AUTO_INCREMENT PRIMARY KEY,
        maintenance_type ENUM ('Repair', 'Renovation', 'Security', 'Cleaning') NOT NULL,
        frequency VARCHAR(100) NOT NULL,
        -- "Needs" relationship: each maintenance is for one location
        location_id INT NOT NULL,
        -- "Does" relationship: each maintenance job is done by one person
        person_id INT NOT NULL,
        CONSTRAINT fk_maintenance_location FOREIGN KEY (location_id) REFERENCES location (location_id) ON UPDATE CASCADE ON DELETE RESTRICT,
        CONSTRAINT fk_maintenance_person FOREIGN KEY (person_id) REFERENCES person (personal_id) ON UPDATE CASCADE ON DELETE RESTRICT
    ) ENGINE = InnoDB;

------------------------------------------------------------
-- 5. PARTICIPATION (ternary relationship)
------------------------------------------------------------
-- Person participates in an activity at a specific location
CREATE TABLE
    participation (
        person_id INT NOT NULL,
        activity_id INT NOT NULL,
        location_id INT NOT NULL,
        PRIMARY KEY (person_id, activity_id, location_id),
        CONSTRAINT fk_part_person FOREIGN KEY (person_id) REFERENCES person (personal_id) ON UPDATE CASCADE ON DELETE CASCADE,
        CONSTRAINT fk_part_activity FOREIGN KEY (activity_id) REFERENCES activity (activity_id) ON UPDATE CASCADE ON DELETE CASCADE,
        CONSTRAINT fk_part_location FOREIGN KEY (location_id) REFERENCES location (location_id) ON UPDATE CASCADE ON DELETE RESTRICT
    ) ENGINE = InnoDB;

SET
    FOREIGN_KEY_CHECKS = 1;