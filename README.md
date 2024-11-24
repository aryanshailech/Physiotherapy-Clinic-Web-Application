# Agrawal Physiotherapy Clinic Web Application

## About
The Agrawal Physiotherapy Clinic web application is designed to provide a comprehensive solution for managing clinic operations, improving administrative efficiency, and enhancing patient care. It bridges the gap between patients, physiotherapists, and administrative staff through role-based access, seamless interaction, and secure management of medical data.

---

## Features

### User Authentication
- Role-based login:
  - **Admin**: Access the admin panel for role and clinic management.
  - **Physiotherapist**: View and manage assigned patients and their treatments.
  - **Receptionist**: Handle patient registration, appointments, and records.
- Secure password storage using hashing.
- Forgot password functionality with email-based OTP verification.
- Session management with role-based permissions.

![Login Page](https://github.com/aryanshailech/Physiotherapy-Clinic-Web-Application/blob/main/Readme_img/login.png)

![Forgot Password](https://github.com/aryanshailech/Physiotherapy-Clinic-Web-Application/blob/main/Readme_img/forgot%20password.png)

---

### Patient Management
- Register new patients with complete details such as name, age, gender, contact, and assigned physiotherapist.
- Search for patients by name, ID, contact number, or email.
- View patient treatment history and assigned physiotherapist details.
- Advanced date-range search for viewing patients added or treated within a specific period.

![Receptionist Dashboard](https://github.com/aryanshailech/Physiotherapy-Clinic-Web-Application/blob/main/Readme_img/receptionist%20dashboard.png)

![Receptionist Search Patient](https://github.com/aryanshailech/Physiotherapy-Clinic-Web-Application/blob/main/Readme_img/receptionist%20search%20patient.png)

![Patient History](https://github.com/aryanshailech/Physiotherapy-Clinic-Web-Application/blob/main/Readme_img/patient%20history.png)

---

### Physiotherapist Management
- Add, edit, or remove physiotherapist profiles, including specialization and contact details.
- View assigned patients and monitor treatment updates.
- Manage physiotherapist-specific specialization data.

![Physiotherapist Dashboard](https://github.com/aryanshailech/Physiotherapy-Clinic-Web-Application/blob/main/Readme_img/physiotherapist%20dashboard.png)

---

### Treatment Management
- Record and update diagnoses, treatment plans, and progress notes.
- Access treatment histories for patients.
- Role-specific permissions to ensure data integrity.

---

### Admin Panel
- Add, edit, or delete roles such as administrators, physiotherapists, and receptionists.
- View and manage profiles for physiotherapists and receptionists.
- Generate analytics to track clinic performance and operational data.

![Admin Dashboard](https://github.com/aryanshailech/Physiotherapy-Clinic-Web-Application/blob/main/Readme_img/admin%20dashboard.png)

---

### Receptionist Dashboard
- Schedule and manage patient appointments.
- Search and retrieve patient records quickly.
- Register new patients with detailed information.

---

### Profile Management
- View and edit user profiles with contact details, address, and profile pictures.
- Upload profile images securely.
- Change passwords with secure validation checks.

![Profile Section](https://github.com/aryanshailech/Physiotherapy-Clinic-Web-Application/blob/main/Readme_img/profile.png)

---

### Notifications and Email
- Email-based notifications for OTP verification during password recovery.
- Alerts for critical updates such as new patient assignments or treatment changes.

---

### File Management
- Secure upload and storage of user and patient images.
- File size limit set to 16 MB to prevent large uploads.

---

## Security Features
- Role-based access control to restrict actions based on user roles.
- Password encryption using hashing.
- Session security to track user login status with strict validation checks.
- Email-based OTP for secure password recovery.
- Input sanitization to prevent SQL injection and other vulnerabilities.

---

## Technologies Used

### Back-End Development
- Python
- Flask
- MySQL

### Front-End Development
- HTML
- CSS

### Libraries and Tools
- Flask-Mail for sending OTPs and email notifications.
- Flask-MySQLdb for database interactions.
- Werkzeug for secure password hashing and file handling.

---

## Database Schema

### Admin
- Fields: `admin_id`, `admin_name`, `email`, `contact_number`, `profile_image`, `address`
- Relations: `Admin_Login`

### Physiotherapist
- Fields: `physiotherapist_id`, `name`, `specialization`, `contact_number`, `profile_image`, `email`, `address`
- Relations: `Physiotherapist_Login`, `Patient`, `Treatment`

### Receptionist
- Fields: `receptionist_id`, `name`, `contact_number`, `email`, `profile_image`, `address`
- Relations: `Receptionist_Login`

### Patient
- Fields: `patient_id`, `name`, `age`, `sex`, `assigned_physio`, `contact_number`, `email`, `address`
- Relations: `Treatment`

### Treatment
- Fields: `treatment_id`, `physiotherapist_id`, `patient_id`, `diagnosis`, `treatment_plan`, `created_at`

### PasswordResetRequests
- Fields: `request_id`, `user_type`, `user_id`, `otp`

---

## Future Enhancements
- Mobile-responsive design for better accessibility.
- Advanced analytics for tracking clinic performance.
- A patient portal for accessing treatment history.
- Payment gateway integration for online transactions.

---

## Screenshots

### Home Page
![Home Page](https://github.com/aryanshailech/Physiotherapy-Clinic-Web-Application/blob/main/Readme_img/home%20page.png)

### About Us Page
![About Us](https://github.com/aryanshailech/Physiotherapy-Clinic-Web-Application/blob/main/Readme_img/about%20us.png)

### Treatments Page
![Treatments](https://github.com/aryanshailech/Physiotherapy-Clinic-Web-Application/blob/main/Readme_img/treatments.png)

### Team
![Team](https://github.com/aryanshailech/Physiotherapy-Clinic-Web-Application/blob/main/Readme_img/team.png)


