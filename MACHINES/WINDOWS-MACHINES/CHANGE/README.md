# Performance Statistics & Metrics: MegaChange Active Directory

## Machine Overview

**Description:** Windows Active Directory environment focused on enterprise attack simulation. The assessment demonstrated a complete domain compromise by chaining weak password policies, insecure Active Directory permissions, and privileged credential exposure through AutoLogon configuration.

**Flags Obtained:** User, Root (Domain Administrator)

**Core Skills:** Active Directory Enumeration, Kerberos Enumeration, Password Attacks, BloodHound Analysis, ACL Abuse, GenericWrite Exploitation, WinRM, Windows Privilege Escalation, Credential Hunting

---

# Effort & Complexity Indicators

**Platform / Origin:** Active Directory Lab

**Operating System:** Windows Server (Domain Controller)

**Official Difficulty:** Hard

**Perceived Difficulty:** Hard – Requires chaining multiple Active Directory attack techniques, privilege delegation abuse, and credential discovery to achieve complete Domain Admin compromise.

---

# Technical Skills Matrix

| Attack Phase                 | Technologies & Techniques       | Proficiency  |
| ---------------------------- | ------------------------------- | ------------ |
| Reconnaissance               | ICMP, Nmap, DNS Enumeration     | Basic        |
| Service Enumeration          | SMB, LDAP, Kerberos, WinRM      | Intermediate |
| User Enumeration             | Kerbrute, DNS, NetExec          | Intermediate |
| Initial Access               | Password Spraying / Brute Force | Advanced     |
| Active Directory Enumeration | BloodHound, bloodhound-python   | Advanced     |
| ACL Exploitation             | GenericWrite Abuse, rpcclient   | Advanced     |
| Lateral Movement             | WinRM, Evil-WinRM               | Advanced     |
| Post Exploitation            | WinPEAS, Registry Analysis      | Intermediate |
| Credential Access            | AutoLogon Credential Discovery  | Advanced     |
| Privilege Escalation         | Domain Administrator Compromise | Expert       |

---

# Post-Mortem & Lessons Learned

## 1. Core Concepts Mastered

* Active Directory attack methodology from external reconnaissance to Domain Administrator.
* Silent Kerberos user enumeration using Kerbrute.
* Password auditing through password spraying and weak credential discovery.
* BloodHound graph analysis to identify dangerous delegated permissions.
* Exploitation of **GenericWrite** permissions for lateral privilege escalation.
* Remote administration through WinRM using Evil-WinRM.
* Windows privilege escalation through insecure AutoLogon registry configuration.
* Credential hunting and post-exploitation automation with WinPEAS.

---

## 2. Challenges Encountered

* Anonymous SMB and LDAP enumeration were properly restricted.
* Guest access and Null Sessions were disabled.
* AS-REP Roasting was not possible because Kerberos pre-authentication was correctly enabled.
* Kerberoasting produced no exploitable Service Principal Names.
* Progress depended entirely on identifying alternative attack paths through Active Directory permissions.

**Key Takeaway:** Secure configurations in isolated services cannot compensate for weak identity management. A single weak password combined with excessive delegated permissions and exposed privileged credentials can result in complete Active Directory compromise.

---

## 3. Defensive Perspective & Hardening Recommendations

To mitigate the vulnerabilities exploited during this assessment, the following security controls should be implemented:

* Enforce strong password policies with a minimum length of 14 characters and banned password lists.
* Eliminate AutoLogon configurations storing privileged credentials in plaintext.
* Deploy Microsoft LAPS for secure local administrator password management.
* Audit Active Directory ACLs regularly and remove unnecessary GenericWrite or GenericAll permissions.
* Restrict WinRM access to privileged administration workstations only.
* Monitor password reset events (Event ID 4724).
* Alert on unauthorized WinRM connections targeting Domain Controllers.
* Deploy Endpoint Detection and Response (EDR) capable of detecting tools such as BloodHound and WinPEAS.
* Implement the Principle of Least Privilege across all administrative accounts.

---

# Attack Chain Summary

```
ICMP Discovery
        ↓
Nmap Enumeration
        ↓
DNS & Kerberos Enumeration
        ↓
Kerbrute User Discovery
        ↓
Password Spraying
        ↓
Compromise of user "alfredo"
        ↓
BloodHound Analysis
        ↓
GenericWrite over sysadmin
        ↓
Password Reset via rpcclient
        ↓
Shell through Evil-WinRM
        ↓
WinPEAS Enumeration
        ↓
AutoLogon Credentials Found
        ↓
Administrator Login
        ↓
DOMAIN ADMIN
```

---

# Final Results

Initial access was obtained through a successful password attack against a standard Active Directory user account protected by a weak password. Internal enumeration identified a dangerous **GenericWrite** delegation over a privileged account, enabling a password reset without prior knowledge of the existing credentials.

Administrative access allowed execution of post-exploitation tools that revealed AutoLogon credentials stored in plaintext within the Windows Registry. These credentials belonged to the Domain Administrator account, resulting in full compromise of the Active Directory environment.

---

# Impact Summary

* Full Active Directory compromise achieved.
* Initial access through weak password policy.
* Successful Kerberos user enumeration.
* Dangerous Active Directory ACL (GenericWrite) exploited.
* Privileged account takeover through password reset.
* Interactive administrative shell obtained via WinRM.
* Domain Administrator credentials recovered from AutoLogon registry keys.
* Complete control over the Domain Controller.
* User and Root flags successfully captured.

---

# Key Takeaways & Professional Growth

* Strengthened practical knowledge of complete Active Directory attack chains.
* Improved understanding of Kerberos-based enumeration techniques.
* Developed advanced proficiency with BloodHound for privilege path analysis.
* Reinforced expertise in Active Directory ACL abuse and delegated permission exploitation.
* Enhanced Windows post-exploitation methodology using WinPEAS.
* Gained practical experience identifying insecure credential storage mechanisms.
* Demonstrated the importance of chaining multiple low-risk vulnerabilities into full enterprise compromise.
* Reinforced defensive understanding of identity security, privilege delegation, and credential management within Windows domains.

