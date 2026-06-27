# Technical Report: Linux Audit MD

---

# Network Description

**Vulnerable server IP:** 192.168.0.23

- **Operating system:** Linux (Debian, inferred from Apache 2.4.25 and the typical Debian OpenSSH build). `cat /etc/os-release` confirmed Debian 9 Stretch.
- **Exposed services:** FTP, SSH, HTTP (WordPress).
- **Topology:** Flat `192.168.0.0/24` network; attacker on the same subnet (e.g., Kali `192.168.0.25`).
- **Additional note:** No firewall was present (`iptables -L` returned empty).

---

# 1. Service Scan and Reconnaissance

## Basic scan

```bash
nmap 192.168.0.23
```

**Result:**  
**Host 192.168.0.23**

- Open ports:
- `21/tcp` = FTP
- `22/tcp` = SSH
- `80/tcp` = HTTP

## Advanced scan with fingerprinting and versions

```bash
nmap -sS --open -sC -sV -n -Pn 192.168.0.23
```

**Detailed result:**

- **Port 21/tcp = FTP**
  - Service: vsftpd 3.0.3
  - Additional information: FTP - anonymous FTP login allowed.
  - Several typical WordPress files and directories are visible:
    - `index.php`, `license.txt`, `readme.html`
    - `wp-activate.php`, `wp-admin/`, `wp-content/`, `wp-includes/`
    - `wp-config.php`, `wp-login.php`, `xmlrpc.php`

<img width="580" height="551" alt="image" src="https://github.com/user-attachments/assets/b450a788-562b-4f6f-8ec6-6072b403844c" />

---

# Vulnerability 1 — Anonymous FTP

**Vulnerability name:** Unauthorized anonymous FTP access  
**Service:** FTP (`vsftpd 3.0.3` on port 21)  
**Severity:** HIGH

**Technical description:**  
The FTP server allows anonymous access without credentials, enabling the attacker to:

- List files and directories (`ls`)
- Download sensitive files (`get`)
- Reconstruct the WordPress structure and obtain access to configuration files.

**Added command:** `ftp 192.168.0.23 -> anonymous:anonymous@ -> get wp-config.php`

**Impact:**

- Exposure of sensitive information (credentials, paths, WordPress files).
- Facilitation of later attacks (brute force, RCE, etc.).

**Recommendations:**

- Disable anonymous access on the FTP server or restrict it to specific users (`/etc/vsftpd.conf: anonymous_enable=NO`).
- Restrict FTP access only to trusted internal networks (`iptables -A INPUT -p tcp --dport 21 -s 192.168.0.0/24 -j ACCEPT`).
- Monitor and log FTP access to detect anomalous activity (`/var/log/vsftpd.log`).

<img width="1167" height="494" alt="image" src="https://github.com/user-attachments/assets/f0d93b00-6895-46d0-a324-8d797aac304d" />

---

# Vulnerability 2 — Information Exposure in WordPress

**Vulnerability name:** Exposure of WordPress configuration and structure information  
**Service:** HTTP (WordPress 5.2.3 on port 80)  
**Severity:** Medium-High (due to the potential for credential exposure)

**Technical description:**

- The web server shows a generic title and content ("MASTER D TEST -- Test machine for MASTER D").
- The Nmap scan reveals that WordPress 5.2.3 is exposed and accessible.
- `WhatWeb` confirms Apache 2.4.25 and PHP 7.0.
- Anonymous FTP access allows downloading files such as `wp-config.php` and `license.txt`, exposing configuration information and versions.

**Impact:**  
An attacker can:

- Reconstruct the WordPress structure.
- Use configuration files to obtain database credentials.
- Exploit older WordPress/PHP versions looking for known vulnerabilities (e.g., CVE-2019-17671 in WP 5.2.3).

**Recommendations:**

- Hide `wp-config.php` and other configuration files from public access (`.htaccess: <Files wp-config.php> deny from all </Files>`).
- Update WordPress and plugins to recent, patched versions.
- Hide server headers (`Apache/2.4.25`, `WordPress 5.2.3`) to make version reconstruction harder (`ServerTokens Prod`).

---

# 2. Evidence, Anonymous FTP Access, and Reading `wp-config.php`

After the Nmap scan and identification of anonymous FTP, the server was accessed using:

**`ftp 192.168.0.23 -> User: anonymous -> Pass: anonymous`**

Inside the downloaded `wp-config.php` file, the following sensitive information was found:

- **DB_USER:** `wordpress`
- **DB_PASSWORD:** `nvtlrqKd0E1jbXu`

**Type of vulnerability:** High  
**Technical impact:** An attacker can use these credentials to:

- Connect directly to the MySQL/MariaDB database if the service is exposed.
  **Added:** `mysql -h 192.168.0.23 -u wordpress -p'nvtlrqKd0E1jbXu'`
- Extract user information, posts, internal configuration, etc.
- Facilitate a brute-force attack against the WordPress panel if the WordPress user also exists in the CMS.

<img width="1186" height="569" alt="image" src="https://github.com/user-attachments/assets/c1d81b46-4cca-4530-a181-c54ab9be1586" />

---

# Validation of Credentials and Discovery of phpMyAdmin

The credentials obtained from `wp-config.php` were not useful for direct access to the main WordPress login.

Therefore, they were assumed to correspond to the database backend. After no relevant results were obtained with fuzzing, a manual check of common administration paths was performed. Finally, the phpMyAdmin panel was located at `http://192.168.0.23/phpmyadmin/`, confirming the presence of an exposed MySQL/MariaDB administration interface.

**Type of vulnerability:** High  
**Technical impact:** An attacker can access database administration, validate or reuse credentials, and obtain sensitive system information.
**Added:** phpMyAdmin version 4.8.1 vulnerable to SQLi (CVE-2018-19968).

**Recommendations:**

- Restrict phpMyAdmin to internal networks or VPN.
- Avoid public exposure.
- Keep it updated and protected with additional access control.

**Result:**  
The system allowed access to the phpMyAdmin administration panel, confirming that the `wordpress` user is a valid user with administrative privileges.

Once phpMyAdmin was identified, the existence of an exposed database administration interface was confirmed. This increases the attack surface because an authenticated attacker may manage sensitive data, modify tables, and in some insecure configurations attempt escalation toward remote code execution.

**Type of vulnerability:** High  
**Technical impact:** Unauthorized access to database administration, possible extraction or modification of sensitive information, and advanced abuse risk if weak configurations or vulnerable versions exist.

**Recommendations:**

- Restrict phpMyAdmin to internal networks or VPN.
- Keep it updated.
- Review database permissions and disable unnecessary functions.
- Protect access with additional authentication and access control lists.

<img width="886" height="441" alt="image" src="https://github.com/user-attachments/assets/202c472b-5d08-4e34-904a-54583a18dc9b" />

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/d5a24153-ad68-45cc-b649-c1e5668e6770" />

---

# Web Exploitation

After the decoy login failed and phpMyAdmin was located, attention shifted to the main WordPress panel for deeper analysis. Nuclei was run against the main page (`http://192.168.0.23`), producing critical results:

**User information exposure through a vulnerable endpoint revealing:**

- **Users:** `webmaster`
- **Password hash:** `$P$Bsq0diLTcye6AS1ofreys4GzRlRvSr1` (phpPass format)
- **Added:** Hashcat crack confirmed `kittykat1`.

**Type of vulnerability:** High  
**Technical impact:** Direct obtainment of valid authentication credentials for WordPress, enabling later attacks.

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/cf3e320b-3356-4cf7-8714-f0d4f62f15d5" />

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/9aa2e51b-e316-4550-9c51-60d574b99aad" />

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/41ed49f0-31d0-4fc7-8861-752c8409e110" />

---

# Successful Access to WordPress Panel

With the credentials obtained from the Nuclei scan (`webmaster + cracked hash`), access to the WordPress administration panel was validated at the main URL:

**Credentials used:**

- User: `webmaster`
- Password: `kittykat1`

**Result:** Successful access to the WordPress dashboard, confirming `http://192.168.0.23/wp-login/`.

**Technical impact:** Full control of the CMS, allowing installation of malicious plugins, upload of PHP files, and modification of site content.

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/d4e5148f-44b4-4aef-8204-6912a2f4713f" />

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/67782633-f294-428f-ad11-f46ab51f9381" />

After confirming administrative access (`webmaster: kittykat1`), the environment was identified as vulnerable to the `exploit/unix/webapp/wp_admin_shell_upload` module due to the permissive configuration of the `/wp-content/plugins/` directory. This automated exploit was chosen for its high reliability in this type of WordPress deployment.

**Result:**

**Authentication:**

- PHP payload uploaded to `/wp-content/plugins/DcFNQmzkwv/htspqyvSRY.php`
- Meterpreter session 1 active (`192.168.0.25:4444 -> 192.168.0.23:56504`)
- Shell stabilized (`id`, `pwd`, `whoami` -> `www-data`)

**Type:** Critical  
**Impact:** Interactive shell with web server privileges.
**Added:** LinPEAS executed -> no obvious SUIDs, but sudo checks pending.

**Recommendations:**

- Disable file uploads in WordPress.
- Remove write permissions from `/wp-content/uploads/` (`chmod 755`).
- Use a WAF against RCE (ModSecurity).
- Monitor plugins/uploads.

<img width="1188" height="556" alt="image" src="https://github.com/user-attachments/assets/30eb1e4b-e7e6-4f5a-897b-7a92a444dce3" />

<img width="1193" height="528" alt="image" src="https://github.com/user-attachments/assets/ec4a572e-0548-4780-ad59-096475a6dac2" />

---

# Initial Post-Exploitation and Privilege Enumeration

With the Meterpreter session active (`www-data`), the shell was stabilized and the system enumerated.
**Added:** `python3 -c 'import pty; pty.spawn("/bin/bash")'` for a TTY shell.

**Analysis:**

- User `www-data` (limited web server privileges).
- No configured sudo permissions for immediate escalation.
  **Command:** `sudo -l` -> no results.

**Type:** Medium

**Recommendations:**

- Apply least privilege policies for `www-data`.
- Restrict interactive shell access in the web user context.
- Implement containers or chroot to isolate web processes.

---

# 4. System User Enumeration

With the stabilized shell (`www-data`), system users were enumerated:
**Added:** `cat /etc/passwd | cut -d: -f1`.

**Analysis:**

- Users with shells: `root`, `xinstructor`, `webmaster`.
- Current user confirmed: `www-data` (UID 33).
- Possible vectors: accounts `xinstructor` and `webmaster` with valid Bash shells.

**Recommendations:**

- Disable shells on unnecessary service accounts.
- Move sensitive home directories away from accessible paths.
- Enforce password policy for non-root accounts.
- Restrict `/etc/passwd` enumeration using AppArmor/SELinux.
- Monitor access to system files from the web context.

<img width="686" height="563" alt="image" src="https://github.com/user-attachments/assets/73f54f72-531b-4c9f-98a2-2779e746c95a" />

---

# 5. Privilege Escalation: `www-data` to `webmaster`

Using the previously obtained credentials `webmaster:kittykat1`, a manual escalation was performed from `www-data`:
**Added:** `su webmaster` -> password `kittykat1`.

**Result:**

- Successful escalation to user `webmaster`.
- Confirmation of elevated privileges relative to `www-data`.

**Type of vulnerability:** High  
**Impact:** Escalation from web user (`www-data`) to a system account with greater privileges (`webmaster`).

**Recommendations:**

- Do not reuse credentials between web services and system accounts.
- Restrict `su` to trusted administrators only.
- Apply a restrictive sudoers policy for the `webmaster` account.

---

# 6. Final Escalation to Root via Sudo

From the `webmaster` user, sudo privileges were enumerated with `sudo -l`.

**Critical result:**  
Full sudo permissions `(ALL) ALL` were present for the `webmaster` user.
**Exploit:** `sudo -u root /bin/bash`

**Recommendations:**

- Remove sudo privileges from non-administrative accounts (`webmaster`).
- Never grant `(ALL) ALL`.
- Enable sudo authentication with unique, non-reused passwords.
- Implement sudo timeouts and detailed logs (`/var/log/auth.log`).

<img width="717" height="585" alt="image" src="https://github.com/user-attachments/assets/e8dfa7f4-2815-46c8-894b-e0cadf411744" />

---

# Vulnerability Summary

| Vulnerability | Severity | Immediate Mitigation |
|---|---|---|
| Anonymous FTP | High | Disable |
| Exposed `wp-config` | Critical | Move outside web root |
| Weak WordPress admin | Critical | 2FA + IP whitelist |
| Sudo `(ALL) ALL` | CRITICAL | Remove immediately |
| Web directory permissions | High | Strict `755/644` |

---

# Auditor Assessment

The infrastructure presents basic configuration failures that allow any external attacker to compromise the entire system in a few steps.

**Complete chain:** Recon → Anonymous FTP → `wp-config` → phpMyAdmin → Nuclei users → WordPress admin → RCE → Sudo Root.

---

# Priority Recommendations

## Critical (24h)

- Remove `sudo ALL` from `webmaster`.
- Disable anonymous FTP.
- Move `wp-config` outside the web root.

## High (1 week)

- Update WordPress and plugins.
- Implement WAF and rate limiting.
- Enable 2FA on administrative panels.

## Medium (1 month)

- Perform a full permissions audit.
- Implement network segmentation.
- Enable SIEM monitoring.

---

# Bibliography

- Nmap documentation: [https://nmap.org](https://nmap.org/)
- WPScan vulnerability database.
- Metasploit framework: [https://metasploit.com](https://metasploit.com/)
- Nuclei templates: WordPress configuration.
- Linux privilege escalation guides.

