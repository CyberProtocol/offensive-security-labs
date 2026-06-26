# Performance Statistics & Metrics: Linux Machine (MD)

---

## Machine Overview

The analyzed target corresponds to a Linux-based system hosting a web application (WordPress + phpMyAdmin) with multiple exposed services and weak configurations that enabled a full attack chain from initial reconnaissance to root compromise.

- Flags obtained: User / Root  
- Environment: Internal network 192.168.0.0/24  
- Target host: 192.168.0.23  
- Operating system: Linux (Debian-based inferred)  
- Services: FTP, SSH, HTTP (WordPress + phpMyAdmin)

---

## Effort & Complexity Indicators

- Platform: HTB-like lab environment  
- Official difficulty: Medium  
- Perceived difficulty: Medium–High  
- Attack type: Web exploitation + privilege escalation chaining  

---

## Technical Skills Matrix

| Phase | Techniques | Level |
|------|------------|------|
| Reconnaissance | Nmap, service fingerprinting | Basic |
| Web Enumeration | WhatWeb, curl, manual inspection | Intermediate |
| Discovery | Directory/subdomain fuzzing | Intermediate |
| CMS Analysis | WordPress + phpMyAdmin review | Intermediate |
| Exploitation | Credential abuse + RCE | Advanced |
| Post-Exploitation | Linux shell handling, enumeration | Intermediate |
| Privilege Escalation | sudo misconfiguration + credential reuse | Advanced |

---

## Attack Chain Summary

Nmap reconnaissance  
↓  
Anonymous FTP enabled  
↓  
Extraction of wp-config.php  
↓  
Database credentials exposed  
↓  
phpMyAdmin access achieved  
↓  
WordPress enumeration  
↓  
User hash retrieved (Nuclei)  
↓  
Password cracking  
↓  
WordPress admin access  
↓  
Plugin upload leading to RCE  
↓  
Shell as www-data  
↓  
Privilege escalation to internal user (webmaster)  
↓  
Misconfigured sudo permissions  
↓  
ROOT compromise  

---

## Impact Summary

- Full system compromise achieved  
- Complete WordPress CMS takeover  
- Database exposure via phpMyAdmin  
- Remote Code Execution (RCE) achieved  
- Privilege escalation to root  
- Exposure of internal system users  

---

## Key Vulnerabilities Identified

### Anonymous FTP Access
Unauthenticated access to sensitive web files.

- Impact: High  
- Risk: Exposure of configuration files

---

### Exposed wp-config.php
Critical configuration file accessible via FTP.

- Impact: Critical  
- Risk: Database credential leakage

---

### Publicly exposed phpMyAdmin
Administrative database interface exposed to the internet.

- Impact: High  
- Risk: full database control

---

### Weak WordPress authentication
Recoverable and crackable password hashes.

- Impact: Critical  
- Result: wp-admin access

---

### Unrestricted file upload
Allows execution of malicious PHP payloads.

- Impact: Critical  
- Result: Remote Code Execution (RCE)

---

### Credential reuse
Same credentials used across multiple services.

- Impact: High  
- Result: lateral movement

---

### Misconfigured sudo (ALL)
Full privilege escalation allowed.

- Impact: Critical  
- Result: immediate root access

---

## Defensive Recommendations

### Services Hardening
- Disable anonymous FTP access
- Restrict SSH to VPN/IP whitelist
- Block public access to phpMyAdmin

### WordPress Security
- Enable 2FA for admin accounts
- Disable PHP execution in upload directories
- Keep CMS and plugins updated

### System Hardening
- Remove sudo ALL ALL permissions
- Separate service and admin accounts
- Avoid credential reuse across services

### Network Security
- Implement network segmentation
- Enforce firewall rules per service
- Enable centralized logging and monitoring

---

## Final Assessment

The compromise was achieved through a chain of misconfigurations rather than a single vulnerability.

The critical failure points were:
- Exposure of sensitive configuration files
- Weak authentication mechanisms
- Excessive privilege assignments
- Poor service segregation

---

## Key Takeaways

- Anonymous FTP is a critical initial entry point
- Exposed configuration files can compromise entire systems
- WordPress without hardening allows fast takeover
- Misconfigured sudo leads directly to root compromise
- Security depends on chained defenses, not isolated fixes
