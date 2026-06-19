## INFORME TÉCNICO DE EXPLOTACIÓN -- MÁQUINA DE POLICY

------------------------------------------------------------------------

### 1️⃣ Verificación de conectividad

Se inició la evaluación comprobando la disponibilidad del host objetivo
mediante prueba ICMP:

    ping 192.168.0.23

![](media/image1.png){width="10.541666666666666in"
height="4.299023403324584in"}

**Observaciones:**

- 6 paquetes transmitidos y recibidos, 0% de pérdida.
- Latencias consistentes.
- Host activo y accesible, listo para fase de enumeración.

------------------------------------------------------------------------

### 2️⃣ Enumeración de servicios expuestos

Escaneo de puertos con detección de versiones y scripts básicos:

    nmap -sS --open -sC -sV -n -Pn 192.168.0.23

![](media/image2.png){width="9.486910542432195in" height="4.71875in"}

**Servicios relevantes identificados:**

  -----------------------------------------------------
  Puerto     Servicio       Versión
  ---------- -------------- ---------------------------
  80/tcp     HTTP           Microsoft IIS 10.0

  135/tcp    MSRPC          Windows RPC

  139/tcp    NetBIOS-SSN    Windows File Sharing

  445/tcp    Microsoft-DS   Windows File Sharing

  5985/tcp   HTTP           Microsoft HTTPAPI 2.0
                            (WinRM)
  -----------------------------------------------------

**Interpretación profesional:**

- El puerto 80 suele ser un punto de inicio en entornos de laboratorio;
  muchas veces se exponen credenciales o configuraciones a través de la
  web.
- Puertos SMB y WinRM permiten enumeración remota y posible escalada si
  existen credenciales válidas.

------------------------------------------------------------------------

### 3️⃣ Análisis del servicio web

Se revisó manualmente la aplicación web usando navegador y herramientas
de desarrollo (F12) para detectar:

- Comentarios HTML
- Posibles endpoints ocultos
- APIs expuestas

![](media/image3.png){width="7.392633420822397in"
height="3.6770647419072615in"}

**Resultado:** No se identificó información sensible.

Decisión técnica: continuar con enumeración automatizada de directorios
(`fuzzing`) para buscar recursos no visibles.

------------------------------------------------------------------------

### 4️⃣ Fuzzing de directorios web

Se realizó enumeración forzada usando `ffuf`:

    ffuf -u http://192.168.0.23/FUZZ -w /usr/share/wordlists/dirb/common.txt -e .zip,.bak,.old,.tar,.gz,.sql -fs 703

![](media/image4.png){width="5.073443788276466in"
height="3.2395833333333335in"}![](media/image5.png){width="5.042361111111111in"
height="3.3848939195100614in"}

![](media/image6.png){width="5.117994313210849in"
height="3.026388888888889in"}![](media/image7.png){width="5.158605643044619in"
height="3.144767060367454in"}

**Justificación profesional:**

- **Extensiones (**`-e`**)**: archivos comprimidos o backups pueden
  contener información sensible.
- **Filtro de tamaño (**`-fs`**)**: el servidor web devolvía respuestas
  repetitivas de 703 bytes; filtrar permitió enfocar la búsqueda en
  archivos de interés y eliminar falsos positivos.

**Resultado del fuzzing:**

- Detectado `groups.zip` como archivo accesible.

![](media/image8.png){width="5.760416666666667in"
height="3.3463265529308837in"}

------------------------------------------------------------------------

### 5️⃣ Descarga y análisis de `groups.zip`

Se descargó el archivo y se confirmó que estaba protegido:

![](media/image9.png){width="5.770833333333333in"
height="3.1465277777777776in"}

Para obtener la contraseña:

1.  Generación de hash con `zip2john`.
2.  Crackeo con `John the Ripper` y wordlists (`rockyou.txt`).

![](media/image10.png){width="5.806517935258093in"
height="4.186805555555556in"}

![](media/image11.png){width="5.572916666666667in"
height="4.21722331583552in"}

**REsultado:** contraseña recuperada y archivo `.tar` extraído.

Dentro se encontró un archivo XML con:

    <User clsid="" name="policy.nyx\XEROSEC">
    <Properties action="U" newName="" fullName="" description="" cpassword="IwLNLy0Ck5xIlXEsPMTbOF1f/NnliQFKeGv139eUEgE"/>
    </User>

------------------------------------------------------------------------

### 6️⃣ Desencriptado del cpassword

Se utilizó `gpp-decrypt` para descifrar la contraseña de GPP:

    gpp-decrypt IwLNLy0Ck5xIlXEsPMTbOF1f/NnliQFKeGv139eUEgE

![](media/image12.png){width="5.395833333333333in"
height="2.356788057742782in"}

**Resultado:**

- Usuario: **XEROSEC**
- Contraseña: **GPP2k26blahblah**

------------------------------------------------------------------------

### 7️⃣ Validación con Enum4Linux

Antes de acceder con WinRM, se validó información en SMB con
credenciales:

    enum4linux -u XEROSEC -p 'GPP2k26blahblah' 192.168.0.23

![](media/image13.png){width="6.197916666666667in"
height="4.072222222222222in"} ![](media/image14.png){width="7.44375in"
height="3.6247714348206475in"}

**Resultado profesional:**

- Confirmación de que el objetivo es un **ordenador suelto**, no un
  Active Directory.
- Información de workgroup y usuarios accesibles.
- No se detectaron recursos compartidos críticos ni configuraciones de
  dominio que pudieran facilitar escalada adicional.

------------------------------------------------------------------------

### 8️⃣ Validación y enumeración avanzada en SMB

Se verificó autenticación con `netexec` sobre la red local 0/24:

    netexec smb 192.168.0.0/24 -u XEROSEC -p 'GPP2k26blahblah'

![](media/image15.png){width="7.820529308836395in"
height="5.688888888888889in"}

**Interpretación profesional:**

- Solo un host respondió con credenciales válidas.
- Recursos compartidos: ADMIN$,C$, IPC\$, pero sin archivos útiles para
  escalada.
- Confirmación final de que era **un único equipo independiente**.

**Pruebas manuales:** `net user`, listado de usuarios y grupos no
arrojaron información adicional relevante.

![](media/image16.png){width="6.84375in" height="5.207163167104112in"}

------------------------------------------------------------------------

### 9️⃣ Acceso remoto mediante WinRM

Dada la apertura de puerto 5985 y credenciales válidas, se estableció
sesión con `evil-winrm`:

    evil-winrm -i 192.168.0.23 -u XEROSEC -p 'GPP2k26blahblah'

![](media/image17.png){width="11.581112204724409in"
height="5.760396981627297in"}

Verificación de contexto:

    whoami
    whoami /groups

Usuario sin privilegios administrativos completos.

------------------------------------------------------------------------

### 🔟 Enumeración automatizada con WinPEAS

Se cargó y ejecutó WinPEAS para análisis profundo:

    upload winPEASx64.exe
    ./winPEASx64.exe

![](media/image19.png){width="11.791666666666666in"
height="5.865125765529309in"}

**Resultado relevante:** variable de entorno con contraseña expuesta

    GigaAdmin123!

![](media/image20.png){width="11.895833333333334in"
height="5.284722222222222in"}

------------------------------------------------------------------------

### 1️⃣1️⃣ Escalada de privilegios y acceso completo

Se utilizó la contraseña expuesta para autenticarse como
**Administrator**:

![](media/image21.png){width="11.71875in" height="5.828857174103237in"}

Verificación de privilegios:

    whoami /priv

**Conclusión:** control total del sistema alcanzado.

------------------------------------------------------------------------

# Conclusión técnica

**Factores críticos que permitieron la intrusión:**

- Exposición de archivos sensibles vía web (`groups.zip` con GPP).
- Contraseñas almacenadas de forma insegura.
- Reutilización de credenciales.
- Servicio WinRM abierto y accesible con credenciales válidas.
- Variables de entorno con información crítica.

**Aprendizajes y buenas prácticas:**

- Revisar siempre exposición web y posibles archivos comprimidos.
- Validar la seguridad de GPP y evitar cpasswords expuestos.
- Enumeración manual previa a automatización ayuda a comprender contexto
  y reducir ruido.
- Documentar cada paso con evidencia facilita reportes profesionales.
