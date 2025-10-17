-- ===================================================================================
-- SQL SCRIPT FOR PATENT LIFECYCLE MANAGEMENT SYSTEM - ADVANCED FEATURES
-- ===================================================================================

-- Use the target database
USE patent_system;


-- ===================================================================================
-- SECTION 1: CONSTRAINTS AND DATA TYPES
-- ===================================================================================
-- This section adds constraints like DEFAULT, ENUM, CHECK, and uses TEXT for CLOB.

-- Add a DEFAULT constraint to the Patents table
ALTER TABLE Patents
MODIFY COLUMN Status VARCHAR(50) DEFAULT 'Pending';

-- Change the Patent_Type to an ENUM for restricted values
ALTER TABLE Patents
MODIFY COLUMN Patent_Type ENUM('Utility', 'Design', 'Plant') NOT NULL;

-- Add a CHECK constraint to ensure cost amounts are positive
-- Note: MySQL 8.0.16+ enforces CHECK constraints. In older versions, it is parsed but ignored.
ALTER TABLE Costs
ADD CONSTRAINT chk_amount_positive CHECK (Amount > 0);

-- Add a TEXT column (similar to CLOB) for the patent's abstract
ALTER TABLE Patents
ADD COLUMN Patent_Abstract TEXT;

-- Example Update: Add an abstract to an existing patent
UPDATE Patents
SET Patent_Abstract = 'A system for near-instantaneous communication between two points, regardless of distance, utilizing the principles of quantum entanglement.'
WHERE P_ID = 1;


-- ===================================================================================
-- SECTION 2: 5 COMPLEX SQL QUERIES (NESTED & CORRELATED)
-- ===================================================================================

-- Query 1: Nested Subquery
-- Find the names of all inventors who have worked on patents in the 'Quantum Computing' domain.
SELECT Name
FROM Inventors
WHERE I_ID IN (
    SELECT IP.I_ID
    FROM Inventor_Patents IP
    JOIN Patents P ON IP.P_ID = P.P_ID
    WHERE P.Domain = 'Quantum Computing'
);

-- Query 2: Correlated Subquery
-- Find patents that have incurred total costs greater than the average cost of all patents.
SELECT
    P.Title,
    (SELECT SUM(C.Amount) FROM Costs C WHERE C.P_ID = P.P_ID) AS TotalCost
FROM
    Patents P
WHERE
    (SELECT SUM(C.Amount) FROM Costs C WHERE C.P_ID = P.P_ID) >
    (SELECT AVG(TotalAmount) FROM (SELECT SUM(Amount) AS TotalAmount FROM Costs GROUP BY P_ID) AS AvgCosts);

-- Query 3: Nested Query with NOT IN
-- List all reviewers who have NOT been assigned to review the patent titled 'Quantum Entanglement Communication System'.
SELECT Name
FROM Reviewers
WHERE R_ID NOT IN (
    SELECT R_ID
    FROM Patent_Reviewers
    WHERE P_ID = (SELECT P_ID FROM Patents WHERE Title = 'Quantum Entanglement Communication System')
);

-- Query 4: Correlated Subquery with EXISTS
-- Find all inventors who have at least one patent that has faced an opposition.
SELECT
    I.Name,
    I.Email
FROM
    Inventors I
WHERE EXISTS (
    SELECT 1
    FROM Inventor_Patents IP
    JOIN Patents_Opposition PO ON IP.P_ID = PO.P_ID
    WHERE IP.I_ID = I.I_ID
);

-- Query 5: Derived Table (Subquery in FROM clause)
-- Find the domain with the highest number of filed patents.
SELECT
    Domain,
    PatentCount
FROM (
    SELECT Domain, COUNT(P_ID) AS PatentCount
    FROM Patents
    GROUP BY Domain
) AS DomainCounts
ORDER BY PatentCount DESC
LIMIT 1;


-- ===================================================================================
-- SECTION 3: TRIGGER, FUNCTION, AND PROCEDURE
-- ===================================================================================

-- TRIGGER: Creates an audit log whenever a patent's status is updated.
-- 1. First, create the audit table.
CREATE TABLE Patent_Status_Audit (
    LogID INT PRIMARY KEY AUTO_INCREMENT,
    P_ID INT,
    Old_Status VARCHAR(50),
    New_Status VARCHAR(50),
    Changed_By VARCHAR(255),
    Changed_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Now, create the trigger.
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

/*
-- Example usage for the trigger:
UPDATE Patents SET Status = 'Under Review' WHERE P_ID = 1;
SELECT * FROM Patent_Status_Audit;
*/


-- FUNCTION: Calculates the current age of a patent in years.
DELIMITER $$
CREATE FUNCTION GetPatentAge(filing_date DATE)
RETURNS DECIMAL(10, 2)
DETERMINISTIC
BEGIN
    DECLARE age DECIMAL(10, 2);
    SET age = DATEDIFF(CURDATE(), filing_date) / 365.25;
    RETURN age;
END$$
DELIMITER ;

/*
-- Example usage for the function:
SELECT Title, Filing_Date, GetPatentAge(Filing_Date) AS PatentAgeInYears FROM Patents;
*/


-- PROCEDURE: Retrieves all patent details for a given domain name.
DELIMITER $$
CREATE PROCEDURE GetPatentsByDomain(IN domain_name VARCHAR(100))
BEGIN
    SELECT
        P_ID,
        Title,
        Appl_Name,
        Filing_Date,
        Status
    FROM Patents
    WHERE Domain = domain_name
    ORDER BY Filing_Date DESC;
END$$
DELIMITER ;

/*
-- Example usage for the procedure:
CALL GetPatentsByDomain('Biotechnology');
*/


-- ===================================================================================
-- SECTION 4: DATA ANALYSIS / VISUALIZATION QUERIES
-- ===================================================================================

-- Aggregate Functions (GROUP BY, HAVING)
-- Find the total renewal fees paid for each patent that has had at least two renewals.
SELECT
    P_ID,
    COUNT(R_No) AS NumberOfRenewals
FROM
    Renewals
WHERE
    Fee_Status LIKE '%Paid%'
GROUP BY
    P_ID
HAVING
    COUNT(R_No) >= 2;

-- Window Function
-- Rank inventors based on the number of patents they have filed.
SELECT
    I.Name,
    COUNT(IP.P_ID) AS PatentCount,
    RANK() OVER (ORDER BY COUNT(IP.P_ID) DESC) AS InventorRank
FROM
    Inventors I
JOIN
    Inventor_Patents IP ON I.I_ID = IP.I_ID
GROUP BY
    I.I_ID;

-- CASE Statement (like SWITCH)
-- Categorize patents based on their status.
SELECT
    Title,
    Status,
    CASE
        WHEN Status = 'Granted' THEN 'Active'
        WHEN Status = 'Expired' OR Status = 'Withdrawn' THEN 'Inactive'
        ELSE 'Pending Action'
    END AS Category
FROM
    Patents;

-- WITH Clause (Common Table Expression - CTE)
-- Find all patents from 'BioGen Labs', then show who reviewed them.
WITH BioGenPatents AS (
    SELECT P_ID, Title, Domain
    FROM Patents
    WHERE Appl_Name = 'BioGen Labs'
)
SELECT
    BGP.Title,
    BGP.Domain,
    E.Exam_Date,
    R.Name AS ReviewerName
FROM
    BioGenPatents BGP
JOIN
    Examination E ON BGP.P_ID = E.P_ID
JOIN
    Reviewers R ON E.R_ID = R.R_ID;


-- ===================================================================================
-- SECTION 5: DEMONSTRATE USER PERMISSIONS (DCL)
-- ===================================================================================

-- Step 1: Create Roles
CREATE ROLE IF NOT EXISTS 'patent_clerk', 'examiner';

-- Step 2: Grant Privileges to Roles
-- Clerk Role: Can view patents, manage costs and renewals.
GRANT SELECT ON patent_system.Patents TO 'patent_clerk';
GRANT SELECT, INSERT, UPDATE ON patent_system.Costs TO 'patent_clerk';
GRANT SELECT, INSERT, UPDATE ON patent_system.Renewals TO 'patent_clerk';

-- Examiner Role: Can view everything, and update examination/patent status.
GRANT SELECT ON patent_system.* TO 'examiner';
GRANT INSERT, UPDATE ON patent_system.Examination TO 'examiner';
GRANT UPDATE(Status) ON patent_system.Patents TO 'examiner'; -- Can only update the Status column

-- Step 3: Create Users (use different passwords in a real system)
CREATE USER IF NOT EXISTS 'clerk_user'@'localhost' IDENTIFIED BY 'password123';
CREATE USER IF NOT EXISTS 'examiner_user'@'localhost' IDENTIFIED BY 'securepass456';

-- Step 4: Assign Roles to Users
GRANT 'patent_clerk' TO 'clerk_user'@'localhost';
GRANT 'examiner' TO 'examiner_user'@'localhost';

-- Step 5: Set the default roles to be active upon login
SET DEFAULT ROLE ALL TO 'clerk_user'@'localhost', 'examiner_user'@'localhost';

-- Final step to apply privilege changes
FLUSH PRIVILEGES;

-- Now, if you log in as 'clerk_user', you cannot update the Examination table.
-- If you log in as 'examiner_user', you cannot insert new data into the Costs table.
-- This demonstrates the successful separation of duties via user permissions.