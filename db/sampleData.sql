USE finalProj_workorder;

-- ===== PERSON =====
INSERT INTO Person (personId, firstName, lastName) VALUES
(1, 'Emily', 'Johnson'),
(2, 'Michael', 'Smith'),
(3, 'Sophia', 'Lee'),
(4, 'Daniel', 'Martinez'),
(5, 'Ava', 'Davis'),
(6, 'Jacob', 'Brown'),
(7, 'Olivia', 'Garcia'),
(8, 'Ethan', 'Wilson'),
(9,  'Grace', 'Miller'),
(10, 'Henry', 'Anderson'),
(11, 'Lily', 'Thompson'),
(12, 'Lucas', 'White'),
(13, 'Chloe', 'Harris'),
(14, 'Noah', 'Taylor'),
(15, 'Zoe', 'Clark');

-- ===== GUARDIAN =====
INSERT INTO Guardian (personId) VALUES
(1),
(2),
(3),
(9),
(10),
(11);

-- ===== STUDENT =====
INSERT INTO Student (personId, guardianId, grade) VALUES
(4, 1, '5'),
(5, 2, '4'),
(6, 3, '6'),
(12, 9,  '3'),
(13, 10, '5'),
(14, 11, '4');

-- ===== VOLUNTEER =====
INSERT INTO Volunteer (personId) VALUES
(7),
(8),
(15),
(10);

-- ===== ADMIN =====
INSERT INTO Admin (personId) VALUES
(1),
(3);

-- ===== MEETING =====
INSERT INTO Meeting (meetId, title) VALUES
(101, 'Parent Orientation'),
(102, 'Volunteer Training'),
(103, 'Small Group Gathering'),
(104, 'Fundraising Kickoff'),
(105, 'End-of-Year Celebration');

-- ===== MEETING SIGN-UPS =====
INSERT INTO MeetingSignUpItem (id, signeeId, signedUpById, meetingId) VALUES
(201, 4, 1, 101), -- Guardian Emily signed up student Daniel
(202, 5, 2, 101),
(203, 6, 3, 101),
(204, 7, 7, 102), -- Volunteer signs themselves up
(205, 8, 1, 102),
(206, 4, 1, 103),
(207, 12, 9, 104),  -- Guardian Grace signs up student Lucas
(208, 13, 10, 104),
(209, 14, 11, 104),
(210, 15, 15, 105), -- Volunteer signs themselves up
(211, 7, 1, 105),   -- Admin Emily signs up Olivia
(212, 8, 3, 105);

-- ===== NOTE ITEM =====
INSERT INTO NoteItem (Id, writerId, meetingId, textContent) VALUES
(301, 1, 101, 'Reviewed school safety procedures and parent expectations.'),
(302, 7, 102, 'Requested additional onboarding materials.'),
(303, 1, 103, 'Discussed next small group activity schedule.'),
(304, 3, 104, 'Outlined fundraising goals and volunteer needs.'),
(305, 10, 104, 'Suggested digital donation campaign.'),
(306, 15, 105, 'Volunteers will help organize event setup.'),
(307, 9, 105, 'Parents requested allergy-friendly snacks.');

-- ===== ATTENDANCE =====
# INSERT INTO attendanceItem (id, signupId, STATUS) VALUES
# (401, 201, 'P'),
# (402, 202, 'A'),
# (403, 203, 'P'),
# (404, 204, 'P'),
# (405, 205, 'P'),
# (406, 206, 'P'),
# (407, 207, 'P'),
# (408, 208, 'P'),
# (409, 209, 'A'),
# (410, 210, 'P'),
# (411, 211, 'P'),
# (412, 212, 'P');

-- ===== SMALL GROUP =====
INSERT INTO smallGroup (meetId, nextMeetingDate) VALUES
(103, '2025-01-20'),
(104, '2025-02-01');

-- ===== EVENT TYPES =====
INSERT INTO eventType (typeId, typeName, description) VALUES
(1, 'Parent Meeting', 'Meetings organized for parents.'),
(2, 'Training Session', 'Sessions to train volunteers or staff.'),
(3, 'Small Group Activity', 'Activities for small groups.'),
(4, 'Fundraiser', 'Events to raise funds.'),
(5, 'Community Celebration', 'Celebrations for the community.');

-- ===== EVENT =====
INSERT INTO Event (meetId, createdByID, typeId, location, startDate, endDate) VALUES
(102, 1, 2, 'Community Center Room B', '2025-02-05', '2025-02-05'), -- Training Session
(101, 3, 1, 'School Library', '2025-01-10', '2025-01-10'), -- Parent Meeting
(103, 7, 3, 'Public Park Pavilion', '2025-01-15', '2025-01-15'), -- Small Group Activity
(104, 3, 4, 'Gymnasium Hall', '2025-02-10', '2025-02-10'), -- Fundraiser
(105, 7, 5, 'School Courtyard', '2025-05-18', '2025-05-18');