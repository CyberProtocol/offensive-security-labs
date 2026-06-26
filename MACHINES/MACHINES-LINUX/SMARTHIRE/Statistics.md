# Performance Statistics & Metrics: SmartHire

## Machine Overview
* **Description:** Linux-based web application focused on subdomain enumeration, MLflow exploitation, credential access, and privilege escalation through misconfigured internal tooling.
* **Flags Obtained:** User, Root
* **Core Skills:** Web Enumeration, Subdomain Discovery, MLflow Exploitation, Python App Analysis, Linux Privilege Escalation

## Effort & Complexity Indicators

* **Platform / Origin:** Hack The Box
* **Operating System:** Ubuntu Linux
* **Official Difficulty:** Medium–Hard
* **Perceived Difficulty:** Medium (requires chaining web + ML exploitation + privilege escalation via internal tooling)

---
 
## Technical Skills Matrix

Quantitative summary of the technical proficiencies demonstrated during the assessment of SmartHire:

| Attack Phase | Technologies & Techniques | Proficiency |
| :--- | :--- | :--- |
| **Reconnaissance** | `Nmap`, service identification, HTTP analysis | Basic |
| **Web Enumeration** | `WhatWeb`, `curl`, manual inspection | Intermediate |
| **Subdomain Discovery** | `FFUF` virtual host fuzzing | Intermediate |
| **Application Analysis** | Login flow testing, API inspection | Intermediate |
| **Exploitation** | MLflow `CVE-2024-37054` RCE | Advanced |
| **Post Exploitation** | Python application enumeration, file analysis | Intermediate |
| **Privilege Escalation** | Plugin abuse via `sudo` execution path | Advanced |

---

## Post-Mortem & Lessons Learned

### 1. Core Concepts Mastered

* **Subdomain Enumeration:** Identified hidden attack surface via virtual host fuzzing.
* **MLflow Exploitation:** Understood impact of insecure model handling and deserialization flaws.
* **Python Application Review:** Analyzed Flask/MLflow-style structure and configuration exposure.
* **Privilege Escalation via Plugins:** Demonstrated how insecure plugin loading can lead to full system compromise.
* **Service Chaining:** Combined web exploitation with internal tooling abuse.

### 2. Challenges Encountered

* Initial access required correct identification of MLflow service version.
* Exploitation depended on validating CVE compatibility with environment.
* Privilege escalation required understanding plugin execution flow in internal tool.
* **Key Takeaway:** Modern systems often fail not at one vulnerability, but at the interaction between services and internal automation tools.

### 3. Defensive Perspective & Hardening Recommendations

To remediate the architectural gaps exploited on SmartHire, the following controls must be implemented:

* **Access Control:** Restrict access to MLflow interfaces and disable unauthenticated model uploads.
* **Artifact Sandboxing:** Validate and sandbox all ML artifacts before execution.
* **Surface Reduction:** Remove unnecessary subdomains and protect internal services behind authentication.
* **Integrity Controls:** Enforce strict permissions on plugin directories.
* **Path Validation:** Avoid dynamic execution paths in privileged tools.
* **Least Privilege:** Apply least privilege for service accounts.

---

### 4. Attack Chain Summary

```text
Nmap
↓
smarthire.htb
↓
Subdomain enumeration (models.smarthire.htb)
↓
MLflow 2.14.1
↓
CVE-2024-37054 exploitation
↓
Shell as svcweb
↓
Python app enumeration (.env, config, DB)
↓
Internal tool discovery (mlflowctl.py)
↓
Writable plugin directory (/plugins/dev)
↓
sudo execution path abuse
↓
ROOT
```

---

## Final Results

Initial access was achieved through exploitation of MLflow (`CVE-2024-37054`) exposed on a subdomain. Local enumeration revealed a Python-based application with sensitive configuration files and an internal administrative tool. A misconfigured plugin directory writable by a low-privileged user allowed execution of arbitrary code through a `sudo`-executed management script, resulting in full root compromise.

---

## Impact Summary

* Full system compromise achieved
* MLflow service exploited via known CVE
* Sensitive configuration files exposed (`.env`, database)
* Arbitrary code execution via plugin system abuse
* Privilege escalation to `root` via `sudo` misconfiguration

---

## Key Takeaways & Professional Growth

* Subdomains often expose forgotten high-risk services
* ML systems are highly sensitive to unsafe model handling
* Internal admin tools are common privilege escalation vectors
* Plugin architectures must enforce strict integrity controls
* Sudo + writable directories is a critical escalation pattern
