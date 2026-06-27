# Performance Statistics & Metrics: Apple Store

## Machine Overview

**Description:** Linux web application focused on authenticated SQL Injection, administrative panel compromise, file upload bypass leading to Remote Code Execution, credential attacks, and Linux privilege escalation to full root access.

**Flags Obtained:** User, Root

**Core Skills:** Web Enumeration, SQL Injection, Burp Suite, SQLMap, Hash Cracking, File Upload Bypass, Reverse Shell, Linux Enumeration, Password Attacks, Linux Privilege Escalation

---

## Effort & Complexity Indicators

**Platform / Origin:** Docker Lab

**Operating System:** Ubuntu Linux

**Official Difficulty:** Hard

**Perceived Difficulty:** Hard *(requires chaining multiple web vulnerabilities with post-exploitation and privilege escalation).*

---

# Technical Skills Matrix

| Attack Phase         | Technologies & Techniques                                          | Proficiency  |
| -------------------- | ------------------------------------------------------------------ | ------------ |
| Reconnaissance       | Nmap, WhatWeb, Service Fingerprinting                              | Basic        |
| Web Enumeration      | Manual Analysis, FFUF, Burp Suite                                  | Intermediate |
| Authentication       | User Registration & Login Analysis                                 | Intermediate |
| SQL Injection        | Time-Based SQL Injection, SQLMap                                   | Advanced     |
| Credential Access    | Database Dumping, SHA1 Hash Cracking                               | Advanced     |
| Web Exploitation     | Admin Panel Compromise, File Upload Bypass (RCE)                   | Advanced     |
| Post Exploitation    | Reverse Shell, TTY Stabilization, Linux Enumeration                | Intermediate |
| Privilege Escalation | Password Reuse, Local Brute Force, Shadow Enumeration, Root Access | Advanced     |

---

# Post-Mortem & Lessons Learned

## 1. Core Concepts Mastered

* Authenticated SQL Injection exploitation leading to full database extraction.
* Password hash extraction and offline cracking.
* Administrative panel compromise using recovered credentials.
* File upload bypass techniques to achieve Remote Code Execution.
* Reverse shell establishment and Linux post-exploitation workflow.
* Local enumeration and privilege escalation to root.

---

## 2. Challenges Encountered

* The SQL Injection was only reachable after authenticating as a standard user.
* File upload restrictions required manual request manipulation using Burp Suite.
* Privilege escalation required chaining weak passwords with insecure system permissions.

**Key Takeaway:** Modern web applications often become fully compromised through the combination of several individually manageable weaknesses rather than a single critical vulnerability.

---

## 3. Defensive Perspective & Hardening Recommendations

To remediate the vulnerabilities exploited during this assessment, the following controls should be implemented:

* Replace dynamic SQL queries with prepared statements and parameterized queries.
* Store passwords using Argon2id or bcrypt instead of legacy hashing algorithms.
* Enforce strong password policies together with Multi-Factor Authentication (MFA).
* Restrict file uploads using strict allowlists and disable script execution inside upload directories.
* Remove unnecessary administrative functionality from low-privileged users.
* Correct permissions on sensitive files such as `/etc/shadow`.
* Monitor outbound connections to detect reverse shells.
* Deploy Web Application Firewall (WAF) and Endpoint Detection & Response (EDR).

---

## 4. Attack Chain Summary

```text
Nmap
      ↓
Apache Web Server
      ↓
Manual Enumeration + FFUF
      ↓
User Registration
      ↓
Authenticated Login
      ↓
Time-Based SQL Injection
      ↓
SQLMap Database Dump
      ↓
Password Hash Extraction
      ↓
Hash Cracking
      ↓
Administrator Panel Access
      ↓
File Upload Bypass
      ↓
Remote Code Execution
      ↓
Reverse Shell (www-data)
      ↓
Linux Enumeration
      ↓
User Discovery (luisillo_o)
      ↓
Password Brute Force
      ↓
User Shell
      ↓
/etc/shadow Enumeration
      ↓
ROOT
```

---

# Final Results

Initial access was achieved through an authenticated SQL Injection vulnerability that enabled complete database extraction and recovery of administrative credentials. Administrative access exposed a vulnerable file upload functionality that was bypassed to obtain Remote Code Execution. Local enumeration revealed weak credentials and insecure system permissions, ultimately allowing full root compromise of the Linux server.

---

# Impact Summary

* Full system compromise achieved
* Authenticated SQL Injection successfully exploited
* Complete database extraction performed
* Administrator credentials recovered
* Administrative panel compromised
* Remote Code Execution obtained through file upload bypass
* Interactive reverse shell established
* Local user credentials compromised
* Privilege escalation to root completed

---

# Key Takeaways & Professional Growth

* Authenticated functionality frequently contains high-impact vulnerabilities.
* SQL Injection remains one of the most critical risks for web applications.
* Weak password policies significantly amplify the impact of database breaches.
* File upload functionality must strictly validate both file type and execution permissions.
* Effective Linux enumeration is essential after gaining initial access.
* Chaining multiple low- and medium-severity vulnerabilities can lead to complete system compromise.
* This assessment reinforced a full offensive workflow from reconnaissance to root access while strengthening practical experience in web exploitation and Linux privilege escalation.
