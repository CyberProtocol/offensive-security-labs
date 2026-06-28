## Automation Module - Deep Scan

This directory contains Python-based tools designed to streamline the reconnaissance and initial enumeration phases during security assessments or lab exercises.

---

## Script: `escaneo_profundo.py`

`escaneo_profundo.py` is an automated reconnaissance script that combines multiple tools into a single sequential workflow. Its purpose is to reduce manual effort, speed up early-stage target profiling, and improve visibility when dealing with exposed web services.

### Execution Flow

1. **Basic connectivity check**
   - Verifies host availability using ICMP echo requests (`ping`).

2. **Intensive network scan**
   - Launches a full Nmap scan to identify open ports, running services, service versions, and default scripts.
   - The script uses `python-nmap`, a Python wrapper that makes it easier to interact with Nmap programmatically [web:11][web:20].

3. **HTTP port validation**
   - If TCP port 80 is closed, the script stops and reports the condition.
   - If TCP port 80 is open, the web enumeration module starts automatically.

### Integrated Web Tools

- **WhatWeb**  
  Identifies technologies, CMS platforms, server-side components, and version information.

- **Katana**  
  Performs deep web crawling and endpoint discovery. Katana supports recursive crawling, JavaScript parsing, and configurable crawl depth, which makes it suitable for mapping hidden routes and application structure [web:78][web:82].

- **Curl**  
  Inspects HTTP headers and server responses to quickly validate behavior and response metadata.

- **FFUF**  
  Performs directory and endpoint fuzzing using the `raft-medium-directories.txt` wordlist from SecLists to discover hidden paths and API routes.

---

## Installation Requirements

To run this script on Linux systems such as Kali, you need Python 3, `python-nmap`, and the external tools used by the automation chain.

```bash
sudo apt update && sudo apt install python3-pip -y
pip3 install python-nmap --break-system-packages
```

In addition, the following tools must be installed and available in the global `PATH`:

- `nmap`
- `whatweb`
- `katana`
- `curl`
- `ffuf`

The SecLists wordlist must also be available at:

```text
/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

---

## Purpose

This module is meant to centralize the first phase of reconnaissance into a single, repeatable workflow. It does not replace manual analysis; instead, it accelerates discovery, standardizes the process, and helps avoid missing exposed assets during the initial assessment.
Si quieres, te lo puedo dejar también más corto y más “portfolio style” para que encaje mejor con el resto del README.md.

mas el comando este ```bash
sudo apt update && sudo apt install python3-pip -y
pip3 install python-nmap --break-system-packages
```
