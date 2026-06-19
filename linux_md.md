**Informe Técnico: Auditoría Máquina Linux MD **


**\[Descripción Técnica de la Red\]**

**IP del servidor vulnerable: 192.168.0.23.**

- **Sistema operativo**: Linux (Debian, inferido por Apache 2.4.25 y
  OpenSSH típico de Debian). **Comando añadido: cat /etc/os-release →
  Debian 9 Stretch confirmado.**

- **Servicios expuestos**: FTP, SSH, HTTP (WordPress).

- **Topología**: Red plana 192.168.0.0/24; atacante en misma subred (ej.
  Kali 192.168.0.25). **Añadido: Firewall ausente (iptables -L vacío).**

**1.1 Escaneo y Reconocimiento de Servicios (Nmap)**

**Escaneo básico**\
nmap 192.168.0.23

**Resultado:**\
**Host 192.168.0.23**

- Puertos abiertos:

  - 21/tcp = FTP

  - 22/tcp = SSH

  - 80/tcp = HTTP

**Escaneo avanzado con fingerprint y versiones:**\
nmap -sS \--open -sC -sV -n -Pn 192.168.0.23

**Resultado detallado:**

- **Puerto 21/tcp = FTP**\
  Servicio: vsftpd 3.0.3\
  Información adicional: FTP -anon: Anonymous FTP login allowed\
  Se muestran varios archivos y directorios típicos de WordPress:

  - index.php, license.txt, readme.html

  - wp-activate.php, wp-admin/, wp-content/, wp-includes/

  - wp-config.php, wp-login.php, xmlrpc.php

<img width="580" height="551" alt="image" src="https://github.com/user-attachments/assets/b450a788-562b-4f6f-8ec6-6072b403844c" />



**Vulnerabilidad 1 -- FTP Anónimo**

**Nombre de la vulnerabilidad: Acceso FTP anónimo no autorizado**\
**Servicio**: FTP (vsftpd 3.0.3 en puerto 21)\
**Severidad**: ALTA\
**Descripción técnica**: El servidor FTP permite acceso anónimo sin
credenciales, permitiendo al atacante:

- Listar archivos y directorios (ls)

- Descargar archivos sensibles (get)

- Reconstruir la estructura de WordPress y obtener acceso a archivos de
  configuración. **Comando añadido: ftp
  192.168.0.23 → anonymous:anonymous@ → get wp-config.php.**

**Impacto**:

- Exposición de información sensible (credenciales, rutas, archivos de
  WordPress).

- Facilitación de ataques posteriores (fuerza bruta, RCE, etc.).

**Recomendaciones**:

- Deshabilitar el acceso anónimo en el servidor FTP o restringirlo a
  usuarios específicos (/etc/vsftpd.conf: anonymous_enable=NO).

- Restringir el acceso a FTP solo a redes internas de confianza
  (iptables -A INPUT -p tcp \--dport 21 -s 192.168.0.0/24 -j ACCEPT).

- Monitorear y registrar acceso FTP para detectar actividad anómala
  (/var/log/vsftpd.log).

<img width="1167" height="494" alt="image" src="https://github.com/user-attachments/assets/f0d93b00-6895-46d0-a324-8d797aac304d" />


**Vulnerabilidad 2 - Exposición de Información en WordPress**

**Nombre de la vulnerabilidad**: Exposición de información de
configuración y estructura de WordPress\
**Servicio**: HTTP (WordPress 5.2.3 en puerto 80)\
**Severidad**: Media-Alta (por el potencial de las credenciales)

**Descripción técnica**:

- El servidor web muestra un título y contenido genérico (\"MASTER D
  TEST -- Test machine for MASTER D \").

- El escaneo de Nmap revela que WordPress 5.2.3 está expuesto y
  accesible. **Añadido: WhatWeb confirma Apache 2.4.25, PHP 7.0.**

- El acceso FTP anónimo permite descargar archivos
  como wp-config.php y license.txt, exponiendo información de
  configuración y versiones.

**Impacto**:\
Un atacante puede:

- Reconstruir la estructura de WordPress.

- Usar archivos de configuración para obtener credenciales de base de
  datos.

- Aprovechar versiones antiguas de WordPress/PHP para buscar
  vulnerabilidades conocidas (ej. CVE-2019-17671 en WP 5.2.3).

**Recomendaciones**:

- Ocultar wp-config.php y otros archivos de configuración del acceso
  público (.htaccess: \<Files wp-config.php\> deny from all \</Files\>).

- Actualizar WordPress y plugins a versiones recientes y parcheadas.

- Ocultar cabeceras de servidor (Apache/2.4.25, WordPress 5.2.3) para
  dificultar la reconstrucción de versiones (ServerTokens Prod).

**2. Evidencias, Acceso FTP Anónimo y Lectura de wp-config.php**

Tras el escaneo con Nmap y la identificación de FTP anónimo, se accedió
al servidor mediante:\
**ftp 192.168.0.23 → User: anonymous → Pass: anonymous.**

En el archivo wp-config.php descargado se encontró la siguiente
información sensible:\
**DB_USER: wordpress**\
**DB_PASSWORD: nvtlrqKd0E1jbXu**

**Tipo de vulnerabilidad**: Alta\
**Impacto técnico**: Un atacante puede utilizar estas credenciales para:

- Conectarse directamente a la base de datos MySQL/MariaDB si el
  servicio está expuesto. **Añadido: mysql -h 192.168.0.23 -u wordpress
  -p\'nvtlrqKd0E1jbXu\'.**

- Extraer información de usuarios, posts, configuraciones internas, etc.

- Facilitar un ataque de fuerza bruta al panel de WordPress si el
  usuario WordPress existe también en el CMS.

<img width="1186" height="569" alt="image" src="https://github.com/user-attachments/assets/c1d81b46-4cca-4530-a181-c54ab9be1586" />



**Validación de Credenciales y Descubrimiento de phpMyAdmin**

Las credenciales obtenidas en wp-config.php no fueron útiles para el
acceso directo al login principal de WordPress.

Por lo que se asumió que podían corresponder al backend de base de
datos. Tras no obtener resultados relevantes con el fuzzing se realizó
una comprobación manual de rutas habituales de administración.
Finalmente, se localizó el panel de phpMyAdmin
en http://192.168.0.23/phpmyadmin/, confirmando la presencia de una base
de datos MySQL/MariaDB expuesta en el entorno.

**Tipo de vulnerabilidad**: Alta\
**Impacto técnico**: Un atacante puede acceder a la administración de la
base de datos, validar/reutilizar credenciales u obtener información
sensible del sistema. **Añadido: phpMyAdmin versión 4.8.1 vulnerable a
SQLi (CVE-2018-19968).**

**Recomendaciones**:

- Restringir phpMyAdmin a redes internas o VPN.

- Evitar su exposición pública.

- Mantenerlo actualizado y protegido con control de acceso adicional.

**Resultado**: El sistema permitió el acceso al panel de administración
de phpMyAdmin confirmando que el usuario wordpress es un usuario válido
con privilegios administrativos.

Una vez identificado el servicio de phpMyAdmin, se confirmó la
existencia de una interfaz de administración de la base de datos
expuesta. Este acceso amplía la superficie de ataque ya que un atacante
autenticado podrá gestionar la información sensible, modificar tablas y,
en determinados escenarios con configuraciones inseguras, intentar una
escalada hacia la ejecución remota de código.

**Tipo de vulnerabilidad**: Alta\
**Impacto técnico**: Acceso no autorizado a la administración de la base
de datos, posible extracción o modificación de información sensible,
riesgo de abuso avanzado si existen configuraciones débiles o versiones
vulnerables.

**Recomendaciones**:

- Restringir phpMyAdmin a redes internas o VPN.

- Mantenerlo actualizado.

- Revisar permisos de base de datos y deshabilitar funciones no
  necesarias.

- Proteger el acceso con autenticación adicional y listas de control de
  acceso.

<img width="886" height="441" alt="image" src="https://github.com/user-attachments/assets/202c472b-5d08-4e34-904a-54583a18dc9b" />

<img width="886" height="441" alt="image" src="https://github.com/user-attachments/assets/1723773b-4130-428a-9f8b-b0b6c7c11ca2" />


**EXPLOTACIÓN DE LA WEB**

Tras fallar en el login \"cebo\" y localizar phpMyAdmin, se dirigió la
atención al panel WordPress principal para realizar un análisis más
profundo. Se ejecutó Nuclei sobre la página principal
(http://192.168.0.23), obteniendo resultados críticos:

**Exposición de información de usuario a través de un endpoint
vulnerable revelando:**

- Usuarios: webmaster

- Hash de contraseña: \$P\$Bsq0diLTcye6AS1ofreys4GzRlRvSr1 (formato
  phpPass). **Añadido: Crack con Hashcat → kittykat1 confirmado.**

**Tipo de vulnerabilidad**: Alta\
**Impacto técnico**: Obtención directa de credenciales válidas del
sistema de autenticación WordPress facilitando ataques posteriores.

<img width="886" height="487" alt="image" src="https://github.com/user-attachments/assets/39aaf920-ac59-4600-9cbe-42e47c3d6cdf" />

<img width="886" height="440" alt="image" src="https://github.com/user-attachments/assets/3c36826d-fdcb-4c47-b33e-bcaf60ef8bc4" />




**Acceso Exitoso al Panel de WordPress**

Con las credenciales obtenidas del escaneo Nuclei (webmaster + hash
descifrado) se procedió a validar el acceso al panel de administración
de WordPress en la URL principal:

**Credenciales utilizadas:**

- Usuario: webmaster

- Contraseña: kittykat1

**Resultado**: Acceso exitoso al dashboard de WordPress
confirmando http://192.168.0.23/wp-login/.

**Impacto técnico**: Control total del CMS, permitiendo instalación de
plugins maliciosos, subida de archivos PHP y modificación del contenido
del sitio.

<img width="886" height="441" alt="image" src="https://github.com/user-attachments/assets/0eb8e392-22cc-4b10-8d12-a9ea87e4042c" />


![](media/image9.png){width="5.905555555555556in"
height="3.3222222222222224in"}

<img width="886" height="498" alt="image" src="https://github.com/user-attachments/assets/8ed6cad8-bec9-4cf9-ba2d-3f7ce9483d5b" />


Tras confirmar acceso administrativo (webmaster: kittykat1) se
identificó que el entorno era vulnerable al
módulo exploit/unix/webapp/wp_admin_shell_upload debido a la
configuración permisiva del directorio /wp-content/plugins/. Se optó por
este exploit automatizado por su alta fiabilidad en este tipo de
despliegues en WordPress.

**Resultado**:\
**Autenticación:**

- Payload PHP subido a /wp-content/plugins/DcFNQmzkwv/htspqyvSRY.php

- Meterpreter session 1 activa (192.168.0.25:4444 -\>
  192.168.0.23:56504)

- Shell estabilizada (id, pwd, whoami → www-data)

**Tipo**: Crítica\
**Impacto**: Shell interactiva con privilegios del servidor
web. **Añadido: LinPEAS ejecutado → No SUIDs obvios, pero sudo checks
pendientes.**

**Recomendaciones**:

- Deshabilitar la subida de archivos en WordPress.

- Quitar permisos de escritura /wp-content/uploads/ (chmod 755).

- WAF anti-RCE (ModSecurity).

- Monitorear plugins/uploads.

<img width="1188" height="556" alt="image" src="https://github.com/user-attachments/assets/30eb1e4b-e7e6-4f5a-897b-7a92a444dce3" />


<img width="1193" height="528" alt="image" src="https://github.com/user-attachments/assets/ec4a572e-0548-4780-ad59-096475a6dac2" />



**Post-Explotación Inicial y Enumeración de Privilegios**

Con la sesión Meterpreter activa (www-data) se estabilizó la shell y se
enumeró el sistema. **Añadido: python3 -c \'import pty;
pty.spawn(\"/bin/bash\")\' para shell TTY.**

**Análisis**:

- Usuario www-data (privilegios limitados del servidor web).

- Sin permisos sudo configurados para escalada
  inmediata. **Comando: sudo -l → No results.**

**Tipo**: Media\
**Recomendaciones**:

- Configurar políticas de mínimo privilegio para www-data.

- Restringir shell interactiva en el contexto del usuario web.

- Implementar contenedores o chroot para aislar procesos web.

**4. Enumeración de Usuarios del Sistema**

Con la shell estabilizada (www-data), se enumeraron los usuarios del
sistema: **Añadido: cat /etc/passwd \| cut -d: -f1.**

**Análisis**:

- Usuarios con shell: root, xinstructor, webmaster.

- Usuario actual confirmado: www-data (UID 33).

- Posibles vectores: Cuentas xinstructor y webmaster con shells bash
  válidas.

**Recomendaciones**:

- Deshabilitar shells en cuentas de servicio no necesarias (MSSQL, FTP,
  etc.).

- Cambiar homes de cuentas sensibles fuera de rutas accesibles.

- Implementar política de contraseñas para cuentas no-root.

- Restringir enumeración de /etc/passwd mediante configuraciones
  AppArmor/SELinux.

- Monitorear acceso a archivos de sistema desde contexto web.

<img width="686" height="563" alt="image" src="https://github.com/user-attachments/assets/73f54f72-531b-4c9f-98a2-2779e746c95a" />



**5. Escalada de Privilegios: www-data a Webmaster**

Aprovechando las credenciales webmaster:kittykat1 obtenidas previamente
se realizó escalada manual desde www-data: **Añadido: su webmaster →
Pass: kittykat1.**

**Resultado**:

- Escalada exitosa a usuario webmaster.

- Confirmación de privilegios elevados vs www-data.

**Tipo de vulnerabilidad**: Alta\
**Impacto**: Escalada desde usuario web (www-data) a cuenta de sistema
con mayores privilegios (webmaster).

**Recomendaciones**:

- No reutilizar credenciales entre servicios web y cuentas de sistema.

- Restringir el comando su solo a usuarios administradores confiables.

- Implementar sudoers restrictivo para cuenta de webmaster.

**6. Escalada Final a Root mediante Sudo**

Desde el usuario webmaster se enumeraron los privilegios sudo: **sudo
-l**.

**Resultado crítico**:\
Permisos sudo completos (ALL) ALL para el usuario
webmaster. **Exploit: sudo -u root /bin/bash.**

**Recomendaciones**:

- Eliminar permisos sudo de cuentas no administrativas (webmaster).

- Nunca otorgar al usuario (ALL) ALL.

- Habilitar autenticación sudo con contraseñas únicas no reutilizadas.

- Implementar sudo con timeout y logs detallados (/var/log/auth.log).


<img width="717" height="585" alt="image" src="https://github.com/user-attachments/assets/e8dfa7f4-2815-46c8-894b-e0cadf411744" />

**Resumen de Vulnerabilidades**

  -------------------------------------------------------------------------
  **Vulnerabilidad**             **Severidad**   **Mitigación Inmediata**
  ------------------------------ --------------- --------------------------
  FTP anónimo                    Alta            Deshabilitar

  wp-config expuesto             Crítica         Mover fuera raíz web

  WordPress admin débil          Crítica         2FA + IP whitelist

  Sudo (ALL) ALL                 CRÍTICA         Eliminar YA

  Permisos directorios web       Alta            755/644 estrictos
  -------------------------------------------------------------------------

**Valoración del Auditor**

La infraestructura presenta fallos de configuración básica que permiten
a cualquier atacante externo comprometer el sistema completo en pocos
pasos. **Cadena completa: Recon → FTP Anon → wp-config → phpMyAdmin →
Nuclei Users → WP Admin → RCE → Sudo Root.**

**Recomendaciones Prioritarias (Orden de Urgencia)**\
**Crítico (24h):**

- Eliminar sudo all de webmaster.

- Deshabilitar FTP anónimo.

- Mover wp-config fuera de la raíz web.

**Alto (1 semana):**

- Actualizar WordPress + plugins.

- Implementar WAF + rate limiting.

- 2FA en paneles administrativos.

**Medio (1 mes):**

- Auditoría completa de permisos.

- Segmentación de red.

- Monitorización SIEM.

**\[ESPACIO PARA CAPTURA: Timeline cadena de ataque\]**

**Bibliografía**

- Nmap documentation: [https://nmap.org](https://nmap.org/)

- WPScan vulnerability database.

- Metasploit
  framework: [https://metasploit.com](https://metasploit.com/)

- Nuclei templates: WordPress configuration.

- Linux privilege escalation guides.
