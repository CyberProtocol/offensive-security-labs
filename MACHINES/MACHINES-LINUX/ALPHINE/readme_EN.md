# Security Audit Report

**Objective:** System identified as Alpine

---

# Network Connectivity Verification

The audit began with a check of the target machine's availability on the network.

**Command executed:** `ping 192.168.0.32`

<img width="1003" height="807" alt="image" src="https://github.com/user-attachments/assets/c96bce33-10ed-41a7-b307-bf6b79f4d125" />

**Observations:**

- The host responded successfully to ICMP requests.
- TTL = 64 and low response times confirm that the system is active.
- Connectivity to other internal hosts was also verified, and no anomalies were identified.

**Recommendations:**

- Restrict ICMP responses to trusted internal networks.
- Monitor suspicious ICMP requests.

An active scan was performed with Nmap to identify exposed services and possible entry vectors.

**Command executed:** `nmap -sS --open -sC -sV -n -Pn 192.168.0.32`

**Main results:**

| Port | Service | Version |
|---|---|---|
| 22/tcp | SSH | OpenSSH 10.2 |
| 80/tcp | HTTP | Apache 2.4.66 |

<img width="1350" height="701" alt="image" src="https://github.com/user-attachments/assets/1c7e2686-3cc9-4854-b9c5-8056e09bb39f" />

**Observations:**

- All discovered ports and services were reviewed, and no additional services or obvious vulnerabilities were identified.

**Recommendations:**

- Limit open ports.
- Configure a firewall and audit periodically.

---

# Web Technology Identification

**WhatWeb** was used to identify server technologies and guide the audit.

**Command executed:** `whatweb http://alpine`

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/ec9550ed-f5af-4df4-bf19-4acfeabb2b31" />

**Observations:**

- Web server: Apache 2.4.66 (Unix).
- Detected technologies: HTML5, scripts, and internal emails.
- Publicly accessible endpoints were reviewed, but no sensitive information or hidden resources were identified.

<img width="1272" height="888" alt="image" src="https://github.com/user-attachments/assets/3defbecc-fc82-46d5-be80-d42589fbd516" />

**Recommendations:**

- Keep the technology stack up to date.
- Hide sensitive information in headers and scripts.

---

# Resource Enumeration -- Fuzzing

Directory and file fuzzing was performed to discover hidden paths and administrative panels.

**Commands executed:**

```bash
ffuf -u http://alpine.nyx/FUZZ -w /usr/share/seclists/Discovery/WebContent/raft-small-directories.txt -c
```

<img width="1089" height="846" alt="image" src="https://github.com/user-attachments/assets/831d49e0-5a51-47cd-b02c-73ea18bed8b2" />

```bash
ffuf -u http://alpine.nyx/FUZZ -w /usr/share/seclists/Discovery/WebContent/small-words.txt -c
```

<img width="983" height="894" alt="image" src="https://github.com/user-attachments/assets/f16132bf-65db-48c0-b1eb-a7c6da18cd9e" />

**Observations:**

- Directories found: /password, /modules, /includes, /cache.
- /server-status protected (403).
- The `~/profile.html` page and the internal dashboard were reviewed, revealing additional sensitive information.

**Recommendations:**

- Restrict access to sensitive directories.
- Disable directory listing.
- Monitor enumeration attempts.

---

# Initial SSH Access

Leaked access credentials were obtained:

<img width="1018" height="601" alt="image" src="https://github.com/user-attachments/assets/4c9092d9-439c-46c1-813e-7173ace1cec0" />

**User:** developer  
**Host:** alpine.nyx  
**Password:** SummerVibes2024!

**Command executed:** `ssh developer@alpine.nyx`

<img width="1012" height="613" alt="image" src="https://github.com/user-attachments/assets/e9c164e6-9fdc-4b21-aa80-044be9127e22" />

**Observations:**

- Access as `developer` confirmed.
- Files within the user's home directory (`user.txt`, `.ssh`) were reviewed, and no additional sensitive information was identified.

<img width="997" height="552" alt="image" src="https://github.com/user-attachments/assets/f589f99f-19ef-42f9-a4fc-2de5ae27dc2b" />

**Recommendations:**

- Change default credentials.
- Periodically review remote access.

---

# Process and Permission Review

Active processes and user permissions were reviewed to evaluate potential privilege escalation vectors.

**Commands executed:**

```bash
ps aux
sudo -l
ls -la /home/developer /home/sysadmin
```

<img width="1022" height="579" alt="image" src="https://github.com/user-attachments/assets/0fb52e1b-32c7-4247-b95c-b940cf018d7d" />

**Observations:**

- Identification of active processes and users (`developer`, `sysadmin`, `apache`, `root`).
- Critical file permissions reviewed, with no additional insecure configurations.
- The `sudo -l` command could not be executed because the user's password was unavailable.

**Recommendations:**

<img width="1000" height="580" alt="image" src="https://github.com/user-attachments/assets/93de888a-76cd-4da0-9f5a-6fd9ca047cc1" />

- Monitor active processes and SSH sessions.

---

# SSH Key Recovery via Git

It was identified that the Git repository contained **commits with SSH key backups**.

**Commands executed:**

```bash
git log --all --pretty=oneline
git show 02f9a18:id_rsa > ~/id_rsa_sysadmin
chmod 600 ~/id_rsa_sysadmin
ssh -i ~/id_rsa_sysadmin sysadmin@localhost
```

**Observations:**

- The Git repository allowed recovery of deleted files from previous commits.
- Access tested as `sysadmin`, without finding additional sensitive information.

<img width="1007" height="669" alt="image" src="https://github.com/user-attachments/assets/2e58fb44-bf92-4134-98b4-ab9197c8d8ab" />

**Recommendations:**

- Do not store private keys in repositories.
- Audit commits and remove sensitive information.

---

# Access to Sensitive Information and Privilege Escalation

Once logged in as sysadmin, an automated cleanup script was discovered at `/opt/scripts/cleanup.sh`, executed periodically via cron.

This script contained a line of code that read files from the `/root` directory and wrote them to a temporary location.

Although the script itself was not directly modifiable by sysadmin, its behavior was predictable.

- The `cleanup.sh` script was found to consolidate files from the `/root` directory into a temporary location.

<img width="1021" height="752" alt="image" src="https://github.com/user-attachments/assets/e7772520-80a4-49b4-938a-72add00ef609" />

**Recommendations:**

- Restrict execution of sensitive scripts.
- Regularly review the permissions and execution logs of automated scripts.
