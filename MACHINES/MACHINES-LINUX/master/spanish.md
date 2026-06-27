# Informe técnico de auditoría Linux

---

# Descripción de red

**IP del servidor vulnerable:** 192.168.0.23

- **Sistema operativo:** Linux (Debian, inferido por Apache 2.4.25 y la compilación típica de OpenSSH en Debian). `cat /etc/os-release` confirmó Debian 9 Stretch.
- **Servicios expuestos:** FTP, SSH, HTTP (WordPress).
- **Topología:** Red plana `192.168.0.0/24`; el atacante está en la misma subred (por ejemplo, Kali `192.168.0.25`).
- **Nota adicional:** No existía firewall (`iptables -L` devolvió vacío).

---

# 1. Escaneo de servicios y reconocimiento

## Escaneo básico

```bash
nmap 192.168.0.23
```

**Resultado:**  
**Host 192.168.0.23**

- Puertos abiertos:
- `21/tcp` = FTP
- `22/tcp` = SSH
- `80/tcp` = HTTP

## Escaneo avanzado con fingerprinting y versiones

```bash
nmap -sS --open -sC -sV -n -Pn 192.168.0.23
```

**Resultado detallado:**

- **Puerto 21/tcp = FTP**
  - Servicio: vsftpd 3.0.3
  - Información adicional: se permite login FTP anónimo.
  - Se observan varios archivos y directorios típicos de WordPress:
    - `index.php`, `license.txt`, `readme.html`
    - `wp-activate.php`, `wp-admin/`, `wp-content/`, `wp-includes/`
    - `wp-config.php`, `wp-login.php`, `xmlrpc.php`

<img width="580" height="551" alt="image" src="https://github.com/user-attachments/assets/b450a788-562b-4f6f-8ec6-6072b403844c" />

---

# Vulnerabilidad 1 — FTP anónimo

**Nombre de la vulnerabilidad:** Acceso FTP anónimo no autorizado  
**Servicio:** FTP (`vsftpd 3.0.3` en el puerto 21)  
**Severidad:** ALTA

**Descripción técnica:**  
El servidor FTP permite acceso anónimo sin credenciales, lo que permite al atacante:

- Listar archivos y directorios (`ls`).
- Descargar archivos sensibles (`get`).
- Reconstruir la estructura de WordPress y obtener acceso a archivos de configuración.

**Comando añadido:** `ftp 192.168.0.23 -> anonymous:anonymous@ -> get wp-config.php`

**Impacto:**

- Exposición de información sensible (credenciales, rutas, archivos de WordPress).
- Facilitación de ataques posteriores (brute force, RCE, etc.).

**Recomendaciones:**

- Deshabilitar el acceso anónimo en el servidor FTP o restringirlo a usuarios específicos (`/etc/vsftpd.conf: anonymous_enable=NO`).
- Restringir el acceso FTP únicamente a redes internas de confianza (`iptables -A INPUT -p tcp --dport 21 -s 192.168.0.0/24 -j ACCEPT`).
- Monitorizar y registrar el acceso FTP para detectar actividad anómala (`/var/log/vsftpd.log`).

<img width="1167" height="494" alt="image" src="https://github.com/user-attachments/assets/f0d93b00-6895-46d0-a324-8d797aac304d" />

---

# Vulnerabilidad 2 — Exposición de información en WordPress

**Nombre de la vulnerabilidad:** Exposición de información de configuración y estructura de WordPress  
**Servicio:** HTTP (WordPress 5.2.3 en el puerto 80)  
**Severidad:** MEDIA-ALTA (por el potencial de exposición de credenciales)

**Descripción técnica:**

- El servidor web muestra un título y contenido genérico ("MASTER D TEST -- Test machine for MASTER D").
- El escaneo Nmap revela que WordPress 5.2.3 está expuesto y accesible.
- `WhatWeb` confirma Apache 2.4.25 y PHP 7.0.
- El acceso FTP anónimo permite descargar archivos como `wp-config.php` y `license.txt`, exponiendo información de configuración y versiones.

**Impacto:**  
Un atacante puede:

- Reconstruir la estructura de WordPress.
- Usar archivos de configuración para obtener credenciales de base de datos.
- Explotar versiones antiguas de WordPress/PHP en busca de vulnerabilidades conocidas (por ejemplo, CVE-2019-17671 en WP 5.2.3).

**Recomendaciones:**

- Ocultar `wp-config.php` y otros archivos de configuración del acceso público (`.htaccess: <Files wp-config.php> deny from all </Files>`).
- Actualizar WordPress y los plugins a versiones recientes y parcheadas.
- Ocultar cabeceras del servidor (`Apache/2.4.25`, `WordPress 5.2.3`) para dificultar la reconstrucción de versiones (`ServerTokens Prod`).

---

# 2. Evidencia, acceso FTP anónimo y lectura de `wp-config.php`

Tras el escaneo Nmap y la identificación de FTP anónimo, se accedió al servidor usando:

**`ftp 192.168.0.23 -> Usuario: anonymous -> Pass: anonymous`**

Dentro del archivo `wp-config.php` descargado se encontró la siguiente información sensible:

- **DB_USER:** `wordpress`
- **DB_PASSWORD:** `nvtlrqKd0E1jbXu`

**Tipo de vulnerabilidad:** Alta  
**Impacto técnico:** Un atacante puede usar estas credenciales para:

- Conectarse directamente a MySQL/MariaDB si el servicio está expuesto.
  **Añadido:** `mysql -h 192.168.0.23 -u wordpress -p'nvtlrqKd0E1jbXu'`
- Extraer información de usuarios, entradas, configuraciones internas, etc.
- Facilitar un ataque por fuerza bruta al panel de WordPress si el usuario de WordPress también existe en el CMS.

<img width="1186" height="569" alt="image" src="https://github.com/user-attachments/assets/c1d81b46-4cca-4530-a181-c54ab9be1586" />

---

# Validación de credenciales y descubrimiento de phpMyAdmin

Las credenciales obtenidas de `wp-config.php` no fueron útiles para acceder directamente al login principal de WordPress.

Por tanto, se asumió que correspondían al backend de base de datos. Tras no obtener resultados relevantes con fuzzing, se realizó una comprobación manual de rutas administrativas comunes. Finalmente, se localizó el panel de phpMyAdmin en `http://192.168.0.23/phpmyadmin/`, confirmando la presencia de una interfaz de administración MySQL/MariaDB expuesta.

**Tipo de vulnerabilidad:** Alta  
**Impacto técnico:** Un atacante puede acceder a la administración de la base de datos, validar o reutilizar credenciales y obtener información sensible del sistema.
**Añadido:** phpMyAdmin versión 4.8.1 vulnerable a SQLi (CVE-2018-19968).

**Recomendaciones:**

- Restringir phpMyAdmin a redes internas o VPN.
- Evitar su exposición pública.
- Mantenerlo actualizado y protegido con control de acceso adicional.

**Resultado:**  
El sistema permitió el acceso al panel de administración phpMyAdmin, confirmando que el usuario `wordpress` es válido y dispone de privilegios administrativos.

Una vez identificado phpMyAdmin, se confirmó la existencia de una interfaz de administración de bases de datos expuesta. Esto aumenta la superficie de ataque porque un atacante autenticado puede gestionar datos sensibles, modificar tablas y, en configuraciones inseguras, intentar una escalada hacia ejecución remota de código.

**Tipo de vulnerabilidad:** Alta  
**Impacto técnico:** Acceso no autorizado a la administración de la base de datos, posible extracción o modificación de información sensible, y riesgo de abuso avanzado si existen configuraciones débiles o versiones vulnerables.

**Recomendaciones:**

- Restringir phpMyAdmin a redes internas o VPN.
- Mantenerlo actualizado.
- Revisar los permisos de la base de datos y deshabilitar funciones innecesarias.
- Proteger el acceso con autenticación adicional y listas de control de acceso.

<img width="886" height="441" alt="image" src="https://github.com/user-attachments/assets/202c472b-5d08-4e34-904a-54583a18dc9b" />

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/d5a24153-ad68-45cc-b649-c1e5668e6770" />

---

# Explotación web

Tras fallar el login señuelo y localizar phpMyAdmin, la atención se centró en el panel principal de WordPress para un análisis más profundo. Se ejecutó Nuclei contra la página principal (`http://192.168.0.23`), obteniendo resultados críticos:

**Exposición de información de usuario a través de un endpoint vulnerable que reveló:**

- **Usuarios:** `webmaster`
- **Hash de contraseña:** `$P$Bsq0diLTcye6AS1ofreys4GzRlRvSr1` (formato phpPass)
- **Añadido:** Hashcat confirmó el crack con `kittykat1`.

**Tipo de vulnerabilidad:** Alta  
**Impacto técnico:** Obtención directa de credenciales válidas para WordPress, permitiendo ataques posteriores.

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/cf3e320b-3356-4cf7-8714-f0d4f62f15d5" />

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/9aa2e51b-e316-4550-9c51-60d574b99aad" />

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/41ed49f0-31d0-4fc7-8861-752c8409e110" />

---

# Acceso exitoso al panel de WordPress

Con las credenciales obtenidas mediante Nuclei (`webmaster + hash crackeado`), se validó el acceso al panel de administración de WordPress en la URL principal:

**Credenciales utilizadas:**

- Usuario: `webmaster`
- Contraseña: `kittykat1`

**Resultado:** Acceso exitoso al panel de WordPress, confirmando `http://192.168.0.23/wp-login/`.

**Impacto técnico:** Control total del CMS, permitiendo instalación de plugins maliciosos, subida de archivos PHP y modificación de contenido del sitio.

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/d4e5148f-44b4-4aef-8204-6912a2f4713f" />

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/67782633-f294-428f-ad11-f46ab51f9381" />

Tras confirmar el acceso administrativo (`webmaster: kittykat1`), el entorno se identificó como vulnerable al módulo `exploit/unix/webapp/wp_admin_shell_upload` debido a la configuración permisiva del directorio `/wp-content/plugins/`. Se eligió este exploit automático por su alta fiabilidad en este tipo de despliegues WordPress.

**Resultado:**

**Autenticación:**

- Carga útil PHP subida a `/wp-content/plugins/DcFNQmzkwv/htspqyvSRY.php`
- Sesión Meterpreter 1 activa (`192.168.0.25:4444 -> 192.168.0.23:56504`)
- Shell estabilizada (`id`, `pwd`, `whoami` -> `www-data`)

**Tipo:** Crítico  
**Impacto:** Shell interactiva con privilegios del servidor web.  
**Añadido:** LinPEAS ejecutado -> sin SUID obvios, pero pendientes comprobaciones con sudo.

**Recomendaciones:**

- Deshabilitar la subida de archivos en WordPress.
- Eliminar permisos de escritura de `/wp-content/uploads/` (`chmod 755`).
- Usar un WAF contra RCE (ModSecurity).
- Monitorizar plugins y cargas de archivos.

<img width="1188" height="556" alt="image" src="https://github.com/user-attachments/assets/30eb1e4b-e7e6-4f5a-897b-7a92a444dce3" />

<img width="1193" height="528" alt="image" src="https://github.com/user-attachments/assets/ec4a572e-0548-4780-ad59-096475a6dac2" />

---

# Post-explotación inicial y enumeración de privilegios

Con la sesión Meterpreter activa (`www-data`), se estabilizó la shell y se enumeró el sistema.
**Añadido:** `python3 -c 'import pty; pty.spawn("/bin/bash")'` para obtener una shell TTY.

**Análisis:**

- Usuario `www-data` (privilegios limitados del servidor web).
- Sin permisos de sudo configurados para escalada inmediata.
  **Comando:** `sudo -l` -> sin resultados.

**Tipo:** Medio

**Recomendaciones:**

- Aplicar políticas de mínimo privilegio para `www-data`.
- Restringir el acceso a shells interactivas desde el contexto del usuario web.
- Implementar contenedores o chroot para aislar procesos web.

---

# 4. Enumeración de usuarios del sistema

Con la shell estabilizada (`www-data`), se enumeraron los usuarios del sistema:
**Añadido:** `cat /etc/passwd | cut -d: -f1`.

**Análisis:**

- Usuarios con shell: `root`, `xinstructor`, `webmaster`.
- Usuario actual confirmado: `www-data` (UID 33).
- Posibles vectores: cuentas `xinstructor` y `webmaster` con shells Bash válidas.

**Recomendaciones:**

- Deshabilitar shells en cuentas de servicio innecesarias.
- Mover los directorios personales sensibles fuera de rutas accesibles.
- Imponer políticas de contraseñas para cuentas no root.
- Restringir la enumeración de `/etc/passwd` usando AppArmor/SELinux.
- Monitorizar el acceso a archivos del sistema desde el contexto web.

<img width="686" height="563" alt="image" src="https://github.com/user-attachments/assets/73f54f72-531b-4c9f-98a2-2779e746c95a" />

---

# 5. Escalada de privilegios de `www-data` a `webmaster`

Usando las credenciales obtenidas previamente `webmaster:kittykat1`, se realizó una escalada manual desde `www-data`:
**Añadido:** `su webmaster` -> contraseña `kittykat1`.

**Resultado:**

- Escalada exitosa al usuario `webmaster`.
- Confirmación de privilegios superiores respecto a `www-data`.

**Tipo de vulnerabilidad:** Alta  
**Impacto:** Escalada desde el usuario web (`www-data`) a una cuenta del sistema con mayores privilegios (`webmaster`).

**Recomendaciones:**

- No reutilizar credenciales entre servicios web y cuentas del sistema.
- Restringir `su` únicamente a administradores de confianza.
- Aplicar una política sudoers restrictiva para la cuenta `webmaster`.

---

# 6. Escalada final a root mediante sudo

Desde el usuario `webmaster`, se enumeraron los privilegios de sudo con `sudo -l`.

**Resultado crítico:**  
La cuenta `webmaster` disponía de permisos sudo completos `(ALL) ALL`.
**Exploit:** `sudo -u root /bin/bash`

**Recomendaciones:**

- Eliminar privilegios sudo de cuentas no administrativas (`webmaster`).
- Nunca conceder `(ALL) ALL`.
- Habilitar autenticación sudo con contraseñas únicas y no reutilizadas.
- Implementar timeouts y registros detallados de sudo (`/var/log/auth.log`).

<img width="717" height="585" alt="image" src="https://github.com/user-attachments/assets/e8dfa7f4-2815-46c8-894b-e0cadf411744" />

---

# Resumen de vulnerabilidades

| Vulnerabilidad | Severidad | Mitigación inmediata |
|---|---|---|
| FTP anónimo | Alta | Deshabilitar |
| `wp-config` expuesto | Crítica | Mover fuera del web root |
| WordPress admin débil | Crítica | 2FA + whitelist IP |
| Sudo `(ALL) ALL` | CRÍTICA | Eliminar inmediatamente |
| Permisos de directorio web | Alta | `755/644` estrictos |

---

# Evaluación del auditor

La infraestructura presenta fallos básicos de configuración que permiten a cualquier atacante externo comprometer todo el sistema en pocos pasos.

**Cadena completa:** Recon → FTP anónimo → `wp-config` → phpMyAdmin → usuarios vía Nuclei → admin WordPress → RCE → Root por sudo.

---

# Recomendaciones prioritarias

## Críticas (24h)

- Eliminar `sudo ALL` de `webmaster`.
- Deshabilitar FTP anónimo.
- Mover `wp-config` fuera del web root.

## Altas (1 semana)

- Actualizar WordPress y plugins.
- Implementar WAF y limitación de tasa.
- Activar 2FA en paneles administrativos.

## Medias (1 mes)

- Realizar una auditoría completa de permisos.
- Implementar segmentación de red.
- Activar monitorización SIEM.

---

# Bibliografía

- Documentación de Nmap: [https://nmap.org](https://nmap.org/)
- Base de vulnerabilidades de WPScan.
- Metasploit framework: [https://metasploit.com/](https://metasploit.com/)
- Plantillas de Nuclei para WordPress.
- Guías de escalada de privilegios en Linux.
