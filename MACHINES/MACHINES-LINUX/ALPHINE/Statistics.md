# Performance Statistics & Metrics: Alpine

## Machine Overview

* **Description:** Linux-based system focused on web enumeration, Git history analysis, and local privilege escalation via misconfigured automation scripts.
* **Flags Obtained:** User, Root
* **Core Skills:** Web Enumeration, Git Forensics, SSH Access, Linux Privilege Escalation, Cron Analysis

## Effort & Complexity Indicators

* **Platform / Origin:** Vulnyx Lab
* **Operating System:** Linux
* **Official Difficulty:** Easy
* **Perceived Difficulty:** Easy–Medium (requires Git history analysis and privilege escalation chaining)

---

## Technical Skills Matrix

| Attack Phase | Technologies & Techniques | Proficiency |
| :--- | :--- | :--- |
| **Reconnaissance** | ICMP probing and port scanning with Nmap | Basic |
| **Web Enumeration** | WhatWeb fingerprinting and directory fuzzing with ffuf | Intermediate |
| **Credential Access** | Exposure of credentials via information disclosure | Intermediate |
| **Initial Access** | SSH access using leaked credentials | Intermediate |
| **Local Enumeration** | Process inspection and permission analysis | Intermediate |
| **Credential Recovery** | Git history analysis for exposed SSH private keys | Advanced |
| **Privilege Escalation** | Abuse of cron-based automation script behavior | Advanced |

---

## Post-Mortem & Lessons Learned

### 1. Core Concepts Mastered

* **Git Forensics:** Learned how sensitive data can persist in Git history even after deletion from working directories.
* **SSH Security:** Reinforced the importance of secure key management and avoiding private key exposure in repositories.
* **Linux Enumeration:** Improved methodology for identifying users, processes, and privilege escalation vectors.
* **Cron Misconfigurations:** Understood how predictable automated tasks can be leveraged for privilege escalation.
* **Attack Chaining:** Combined information disclosure, credential reuse, and system misconfiguration to achieve full compromise.

---

### 2. Challenges Encountered

* **Initial Access:** Access was achieved through leaked credentials discovered during enumeration.
* **Privilege Escalation Path Discovery:** Required analysis of scripts executed via cron to identify predictable file handling behavior.

* **Key Takeaway:** Sensitive information stored in version control systems and poorly designed automation tasks can significantly reduce system security.

---

### 3. Defensive Perspective

* Prevent storage of private keys or secrets in Git repositories.
* Implement secret scanning tools (e.g., Git hooks or CI validation).
* Restrict access to sensitive automation scripts in `/opt` and root-owned directories.
* Audit cron jobs and scheduled tasks regularly.
* Apply strict file permission policies across system scripts.
* Monitor for unauthorized access to backup or temporary directories.

---

### 4. Professional Growth

* Improved understanding of real-world attack chains combining misconfiguration and information disclosure.
* Strengthened Git reconnaissance skills for penetration testing engagements.
* Developed a more systematic approach to Linux privilege escalation.
* Reinforced importance of secure automation design in system administration.
