# Performance Statistics & Metrics: Helix

## Machine Overview

* **Description:** Linux-based industrial environment focused on web enumeration, service exploitation (Apache NiFi), credential recovery, and privilege escalation through misconfigured operational controls.
* **Flags Obtained:** User, Root
* **Core Skills:** Network Enumeration, Web Exploitation, Subdomain Discovery, CVE Exploitation, SSH Key Recovery, OPC UA Abuse, Linux Privilege Escalation

---

## Effort & Complexity Indicators

* **Platform / Origin:** Hack The Box
* **Operating System:** Ubuntu Linux
* **Official Difficulty:** Medium–Hard
* **Perceived Difficulty:** Medium (multi-stage chaining with industrial protocol abuse)

---

## Technical Skills Matrix

| Attack Phase | Technologies & Techniques | Proficiency |
| :--- | :--- | :--- |
| **Reconnaissance** | Nmap scanning, service enumeration | Basic |
| **Web Enumeration** | WhatWeb fingerprinting, manual inspection | Intermediate |
| **Subdomain Discovery** | Virtual host fuzzing with ffuf | Intermediate |
| **Service Analysis** | Apache NiFi identification & versioning | Advanced |
| **Exploitation** | CVE-2023-34468 exploitation (NiFi RCE) | Advanced |
| **Post Exploitation** | Linux enumeration, service inspection | Intermediate |
| **Credential Recovery** | SSH private key extraction from filesystem | Advanced |
| **Lateral Movement** | SSH authentication via recovered key | Advanced |
| **Privilege Escalation** | OPC UA manipulation + sudo binary abuse | Expert |

---

## Post-Mortem & Lessons Learned

### 1. Core Concepts Mastered

* **Service Enumeration:** Identified attack surface through port scanning and virtual host discovery.
* **Apache NiFi Exploitation:** Understood real-world impact of exposed management interfaces and known CVEs.
* **Credential Exposure:** Demonstrated how backups and system artifacts can leak private SSH keys.
* **Industrial Protocol Abuse:** Learned how OPC UA write operations can influence system state.
* **Privilege Escalation Chains:** Combined service misconfiguration with sudo delegation to achieve root access.

---

### 2. Challenges Encountered

* Initial exploitation attempts against NiFi required validation of correct target parameters.
* Subdomain enumeration was required to fully expose attack surface.
* Privilege escalation depended on understanding system “maintenance mode” logic.
* Industrial context added abstraction beyond typical Linux exploitation.

* **Key Takeaway:** Industrial systems often hide critical logic behind operational states that can be abused if not properly secured.

---

### 3. Defensive Perspective

* Restrict access to Apache NiFi administration interfaces.
* Apply timely patches for known CVEs (e.g., CVE-2023-34468).
* Disable or strictly protect virtual host enumeration exposure.
* Remove sensitive backups such as private SSH keys from disk.
* Enforce strict sudo policies and avoid binary delegation without validation.
* Secure OPC UA endpoints with authentication and role-based access control.

---

### 4. Attack Chain Summary

```
Nmap
↓
helix.htb
↓
Subdomain fuzzing (flow.helix.htb)
↓
Apache NiFi 1.21.0
↓
CVE-2023-34468 RCE
↓
Shell as nifi
↓
SSH key recovery (operator_id_ed25519.bak)
↓
SSH access (operator)
↓
PDF + system documentation
↓
OPC UA state manipulation
↓
sudo helix-maint-console
↓
ROOT
```

---

## Final Results

Initial access was achieved through exploitation of Apache NiFi using a known vulnerability (CVE-2023-34468). From there, local enumeration revealed sensitive artifacts including an SSH private key, enabling lateral movement to the operator user. Final privilege escalation was achieved by abusing operational state conditions combined with a sudo-allowed maintenance binary, resulting in full root compromise.

---

## Impact Summary

* Full system compromise achieved
* Sensitive configuration and operational documents accessed
* SSH credentials recovered from filesystem artifacts
* Industrial control logic abused for privilege escalation

---

## Key Takeaways

* Exposed management services significantly increase attack surface
* Backup artifacts are a common source of credential leakage
* Industrial logic (OPC UA / maintenance states) must be secured at design level
* Privilege escalation often relies on combining multiple weak assumptions rather than a single flaw
