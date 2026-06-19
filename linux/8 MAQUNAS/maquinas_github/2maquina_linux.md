**Informe de Auditoría de Seguridad**

**Objetivo:** Sistema identificado como *Alpine*

# Verificación de Conectividad de Red 

Se inició la auditoría con una comprobación de la disponibilidad de la
máquina objetivo en la red.

**Comando ejecutado:** ping 192.168.0.32

![](media/image1.jpg){width="5.221527777777778in"
height="5.1561111111111115in"}

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

> ![](media/image2.png){width="7.073333333333333in"
> height="3.67in"}22/tcp SSH OpenSSH 10.2 80/tcp HTTP Apache 2.4.66

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

> **Observaciones:**

- Servidor web: Apache 2.4.66 (Unix).

- Tecnologías detectadas: HTML5, scripts y correos internos.

- ![](media/image3.png){width="6.573333333333333in"
  height="4.586666666666667in"}Se revisaron posibles APIs y endpoints,
  pero **no se encontró información sensible ni recursos ocultos**.

> ![](media/image4.png){width="6.573333333333333in"
> height="4.680001093613298in"}

**Recomendaciones:**

- Mantener actualizado el stack tecnológico.

- Ocultar información sensible en headers y scripts.

# Enumeración de Recursos -- Fuzzing 

Se realizó **fuzzing de directorios y archivos web** para descubrir
rutas ocultas y paneles administrativos.

**Comandos ejecutados:**

ffuf -u http://alpine.nyx/FUZZ -w
/usr/share/seclists/Discovery/WebContent/raft-small-directories.txt -c

ffuf -u http://alpine.nyx/FUZZ -w
/usr/share/seclists/Discovery/WebContent/small-words.txt -c

![](media/image5.jpg){width="5.6958344269466314in"
height="5.624444444444444in"}

![](media/image6.jpg){width="6.875in" height="6.125in"}

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

Usuario: developer

Host: alpine.nyx

![](media/image7.png){width="7.073333333333333in"
height="4.263333333333334in"}Password: SummerVibes2024!

**Comando ejecutado:** ssh developer@alpine.nyx

![](media/image8.png){width="7.073333333333333in"
height="4.376666666666667in"}![](media/image9.png){width="7.073333333333333in"
height="4.123333333333333in"}

**Observaciones:**

- Acceso confirmado a ~developer~.

- Se revisaron archivos del home (~user.txt~, ~.ssh~) y **no se encontró
  contenido sensible adicional**.

**Recomendaciones:**

- Cambiar credenciales predeterminadas.

- Revisar accesos remotos periódicamente.

# Revisión de Procesos y Permisos 

Se revisaron procesos activos y permisos de usuarios para evaluar
posibles vectores de escalamiento. **Comandos ejecutados:**

ps aux sudo -l

![](media/image10.png){width="7.073333333333333in"
height="4.263333333333334in"}ls -la /home/developer /home/sysadmin

**Observaciones:**

- Identificación de procesos y usuarios activos (~developer~,
  ~sysadmin~, ~apache~, root).

- Permisos de archivos críticos revisados, **sin configuraciones
  inseguras adicionales**.

- ~sudo\ -l~ descartado por contraseña no disponible.

**Recomendaciones:**

- ![](media/image11.png){width="7.073333333333333in"
  height="4.323333333333333in"}Monitorizar procesos y sesiones SSH
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

**Recomendaciones:**

- No almacenar claves privadas en repositorios.

- ![](media/image12.png){width="7.073333333333333in"
  height="5.003333333333333in"}Auditar commits y eliminar información
  sensible.

# Acceso a Información Sensible y Escalamiento 

Tras acceder como ~sysadmin~, se revisaron scripts y archivos críticos.

**Comandos ejecutados:**

cat /home/sysadmin/NOTES.txt cat /opt/scripts/cleanup.sh cat
/tmp/root_flag

**Observaciones:**

- ~NOTES.txt~ mostraba tareas completadas y pendientes.

- ~cleanup.sh~ contiene instrucciones para consolidar archivos de root.

- ![](media/image13.png){width="7.073333333333333in"
  height="5.596667760279965in"}Verificado ~/tmp/root_flag~ y **no se
  encontró información crítica expuesta directamente**.

**Recomendaciones:**

- Restringir ejecución de scripts sensibles.

- Revisar logs y permisos de scripts automatizados.
