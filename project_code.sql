CREATE DATABASE IF NOT EXISTS patent_system;
USE patent_system;


-- Table for Inventors
CREATE TABLE Inventors (
    I_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Organization VARCHAR(255),
    Email VARCHAR(255) UNIQUE,
    Phone_No VARCHAR(20)
);

-- Table for Reviewers
CREATE TABLE Reviewers (
    R_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Designation VARCHAR(255),
    Organisation VARCHAR(255)
);

-- Table for Patents
CREATE TABLE Patents (
    P_ID INT PRIMARY KEY AUTO_INCREMENT,
    Appl_Name VARCHAR(255) NOT NULL,
    Filing_Date DATE NOT NULL,
    Domain VARCHAR(100),
    Status VARCHAR(50),
    Patent_Type VARCHAR(50),
    Title VARCHAR(255) NOT NULL
);

-- Table for Examinations (depends on Patents and Reviewers)
CREATE TABLE Examination (
    Exam_ID INT PRIMARY KEY AUTO_INCREMENT,
    P_ID INT,
    Exam_Date DATE,
    Decision VARCHAR(255),
    R_ID INT,
    Legal_Review_Status VARCHAR(100),
    FOREIGN KEY (P_ID) REFERENCES Patents(P_ID) ON DELETE CASCADE,
    FOREIGN KEY (R_ID) REFERENCES Reviewers(R_ID) ON DELETE SET NULL
);

-- Table for Costs (depends on Patents)
CREATE TABLE Costs (
    Cost_ID INT PRIMARY KEY AUTO_INCREMENT,
    P_ID INT,
    Cost_Type VARCHAR(100),
    Amount DECIMAL(10, 2),
    Date_Paid DATE,
    FOREIGN KEY (P_ID) REFERENCES Patents(P_ID) ON DELETE CASCADE
);

-- Table for Renewals (depends on Patents)
CREATE TABLE Renewals (
    R_No INT PRIMARY KEY AUTO_INCREMENT,
    P_ID INT,
    R_Date DATE,
    Fee_Status VARCHAR(50),
    Expiry_Date DATE,
    FOREIGN KEY (P_ID) REFERENCES Patents(P_ID) ON DELETE CASCADE
);

-- Junction table for the M:N relationship between Patents and Reviewers
CREATE TABLE Patent_Reviewers (
    P_ID INT,
    R_ID INT,
    PRIMARY KEY (P_ID, R_ID),
    FOREIGN KEY (P_ID) REFERENCES Patents(P_ID) ON DELETE CASCADE,
    FOREIGN KEY (R_ID) REFERENCES Reviewers(R_ID) ON DELETE CASCADE
);

-- Table for Patent Stages (describes a multivalued attribute)
CREATE TABLE Patent_Stages (
    P_ID INT,
    Stage_Name VARCHAR(100),
    Stage_Date DATE,
    PRIMARY KEY (P_ID, Stage_Name),
    FOREIGN KEY (P_ID) REFERENCES Patents(P_ID) ON DELETE CASCADE
);

-- Junction table for the M:N relationship between Inventors and Patents
CREATE TABLE Inventor_Patents (
    I_ID INT,
    P_ID INT,
    PRIMARY KEY (I_ID, P_ID),
    FOREIGN KEY (I_ID) REFERENCES Inventors(I_ID) ON DELETE CASCADE,
    FOREIGN KEY (P_ID) REFERENCES Patents(P_ID) ON DELETE CASCADE
);



-- Insert into Inventors
INSERT INTO Inventors (Name, Organization, Email, Phone_No) VALUES
('Dr. Evelyn Reed', 'Quantum Innovations Inc.', 'e.reed@qii.com', '555-0101'),
('Ben Carter', 'BioGen Labs', 'b.carter@biogen.com', '555-0102');

-- Insert into Reviewers
INSERT INTO Reviewers (Name, Designation, Organisation) VALUES
('Dr. Alan Grant', 'Senior Examiner', 'Global Patent Office'),
('Dr. Ellie Sattler', 'Specialist Examiner', 'Global Patent Office');

-- Insert into Patents
INSERT INTO Patents (Appl_Name, Filing_Date, Domain, Status, Patent_Type, Title) VALUES
('Quantum Innovations Inc.', '2024-01-15', 'Quantum Computing', 'Pending', 'Utility', 'Quantum Entanglement Communication System'),
('BioGen Labs', '2024-03-22', 'Biotechnology', 'Granted', 'Utility', 'CRISPR-Based Gene Therapy for Neurological Disorders');

-- Insert into Examination
-- Note: P_ID 1 = Quantum Patent, P_ID 2 = BioGen Patent. R_ID 1 = Dr. Grant, R_ID 2 = Dr. Sattler.
INSERT INTO Examination (P_ID, Exam_Date, Decision, R_ID, Legal_Review_Status) VALUES
(1, '2025-02-10', 'First Office Action Issued', 1, 'In Progress'),
(2, '2024-11-05', 'Notice of Allowance', 2, 'Complete');

-- Insert into Costs
INSERT INTO Costs (P_ID, Cost_Type, Amount, Date_Paid) VALUES
(1, 'Filing Fee', 1500.00, '2024-01-15'),
(2, 'Issue Fee', 2000.00, '2025-01-20');

-- Insert into Renewals
INSERT INTO Renewals (P_ID, R_Date, Fee_Status, Expiry_Date) VALUES
(2, '2029-01-15', 'First Renewal Paid', '2033-01-15'),
(2, '2033-01-10', 'Second Renewal Paid', '2037-01-15');

-- Insert into Patent_Reviewers
-- Dr. Grant (1) reviews the Quantum Patent (1)
-- Dr. Sattler (2) reviews the BioGen Patent (2)
INSERT INTO Patent_Reviewers (P_ID, R_ID) VALUES
(1, 1),
(2, 2);

-- Insert into Patent_Stages
INSERT INTO Patent_Stages (P_ID, Stage_Name, Stage_Date) VALUES
(1, 'Filed', '2024-01-15'),
(2, 'Granted', '2025-01-20');

-- Insert into Inventor_Patents
-- Dr. Reed (1) is the inventor for the Quantum Patent (1)
-- Ben Carter (2) is the inventor for the BioGen Patent (2)
INSERT INTO Inventor_Patents (I_ID, P_ID) VALUES
(1, 1),
(2, 2);

-- Use the database created earlier
USE patent_system;
CREATE TABLE Patents_Opposition (
    O_ID INT PRIMARY KEY AUTO_INCREMENT,
    P_ID INT,
    O_Date DATE NOT NULL,
    Reason TEXT,
    FOREIGN KEY (P_ID) REFERENCES Patents(P_ID) ON DELETE CASCADE
);


INSERT INTO Patents_Opposition (P_ID, O_Date, Reason) VALUES
(1, '2025-05-20', 'Prior art exists from a research paper published in 2022, making the claims not novel.'),
(1, '2025-06-01', 'The claimed invention is considered obvious to a person with ordinary skill in the art.');