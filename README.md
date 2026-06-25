# Offensive Security Portfolio - Core Labs, Active Directory, and Automation

This repository serves as a professional offensive security portfolio. It consolidates custom-built scripts for audit automation alongside detailed technical documentation (Writeups) covering intrusion, initial access, privilege escalation, and full infrastructure compromise across GNU/Linux and Microsoft Windows environments.

---

## Repository Structure and Architecture

The project is logically structured into independent operational modules, preventing cross-contamination between documentation assets and development binaries. 

*   **automation-scripts/**: Directory containing custom Python and Bash utilities designed to optimize execution times during the reconnaissance phase.
*   **MACHINES/MACHINES-LINUX/**: Technical step-by-step guides focused on vulnerability exploitation, local enumeration, and administrative privilege escalation within Linux systems.
*   **ACTIVE-DIRECTORY/**: Advanced documentation regarding identity auditing, enterprise Windows Server exploitation, and domain-level attack vectors.

---

## Technical Design Advantages

A key strength of this repository is its strict adherence to modern security development standards through structural modularity. By completely isolating the development module (`automation-scripts/`) from the operational logs (`MACHINES/`), the repository eliminates path dependency conflicts. This decoupling allows tools to scale independently while keeping the writeup tree pristine, clean, and highly indexable for automated parsing.

---

## Featured Automation Projects

### Deep Scan (automation-scripts/escaneo_profundo.py)
A modular Python script designed to unify and sequence initial reconnaissance against a target, reducing manual terminal interaction and preventing task omission.

*   **Technical Execution Flow:**
    1.  **Network Validation**: Verification of active network connectivity using ICMP requests (Ping).
    2.  **Port Enumeration**: Automated intensive scans using the Nmap API to identify open ports, active services, and operating system versions.
    3.  **Automated Web Arsenal**: Upon detecting TCP port 80 in an open state, the script sequentially deploys WhatWeb, Katana, Curl, and Ffuf (utilizing the raft-medium dictionary from SecLists).

---

## Intrusion Labs and Evaluated Environments (Writeups)

### Enterprise Windows & Active Directory (AD) Infrastructure
Documentation focused on compromising identity services and Windows-based corporate networks:
*   **Domain Enumeration**: User, group, trust relationship, and password policy enumeration utilizing the Impacket ecosystem, BloodHound, and NetExec.
*   **Authentication Exploitation**: Targeted attacks against authentication protocols, including Kerberoasting, AS-REP Roasting, and local network poisoning (LLMNR/NBT-NS via Responder).
*   **Privilege Escalation**: Lateral movement, local Windows privilege escalation (Token Manipulation, UAC Bypasses), and full Domain Controller (DC) compromise.

### Linux Infrastructure (MACHINES-LINUX)
Analysis of the full attack chain within open-source operating systems:
*   **helix.md**: Intrusion via compromised web services, local enumeration, and administrative privilege escalation (Root).
*   **smarthire.md**: Identification of insecure configurations and exploitation of weaknesses within internal network services.
*   **linux-apolo.md**: Auditing of specific services, local vector exploitation, and advanced post-exploitation techniques.
*   **linux-alpine.md**: Exploitation methodologies on lightweight, minimal containerized Linux distributions.
*   **2maquina_linux.md**: Technical logs and alternative methodologies applied during GNU/Linux system audits.
*   **linux_master.md**: Advanced technical cheat sheets, quick workflows, and useful command references.

---

## Technical Requirements and Dependencies

To deploy and utilize the tools within this portfolio, a Linux-based system (such as Kali Linux) with native tools present in the global PATH (Nmap, WhatWeb, Katana, Curl, Ffuf, Impacket suite) is required, along with the following Python automation library:

```bash
pip3 install python-nmap --break-system-packages
```

---

## Legal Disclaimer

All content, tools, and documentation hosted within this repository have been developed strictly for educational purposes and security research. All testing has been conducted within controlled lab environments or properly authorized platforms. I hold no responsibility for any misuse or damaging actions taken by third parties with this information.
