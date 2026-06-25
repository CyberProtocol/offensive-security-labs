# Modulo de Automatizacion - Escaneo Profundo

Este directorio contiene herramientas en Python desarrolladas para agilizar las fases de reconocimiento y enumeracion inicial durante auditorias de seguridad o resolucion de laboratorios.

---

## Script: escaneo_profundo.py

Script automatizado que unifica multiples herramientas de reconocimiento en un solo flujo secuencial. Evita la ejecucion manual de comandos basicos y optimiza el tiempo de respuesta ante puertos web expuestos.

### Flujo de Ejecucion

1. Verificacion de conectividad basica mediante envio de paquetes ICMP (Ping).
2. Lanzamiento de un escaneo pesado con Nmap para detectar puertos abiertos, servicios, versiones y ejecucion de scripts basicos de reconocimiento.
3. Analisis del estado del puerto 80 TCP:
   * Si el puerto esta cerrado, el script finaliza notificando la situacion.
   * Si el puerto esta abierto, se activa de forma automatica el arsenal de herramientas web.

### Herramientas Web Integradas

* WhatWeb: Analisis e identificacion de tecnologias, gestores de contenido (CMS) y librerias del servidor.
* Katana: Crawling y mapeo avanzado de rutas, formularios y endpoints con profundidad de nivel 10.
* Curl: Inspeccion tecnica de cabeceras HTTP y medicion del tamaño de la respuesta del servidor.
* Ffuf: Fuzzing de directorios y APIs ocultas utilizando el diccionario raft-medium de SecLists.

---

## Requisitos de Instalacion

Para utilizar este script en sistemas como Kali Linux, es necesario contar con Python 3 y la libreria de control de Nmap.

```bash
sudo apt update && sudo apt install python3-pip -y
pip3 install python-nmap --break-system-packages
```

Ademas, el sistema operativo debe tener instaladas y accesibles en el PATH global las herramientas nativas: nmap, whatweb, katana, curl y ffuf, junto con los diccionarios de SecLists en la ruta especificada por el codigo.
