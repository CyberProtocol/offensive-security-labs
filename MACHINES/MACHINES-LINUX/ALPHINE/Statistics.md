nforme de Auditoría de Seguridad

Objetivo: Sistema identificado como Alpine

Verificación de Conectividad de Red
Se inició la auditoría con una comprobación de la disponibilidad de la máquina objetivo en la red.

Comando ejecutado: ping 192.168.0.32

image
Observaciones:

El host respondió exitosamente a las solicitudes ICMP.

El TTL = 64 y tiempos de respuesta bajos confirman que el sistema está activo.

Se revisó la conectividad a otros hosts internos, pero no se encontraron anomalías.

Recomendaciones:

Restringir respuestas ICMP a redes internas confiables.

Monitorizar solicitudes ICMP sospechosas.

Escaneo de Puertos
Se realizó un escaneo activo con Nmap para identificar servicios expuestos y posibles vectores de entrada. Comando ejecutado: nmap -sS --open -sC -sV -n -Pn 192.168.0.32 Resultados principales:

Puerto Servicio Versión

22/tcp SSH OpenSSH 10.2 80/tcp HTTP Apache 2.4.66

image
Observaciones:

Se revisaron todos los puertos y servicios conocidos, pero no se detectaron servicios adicionales ni vulnerabilidades evidentes.
Recomendaciones:

Limitar los puertos abiertos.

Configurar firewall y auditar periódicamente.

Identificación de Tecnologías Web
Se utilizó WhatWeb para identificar tecnologías del servidor y orientar la auditoría.

Comando ejecutado: whatweb http://alpine. image

Observaciones:

Servidor web: Apache 2.4.66 (Unix).

Tecnologías detectadas: HTML5, scripts y correos internos.

Se revisaron posibles APIs y endpoints, pero no se encontró información sensible ni recursos ocultos.

image
Recomendaciones:

Mantener actualizado el stack tecnológico.

Ocultar información sensible en headers y scripts.

Enumeración de Recursos -- Fuzzing
Se realizó fuzzing de directorios y archivos web para descubrir rutas ocultas y paneles administrativos.

Comandos ejecutados:

ffuf -u http://alpine.nyx/FUZZ -w /usr/share/seclists/Discovery/WebContent/raft-small-directories.txt -c

image
ffuf -u http://alpine.nyx/FUZZ -w /usr/share/seclists/Discovery/WebContent/small-words.txt -c

image
Observaciones: • Se encontraron directorios: /password, /modules, /includes, /cache. • /server-status protegido (403).

Revisado /profile.html y dashboard interno, con información sensible adicional.
Recomendaciones:

Restringir acceso a directorios sensibles.

Deshabilitar listado de directorios.

Monitorizar intentos de enumeración.

Acceso SSH Inicial
Se obtuvieron credenciales de acceso filtradas:

image
Usuario: developer

Host: alpine.nyx

Password: SummerVibes2024!

Comando ejecutado: ssh developer@alpine.nyx

image
Observaciones:

Acceso confirmado a developer.

Se revisaron archivos del home (user.txt, .ssh) y no se encontró contenido sensible adicional.>

image
Recomendaciones:

Cambiar credenciales predeterminadas.

Revisar accesos remotos periódicamente.

Revisión de Procesos y Permisos
Se revisaron procesos activos y permisos de usuarios para evaluar posibles vectores de escalamiento. Comandos ejecutados:

ps aux sudo -l

ls -la /home/developer /home/sysadmin

image
Observaciones:

Identificación de procesos y usuarios activos (developer, sysadmin, apache, root).

Permisos de archivos críticos revisados, sin configuraciones inseguras adicionales.

sudo\ -l descartado por contraseña no disponible.

Recomendaciones:

image
Monitorizar procesos y sesiones SSH activas.
Recuperación de Clave SSH vía Git
Se identificó que el repositorio Git contenía commits con backups de claves SSH.

Comandos ejecutados:

git log --all --pretty=oneline git show 02f9a18:id_rsa > ~/id_rsa_sysadmin chmod 600 ~/id_rsa_sysadmin

ssh -i ~/id_rsa_sysadmin sysadmin@localhost

Observaciones:

Git permitió recuperar archivos borrados de commits anteriores.

Probado acceso como sysadmin, sin encontrar información sensible adicional.

image
Recomendaciones:

No almacenar claves privadas en repositorios.

Auditar commits y eliminar información sensible.

Acceso a Información Sensible y Escalamiento
Una vez dentro como sysadmin, se descubrió un script de limpieza automatizado en /opt/scripts/cleanup.sh, que se ejecutaba periódicamente a través de cron.

Este script contenía una línea de código que leía archivos del directorio /root y los escribía en una ubicación temporal.

Aunque el script en sí no era directamente modicable por sysadmin, su comportamiento era predecible.

cleanup.sh contiene instrucciones para consolidar archivos de root.
image
Recomendaciones:

Restringir ejecución de scripts sensibles.

Revisar logs y permisos de scripts automatizados.
