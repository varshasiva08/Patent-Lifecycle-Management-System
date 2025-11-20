CREATE DATABASE IF NOT EXISTS patent_system;
USE patent_system;


-- Table for Inventors
CREATE TABLE Inventors (
    I_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(20) NOT NULL,
    Organization VARCHAR(150),
    Email VARCHAR(50) UNIQUE,
    Phone_No VARCHAR(50),
    Password VARCHAR(30) NOT NULL
);

-- Table for Reviewers 
CREATE TABLE Reviewers (
    R_ID INT PRIMARY KEY AUTO_INCREMENT,
    Email VARCHAR(50) UNIQUE,
    Name VARCHAR(20) NOT NULL,
    Designation VARCHAR(20),
    Organisation VARCHAR(50),
    Comment VARCHAR(100),
    Password VARCHAR(30) NOT NULL,
    Is_Active BOOLEAN DEFAULT TRUE,
    Deleted_Date DATE DEFAULT NULL
);

-- Table for Patents
CREATE TABLE Patents (
    P_ID INT PRIMARY KEY AUTO_INCREMENT,
    Appl_Name VARCHAR(30) NOT NULL,
    Filing_Date DATE NOT NULL,
    Domain VARCHAR(30),
    Status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    Patent_Type ENUM('Utility','Design','Plant') NOT NULL,
    Title VARCHAR(100) NOT NULL,
    Description TEXT NOT NULL,
    All_Reviews_Complete BOOLEAN DEFAULT FALSE,
    Final_Review_Date DATE DEFAULT NULL
);

-- Table for Costs
CREATE TABLE Costs (
    Cost_ID INT PRIMARY KEY AUTO_INCREMENT,
    P_ID INT,
    Cost_Type VARCHAR(20),
    Amount DECIMAL(10, 2) NOT NULL,
    Date_Paid DATE,
    FOREIGN KEY (P_ID) REFERENCES Patents(P_ID),
    CHECK (Amount > 0)
);

-- Table for Renewals
CREATE TABLE Renewals (
    R_No INT PRIMARY KEY AUTO_INCREMENT,
    P_ID INT,
    R_Date DATE,
    Fee_Status VARCHAR(20),
    Expiry_Date DATE NOT NULL,
    FOREIGN KEY (P_ID) REFERENCES Patents(P_ID)
);

-- Patent_Reviewers
CREATE TABLE Patent_Reviewers (
    P_ID INT,
    R_ID INT,
    Reviewer_Name VARCHAR(20) NOT NULL,
    Assignment_Date DATE,
    Review_Date DATE,
    Review_Status VARCHAR(50) DEFAULT 'Assigned',
    Decision VARCHAR(100),
    Comments TEXT,
    PRIMARY KEY (P_ID, R_ID),
    FOREIGN KEY (P_ID) REFERENCES Patents(P_ID) ON DELETE CASCADE,
    FOREIGN KEY (R_ID) REFERENCES Reviewers(R_ID) ON DELETE NO ACTION
);

-- Patent_Stages
CREATE TABLE Patent_Stages (
    P_ID INT,
    Stage_Name VARCHAR(100),
    Stage_Date DATE,
    Stage_Status VARCHAR(50) DEFAULT 'In Progress',
    Review_Complete BOOLEAN DEFAULT FALSE,
    Completed_By VARCHAR(100),
    Completion_Date DATE,
    PRIMARY KEY (P_ID, Stage_Name),
    FOREIGN KEY (P_ID) REFERENCES Patents(P_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Inventor_Patents
CREATE TABLE Inventor_Patents (
    I_ID INT,
    P_ID INT,
    PRIMARY KEY (I_ID, P_ID),
    FOREIGN KEY (I_ID) REFERENCES Inventors(I_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (P_ID) REFERENCES Patents(P_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Patents_Opposition 
CREATE TABLE Patents_Opposition (
    O_ID INT PRIMARY KEY AUTO_INCREMENT,
    Email VARCHAR(50) NOT NULL,
    Patent_Title VARCHAR(50) NOT NULL,
    O_Date DATE NOT NULL,
    Reason TEXT
);


-- Sample data insertion

INSERT INTO Inventors (Name, Organization, Email, Phone_No, Password) VALUES
('Dr. Evelyn Reed', 'Quantum Innovations Inc.', 'e.reed@qii.com', '555-0101', 'inv123'),
('Ben Carter', 'BioGen Labs', 'b.carter@biogen.com', '555-0102', 'inv123');

-- Corrected reviewers insertion 
INSERT INTO Reviewers (Email, Name, Designation, Organisation, Comment, Password, Is_Active) VALUES
('alan@iii.com', 'Dr. Alan Grant', 'Senior Examiner', 'Global Patent Office', 'Quantum tech expert', 'rev123', TRUE),
('ellie@yyy.com', 'Dr. Ellie Sattler', 'Specialist Examiner', 'Global Patent Office', 'Biotech specialist', 'rev123', TRUE);

-- Patents
INSERT INTO Patents (Appl_Name, Filing_Date, Domain, Status, Patent_Type, Title, Description, All_Reviews_Complete) VALUES
('Quantum Innovations Inc.', '2024-01-15', 'Quantum Computing', 'Under Review', 'Utility', 'Quantum Entanglement Communication System', 'Revolutionary quantum communication method', FALSE),
('BioGen Labs', '2024-03-22', 'Biotechnology', 'Granted', 'Utility', 'CRISPR-Based Gene Therapy for Neurological Disorders', 'Novel gene therapy approach', TRUE);

-- Costs
INSERT INTO Costs (P_ID, Cost_Type, Amount, Date_Paid) VALUES
(1, 'Filing Fee', 1500.00, '2024-01-15'),
(2, 'Issue Fee', 2000.00, '2025-01-20');

-- Renewals 
INSERT INTO Renewals (P_ID, R_Date, Fee_Status, Expiry_Date) VALUES
(2, '2029-01-15', 'First Renewal Paid', '2033-01-15'),
(2, '2033-01-10', 'Second Renewal Paid', '2037-01-15'),
(1, '2029-02-01', 'First Renewal Pending', '2033-02-01');

-- Patent_Reviewers 
INSERT INTO Patent_Reviewers (P_ID, R_ID, Reviewer_Name, Assignment_Date, Review_Date, Review_Status, Decision, Comments) VALUES
(1, 1, 'Dr. Alan Grant', '2024-02-01', '2025-02-10', 'Completed', 'Needs Revision', 'Prior art concerns addressed'),
(2, 2, 'Dr. Ellie Sattler', '2024-04-01', '2024-11-05', 'Completed', 'Approved', 'All requirements met');

-- Patent_Stages
INSERT INTO Patent_Stages (P_ID, Stage_Name, Stage_Date, Stage_Status, Review_Complete, Completed_By, Completion_Date) VALUES
(1, 'Filed', '2024-01-15', 'Completed', FALSE, NULL, '2024-01-15'),
(1, 'Initial Review', '2024-02-01', 'Completed', TRUE, 'Dr. Alan Grant', '2025-02-10'),
(1, 'Technical Review', '2025-02-15', 'In Progress', FALSE, NULL, NULL),
(2, 'Filed', '2024-03-22', 'Completed', FALSE, NULL, '2024-03-22'),
(2, 'Initial Review', '2024-04-01', 'Completed', TRUE, 'Dr. Ellie Sattler', '2024-08-15'),
(2, 'Technical Review', '2024-09-01', 'Completed', TRUE, 'Dr. Ellie Sattler', '2024-11-05'),
(2, 'Granted', '2025-01-20', 'Completed', FALSE, NULL, '2025-01-20');

-- Inventor_Patents
INSERT INTO Inventor_Patents (I_ID, P_ID) VALUES
(1, 1),
(2, 2);

-- Oppositions
INSERT INTO Patents_Opposition (Email, Patent_Title, O_Date, Reason) VALUES
('john.doe@email.com', 'Quantum Entanglement Communication System', '2025-05-20', 'Prior art exists from a 2022 paper.'),
('jane.smith@email.com', 'Quantum Entanglement Communication System', '2025-06-01', 'The invention is considered obvious.');


-- Single Trigger, Function, Procedure
-- Trigger log table
CREATE TABLE IF NOT EXISTS Patent_Status_Audit (
    LogID INT PRIMARY KEY AUTO_INCREMENT,
    P_ID INT,
    Old_Status VARCHAR(50),
    New_Status VARCHAR(50),
    Changed_By VARCHAR(50),
    Changed_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$
CREATE TRIGGER after_patent_status_update
AFTER UPDATE ON Patents
FOR EACH ROW
BEGIN
    IF OLD.Status <> NEW.Status THEN
        INSERT INTO Patent_Status_Audit (P_ID, Old_Status, New_Status, Changed_By)
        VALUES (OLD.P_ID, OLD.Status, NEW.Status, USER());
    END IF;
END$$
DELIMITER ;

-- Function: Patent age in years (decimal)
DELIMITER $$
CREATE FUNCTION GetPatentAge(filing_date DATE)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE age DECIMAL(10,2);
    SET age = DATEDIFF(CURDATE(), filing_date) / 365.25;
    RETURN age;
END$$
DELIMITER ;

-- Procedure: Get patents by domain
DELIMITER $$
CREATE PROCEDURE GetPatentsByDomain(IN domain_name VARCHAR(100))
BEGIN
    SELECT P_ID, Title, Appl_Name, Filing_Date, Status, All_Reviews_Complete
    FROM Patents
    WHERE Domain = domain_name
    ORDER BY Filing_Date DESC;
END$$
DELIMITER ;


-- 1. Nested Query Example -Get all reviewers who have reviewed patents that are 'Granted'
SELECT DISTINCT R.R_ID, R.Name, R.Email
FROM Reviewers R
WHERE R.R_ID IN (
    SELECT PR.R_ID
    FROM Patent_Reviewers PR
    WHERE PR.P_ID IN (
        SELECT P_ID
        FROM Patents
        WHERE Status = 'Granted'
    )
);

-- 2. Join Query Example -Show patents with their assigned reviewers
SELECT P.P_ID, P.Title AS Patent_Title, R.R_ID AS Reviewer_ID, R.Name AS Reviewer_Name, PR.Review_Status
FROM Patents P
JOIN Patent_Reviewers PR ON P.P_ID = PR.P_ID
JOIN Reviewers R ON PR.R_ID = R.R_ID
ORDER BY P.Title;

-- 3. Aggregate Query Example -Count of paid renewals per patent, only patents with 2 or more paid renewals
SELECT P_ID, COUNT(R_No) AS NumberOfPaidRenewals
FROM Renewals
WHERE Fee_Status LIKE '%Paid%'
GROUP BY P_ID
HAVING COUNT(R_No) >= 2;


