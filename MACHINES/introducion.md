# Offensive Security Labs

This repository contains a collection of offensive security laboratories focused on real-world attack simulation across Windows, Linux, Active Directory, and web application environments.

It includes a complete penetration testing methodology, modern exploitation techniques, and an automation module for advanced reconnaissance.

---

## Objective

This project aims to develop practical skills in:

- System reconnaissance and enumeration
- Web application and internal service exploitation
- Privilege escalation on Linux and Windows systems
- Active Directory attacks
- Real attack surface analysis
- Automation of initial penetration testing phases

---

## Methodology

A structured workflow based on professional penetration testing practices is followed:

1. Reconnaissance (OSINT + network)
2. Active enumeration (Nmap, SMB, LDAP, HTTP)
3. Web application analysis
4. Exploitation of vulnerabilities
5. Post-exploitation
6. Privilege escalation
7. Lateral movement (pivoting)
8. Data exfiltration

---

## Lab Overview

---

## Web Application Exploitation (Extended)

Web labs simulate real-world vulnerable applications with multiple attack layers.

### Techniques used

- SQL Injection (boolean-based, time-based, error-based)
- Authentication bypass techniques
- Hidden endpoint discovery
- Directory listing and advanced fuzzing
- File upload bypass (.php, .phtml, .phar)
- Remote Code Execution (RCE)
- Session hijacking and cookie reuse
- Backup file exposure (.zip, .tar, .bak)
- REST API abuse
- User enumeration via APIs and forms

---

### Common findings

- Fully exposed databases
- Administrative panels without MFA
- Executable file uploads on web servers
- Exposed configuration files (config.php, wp-config.php)
- Outdated CMS versions (WordPress, Apache, PHP)
- Lack of rate limiting on login forms

---

### Simulated impact

- User database exfiltration
- Credential and hash dumping
- Administrative panel access
- Remote command execution
- Full backend compromise

---

## Windows Exploitation (Extended)

Focused on Windows environments and exposed enterprise services.

### Techniques used

- SMB enumeration (null sessions)
- WinRM exploitation (port 5985)
- RPC and NetBIOS enumeration
- Kerberos attacks (AS-REP Roasting, Kerberoasting)
- Password spraying on local and domain accounts
- Credential dumping (LSA / NTDS.dit)
- Pass-the-Hash (PTH)
- Group Policy Preferences (GPP) abuse
- Registry misconfigurations (AutoLogon)
- Token impersonation
- Remote service execution (PsExec, WMI, WinRM)

---

### Common findings

- Weak passwords (Password1, Welcome123)
- Credentials stored in registry
- Exposed administrative services without segmentation
- Overprivileged users
- Poor SMB hardening
- WinRM exposed to non-trusted networks

---

### Simulated impact

- Initial access as a standard user
- Privilege escalation to Administrator / SYSTEM
- Full NTDS hash dumping
- Complete system compromise
- Internal lateral movement

---

## Linux Privilege Escalation

- SUID misconfigurations
- Insecure cron jobs
- Password reuse
- SSH key leaks
- /etc/shadow exposure
- PATH hijacking
- Basic kernel privilege escalation

---

## Active Directory Labs

- Kerberos enumeration
- BloodHound attack path analysis
- AS-REP and Kerberoasting attacks
- DCSync attacks
- Domain Admin compromise
- Golden Ticket simulation
- Lateral movement via SMB / WinRM / PsExec

---

## Automation Module - Deep Scanning

This directory contains Python tools designed to automate and accelerate the reconnaissance phase during penetration testing or lab environments.

---

## Script: escaneo_profundo.py

This automated script unifies multiple reconnaissance tools into a single sequential workflow.

The main goal is to reduce manual enumeration time and centralize initial target intelligence gathering.

---

## Execution Flow

### 1. Connectivity Check
- ICMP ping validation
- Host availability verification

---

### 2. Network Scanning (Nmap)
- SYN stealth scan
- Service and version detection
- Default NSE script execution
- Open port identification

---

### 3. HTTP Port Validation

If port 80 is open:

- Web reconnaissance module is automatically triggered

If not:

- The script terminates with status output

---

## Web Reconnaissance Tools

### WhatWeb
- Full technology fingerprinting
- CMS and framework detection
- Server version identification

---

### Katana
- Deep web crawling
- Endpoint discovery
- Form and parameter mapping
- High-depth recursive scanning (level 10)

---

### Curl
- HTTP header analysis
- Server response inspection
- Sensitive information detection in headers

---

### FFUF
- Directory and file fuzzing
- Hidden endpoint discovery
- API enumeration
- Uses SecLists wordlist (raft-medium)

---

## Installation Requirements

```bash
sudo apt update && sudo apt install python3-pip -y
pip3 install python-nmap --break-system-packages
