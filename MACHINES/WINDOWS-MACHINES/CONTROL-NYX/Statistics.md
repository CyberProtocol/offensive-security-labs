# Performance Statistics & Metrics: Controller

## Machine Overview

**Description:** Windows Active Directory assessment focused on enterprise compromise through Kerberos enumeration, AS-REP Roasting, password spraying, remote administration abuse, credential dumping, and Pass-the-Hash techniques, ultimately leading to complete Domain Controller compromise.

**Flags Obtained:** User, Root

**Core Skills:** Active Directory Enumeration, Kerberos Attacks, AS-REP Roasting, Password Spraying, SMB Enumeration, WinRM, BloodHound, SharpHound, WinPEAS, DCSync, NTDS.DIT Extraction, Pass-the-Hash, Windows Privilege Escalation

---

## Effort & Complexity Indicators

**Platform / Origin:** Active Directory Lab

**Operating System:** Windows Server 2019 (Domain Controller)

**Official Difficulty:** Hard

**Perceived Difficulty:** Hard – Requires chaining multiple Active Directory attack vectors, including Kerberos exploitation, password attacks, domain enumeration, credential dumping, and remote administration to achieve complete Domain Administrator compromise.

---

## Technical Skills Matrix

| Attack Phase | Technologies & Techniques | Proficiency |
|--------------|--------------------------|-------------|
| Reconnaissance | ICMP, Nmap, Service Enumeration | Basic |
| Network Enumeration | DNS, LDAP, SMB, Kerberos | Intermediate |
| User Enumeration | Kerbrute, LDAP Enumeration | Advanced |
| Initial Access | AS-REP Roasting, Password Spraying | Advanced |
| Domain Enumeration | NetExec, BloodHound, SharpHound | Advanced |
| Remote Access | WinRM, Evil-WinRM | Advanced |
| Credential Access | NTDS.DIT Extraction, DCSync, SecretsDump | Expert |
| Lateral Movement | SMB, WinRM | Advanced |
| Privilege Escalation | Pass-the-Hash, PsExec | Expert |
| Post Exploitation | WinPEAS, Credential Analysis | Advanced |

---

## Post-Mortem & Lessons Learned

### 1. Core Concepts Mastered

- Performed complete Active Directory reconnaissance without prior credentials.
- Enumerated valid domain users using Kerberos-based techniques.
- Exploited an account vulnerable to AS-REP Roasting to obtain initial credentials.
- Demonstrated the impact of weak password policies through password spraying.
- Leveraged WinRM for interactive remote administration after obtaining valid credentials.
- Executed comprehensive post-exploitation using WinPEAS and SharpHound.
- Extracted the NTDS.DIT database through DCSync, obtaining credential material for every domain account.
- Achieved Domain Administrator access using Pass-the-Hash techniques.

### 2. Challenges Encountered

- Initial anonymous access provided limited SMB permissions despite a successful Null Session.
- User enumeration required multiple Kerberos wordlists before identifying valuable accounts.
- Effective privilege escalation depended on combining several attack vectors rather than exploiting a single critical vulnerability.

**Key Takeaway:** Active Directory environments frequently fail due to the combination of weak authentication policies, insecure Kerberos configurations, excessive privileges, and exposed administrative services rather than a single isolated vulnerability.

---

## Defensive Perspective & Hardening Recommendations

To mitigate the attack chain demonstrated during this assessment, the following security controls should be implemented:

- Disable SMB Null Sessions and restrict anonymous access.
- Enforce Kerberos Pre-Authentication for every domain account.
- Apply strong password policies with account lockout protection against password spraying.
- Restrict DCSync permissions exclusively to authorized Domain Controllers.
- Limit WinRM access to dedicated administration hosts.
- Audit SYSVOL permissions and sensitive Group Policy Objects.
- Monitor Kerberos authentication anomalies, DCSync operations, WinRM sessions, and remote service creation.
- Deploy EDR solutions capable of detecting credential dumping and Active Directory reconnaissance tools.

---

## Attack Chain Summary

```text
Host Discovery
        ↓
Nmap Enumeration
        ↓
DNS / LDAP Enumeration
        ↓
Kerbrute User Enumeration
        ↓
AS-REP Roasting
        ↓
Credential Recovery (b.lewis)
        ↓
Password Spraying
        ↓
WinRM Access (j.levy)
        ↓
WinPEAS & SharpHound
        ↓
DCSync / NTDS.DIT Extraction
        ↓
Pass-the-Hash
        ↓
DOMAIN ADMIN
        ↓
ROOT
```

---

## Final Results

Initial access was obtained by exploiting a domain account vulnerable to AS-REP Roasting, followed by offline password cracking. Additional credential compromise through password spraying enabled remote access via WinRM. Post-exploitation activities revealed sufficient privileges to perform a DCSync attack, resulting in the extraction of the NTDS.DIT database and all domain credential material. Finally, Pass-the-Hash was used to authenticate as the Domain Administrator, achieving complete compromise of the Active Directory environment.

---

## Impact Summary

- Complete Active Directory compromise achieved.
- Successful Kerberos user enumeration.
- AS-REP Roasting vulnerability exploited.
- Weak password policy successfully abused.
- Interactive remote administration through WinRM.
- Full NTDS.DIT database extracted.
- Domain Administrator compromise via Pass-the-Hash.
- User and Root flags successfully obtained.

---

## Key Takeaways & Professional Growth

- Strengthened expertise in enterprise Active Directory attack methodologies.
- Improved proficiency in Kerberos enumeration and authentication attacks.
- Reinforced practical experience with BloodHound and SharpHound for domain analysis.
- Developed advanced understanding of DCSync operations and credential extraction.
- Enhanced Windows post-exploitation workflow using WinPEAS.
- Demonstrated the importance of chaining multiple weaknesses into full Domain Controller compromise.
- Reinforced defensive understanding of identity security, Kerberos hardening, privileged access management, and credential protection.
