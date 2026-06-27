# Performance Statistics & Metrics: Alpine

## Machine Overview

**Description:** Linux-based security assessment focused on web enumeration, credential discovery, SSH access, Git history exploitation, and privilege escalation through misconfigured automation scripts and cron jobs. The attack demonstrates how information leakage and insecure operational practices can lead to full system compromise.

**Flags Obtained:** User, Root

**Core Skills:** Network Enumeration, Nmap, Web Fuzzing, WhatWeb, SSH Access, Credential Management, Git History Analysis, Linux Privilege Escalation, Cron Job Abuse, Script Analysis

---

## Effort & Complexity Indicators

**Platform / Origin:** Linux Lab

**Operating System:** Alpine Linux / Unix-based system

**Official Difficulty:** Medium–Hard

**Perceived Difficulty:** Medium–Hard – Requires chaining credential discovery, SSH access, Git-based information recovery, and privilege escalation via scheduled automation tasks.

---

# Technical Skills Matrix

| Attack Phase                | Technologies & Techniques              | Proficiency  |
| --------------------------- | -------------------------------------- | ------------ |
| Reconnaissance              | ICMP, Nmap                             | Basic        |
| Service Enumeration         | SSH, HTTP Fingerprinting               | Intermediate |
| Web Enumeration             | WhatWeb, FFUF Directory Fuzzing        | Intermediate |
| Credential Access           | Credential Leak Analysis               | Advanced     |
| Remote Access               | SSH Authentication                     | Advanced     |
| System Enumeration          | ps, sudo -l, file permissions analysis | Intermediate |
| Source Control Exploitation | Git Log Analysis, Commit Recovery      | Advanced     |
| Privilege Escalation        | Cron Job Abuse, Script Analysis        | Advanced     |

---

# Post-Mortem & Lessons Learned

## 1. Core Concepts Mastered

* Performed full network and service enumeration on a Linux target.
* Identified exposed web directories and internal application structure through fuzzing.
* Obtained initial SSH access using exposed credentials.
* Conducted local system enumeration to identify users, processes, and privilege boundaries.
* Extracted sensitive SSH keys from Git commit history.
* Leveraged recovered private keys to escalate access to higher-privileged user accounts.
* Analyzed scheduled scripts executed via cron for privilege escalation opportunities.
* Identified predictable automation behavior leading to root-level impact.

---

## 2. Challenges Encountered

* Initial enumeration did not reveal direct exploitation paths from web services.
* Privilege escalation required pivoting from system enumeration to Git history analysis.
* Cron-based automation was not directly modifiable, requiring analysis of predictable behavior instead.
* Root access depended on indirect information flow rather than direct misconfiguration exploitation.

**Key Takeaway:** Sensitive data exposure in version control systems and predictable automation tasks often provide indirect but powerful privilege escalation paths in Linux environments.

---

## 3. Defensive Perspective & Hardening Recommendations

To mitigate the attack chain demonstrated in this assessment, the following security controls should be applied:

* Restrict ICMP responses to trusted internal networks only.
* Minimize exposed services and enforce firewall rules for SSH and HTTP.
* Remove sensitive files such as private SSH keys from Git repositories.
* Enforce secret scanning in version control systems before commits.
* Implement proper access control on user home directories and configuration files.
* Audit cron jobs and scheduled scripts for unintended data exposure.
* Avoid scripts that process or expose sensitive root-level files.
* Monitor system activity and scheduled task execution for anomalies.

---

# Attack Chain Summary

```text
ICMP Discovery
      ↓
Nmap Enumeration
      ↓
Web Fingerprinting (WhatWeb)
      ↓
Directory Fuzzing (FFUF)
      ↓
Credential Discovery
      ↓
SSH Access (developer)
      ↓
Local Enumeration
      ↓
Git History Analysis
      ↓
SSH Key Recovery (sysadmin)
      ↓
Privilege Escalation via SSH
      ↓
Cron Job Analysis (/opt/scripts/cleanup.sh)
      ↓
ROOT
```

---

# Final Results

Initial access was achieved through valid SSH credentials obtained during the enumeration phase. Further system analysis revealed sensitive SSH private keys stored in Git commit history, enabling lateral movement to a higher-privileged account. Subsequent enumeration identified a scheduled automation script executed via cron that exposed predictable access to sensitive root-level data, ultimately resulting in full system compromise.

---

# Impact Summary

* Full Linux system compromise achieved
* Valid SSH credentials used for initial access
* Sensitive data discovered in Git commit history
* SSH private key recovered and reused
* Privilege escalation via sysadmin account achieved
* Cron job automation misconfiguration exploited
* Root-level access obtained successfully

---

# Key Takeaways & Professional Growth

* Strengthened understanding of Linux enumeration and privilege boundaries.
* Improved ability to extract sensitive data from Git repositories and commit history.
* Reinforced SSH-based lateral movement techniques using private keys.
* Developed awareness of risks introduced by automation and cron jobs.
* Demonstrated how indirect information leaks can lead to full system compromise.
* Enhanced overall methodology from initial access to root through chained misconfigurations.
