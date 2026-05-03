**Informe de Auditoría de Seguridad**

**Objetivo:** Sistema identificado como *Alpine*

# Verificación de Conectividad de Red 

Se inició la auditoría con una comprobación de la disponibilidad de la
máquina objetivo en la red.

**Comando ejecutado:** ping 192.168.0.32

<img width="501" height="495" alt="image" src="https://github.com/user-attachments/assets/f52cbd96-6fb8-49c5-8650-e6d030ea4d17" />


**Observaciones:**

- El host respondió exitosamente a las solicitudes ICMP.

- El TTL = 64 y tiempos de respuesta bajos confirman que el sistema está
  activo.

- Se revisó la conectividad a otros hosts internos, pero **no se
  encontraron anomalías**.

**Recomendaciones:**

- Restringir respuestas ICMP a redes internas confiables.

- Monitorizar solicitudes ICMP sospechosas.

# Escaneo de Puertos 

Se realizó un escaneo activo con Nmap para identificar servicios
expuestos y posibles vectores de entrada. **Comando ejecutado:** nmap
-sS \--open -sC -sV -n -Pn 192.168.0.32 **Resultados principales:**

**Puerto Servicio Versión**

22/tcp SSH OpenSSH 10.2 80/tcp HTTP Apache 2.4.66

<img width="679" height="352" alt="image" src="https://github.com/user-attachments/assets/8f553685-7ffe-4a39-8b4c-7b159018b977" />


**Observaciones:**

- Se revisaron todos los puertos y servicios conocidos, pero **no se
  detectaron servicios adicionales ni vulnerabilidades evidentes**.

**Recomendaciones:**

- Limitar los puertos abiertos.

- Configurar firewall y auditar periódicamente.

# Identificación de Tecnologías Web 

Se utilizó **WhatWeb** para identificar tecnologías del servidor y
orientar la auditoría.

**Comando ejecutado:** whatweb http://alpine.
<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/ec9550ed-f5af-4df4-bf19-4acfeabb2b31" />


> **Observaciones:**

- Servidor web: Apache 2.4.66 (Unix).

- Tecnologías detectadas: HTML5, scripts y correos internos.

- Se revisaron posibles APIs y endpoints,
  pero **no se encontró información sensible ni recursos ocultos**.
  
  <img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/5cef9d1d-a317-4d17-9b96-8dfc0f6d9766" />



**Recomendaciones:**

- Mantener actualizado el stack tecnológico.

- Ocultar información sensible en headers y scripts.

# Enumeración de Recursos -- Fuzzing 

Se realizó **fuzzing de directorios y archivos web** para descubrir
rutas ocultas y paneles administrativos.

**Comandos ejecutados:**

ffuf -u http://alpine.nyx/FUZZ -w
/usr/share/seclists/Discovery/WebContent/raft-small-directories.txt -c

<img width="854" height="844" alt="image" src="https://github.com/user-attachments/assets/ac8d20e8-bec7-4d04-b1b1-a89c265dc822" />


ffuf -u http://alpine.nyx/FUZZ -w
/usr/share/seclists/Discovery/WebContent/small-words.txt -c

<img width="660" height="588" alt="image" src="https://github.com/user-attachments/assets/74b27344-0b31-407c-b082-2230c8c848c1" />




**Observaciones:** • Se encontraron directorios: /password, /modules,
/includes, /cache. • /server-status protegido (403).

- Revisado ~/profile.html~ y dashboard interno, **con información
  sensible adicional**.

**Recomendaciones:**

- Restringir acceso a directorios sensibles.

- Deshabilitar listado de directorios.

- Monitorizar intentos de enumeración.

# Acceso SSH Inicial 

Se obtuvieron credenciales de acceso filtradas:

<img width="679" height="409" alt="image" src="https://github.com/user-attachments/assets/d863be72-4b7b-4535-b12b-fc8f04b58891" />


Usuario: developer

Host: alpine.nyx

Password: SummerVibes2024!

**Comando ejecutado:** ssh developer@alpine.nyx

<img width="679" height="421" alt="image" src="https://github.com/user-attachments/assets/e92b4d1d-04f4-43e7-adb5-c84cf854264c" />


**Observaciones:**

- Acceso confirmado a ~developer~.

- Se revisaron archivos del home (~user.txt~, ~.ssh~) y **no se encontró
  contenido sensible adicional**.

  <img width="679" height="396" alt="image" src="https://github.com/user-attachments/assets/fe58fd3e-5ac5-465d-a30b-50f8d831ab76" />


**Recomendaciones:**

- Cambiar credenciales predeterminadas.

- Revisar accesos remotos periódicamente.

# Revisión de Procesos y Permisos 

Se revisaron procesos activos y permisos de usuarios para evaluar
posibles vectores de escalamiento. **Comandos ejecutados:**

ps aux sudo -l

ls -la /home/developer /home/sysadmin

<img width="679" height="409" alt="image" src="https://github.com/user-attachments/assets/c1775c84-b943-4a74-8f9c-3d5ab53a9cb1" />


**Observaciones:**

- Identificación de procesos y usuarios activos (~developer~,
  ~sysadmin~, ~apache~, root).

- Permisos de archivos críticos revisados, **sin configuraciones
  inseguras adicionales**.

- ~sudo\ -l~ descartado por contraseña no disponible.

**Recomendaciones:**

<img width="1061" height="648" alt="image" src="https://github.com/user-attachments/assets/3febf4b2-fc42-4cd3-bb85-ba1eb65518db" />

- Monitorizar procesos y sesiones SSH
  activas.

# Recuperación de Clave SSH vía Git 

Se identificó que el repositorio Git contenía **commits con backups de
claves SSH**.

**Comandos ejecutados:**

git log \--all \--pretty=oneline git show 02f9a18:id_rsa \>
\~/id_rsa_sysadmin chmod 600 \~/id_rsa_sysadmin

ssh -i \~/id_rsa_sysadmin sysadmin@localhost



**Observaciones:**

- Git permitió recuperar archivos borrados de commits anteriores.

- Probado acceso como ~sysadmin~, **sin encontrar información sensible
  adicional**.
  
<img width="679" height="481" alt="image" src="https://github.com/user-attachments/assets/99ca40c2-2972-4d1e-b574-a13a639b2f37" />


**Recomendaciones:**

- No almacenar claves privadas en repositorios.

- Auditar commits y eliminar información
  sensible.

# Acceso a Información Sensible y Escalamiento 

Una vez dentro como sysadmin, se descubrió un script de limpieza
automatizado en /opt/scripts/cleanup.sh, que se ejecutaba
periódicamente a través de cron.

Este script contenía una línea de
código que leía archivos del directorio /root y los escribía en una
ubicación temporal. 

Aunque el script en sí no era directamente
modicable por sysadmin, su comportamiento era predecible.
- ~cleanup.sh~ contiene instrucciones para consolidar archivos de root.

- <img width="679" height="538" alt="image" src="https://github.com/user-attachments/assets/0795e7b3-7540-48d2-9588-57b2ca5bdb7d" />


**Recomendaciones:**

- Restringir ejecución de scripts sensibles.

- Revisar logs y permisos de scripts automatizados.
