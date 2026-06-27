# Technical Report – Red Team Operation

## Full Active Directory Compromise: From Standard User to Domain Administrator  
**Status:** Completed (Root Obtained)

## 1. Executive Summary

This offensive security assessment simulated a realistic attack against an Active Directory environment. The objective was to demonstrate the impact of a chain of common misconfigurations. Starting with no initial access, full Domain Administrator compromise was achieved in a short time frame.

The attack chain leveraged the following weaknesses:

1. Weak passwords in standard user accounts.
2. Misconfigured delegated permissions (GenericWrite).
3. Insecure storage of privileged credentials (AutoLogon).

This document provides a complete technical narrative, step by step, serving both as evidence of the identified vulnerabilities and as a remediation guide.

## 2. Detailed Technical Narrative (Kill Chain)

### Phase 1: Initial Reconnaissance and Host Availability Confirmation

The operation began by verifying basic connectivity to the target at `192.168.0.19`. A successful ICMP response confirmed that the asset was online and reachable from the attacker’s position within the network.

- Finding: `TTL=128` indicated a Windows Server system.
- Decision: Proceed with port scanning to identify exposed services.

![Figure 1: Initial connectivity confirmation](https://github.com/user-attachments/assets/150e6a63-e96a-4127-ad68-1ac91084e1c3)

### Phase 2: Service Enumeration and Target Role Identification

A comprehensive Nmap scan was conducted to identify open ports and service versions. The results were critical: the target was not just any server, but the Domain Controller (DC) of the `megachange.nyx` domain.

- Key Services: DNS (53), Kerberos (88), LDAP (389), SMB (445), and WinRM (5985).
- Analysis: The presence of an exposed WinRM service would become a crucial attack vector later.

![Identification of the Domain Controller and exposed services](https://github.com/user-attachments/assets/9cc967af-c45a-4862-9cca-165b787014b8)

### Phase 3: Domain Mapping via DNS

Before proceeding with active attacks, it was necessary to understand the domain structure. Using `dig` and `fierce`, the DNS service was queried.

- Finding: The `megachange.nyx` domain and its delegation were confirmed. No hidden subdomains were discovered, indicating that the external attack surface was well contained.
- Pivot: With no DNS-based attack vectors available, the next logical step was unauthenticated enumeration via SMB and LDAP.

![Initial domain structure mapping](https://github.com/user-attachments/assets/7dd44797-3c59-44a7-b154-cbf9688192ed)

![Initial domain structure mapping](https://github.com/user-attachments/assets/b5ecce73-40b9-462c-a5c3-e3e696a8d2d7)

### Phase 4: Anonymous Enumeration Attempts (Failed)

Classic misconfiguration vectors were tested:

1. SMB Null Sessions: Blocked (`STATUS_ACCESS_DENIED`).
2. Guest Account: Properly disabled.
3. RID Brute Force: Blocked due to insufficient permissions.

- Defensive Insight: Basic hardening on the Domain Controller was correctly implemented against anonymous access.
- Conclusion: Valid credentials were required to proceed further.

![Outputs from failed enumeration attempts with nxc/netexec](https://github.com/user-attachments/assets/cdd56a93-e6a8-4ca5-a73f-8d352e2cbdf1)

### Phase 5: User Enumeration via Kerberos

Since unauthenticated enumeration was not possible, Kerbrute was used to identify valid usernames without triggering account lockouts (a stealthy technique).

- Discovered Users: `alfredo`, `administrator`, `change`.
- Strategy: `alfredo` appeared to be a standard user, making it an ideal initial brute-force target.

![Silent identification of valid users via Kerberos](https://github.com/user-attachments/assets/b9f54ff0-b193-411b-815e-d5876b58cb0c)

### Phase 6: Brute Force and Initial Access

Using the discovered usernames, a brute-force attack was executed against `alfredo` via SMB using the `rockyou.txt` wordlist.

- Critical Finding: The password was `Password1`.
- Impact: Initial access was obtained in fewer than 25 attempts, demonstrating a weak or poorly enforced password policy.

Technical Note – Exhaustion of Alternative Vectors:

Before relying solely on brute force, more advanced Kerberos attack vectors were tested:

- AS-REP Roasting: `GetNPUsers` was executed against `alfredo`, but the account was not vulnerable (pre-authentication enabled).
- Kerberoasting: `GetUserSPNs` was executed to identify exploitable SPNs, but no entries were found.

These results confirmed that Kerberos was properly configured, leaving weak human password practices as the only viable entry point.

![Initial compromise achieved due to weak credentials](https://github.com/user-attachments/assets/1a80c866-d730-4f27-881c-c047b532fa46)

![Initial compromise achieved due to weak credentials](https://github.com/user-attachments/assets/4d4320a9-ae0d-4536-8c9b-1e84604f3d9c)

### Phase 7: Internal Enumeration with Valid Credentials

With access as `alfredo`, internal resources were enumerated.

- Shares: Read access to `SYSVOL` and `NETLOGON` (expected), with no obvious sensitive files.
- Users: The presence of a `sysadmin` account was confirmed, created on the same day as `alfredo`.
- Hypothesis: The simultaneous creation suggested a potential relationship in permissions between both accounts.

![Post-compromise internal enumeration](https://github.com/user-attachments/assets/eccd01fc-d8c8-4832-bc98-e4d3bf5a9ca0)

### Phase 8: Privilege Escalation Path Discovery (BloodHound)

To validate the hypothesis, BloodHound (via `bloodhound-python`) was used to map trust relationships within Active Directory.

- Critical Finding: `alfredo` had `GenericWrite` permissions over `sysadmin`.
- Meaning: This allows modification of sensitive attributes of another user, including forcing a password reset—an extremely dangerous delegated permission.

![Critical trust relationship identified for privilege escalation](https://github.com/user-attachments/assets/ba2308d3-0481-4444-936a-2d900e7af66c)

![Critical trust relationship identified for privilege escalation](https://github.com/user-attachments/assets/9f7e6827-6db5-4ac8-99a9-476ce5321851)

### Phase 9: Exploitation and Lateral Movement

The `GenericWrite` permission was exploited using `rpcclient` to reset the `sysadmin` password without knowing the original one.

- Action: `setuserinfo2 sysadmin 23 NewPassword123!`
- Result: Silent success (no errors returned by `rpcclient`).
- Verification: Access was confirmed using `netexec`, showing the `(Pwn3d!)` indicator, meaning `sysadmin` had local administrator privileges on the Domain Controller.

![Successful lateral movement to a privileged account](https://github.com/user-attachments/assets/032c59cc-db63-4bcd-a302-0e1592d47430)

### Phase 10: Remote Access and Post-Exploitation (WinRM)

Since `sysadmin` had administrative privileges and WinRM (port 5985) was exposed, a full interactive shell was established using Evil-WinRM.

- Advantage: Full PowerShell execution capabilities on the target system, significantly more powerful than SMB access.
- Preparation: Post-exploitation tools (`winPEASx64.exe` and `SharpHound.zip`) were uploaded to the user’s desktop for deeper analysis.

![Remote shell established and tooling deployed](https://github.com/user-attachments/assets/30e8407f-8061-4562-8378-93b6f1dd1952)

### Phase 11: Automated Analysis with WinPEAS

WinPEAS was executed to identify misconfigurations, stored credentials, and local privilege escalation vectors.

- Process: The tool scanned the registry, scheduled tasks, services, and policies.
- Initial Result: No kernel vulnerabilities or misconfigured services were found; the system was properly patched.

![Execution of automated enumeration with WinPEAS](https://github.com/user-attachments/assets/bfcdc528-0daf-4879-b832-ef7cdc3d30be)

### Phase 12: Critical Discovery – AutoLogon

During deeper analysis, WinPEAS identified a critical configuration in the Windows registry: AutoLogon enabled for the `administrator` account.

- Maximum Critical Finding: The Domain Administrator password (`d0m@in_c0ntr0ll3r`) was stored in plaintext in the registry.
- Impact: This provides immediate and complete control over the entire Active Directory forest. This practice is strictly forbidden due to its extreme risk.

![Catastrophic exposure of Domain Admin credentials in plaintext](https://github.com/user-attachments/assets/d98beed7-6307-4ba9-91df-f9486a6e162d)

![Catastrophic exposure of Domain Admin credentials in plaintext](https://github.com/user-attachments/assets/107a78a1-99f7-4064-a05e-6da6d3c9a3f9)

### Phase 13: Full Domain Compromise

Using the recovered credentials, a new session was established as `administrator`.

- Verification: The command `whoami /groups` confirmed membership in `Domain Admins`, `Enterprise Admins`, and `Schema Admins`.
- Status: Full control of the infrastructure, including the ability to modify the schema, create Golden Tickets, and access any data.

![Confirmation of maximum privilege level (Domain Admin)](https://github.com/user-attachments/assets/d46506cd-579c-427d-ae85-828d6641f0b8)

![Confirmation of maximum privilege level (Domain Admin)](https://github.com/user-attachments/assets/ddb7d64c-2d7e-4b49-a376-2d2d18d3924a)

### Phase 14: Objective Completion (Root)

To finalize the operation, the administrator’s desktop was accessed and the `root.txt` flag was retrieved.

- Result: Both `user.txt` (as `sysadmin`) and `root.txt` (as `administrator`) were obtained.
- Conclusion: The attack chain was complete and fully successful.

## 3. Defensive Recommendations (Blue Team)

To prevent this attack chain from recurring, the following security improvements are recommended, prioritized by impact:

### 1. Credential Hygiene (Critical Priority)

- Password Policy: Enforce a minimum length of 14+ characters and implement banned password lists to prevent weak combinations such as `Password1`.
- Disable AutoLogon: Audit and immediately remove any `DefaultPassword` registry keys located at `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon`. Privileged credentials must never be stored in plaintext.
- LAPS: Implement Local Administrator Password Solution (LAPS) to securely manage and rotate local administrator passwords.

### 2. Active Directory Hardening

- ACL Auditing: Regularly review delegated permissions such as `GenericWrite`, `GenericAll`, or `ForceChangePassword`. Standard users must never have write permissions over privileged accounts.
- WinRM Segmentation: Restrict port 5985 via firewall rules to only allow connections from privileged administrative workstations (PAWs/Jump Boxes), not from the entire network.

### 3. Detection and Monitoring

- Password Reset Alerts: Configure SOC alerts for Event ID 4724 (password reset attempts), especially when initiated by non-privileged accounts.
- WinRM Monitoring: Alert on WinRM connections (Event ID 6) to Domain Controllers originating from unauthorized subnets.
- EDR Deployment: Deploy EDR solutions capable of detecting post-exploitation tools such as WinPEAS or BloodHound.

### 4. Conclusion

This operation demonstrated how a chain of seemingly minor issues—a weak password, misconfigured permissions, and plaintext credential storage—can combine to enable full domain compromise.

The key takeaway is that security is not only about patching systems; it requires rigorous management of identities, permissions, and configurations. Implementing the recommendations above will significantly increase the difficulty for any real attacker.
