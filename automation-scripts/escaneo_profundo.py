import os
import nmap

# 1. Entrada de datos (IP o dominio tipo flow.helix.htb)
ip_victima = input("pon la ip o dominio victima: ")

# 2. Comprobación de conectividad
conectividad = os.system(f"ping -c 3 {ip_victima}")

if conectividad == 0:
    # STEP 1: ESCANEO PESADO DE NMAP PRIMERO
    print("\n[+] [1/5] Lanzando el escaneo pesado de Nmap primero...")
    print("[+] Esto puede tardar unos minutos, ten paciencia...\n")
    
    nm = nmap.PortScanner()
    # Ejecutamos el escaneo (eliminamos -oN de arguments ya que python-nmap no maneja bien salidas a archivo externas aquí)
    nm.scan(ip_victima, arguments="-sS --open -sC -sV -n -Pn")
    print("[+] Escaneo de Nmap finalizado.")
    
    # CORRECCIÓN LÓGICA: Comprobar específicamente si el puerto 80 TCP existe y está abierto
    try:
        estado_puerto_80 = nm[ip_victima]['tcp'][80]['state']
    except KeyError:
        estado_puerto_80 = 'closed'

    # SI EL PUERTO 80 ESTÁ ABIERTO, DISPARAMOS EL ARSENAL WEB
    if estado_puerto_80 == 'open':
        print("\n" + "="*50)
        print("[+] ¡Puerto 80 ABIERTO! Iniciando herramientas web automáticas.")
        print("="*50 + "\n")
        
        # STEP 2: WHATWEB
        print("[+] [2/5] Ejecutando WhatWeb para identificar tecnologías...")
        os.system(f"whatweb http://{ip_victima}")
        print("\n" + "-"*30 + "\n")
        
        # STEP 3: KATANA (Con tus parámetros exactos de crawling)
        print("[+] [3/5] Ejecutando Katana con parámetros avanzados...")
        os.system(f"katana -u http://{ip_victima} -jc -kf all -d 10")
        print("\n" + "-"*30 + "\n")
        
        # STEP 4: CURL BÁSICO
        print("[+] [4/5] Ejecutando Curl para inspeccionar la respuesta y el Size...")
        os.system(f"curl -I http://{ip_victima}")
        print("\n" + "-"*30 + "\n")
        
        # STEP 5: FUZZING DE APIS (Ffuf + raft-medium)
        print("[+] [5/5] Lanzando Ffuf con diccionario raft-medium para buscar APIs...")
        ruta_diccionario = "/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt"
        os.system(f"ffuf -u http://{ip_victima}/FUZZ -w {ruta_diccionario} -mc 200,301,302")
        
        print("\n[+] ¡Flujo automatizado terminado con éxito!")
        
    else:
        print("\n[-] El puerto 80 está cerrado o filtrado. Nos saltamos la fase web.")

# CORRECCIÓN DE SINTAXIS: Se añade el bloque else para cerrar el IF del ping inicial
else:
    print("\n[-] No hay conectividad con la víctima (Ping fallido). Abortando.")
