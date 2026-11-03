-- CarePoint Hospital Management System database
-- MySQL 8.0+
CREATE DATABASE IF NOT EXISTS hospitalemergencydb
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hospitalemergencydb;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS prescription;
DROP TABLE IF EXISTS emergency_case;
DROP TABLE IF EXISTS ambulance;
DROP TABLE IF EXISTS appointment;
DROP TABLE IF EXISTS bed;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS medical_history;
DROP TABLE IF EXISTS doctor;
DROP TABLE IF EXISTS department;
DROP TABLE IF EXISTS medicine;
DROP TABLE IF EXISTS driver;
DROP TABLE IF EXISTS hospital;
DROP TABLE IF EXISTS city;
DROP TABLE IF EXISTS citizen;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE citizen (
  citizen_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  phone VARCHAR(20),
  email VARCHAR(150) UNIQUE,
  address TEXT,
  date_of_birth DATE,
  gender ENUM('Male','Female','Other') DEFAULT 'Other',
  medical_history TEXT,
  password_hash VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE city (
  city_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  area VARCHAR(150)
) ENGINE=InnoDB;

CREATE TABLE hospital (
  hospital_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  type VARCHAR(80),
  location TEXT,
  phone VARCHAR(20),
  total_beds INT DEFAULT 0,
  facilities TEXT,
  contact_person VARCHAR(120),
  city_id INT,
  CONSTRAINT fk_hospital_city FOREIGN KEY (city_id) REFERENCES city(city_id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE department (
  department_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  description TEXT,
  head_doctor_id INT NULL
) ENGINE=InnoDB;

CREATE TABLE doctor (
  doctor_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  specialization VARCHAR(120) NOT NULL,
  phone VARCHAR(20),
  department_id INT,
  experience_years INT DEFAULT 0,
  availability_status ENUM('Available','Unavailable','On Leave') DEFAULT 'Available',
  CONSTRAINT fk_doctor_department FOREIGN KEY (department_id) REFERENCES department(department_id)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

ALTER TABLE department
  ADD CONSTRAINT fk_department_head_doctor FOREIGN KEY (head_doctor_id) REFERENCES doctor(doctor_id)
  ON UPDATE CASCADE ON DELETE SET NULL;

CREATE TABLE medical_history (
  history_id INT AUTO_INCREMENT PRIMARY KEY,
  citizen_id INT NOT NULL,
  `condition` VARCHAR(200) NOT NULL,
  allergies TEXT,
  chronic_issues TEXT,
  notes TEXT,
  CONSTRAINT fk_history_citizen FOREIGN KEY (citizen_id) REFERENCES citizen(citizen_id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE appointment (
  appointment_id INT AUTO_INCREMENT PRIMARY KEY,
  citizen_id INT NOT NULL,
  doctor_id INT NOT NULL,
  hospital_id INT NOT NULL,
  department_id INT NOT NULL,
  appointment_date DATETIME NOT NULL,
  status ENUM('Booked','Confirmed','Completed','Cancelled') DEFAULT 'Booked',
  document_time TIME NULL,
  reason TEXT,
  CONSTRAINT fk_appointment_citizen FOREIGN KEY (citizen_id) REFERENCES citizen(citizen_id),
  CONSTRAINT fk_appointment_doctor FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id),
  CONSTRAINT fk_appointment_hospital FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id),
  CONSTRAINT fk_appointment_department FOREIGN KEY (department_id) REFERENCES department(department_id)
) ENGINE=InnoDB;

CREATE TABLE medicine (
  medicine_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  generic_name VARCHAR(150),
  dosage_form VARCHAR(80),
  description TEXT
) ENGINE=InnoDB;

CREATE TABLE prescription (
  prescription_id INT AUTO_INCREMENT PRIMARY KEY,
  appointment_id INT NOT NULL,
  doctor_id INT NOT NULL,
  medicine_id INT NOT NULL,
  dosage VARCHAR(120) NOT NULL,
  advice TEXT,
  `date` DATE NOT NULL,
  CONSTRAINT fk_prescription_appointment FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id),
  CONSTRAINT fk_prescription_doctor FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id),
  CONSTRAINT fk_prescription_medicine FOREIGN KEY (medicine_id) REFERENCES medicine(medicine_id)
) ENGINE=InnoDB;

CREATE TABLE bed (
  bed_id INT AUTO_INCREMENT PRIMARY KEY,
  hospital_id INT NOT NULL,
  bed_type VARCHAR(80) NOT NULL,
  status ENUM('Available','Occupied','Maintenance') DEFAULT 'Available',
  CONSTRAINT fk_bed_hospital FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE staff (
  staff_id INT AUTO_INCREMENT PRIMARY KEY,
  hospital_id INT NOT NULL,
  name VARCHAR(120) NOT NULL,
  role VARCHAR(100) NOT NULL,
  shift ENUM('Morning','Evening','Night','Rotational') DEFAULT 'Morning',
  CONSTRAINT fk_staff_hospital FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE driver (
  driver_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  phone VARCHAR(20),
  license_no VARCHAR(80) NOT NULL UNIQUE,
  availability_status ENUM('Available','Unavailable') DEFAULT 'Available'
) ENGINE=InnoDB;

CREATE TABLE emergency_case (
  case_id INT AUTO_INCREMENT PRIMARY KEY,
  citizen_id INT NOT NULL,
  type VARCHAR(100) NOT NULL,
  severity ENUM('Low','Medium','High','Critical') NOT NULL,
  description TEXT,
  time_reported DATETIME DEFAULT CURRENT_TIMESTAMP,
  status ENUM('Reported','Assigned','In Progress','Resolved','Closed') DEFAULT 'Reported',
  CONSTRAINT fk_emergency_citizen FOREIGN KEY (citizen_id) REFERENCES citizen(citizen_id)
) ENGINE=InnoDB;

CREATE TABLE ambulance (
  ambulance_id INT AUTO_INCREMENT PRIMARY KEY,
  vehicle_no VARCHAR(40) NOT NULL UNIQUE,
  driver_id INT,
  staff_id INT,
  location VARCHAR(200),
  phone VARCHAR(20),
  case_id INT NULL,
  CONSTRAINT fk_ambulance_driver FOREIGN KEY (driver_id) REFERENCES driver(driver_id) ON DELETE SET NULL,
  CONSTRAINT fk_ambulance_staff FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE SET NULL,
  CONSTRAINT fk_ambulance_case FOREIGN KEY (case_id) REFERENCES emergency_case(case_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Starter records so the dashboard and dropdowns are immediately usable.
INSERT INTO city(name, area) VALUES ('Solapur','Maharashtra');
INSERT INTO hospital(name,type,location,phone,total_beds,facilities,contact_person,city_id)
VALUES ('CarePoint General Hospital','General','Solapur, Maharashtra','0217-000000',100,'Emergency, ICU, Pharmacy','Hospital Administrator',1);
INSERT INTO department(name,description) VALUES
('General Medicine','General health consultations'),
('Cardiology','Heart and cardiovascular care'),
('Emergency','Emergency and trauma care');
INSERT INTO doctor(name,specialization,phone,department_id,experience_years,availability_status) VALUES
('Dr. Ayesha Khan','General Medicine','9000000001',1,8,'Available'),
('Dr. Rahul Patil','Cardiology','9000000002',2,10,'Available'),
('Dr. Neha Shaikh','Emergency Medicine','9000000003',3,5,'Available');
UPDATE department SET head_doctor_id=1 WHERE department_id=1;
UPDATE department SET head_doctor_id=2 WHERE department_id=2;
UPDATE department SET head_doctor_id=3 WHERE department_id=3;
-- 50 fictional demo citizens. INSERT IGNORE makes this safe to re-run by unique email.
INSERT IGNORE INTO citizen(name,phone,email,address,date_of_birth,gender) VALUES
('Sample Citizen','9000000010','citizen@example.com','Solapur','1998-05-12','Other'),
('Aarav Sharma','9000000101','citizen01@carepoint-demo.test','Jule Solapur, Solapur','1981-02-02','Male'),
('Anaya Patel','9000000102','citizen02@carepoint-demo.test','Saat Rasta, Solapur','1982-03-03','Female'),
('Vivaan Deshmukh','9000000103','citizen03@carepoint-demo.test','Vijapur Road, Solapur','1983-04-04','Male'),
('Diya Joshi','9000000104','citizen04@carepoint-demo.test','Railway Lines, Solapur','1984-05-05','Female'),
('Aditya Kulkarni','9000000105','citizen05@carepoint-demo.test','Akkalkot Road, Solapur','1985-06-06','Male'),
('Isha Shah','9000000106','citizen06@carepoint-demo.test','Hotgi Road, Solapur','1986-07-07','Female'),
('Arjun More','9000000107','citizen07@carepoint-demo.test','Jule Solapur, Solapur','1987-08-08','Male'),
('Saanvi Khan','9000000108','citizen08@carepoint-demo.test','Saat Rasta, Solapur','1988-09-09','Female'),
('Reyansh Pawar','9000000109','citizen09@carepoint-demo.test','Vijapur Road, Solapur','1989-10-10','Male'),
('Myra Shaikh','9000000110','citizen10@carepoint-demo.test','Railway Lines, Solapur','1990-11-11','Female'),
('Krishna Jadhav','9000000111','citizen11@carepoint-demo.test','Akkalkot Road, Solapur','1991-12-12','Male'),
('Aadhya Patil','9000000112','citizen12@carepoint-demo.test','Hotgi Road, Solapur','1992-01-13','Female'),
('Ishaan Chavan','9000000113','citizen13@carepoint-demo.test','Jule Solapur, Solapur','1993-02-14','Male'),
('Pari Singh','9000000114','citizen14@carepoint-demo.test','Saat Rasta, Solapur','1994-03-15','Female'),
('Atharv Nair','9000000115','citizen15@carepoint-demo.test','Vijapur Road, Solapur','1995-04-16','Male'),
('Sara Ansari','9000000116','citizen16@carepoint-demo.test','Railway Lines, Solapur','1996-05-17','Female'),
('Kabir Mehta','9000000117','citizen17@carepoint-demo.test','Akkalkot Road, Solapur','1997-06-18','Male'),
('Riya Gupta','9000000118','citizen18@carepoint-demo.test','Hotgi Road, Solapur','1998-07-19','Female'),
('Dhruv Bhosale','9000000119','citizen19@carepoint-demo.test','Jule Solapur, Solapur','1999-08-20','Male'),
('Kiara Jain','9000000120','citizen20@carepoint-demo.test','Saat Rasta, Solapur','2000-09-21','Female'),
('Rudra Mane','9000000121','citizen21@carepoint-demo.test','Vijapur Road, Solapur','2001-10-22','Male'),
('Navya Rao','9000000122','citizen22@carepoint-demo.test','Railway Lines, Solapur','2002-11-23','Female'),
('Omkar Shinde','9000000123','citizen23@carepoint-demo.test','Akkalkot Road, Solapur','2003-12-24','Male'),
('Aarohi Verma','9000000124','citizen24@carepoint-demo.test','Hotgi Road, Solapur','2004-01-25','Female'),
('Yash Sutar','9000000125','citizen25@carepoint-demo.test','Jule Solapur, Solapur','1980-02-26','Male'),
('Zara Sheikh','9000000126','citizen26@carepoint-demo.test','Saat Rasta, Solapur','1981-03-27','Female'),
('Samar Khan','9000000127','citizen27@carepoint-demo.test','Vijapur Road, Solapur','1982-04-01','Male'),
('Tara Kulkarni','9000000128','citizen28@carepoint-demo.test','Railway Lines, Solapur','1983-05-02','Female'),
('Vedant Pawar','9000000129','citizen29@carepoint-demo.test','Akkalkot Road, Solapur','1984-06-03','Male'),
('Ira Desai','9000000130','citizen30@carepoint-demo.test','Hotgi Road, Solapur','1985-07-04','Female'),
('Siddharth More','9000000131','citizen31@carepoint-demo.test','Jule Solapur, Solapur','1986-08-05','Male'),
('Meera Joshi','9000000132','citizen32@carepoint-demo.test','Saat Rasta, Solapur','1987-09-06','Female'),
('Athiya Patil','9000000133','citizen33@carepoint-demo.test','Vijapur Road, Solapur','1988-10-07','Female'),
('Rohan Kadam','9000000134','citizen34@carepoint-demo.test','Railway Lines, Solapur','1989-11-08','Male'),
('Nisha Shaikh','9000000135','citizen35@carepoint-demo.test','Akkalkot Road, Solapur','1990-12-09','Female'),
('Manav Shah','9000000136','citizen36@carepoint-demo.test','Hotgi Road, Solapur','1991-01-10','Male'),
('Pihu Sharma','9000000137','citizen37@carepoint-demo.test','Jule Solapur, Solapur','1992-02-11','Female'),
('Kunal Jadhav','9000000138','citizen38@carepoint-demo.test','Saat Rasta, Solapur','1993-03-12','Male'),
('Aditi Nair','9000000139','citizen39@carepoint-demo.test','Vijapur Road, Solapur','1994-04-13','Female'),
('Neil Mehta','9000000140','citizen40@carepoint-demo.test','Railway Lines, Solapur','1995-05-14','Male'),
('Tanvi Deshmukh','9000000141','citizen41@carepoint-demo.test','Akkalkot Road, Solapur','1996-06-15','Female'),
('Pranav Chavan','9000000142','citizen42@carepoint-demo.test','Hotgi Road, Solapur','1997-07-16','Male'),
('Mahi Gupta','9000000143','citizen43@carepoint-demo.test','Jule Solapur, Solapur','1998-08-17','Female'),
('Sameer Ansari','9000000144','citizen44@carepoint-demo.test','Saat Rasta, Solapur','1999-09-18','Male'),
('Sia Jain','9000000145','citizen45@carepoint-demo.test','Vijapur Road, Solapur','2000-10-19','Female'),
('Harsh Bhosale','9000000146','citizen46@carepoint-demo.test','Railway Lines, Solapur','2001-11-20','Male'),
('Anvi Rao','9000000147','citizen47@carepoint-demo.test','Akkalkot Road, Solapur','2002-12-21','Female'),
('Ritesh Mane','9000000148','citizen48@carepoint-demo.test','Hotgi Road, Solapur','2003-01-22','Male'),
('Ishita Verma','9000000149','citizen49@carepoint-demo.test','Jule Solapur, Solapur','2004-02-23','Female');

-- Demo login for the 50 fictional citizens. Password for all: CarePoint@123
-- Werkzeug-compatible PBKDF2-SHA256 hash; updates only the seeded demo email range.
UPDATE citizen
SET password_hash = 'pbkdf2:sha256:600000$7f9e905d4b4aa82d2bdcf4d599a7ae82$62402648ec506ded82a340a1a7016b5a4637eb103bce62af6516be97bab5a4ad'
WHERE email LIKE 'citizen%@carepoint-demo.test';

INSERT INTO medicine(name,generic_name,dosage_form,description) VALUES
('Paracetamol 500mg','Paracetamol','Tablet','Pain and fever relief'),
('Amoxicillin 500mg','Amoxicillin','Capsule','Antibiotic; use only as prescribed');
INSERT INTO staff(hospital_id,name,role,shift) VALUES (1,'Sample Nurse','Nurse','Morning');
INSERT INTO driver(name,phone,license_no,availability_status) VALUES ('Sample Driver','9000000020','MH13-DRIVER-001','Available');
INSERT INTO bed(hospital_id,bed_type,status) VALUES (1,'General','Available'),(1,'ICU','Available');
INSERT INTO appointment(citizen_id,doctor_id,hospital_id,department_id,appointment_date,status,reason)
VALUES (1,1,1,1,DATE_ADD(NOW(), INTERVAL 1 DAY),'Booked','Initial sample appointment');
INSERT INTO emergency_case(citizen_id,type,severity,description,status)
VALUES (1,'Medical emergency','Medium','Sample case for demonstration','Reported');
INSERT INTO ambulance(vehicle_no,driver_id,staff_id,location,phone,case_id)
VALUES ('MH13-AMB-001',1,1,'Solapur','9000000030',1);
