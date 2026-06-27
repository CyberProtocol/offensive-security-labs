# Performance Statistics & Metrics: Policy

## Machine Overview

**Description:** Windows-based penetration testing assessment focused on web enumeration, Group Policy Preferences (GPP) credential disclosure, SMB validation, and privilege escalation through insecure credential storage. The attack chain demonstrated how exposed backup files and misconfigured administrative practices can lead to complete system compromise.

**Flags Obtained:** User, Root (Administrator)

**Core Skills:** Web Enumeration, FFUF, Archive Analysis, John the Ripper, GPP Credential Decryption, SMB Enumeration, NetExec, Enum4Linux, Evil-WinRM, WinPEAS, Windows Privilege Escalation

---

# Effort & Complexity Indicators

**Platform / Origin:** Windows Lab

**Operating System:** Windows Server (Microsoft IIS 10.0)

**Official Difficulty:** Medium

**Perceived Difficulty:** Medium – Requires combining web enumeration, credential recovery from Group Policy Preferences, remote administration, and local privilege escalation through insecure system configuration.

---

# Technical Skills Matrix

| Attack Phase         | Technologies & Techniques                 | Proficiency  |
| -------------------- | ----------------------------------------- | ------------ |
| Reconnaissance       | ICMP, Nmap, Service Enumeration           | Basic        |
| Web Enumeration      | Manual Analysis, FFUF Directory Fuzzing   | Intermediate |
| File Analysis        | ZIP Extraction, TAR Analysis              | Intermediate |
| Credential Recovery  | zip2john, John the Ripper, GPP Decryption | Advanced     |
| SMB Enumeration      | Enum4Linux, NetExec                       | Intermediate |
| Remote Access        | Evil-WinRM                                | Advanced     |
| Post Exploitation    | WinPEAS, Environment Enumeration          | Advanced     |
| Credential Access    | Environment Variable Discovery            | Advanced     |
| Privilege Escalation | Administrator Credential Reuse            | Advanced     |

---

# Post-Mortem & Lessons Learned

## 1. Core Concepts Mastered

* Performed comprehensive enumeration of a Windows web server hosted on Microsoft IIS.
* Identified hidden resources through directory fuzzing and extension discovery.
* Recovered protected archives using password cracking techniques.
* Extracted sensitive Group Policy Preference (GPP) files containing encrypted credentials.
* Decrypted the **cpassword** value using the publicly known GPP encryption key.
* Validated recovered credentials against SMB and WinRM services.
* Conducted Windows post-exploitation using WinPEAS.
* Escalated privileges after identifying administrator credentials exposed through environment variables.

---

## 2. Challenges Encountered

* Initial web inspection revealed no obvious vulnerabilities, requiring extensive directory fuzzing.
* Protected archive files required offline password cracking before further analysis.
* SMB enumeration confirmed the target was a standalone Windows system rather than an Active Directory environment, requiring adaptation of the attack strategy.
* Privilege escalation depended on careful post-exploitation rather than service exploitation.

**Key Takeaway:** Sensitive administrative artifacts exposed through web services, combined with insecure credential management, can provide a complete attack path even when no software vulnerabilities are present.

---

## 3. Defensive Perspective & Hardening Recommendations

To prevent similar attack chains, the following security controls should be implemented:

* Remove backup archives and administrative files from publicly accessible web directories.
* Eliminate legacy Group Policy Preference passwords (**cpassword**) from all systems.
* Restrict access to sensitive configuration files through proper web server permissions.
* Disable unnecessary WinRM exposure or restrict access to trusted administrative networks.
* Avoid storing privileged credentials within environment variables or plaintext configuration files.
* Perform periodic web content audits to identify unintended file exposure.
* Deploy endpoint monitoring capable of detecting WinPEAS, credential extraction, and suspicious WinRM activity.
* Apply the Principle of Least Privilege to administrative accounts and remote management services.

---

# Attack Chain Summary

```text
Host Discovery
        ↓
Nmap Enumeration
        ↓
Web Enumeration
        ↓
Directory Fuzzing (FFUF)
        ↓
Discovery of groups.zip
        ↓
Password Cracking (John the Ripper)
        ↓
GPP File Extraction
        ↓
cpassword Decryption
        ↓
Valid SMB Credentials
        ↓
WinRM Access
        ↓
WinPEAS Enumeration
        ↓
Administrator Credential Discovery
        ↓
Privilege Escalation
        ↓
ROOT
```

---

# Final Results

Initial access was achieved after identifying an exposed archive file through web directory enumeration. Offline password cracking allowed extraction of a Group Policy Preferences configuration file containing an encrypted **cpassword** value. Decryption of the credential provided valid user authentication, enabling remote access through WinRM.

Post-exploitation activities identified administrative credentials stored insecurely within system environment variables. Credential reuse allowed authentication as the local Administrator, resulting in complete compromise of the Windows host.

---

# Impact Summary

* Complete Windows system compromise achieved.
* Hidden web resources successfully identified through directory fuzzing.
* Password-protected archive cracked offline.
* Group Policy Preference credentials recovered and decrypted.
* Valid SMB and WinRM authentication obtained.
* Administrative credentials exposed through insecure environment variables.
* Privilege escalation to Administrator achieved.
* User and Root privileges successfully obtained.

---

# Key Takeaways & Professional Growth

* Improved proficiency in Windows web enumeration and hidden resource discovery.
* Strengthened understanding of Group Policy Preferences credential exposure.
* Reinforced practical experience with password cracking and credential recovery techniques.
* Enhanced Windows post-exploitation methodology using WinPEAS.
* Demonstrated effective adaptation between standalone Windows systems and Active Directory environments.
* Increased awareness of credential exposure risks within administrative configurations.
* Reinforced the importance of secure remote management, credential hygiene, and least-privilege principles in Windows infrastructures.
