# # Custom Automation Tool: Deep Scan (escaneo_profundo.py)

This module contains a modular Python script designed to automate the initial reconnaissance and enumeration phases against a target infrastructure. By sequencing multiple industry-standard security tools into a single execution flow, this utility optimizes verification times and ensures no critical asset visibility is omitted.

---

## Technical Features

*   **Network Pre-flight Validation**: Conducts live-host verification via ICMP echo requests (Ping) to prevent unnecessary scan executions on dead targets.
*   **Target Flexibility**: Supports both single IP addresses and fully qualified domain names (FQDN) as input variables.
*   **Intensive Port Auditing**: Integrates with the Nmap API to perform synchronous service version discovery, operating system detection, and default script execution.
*   **Conditional Web Arsenal Deployment**: Automatically detects the state of TCP port 80. If open, it triggers a sequential web attack surface mapping without manual intervention.

---

## Automated Tool Integration

When an active web server is identified on port 80, the script chains the following tools in succession:

1.  **WhatWeb**: Fingerprints web technologies, content management systems (CMS), and active server-side libraries.
2.  **Katana**: Executes an advanced, high-performance web crawling operation up to a depth level of 10 to map hidden paths and endpoints.
3.  **Curl**: Performs raw HTTP header inspection to check responses, server configurations, and payload sizes.
4.  **Ffuf**: Runs structured directory and API fuzzing against the target web application root using the `raft-medium-directories.txt` wordlist from SecLists.

---

## System Requirements and Dependencies

The script is built to run natively on Linux environments (such as Kali Linux). Ensure the following binaries are installed and accessible via the system global PATH:
*   `nmap`
*   `whatweb`
*   `katana`
*   `curl`
*   `ffuf`

### Wordlist Requirements
The fuzzing engine expects the SecLists discovery directory to be present at the standard path:
`/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt`

### Python Dependencies
Install the required wrapper library using `pip3`. On modern Linux distributions with externally managed environments, use the system packages bypass flag:

```bash
sudo apt update && sudo apt install python3-pip -y
pip3 install python-nmap --break-system-packages
```

---

## Usage

Execute the script from the terminal with root privileges to allow Nmap raw packet crafting features:

```bash
sudo python3 escaneo_profundo.py
```

---

## Legal Disclaimer

This automation tool is designed exclusively for authorized penetration testing, security audits, and educational research within controlled laboratory environments. Unauthorized usage against production systems without explicit written consent is strictly illegal.
