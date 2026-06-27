# Informe de auditoría de seguridad

**Objetivo:** Sistema identificado como Alpine

---

# Verificación de conectividad de red

La auditoría comenzó con una comprobación de la disponibilidad de la máquina objetivo en la red.

**Comando ejecutado:** `ping 192.168.0.32`

<img width="1003" height="807" alt="image" src="https://github.com/user-attachments/assets/c96bce33-10ed-41a7-b307-bf6b79f4d125" />

**Observaciones:**

- El host respondió correctamente a las solicitudes ICMP.
- TTL = 64 y los tiempos de respuesta bajos confirman que el sistema está activo.
- También se verificó la conectividad con otros hosts internos y no se identificaron anomalías.

**Recomendaciones:**

- Restringir las respuestas ICMP a redes internas de confianza.
- Monitorizar solicitudes ICMP sospechosas.

Se realizó un escaneo activo con Nmap para identificar servicios expuestos y posibles vectores de entrada.

**Comando ejecutado:** `nmap -sS --open -sC -sV -n -Pn 192.168.0.32`

**Resultados principales:**

| Puerto | Servicio | Versión |
|---|---|---|
| 22/tcp | SSH | OpenSSH 10.2 |
| 80/tcp | HTTP | Apache 2.4.66 |

<img width="1350" height="701" alt="image" src="https://github.com/user-attachments/assets/1c7e2686-3cc9-4854-b9c5-8056e09bb39f" />

**Observaciones:**

- Todos los puertos y servicios descubiertos fueron revisados, y no se identificaron servicios adicionales ni vulnerabilidades obvias.

**Recomendaciones:**

- Limitar los puertos abiertos.
- Configurar un firewall y auditar periódicamente.

---

# Identificación de tecnologías web

Se utilizó **WhatWeb** para identificar las tecnologías del servidor y orientar la auditoría.

**Comando ejecutado:** `whatweb http://alpine`

<img width="1920" height="955" alt="image" src="https://github.com/user-attachments/assets/ec9550ed-f5af-4df4-bf19-4acfeabb2b31" />

**Observaciones:**

- Servidor web: Apache 2.4.66 (Unix).
- Tecnologías detectadas: HTML5, scripts y correos internos.
- Se revisaron los endpoints accesibles públicamente, pero no se identificó información sensible ni recursos ocultos.

<img width="1272" height="888" alt="image" src="https://github.com/user-attachments/assets/3defbecc-fc82-46d5-be80-d42589fbd516" />

**Recomendaciones:**

- Mantener actualizado el stack tecnológico.
- Ocultar información sensible en cabeceras y scripts.

---

# Enumeración de recursos -- Fuzzing

Se realizó fuzzing de directorios y archivos para descubrir rutas ocultas y paneles administrativos.

**Comandos ejecutados:**

```bash
ffuf -u http://alpine.nyx/FUZZ -w /usr/share/seclists/Discovery/WebContent/raft-small-directories.txt -c
```

<img width="1089" height="846" alt="image" src="https://github.com/user-attachments/assets/831d49e0-5a51-47cd-b02c-73ea18bed8b2" />

```bash
ffuf -u http://alpine.nyx/FUZZ -w /usr/share/seclists/Discovery/WebContent/small-words.txt -c
```

<img width="983" height="894" alt="image" src="https://github.com/user-attachments/assets/f16132bf-65db-48c0-b1eb-a7c6da18cd9e" />

**Observaciones:**

- Directorios encontrados: `/password`, `/modules`, `/includes`, `/cache`.
- `/server-status` protegido (403).
- La página `~/profile.html` y el panel interno fueron revisados, revelando información sensible adicional.

**Recomendaciones:**

- Restringir el acceso a directorios sensibles.
- Deshabilitar el listado de directorios.
- Monitorizar intentos de enumeración.

---

# Acceso SSH inicial

Se obtuvieron credenciales de acceso filtradas:

<img width="1018" height="601" alt="image" src="https://github.com/user-attachments/assets/4c9092d9-439c-46c1-813e-7173ace1cec0" />

**Usuario:** developer  
**Host:** alpine.nyx  
**Contraseña:** SummerVibes2024!

**Comando ejecutado:** `ssh developer@alpine.nyx`

<img width="1012" height="613" alt="image" src="https://github.com/user-attachments/assets/e9c164e6-9fdc-4b21-aa80-044be9127e22" />

**Observaciones:**

- Se confirmó el acceso como `developer`.
- Se revisaron los archivos dentro del directorio personal del usuario (`user.txt`, `.ssh`) y no se identificó información sensible adicional.

<img width="997" height="552" alt="image" src="https://github.com/user-attachments/assets/f589f99f-19ef-42f9-a4fc-2de5ae27dc2b" />

**Recomendaciones:**

- Cambiar las credenciales por defecto.
- Revisar periódicamente el acceso remoto.

---

# Revisión de procesos y permisos

Se revisaron los procesos activos y los permisos de usuario para evaluar posibles vectores de escalada de privilegios.

**Comandos ejecutados:**

```bash
ps aux
sudo -l
ls -la /home/developer /home/sysadmin
```

<img width="1022" height="579" alt="image" src="https://github.com/user-attachments/assets/0fb52e1b-32c7-4247-b95c-b940cf018d7d" />

**Observaciones:**

- Identificación de procesos y usuarios activos (`developer`, `sysadmin`, `apache`, `root`).
- Se revisaron permisos críticos de archivos, sin encontrar configuraciones inseguras adicionales.
- El comando `sudo -l` no pudo ejecutarse porque no se disponía de la contraseña del usuario.

**Recomendaciones:**

<img width="1000" height="580" alt="image" src="https://github.com/user-attachments/assets/93de888a-76cd-4da0-9f5a-6fd9ca047cc1" />

- Monitorizar procesos activos y sesiones SSH.

---

# Recuperación de clave SSH mediante Git

Se identificó que el repositorio Git contenía **commits con copias de seguridad de claves SSH**.

**Comandos ejecutados:**

```bash
git log --all --pretty=oneline
git show 02f9a18:id_rsa > ~/id_rsa_sysadmin
chmod 600 ~/id_rsa_sysadmin
ssh -i ~/id_rsa_sysadmin sysadmin@localhost
```

**Observaciones:**

- El repositorio Git permitió recuperar archivos eliminados de commits anteriores.
- Se probó el acceso como `sysadmin`, sin encontrar información sensible adicional.

<img width="1007" height="669" alt="image" src="https://github.com/user-attachments/assets/2e58fb44-bf92-4134-98b4-ab9197c8d8ab" />

**Recomendaciones:**

- No almacenar claves privadas en repositorios.
- Auditar commits y eliminar información sensible.

---

# Acceso a información sensible y escalada de privilegios

Una vez autenticado como sysadmin, se descubrió un script automatizado de limpieza en `/opt/scripts/cleanup.sh`, ejecutado periódicamente mediante cron.

Este script contenía una línea de código que leía archivos del directorio `/root` y los escribía en una ubicación temporal.

Aunque el script no era modificable directamente por sysadmin, su comportamiento era predecible.

- El script `cleanup.sh` consolidaba archivos del directorio `/root` en una ubicación temporal.

<img width="1021" height="752" alt="image" src="https://github.com/user-attachments/assets/e7772520-80a4-49b4-938a-72add00ef609" />

**Recomendaciones:**

- Restringir la ejecución de scripts sensibles.
- Revisar periódicamente los permisos y los registros de ejecución de scripts automatizados.
