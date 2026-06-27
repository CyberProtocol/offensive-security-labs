# Security Audit Report

**Objective:** System identified as Alpine

## Network Connectivity Verification

The audit was initiated with a check of the target machine's availability on the network.

**Command executed:** `ping 192.168.0.32`

![Network connectivity check](https://github.com/user-attachments/assets/c96bce33-10ed-41a7-b307-bf6b79f4d125)

### Observations:

- The host responded successfully to ICMP requests.
- TTL = 64 and low response times confirm that the system is active.
- Connectivity to other internal hosts was reviewed, but no anomalies were found.

### Recommendations:

- Restrict ICMP responses to trusted internal networks.
- Monitor suspicious ICMP requests.

## Service Enumeration with Nmap

An active scan with Nmap was performed to identify exposed services and possible entry vectors.

**Command executed:** `nmap -sS --open -sC -sV -n -Pn 192.168.0.32`

### Main Results:

| Port | Service | Version |
|------|---------|---------|
| 22/tcp | SSH | OpenSSH 10.2 |
| 80/tcp | HTTP | Apache 2.4.66 |

![Nmap scan results](https://github.com/user-attachments/assets/1c7e2686-3cc9-4854-b9c5-8056e09bb39f)

### Observations:

- All known ports and services were reviewed, but **no additional services or evident vulnerabilities were detected**.

### Recommendations:

- Limit open ports.
- Configure firewall and audit periodically.

## Web Technology Identification

**WhatWeb** was used to identify server technologies and guide the audit.

**Command executed:** `whatweb http://alpine`

![WhatWeb results](https://github.com/user-attachments/assets/ec9550ed-f5af-4df4-bf19-4acfeabb2b31)

### Observations:

- Web server: Apache 2.4.66 (Unix).
- Detected technologies: HTML5, scripts, and internal emails.
- Possible APIs and endpoints were reviewed, but **no sensitive information or hidden resources were found**.

![Additional technology scan](https://github.com/user-attachments/assets/3defbecc-fc82-46d5-be80-d42589fbd516)

### Recommendations:

- Keep the technology stack up to date.
- Hide sensitive information in headers and scripts.

## Resource Enumeration -- Fuzzing

**Fuzzing of directories and web files** was performed to discover hidden routes and administrative panels.

**Commands executed:**

```
ffuf -u http://alpine.nyx/FUZZ -w /usr/share/seclists/Discovery/WebContent/raft-small-directories.txt -c
```

![Fuzzing directories](https://github.com/user-attachments/assets/831d49e0-5a51-47cd-b02c-73ea18bed8b2)

```
ffuf -u http://alpine.nyx/FUZZ -w /usr/share/seclists/Discovery/WebContent/small-words.txt -c
```

![Fuzzing files](https://github.com/user-attachments/assets/f16132bf-65db-48c0-b1eb-a7c6da18cd9e)

### Observations:

- Discovered directories: `/password`, `/modules`, `/includes`, `/cache`.
- `/server-status` protected (403).
- Reviewed `~/profile.html~` and internal dashboard **with additional sensitive information**.

### Recommendations:

- Restrict access to sensitive directories.
- Disable directory listing.
- Monitor enumeration attempts.

## Initial SSH Access

Leaked access credentials were obtained:

![Credentials found](https://github.com/user-attachments/assets/4c9092d9-439c-46c1-813e-7173ace1cec0)

**Username:** developer  
**Host:** alpine.nyx  
**Password:** SummerVibes2024!

**Command executed:** `ssh developer@alpine.nyx`

![SSH access confirmation](https://github.com/user-attachments/assets/e9c164e6-9fdc-4b21-aa80-044be9127e22)

### Observations:

- Access confirmed to `~developer~`.
- Home files were reviewed (`~user.txt~`, `~.ssh~`) and **no additional sensitive content was found**.

![Home directory review](https://github.com/user-attachments/assets/f589f99f-19ef-42f9-a4fc-2de5ae27dc2b)

### Recommendations:

- Change default credentials.
- Review remote access periodically.

## Process and Permission Review

Active processes and user permissions were reviewed to assess possible escalation vectors.

**Commands executed:**

```
ps aux
sudo -l
ls -la /home/developer /home/sysadmin
```

![Process and permission review](https://github.com/user-attachments/assets/0fb52e1b-32c7-4247-b95c-b940cf018d7d)

### Observations:

- Identification of active processes and users (`~developer~`, `~sysadmin~`, `~apache~`, root).
- Critical file permissions reviewed, **without additional insecure configurations**.
- `~sudo -l~` ruled out due to unavailable password.

### Recommendations:

![Additional process review](https://github.com/user-attachments/assets/93de888a-76cd-4da0-9f5a-6fd9ca047cc1)

- Monitor processes and active SSH sessions.

## SSH Key Recovery via Git

It was identified that the Git repository contained **commits with SSH key backups**.

**Commands executed:**

```
git log --all --pretty=oneline
git show 02f9a18:id_rsa > ~/id_rsa_sysadmin
chmod 600 ~/id_rsa_sysadmin
ssh -i ~/id_rsa_sysadmin sysadmin@localhost
```

![SSH key recovery](https://github.com/user-attachments/assets/2e58fb44-bf92-4134-98b4-ab9197c8d8ab)

### Observations:

- Git allowed recovery of deleted files from previous commits.
- Access tested as `~sysadmin~`, **without finding additional sensitive information**.

### Recommendations:

- Do not store private keys in repositories.
- Audit commits and remove sensitive information.

## Access to Sensitive Information and Escalation

Once inside as sysadmin, an automated cleanup script was discovered at `/opt/scripts/cleanup.sh`, which was executed periodically through cron.

This script contained a line of code that read files from the `/root` directory and wrote them to a temporary location.

Although the script itself was not directly modifiable by sysadmin, its behavior was predictable.

- `~cleanup.sh~` contains instructions to consolidate root files.

![Cleanup script analysis](https://github.com/user-attachments/assets/e7772520-80a4-49b4-938a-72add00ef609)

### Recommendations:

- Restrict execution of sensitive scripts.
- Review logs and permissions of automated scripts.
