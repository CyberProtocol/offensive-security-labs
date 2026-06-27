# Performance Statistics & Metrics: WordPress Windows

## Machine Overview

**Description:** Windows-based penetration testing assessment focused on compromising a WordPress application to obtain remote access through SMB and WinRM. The attack chain combined web enumeration, password attacks, credential reuse, SMB exploitation, and post-exploitation techniques to achieve full administrative control of the target system.

**Flags Obtained:** User, Root (Administrator)

**Core Skills:** Web Enumeration, WordPress Assessment, FFUF, WPScan, CEWL, Password Attacks, SMB Enumeration, WinRM, Metasploit, Meterpreter, Credential Harvesting, Windows Post-Exploitation

---

# Effort & Complexity Indicators

**Platform / Origin:** Windows Lab

**Operating System:** Windows Server / Windows 10 (Apache + WordPress)

**Official Difficulty:** Medium

**Perceived Difficulty:** Medium–Hard – Requires chaining multiple weaknesses across web services, authentication mechanisms, SMB, and Windows remote management.

---

# Technical Skills Matrix

| Attack Phase          | Technologies & Techniques                     | Proficiency  |
| --------------------- | --------------------------------------------- | ------------ |
| Reconnaissance        | Nmap, Service Enumeration                     | Basic        |
| Web Enumeration       | WhatWeb, FFUF, Manual Analysis                | Intermediate |
| WordPress Analysis    | WPScan, REST API Enumeration, Nuclei          | Advanced     |
| Password Attacks      | CEWL, Custom Wordlists, WordPress Brute Force | Advanced     |
| Credential Validation | NetExec, SMB Enumeration                      | Intermediate |
| Remote Code Execution | PsExec, Metasploit, Meterpreter               | Advanced     |
| Post Exploitation     | File Discovery, wp-config.php Analysis        | Advanced     |
| Credential Access     | Plaintext Database Credentials                | Advanced     |
| Remote Administration | Evil-WinRM                                    | Advanced     |
| Privilege Escalation  | Credential Reuse to Administrator             | Advanced     |

---

# Post-Mortem & Lessons Learned

## 1. Core Concepts Mastered

* Performed complete enumeration of a Windows-hosted WordPress application.
* Identified exposed WordPress components through directory fuzzing.
* Enumerated valid users using the WordPress REST API.
* Generated custom password dictionaries using CEWL to improve password attack effectiveness.
* Successfully performed a targeted brute-force attack against the WordPress authentication portal.
* Validated compromised credentials against SMB services.
* Achieved remote code execution through authenticated SMB access.
* Retrieved sensitive configuration files containing plaintext database credentials.
* Reused recovered credentials to obtain administrative access via WinRM.

---

## 2. Challenges Encountered

* Incorrect WordPress URL configuration redirected authenticated sessions to localhost, preventing direct administrative access.
* Web exploitation alone was insufficient; pivoting toward SMB services was required.
* Privilege escalation depended on identifying credential reuse between the web application and Windows administrative services.

**Key Takeaway:** A combination of weak passwords, exposed WordPress functionality, insecure credential storage, and password reuse enabled complete system compromise without exploiting memory corruption or zero-day vulnerabilities.

---

## 3. Defensive Perspective & Hardening Recommendations

To prevent similar attack chains, the following security controls should be implemented:

* Keep WordPress, Apache, PHP, and all plugins fully updated.
* Restrict access to WordPress administrative endpoints using IP allowlists or VPN access.
* Disable unnecessary WordPress REST API endpoints and XML-RPC functionality.
* Remove publicly accessible documentation files such as **readme.html** and **license.txt**.
* Implement account lockout policies and Multi-Factor Authentication (MFA).
* Prevent credential reuse across web applications and operating system accounts.
* Restrict SMB and WinRM access to trusted management networks only.
* Protect sensitive configuration files such as **wp-config.php** through proper filesystem permissions.
* Monitor authentication attempts against WordPress, SMB, and WinRM services.

---

# Attack Chain Summary

```text
Nmap Enumeration
        ↓
Web Enumeration
        ↓
WordPress Discovery
        ↓
FFUF Directory Fuzzing
        ↓
REST API User Enumeration
        ↓
Custom Wordlist Generation (CEWL)
        ↓
WPScan Brute Force
        ↓
Valid WordPress Credentials
        ↓
SMB Authentication
        ↓
Remote Code Execution (PsExec)
        ↓
Meterpreter Shell
        ↓
wp-config.php Extraction
        ↓
Database Credential Recovery
        ↓
Credential Reuse
        ↓
Administrator Access via WinRM
        ↓
ROOT
```

---

# Final Results

Initial access was achieved through reconnaissance of a publicly accessible WordPress application. User enumeration and custom dictionary generation enabled a successful password attack against the authentication portal. Although an incorrect WordPress configuration prevented direct administrative login, the recovered credentials were successfully reused against SMB services.

Authenticated SMB access enabled remote code execution and post-exploitation activities, including retrieval of the **wp-config.php** configuration file. Plaintext database credentials stored within the application configuration were subsequently reused to authenticate through WinRM as the local Administrator, resulting in complete compromise of the Windows system.

---

# Impact Summary

* Complete Windows system compromise achieved.
* WordPress user enumeration successful.
* Custom password attack using CEWL and WPScan.
* Valid credentials reused across multiple services.
* Remote code execution obtained through authenticated SMB access.
* Sensitive application configuration files exposed.
* Plaintext credentials recovered from **wp-config.php**.
* Administrative access obtained through WinRM.
* User and Root privileges successfully achieved.

---

# Key Takeaways & Professional Growth

* Strengthened practical knowledge of WordPress security assessments.
* Improved proficiency with web enumeration methodologies and directory fuzzing.
* Gained experience creating customized password dictionaries using CEWL.
* Reinforced credential validation techniques across SMB and WinRM services.
* Enhanced Windows post-exploitation workflow through Meterpreter.
* Improved understanding of credential reuse risks across application and operating system layers.
* Demonstrated how multiple medium-severity weaknesses can be chained into a complete system compromise.
* Reinforced defensive awareness regarding WordPress hardening, password management, service exposure, and credential protection.
