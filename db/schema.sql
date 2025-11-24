DROP DATABASE IF EXISTS finalProj_workorder;
CREATE DATABASE finalProj_workorder;
USE finalProj_workorder;

CREATE TABLE Person(
    personId INT PRIMARY KEY,
    firstName VARCHAR(50) NOT NULL,
    lastName VARCHAR(50) NOT NULL
);

CREATE TABLE Student(
    personId INT,
    guardianId INT NOT NULL,
    grade CHAR(1) NOT NULL,
    FOREIGN KEY (personId) REFERENCES Person(personId)
    ON DELETE CASCADE
    FOREIGN KEY(guardianId) REFERENCES Gaurdian(personId)
    ON DELETE RESTRICT
);

CREATE TABLE Volunteer(
    personId INT,
    FOREIGN KEY (personId) REFERENCES Person(personId)
    ON DELETE CASCADE
);

CREATE TABLE Admin(
    personId INT,
    FOREIGN KEY (personId) REFERENCES Person(personId)
    ON DELETE CASCADE
);

CREATE TABLE Guardian(
    personId INT,
    FOREIGN KEY (personId) REFERENCES Person(personId)
    ON DELETE CASCADE
);

CREATE TABLE Meeting(
    meetId INT PRIMARY KEY,
    title VARCHAR(100) NOT NULL
);

CREATE TABLE MeetingSignUpItem(
    id INT PRIMARY KEY,
    signeeId INT NOT NULL,
    signedUpById INT NOT NULL,
    meetingId INT NOT NULL,
    FOREIGN KEY (signedUpById) REFERENCES Person(personId)
    ON DELETE RESTRICT,
    FOREIGN KEY (signeeId) REFERENCES Person(personId)
    ON DELETE RESTRICT,
    FOREIGN KEY (meetingId) REFERENCES Meeting(meetId)
    ON DELETE CASCADE
);

CREATE TABLE NoteItem(
    Id INT PRIMARY KEY,
    writerId INT NOT NULL,
    meetingId INT NOT NULL,
    textContent VARCHAR(MAX),
    FOREIGN KEY (meetingId) REFERENCES Meeting(meetId)
    ON DELETE RESTRICT,
    FOREIGN KEY(writerId) REFERENCES Person(personId)
    ON DELETE CASCADE
);

CREATE TABLE attendanceItem(
    id INT PRIMARY KEY,
    signupId INT NOT NULL,
    STATUS CHAR(1) NOT NULL,
    FOREIGN KEY (signupId) REFERENCES MeetingSignUpItem(signeeId)
    ON DELETE CASCADE
);

CREATE TABLE smallGroup(
    meetId INT NOT NULL,
    nextMeetingDate DATE,
    FOREIGN KEY (meetId) REFERENCES Meeting(meetId)
    ON DELETE CASCADE
);

CREATE TABLE Event(
    meetId INT NOT NULL,
    createdByID INT NOT NULL,
    type VARCHAR(50) NOT NULL,
    location VARCHAR(100) NOT NULL,
    startDate DATE NOT NULL,
    endDate DATE NOT NULL,
    FOREIGN KEY (meetID) REFERENCES Meeting(meetId)
    ON DELETE CASCADE,
    FOREIGN KEY (createdByID) REFERENCES Person(personId)
    ON DELETE RESTRICT
);