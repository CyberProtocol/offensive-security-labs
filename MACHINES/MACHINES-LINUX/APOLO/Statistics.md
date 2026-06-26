# Performance Statistics & Metrics: Apple Store

## Machine Overview

* **Description:** Linux web application focused on chained exploitation: SQL Injection, credential dumping, file upload abuse, and privilege escalation to root.
* **Flags Obtained:** User, Root
* **Core Skills:** Web Enumeration, SQL Injection, Burp Suite, SQLMap, File Upload Bypass, Linux Privilege Escalation

## Effort & Complexity Indicators

* **Platform / Origin:** Docker Lab
* **Operating System:** Ubuntu Linux
* **Official Difficulty:** Medium
* **Perceived Difficulty:** Medium – Requires chaining multiple vulnerabilities across web and system layers.

---

## Technical Skills Matrix

| Attack Phase | Technologies & Techniques | Proficiency |
| :--- | :--- | :--- |
| **Reconnaissance** | ICMP probing, Nmap scanning, WhatWeb fingerprinting | Basic |
| **Web Enumeration** | Directory fuzzing with ffuf, manual application analysis | Intermediate |
| **Authentication** | Registration and login flow analysis | Intermediate |
| **SQL Injection** | Time-based SQLi using Burp Suite and SQLMap | Advanced |
| **Credential Access** | Database extraction and hash cracking | Advanced |
| **Web Exploitation** | Admin panel compromise and file upload bypass (RCE) | Advanced |
| **Post-Exploitation** | Shell stabilization and system enumeration | Intermediate |
| **Privilege Escalation** | Weak credentials and misconfigurations leading to root | Advanced |

---

## Post-Mortem & Lessons Learned

### 1. Core Concepts Mastered

* **SQL Injection:** Exploited authenticated SQL Injection to extract sensitive database data.
* **Credential Security:** Understood impact of weak hashing and offline password cracking.
* **File Upload Security:** Bypassed weak validation to achieve Remote Code Execution.
* **Linux Enumeration:** Improved post-exploitation workflow and system reconnaissance.
* **Privilege Escalation:** Chained multiple weaknesses into full system compromise.

---

### 2. Challenges Encountered

* Initial focus on application logic delayed discovery of injection point.
* File upload restrictions required request manipulation and extension bypass.
* Privilege escalation required combining credential reuse and system misconfiguration.

* **Key Takeaway:** Small weaknesses can be chained into full system compromise.

---

### 3. Defensive Perspective

* Use prepared statements for all database queries to prevent SQL Injection.
* Enforce strong password policies and secure hashing (Argon2/bcrypt).
* Protect admin interfaces with MFA and monitoring.
* Restrict file uploads using strict allowlists and disable execution in upload directories.
* Apply least privilege across system and application layers.
* Monitor outbound connections for reverse shell detection.

---

### 4. Professional Growth

* Strengthened understanding of full web-to-root attack chains.
* Improved ability to pivot between vulnerability classes.
* Enhanced manual validation skills using Burp Suite.
* Reinforced importance of input validation at every layer.
