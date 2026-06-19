## INFORME TÉCNICO DE EXPLOTACIÓN -- MÁQUINA DE POLICY

------------------------------------------------------------------------

### 1️⃣ Verificación de conectividad

Se inició la evaluación comprobando la disponibilidad del host objetivo
mediante prueba ICMP:

    ping 192.168.0.23

<img width="1012" height="413" alt="image" src="https://github.com/user-attachments/assets/6733248c-c649-4c31-88d7-690b8f20b38d" />


**Observaciones:**

- 6 paquetes transmitidos y recibidos, 0% de pérdida.
- Latencias consistentes.
- Host activo y accesible, listo para fase de enumeración.

------------------------------------------------------------------------

### 2️⃣ Enumeración de servicios expuestos

Escaneo de puertos con detección de versiones y scripts básicos:

    nmap -sS --open -sC -sV -n -Pn 192.168.0.23

<img width="911" height="453" alt="image" src="https://github.com/user-attachments/assets/e38fe08b-900d-45ce-8bcc-a5ca379a5154" />


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

<img width="710" height="353" alt="image" src="https://github.com/user-attachments/assets/2f65d2eb-7c0f-45ed-ab99-9ea4bf50f057" />


**Resultado:** No se identificó información sensible.

Decisión técnica: continuar con enumeración automatizada de directorios
(`fuzzing`) para buscar recursos no visibles.

------------------------------------------------------------------------

### 4️⃣ Fuzzing de directorios web

Se realizó enumeración forzada usando `ffuf`:

    ffuf -u http://192.168.0.23/FUZZ -w /usr/share/wordlists/dirb/common.txt -e .zip,.bak,.old,.tar,.gz,.sql -fs 703

<img width="487" height="311" alt="image" src="https://github.com/user-attachments/assets/3bd00782-ea8c-4050-816a-e34d754f063f" />


<img width="484" height="325" alt="image" src="https://github.com/user-attachments/assets/24ed82bc-3361-4227-9096-21e2f918d256" />


**Justificación profesional:**

- **Extensiones (**`-e`**)**: archivos comprimidos o backups pueden
  contener información sensible.
- **Filtro de tamaño (**`-fs`**)**: el servidor web devolvía respuestas
  repetitivas de 703 bytes; filtrar permitió enfocar la búsqueda en
  archivos de interés y eliminar falsos positivos.

**Resultado del fuzzing:**

- Detectado `groups.zip` como archivo accesible.



------------------------------------------------------------------------

### 5️⃣ Descarga y análisis de `groups.zip`

Se descargó el archivo y se confirmó que estaba protegido:

<img width="553" height="321" alt="image" src="https://github.com/user-attachments/assets/1f4d5934-5fb7-4087-9a8a-ed5a9c2ece12" />




Para obtener la contraseña:

1.  Generación de hash con `zip2john`.
2.  Crackeo con `John the Ripper` y wordlists (`rockyou.txt`).

<img width="554" height="302" alt="image" src="https://github.com/user-attachments/assets/c8b436b7-9e30-4dad-b918-295f6ba69dca" />


<img width="535" height="405" alt="image" src="https://github.com/user-attachments/assets/fb074c72-b973-433d-b4f5-e4a44a7f537e" />



**REsultado:** contraseña recuperada y archivo `.tar` extraído.

Dentro se encontró un archivo XML con:

    <User clsid="" name="policy.nyx\XEROSEC">
    <Properties action="U" newName="" fullName="" description="" cpassword="IwLNLy0Ck5xIlXEsPMTbOF1f/NnliQFKeGv139eUEgE"/>
    </User>

------------------------------------------------------------------------

### 6️⃣ Desencriptado del cpassword

Se utilizó `gpp-decrypt` para descifrar la contraseña de GPP:

    gpp-decrypt IwLNLy0Ck5xIlXEsPMTbOF1f/NnliQFKeGv139eUEgE

<img width="518" height="226" alt="image" src="https://github.com/user-attachments/assets/68d2a564-e2b2-4849-8dab-ed7cf6562ae9" />


**Resultado:**

- Usuario: **XEROSEC**
- Contraseña: **GPP2k26blahblah**

------------------------------------------------------------------------

### 7️⃣ Validación con Enum4Linux

Antes de acceder con WinRM, se validó información en SMB con
credenciales:

    enum4linux -u XEROSEC -p 'GPP2k26blahblah' 192.168.0.23

<img width="595" height="391" alt="image" src="https://github.com/user-attachments/assets/95d9bdae-e168-4c8c-8e78-da499972f916" />

<img width="715" height="348" alt="image" src="https://github.com/user-attachments/assets/b020bda8-2057-4169-9f32-2e0e05e956e1" />


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

<img width="751" height="546" alt="image" src="https://github.com/user-attachments/assets/946fc262-a5d9-4cac-8411-20943b8d99bf" />


**Interpretación profesional:**

- Solo un host respondió con credenciales válidas.
- Recursos compartidos: ADMIN$,C$, IPC\$, pero sin archivos útiles para
  escalada.
- Confirmación final de que era **un único equipo independiente**.

**Pruebas manuales:** `net user`, listado de usuarios y grupos no
arrojaron información adicional relevante.

<img width="657" height="500" alt="image" src="https://github.com/user-attachments/assets/f8922cc0-a019-4b15-8d74-108cd9ee9117" />


------------------------------------------------------------------------

### 9️⃣ Acceso remoto mediante WinRM

Dada la apertura de puerto 5985 y credenciales válidas, se estableció
sesión con `evil-winrm`:

    evil-winrm -i 192.168.0.23 -u XEROSEC -p 'GPP2k26blahblah'

<img width="1112" height="553" alt="image" src="https://github.com/user-attachments/assets/e6995045-40f1-4cb4-b9c8-5fb557f34b63" />


Verificación de contexto:

    whoami
    whoami /groups

 <img width="1105" height="550" alt="image" src="https://github.com/user-attachments/assets/9d25498e-6f04-4a08-8197-fa32cd09a1b2" />
  


Usuario sin privilegios administrativos completos.

------------------------------------------------------------------------

### 🔟 Enumeración automatizada con WinPEAS

Se cargó y ejecutó WinPEAS para análisis profundo:

    upload winPEASx64.exe
    ./winPEASx64.exe
    
<img width="1132" height="563" alt="image" src="https://github.com/user-attachments/assets/5f57a831-a7b9-427d-9e2d-28d3c7050151" />


**Resultado relevante:** variable de entorno con contraseña expuesta

    GigaAdmin123!

<img width="1142" height="507" alt="image" src="https://github.com/user-attachments/assets/3730b5a0-3abd-4c19-a478-0f68b1e4daf7" />


------------------------------------------------------------------------

### 1️⃣1️⃣ Escalada de privilegios y acceso completo

Se utilizó la contraseña expuesta para autenticarse como
**Administrator**:

<img width="1125" height="560" alt="image" src="https://github.com/user-attachments/assets/1c5009a1-ff29-4bea-b7c7-b8ed8a76f608" />

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
