**INFORME TÉCNICO DE OPERACIÓN RED TEAM

*Compromiso Total de Active Directory: De Usuario Estándar a Domain
Admin*
Estado: ✅ Completado (Root Obtenido)

1\. RESUMEN DE LA OPERACIÓN

En esta evaluación de seguridad ofensiva se simuló un ataque realista
contra un entorno Active Directory. El objetivo era demostrar el impacto
de una cadena de misconfiguraciones comunes. Partiendo de ningún acceso
inicial, se logró el compromiso total del  (Domain Admin) en menos de

La cadena de ataque explotó:

1.  Contraseñas débiles en usuarios estándar.

2.  Permisos delegados mal configurados (GenericWrite).

3.  Almacenamiento inseguro de credenciales privilegiadas (AutoLogon).

Este documento detalla la narrativa técnica completa, paso a paso,
sirviendo como evidencia de las vulnerabilidades encontradas y guía para
su remediación.

2\. NARRATIVA TÉCNICA DETALLADA (KILL CHAIN)

FASE 1: Reconocimiento Inicial y Confirmación de Vivo

La operación comenzó con la verificación de conectividad básica contra
el objetivo 192.168.0.19. El éxito en la respuesta ICMP confirmó que el
activo estaba en línea y accesible desde mi posición en la red.

- Hallazgo: TTL=128 indicó un sistema Windows Server.

- Decisión: Proceder a escaneo de puertos para identificar servicios.


<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/150e6a63-e96a-4127-ad68-1ac91084e1c3" />



\> Pie: Figura 1: Confirmación de conectividad inicial.

FASE 2: Enumeración de Servicios y Rol del Objetivo

Se ejecutó un escaneo exhaustivo con Nmap para identificar puertos
abiertos y versiones de servicios. El resultado fue crítico: el objetivo
no era un servidor cualquiera, sino el Domain Controller (DC) del
dominio megachange.nyx.

- Servicios Clave: DNS (53), Kerberos (88), LDAP (389), SMB (445)
  y WinRM (5985).

- Análisis: La presencia de WinRM abierto sería un vector crucial más
  adelante.

<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/14e2c2ea-a823-4a53-9c3c-266d9b55086f" />


Identificación del Domain Controller y servicios expuestos.

FASE 3: Mapeo del Dominio vía DNS

Antes de atacar, necesitaba entender la estructura del dominio.
Usando dig y fierce, interrogué el servicio DNS.

- Hallazgo: Se confirmó el dominio megachange.nyx y su delegación. No se
  encontraron subdominios ocultos, lo que indicaba que la superficie de
  ataque externa estaba bien contenida.

- Pivot: Al no haber vectores DNS, el siguiente paso lógico fue intentar
  enumerar sin credenciales en SMB y LDAP.

<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/7dd44797-3c59-44a7-b154-cbf9688192ed" />



<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/b5ecce73-40b9-462e-ab5c-3e696a8d2d7f" />



Mapeo inicial de la estructura del dominio.

FASE 4: Intentos de Enumeración Anónima (Fallidos)

Se probaron vectores clásicos de configuración errónea:

1.  Null Sessions en SMB: Bloqueadas (STATUS_ACCESS_DENIED).

2.  Cuenta Guest: Deshabilitada correctamente.

3.  RID Brute: Bloqueado por permisos insuficientes.

- Lección Defensiva: El hardening básico del DC era correcto para
  accesos anónimos.

- Conclusión: Para progresar, era obligatorio obtener credenciales
  válidas primero.

<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/51d5323a-eecb-4016-9ef8-a075b319afea" />


Outputs de los intentos fallidos con nxc/netexec

Vectores anónimos bloqueados por hardening correcto.

FASE 5: Enumeración de Usuarios vía Kerberos

Dado que no podía enumerar sin autenticación, usé Kerbrute para
identificar usuarios válidos sin bloquear cuentas (técnica silenciosa).

- Usuarios Descubiertos: alfredo, administrator, change.

- Estrategia: alfredo parecía un usuario estándar, el objetivo perfecto
  para fuerza bruta inicial.

<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/b9f54ff0-b193-411b-815e-d5876b58cb0c" />


\> KERBRUTE USERENUM

\> Identificación silenciosa de usuarios válidos.

FASE 6: Fuerza Bruta y Punto de Entrada (Brecha Inicial)

Con la lista de usuarios, ejecuté un ataque de fuerza bruta
contra alfredo vía SMB usando la lista rockyou.txt.

- 🚨 HALLAZGO CRÍTICO: La contraseña era Password1.

- Impacto: Se obtuvo acceso inicial válido en menos de 25 intentos. Esto
  demostró una política de contraseñas inexistente o mal aplicada

- Nota Técnica - Agotamiento de Vectores:

- Antes de depender exclusivamente de la fuerza bruta, intenté explotar
  vectores más sofisticados contra Kerberos para descartar
  configuraciones erróneas críticas:

- AS-REP Roasting: Ejecuté GetNPUsers contra alfredo, pero no fue
  vulnerable (preautenticación habilitada).

- Kerberoasting: Ejecuté GetUserSPNs buscando SPNs explotables, pero no
  se encontraron entradas (No entries found!).

- Estos fallos confirmaron que la configuración de Kerberos era
  correcta, obligándome a depender de la debilidad de la contraseña
  humana (Password1) como único vector de entrada viable.

<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/1a80c866-d730-4f27-881c-c047b532fa46" />


<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/b9a4390c-9fac-43a6-843b-45c2d2595967" />


\> NETEXEC mostrando el éxito con \'Password1\'

\> Compromiso inicial debido a contraseña débil.

FASE 7: Enumeración Interna con Credenciales

Ya dentro como alfredo, enumeré qué recursos eran accesibles.

- Shares: Acceso de lectura a SYSVOL y NETLOGON (normal), pero sin
  archivos sensibles obvios.

- Usuarios: Confirmé la existencia de sysadmin, una cuenta creada el
  mismo día que alfredo.

- Hipótesis: Si alfredo y sysadmin fueron creados juntos, ¿habría una
  relación de permisos entre ellos?

<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/4a526a0d-ca69-4338-a723-781cccee160b" />


\> enumeración de shares y usuarios con credenciales

\> Enumeración interna post-compromiso.

FASE 8: Búsqueda de Vectores de Escalada (BloodHound)

Para responder a la hipótesis,
ejecuté BloodHound (vía bloodhound-python) para mapear relaciones de
confianza en el AD.

- 🚨 HALLAZGO DECISIVO: alfredo tenía el
  permiso GenericWrite sobre sysadmin.

- Significado: Esto permite a un usuario estándar modificar atributos
  críticos de otro usuario, incluyendo forzar un cambio de contraseña.
  Una delegación de permisos peligrosa y olvidada.

<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/d3ebabfb-1efe-41d7-837b-5175073fc5aa" />


<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/d9fa62ad-7b79-49e8-9506-6bb964b6cf36" />


\> BloodHound mostrando la arista GenericWrite

\> Relación de confianza crítica identificada para escalada.

FASE 9: Explotación y Escalada Lateral

Usé rpcclient para explotar el permiso GenericWrite y cambiar la
contraseña de sysadmin sin conocer la anterior.

- Acción: setuserinfo2 sysadmin 23 NuevaPassword123!

- Resultado: Éxito silencioso (sin errores = éxito en rpcclient).

- Verificación: Confirmé el nuevo acceso con netexec, obteniendo el
  marcador (Pwn3d!), lo que indica que sysadmin es administrador local
  del DC.


<img width="1024" height="441" alt="image" src="https://github.com/user-attachments/assets/42d83700-8e71-49a0-a5d6-4a4d13cf9e38" />


\>Comando rpcclient y verificación con netexec (Pwn3d!)

\> Escalada lateral exitosa a cuenta privilegiada.

FASE 10: Acceso Remoto y Post-Explotación (WinRM)

Dado que sysadmin tenía permisos de administración y el puerto 5985
(WinRM) estaba abierto, establecí una shell interactiva completa
usando Evil-WinRM.

- Ventaja: Esto me dio capacidad de ejecución de PowerShell completa en
  el servidor, mucho más potente que SMB.

- Preparación: Subí mis herramientas de post-explotación
  (winPEASx64.exe y SharpHound.zip) al escritorio del usuario para un
  análisis profundo.

<img width="1024" height="441" alt="image" src="https://github.com/user-attachments/assets/30e8407f-8061-4562-8378-93b6f1dd1952" />


Shell de Evil-WinRM y listado de herramientas subidas (ls)

Establecimiento de shell remota y despliegue de herramientas.

FASE 11: Análisis Automatizado con WinPEAS

Ejecuté WinPEAS para buscar configuraciones erróneas, credenciales
guardadas y vectores de escalada local.

- Proceso: La herramienta escaneó registro, tareas programadas,
  servicios y políticas.

- Resultado Inicial: No se encontraron vulnerabilidades de kernel ni
  servicios mal configurados. El sistema estaba parcheado.

<img width="1024" height="441" alt="image" src="https://github.com/user-attachments/assets/d1778484-83e0-4b01-84b1-4460ade2c6f1" />


\> Banner de WinPEAS y sección inicial de escaneo

\> Ejecución de WinPEAS para búsqueda automatizada de vectores.

FASE 12: El Hallazgo Catastrófico (AutoLogon)

Mientras WinPEAS profundizaba, identificó una configuración crítica en
el registro de Windows: AutoLogon habilitado para la
cuenta administrator.

- 🚨 HALLAZGO CRÍTICO MÁXIMO: La contraseña del administrador del
  dominio (d0m@in_c0ntr0ll3r) estaba almacenada en TEXTO CLARO en el
  registro.

- Impacto: Esto otorga control total e inmediato de todo el bosque
  Active Directory. Es una práctica prohibida por su extrema
  peligrosidad.

<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/c58675bb-d8d1-49dc-aa59-a5f5b461c841" />


<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/44600b6c-e24a-48b9-84f8-04f606305bb6" />


 

\> Pie: Figura 12: Hallazgo catastrófico de credenciales de Domain Admin
en texto claro.

FASE 13: Compromiso Total del Bosque (Domain Admin)

Con las credenciales obtenidas, inicié una nueva sesión
como administrator.

- Verificación: El comando whoami /groups confirmó la pertenencia
  a Domain Admins, Enterprise Admins y Schema Admins.

- Estado: Control absoluto de la infraestructura. Capacidad para
  modificar el esquema, crear usuarios dorados (Golden Ticket) y acceder
  a cualquier dato.

<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/ab00b42f-b0dd-40b5-a5f2-2e11a29b3499" />


<img width="924" height="441" alt="image" src="https://github.com/user-attachments/assets/90b26e4d-302d-41e4-9f4c-e267cfd011f3" />


\ Whoami /groups mostrando los grupos privilegiados

\>Confirmación de privilegios máximos (Domain Admin).

FASE 14: Captura del Objetivo Final (Root)

Para cerrar la operación con éxito, navegué al escritorio del
administrador y capturé la flag root.txt.

- Resultado: user.txt (como sysadmin) y root.txt (como administrator)
  obtenidas.

- Conclusión: La cadena de ataque fue completa y exitosa.

text

3\. RECOMENDACIONES DEFENSIVAS (BLUE TEAM)

Para evitar que esta cadena de ataque se repita, se recomiendan las
siguientes mejoras de seguridad, priorizadas por impacto:

🛡️ 1. Higiene de Credenciales (Prioridad Crítica)

- Política de Contraseñas: Implementar una longitud mínima de 14+
  caracteres y usar listas de contraseñas prohibidas (ban lists) para
  evitar combinaciones como Password1.

- Eliminar AutoLogon: Auditar y eliminar inmediatamente cualquier clave
  de registro DefaultPassword en HKLM\\SOFTWARE\\Microsoft\\Windows
  NT\\CurrentVersion\\Winlogon. Las credenciales
  privilegiadas nunca deben almacenarse en texto claro.

- LAPS: Implementar LAPS (Local Administrator Password Solution) para
  gestionar contraseñas locales de forma segura y rotativa.

🛡️ 2. Endurecimiento de Active Directory

- Auditoría de ACLs: Revisar periódicamente permisos delegados
  como GenericWrite, GenericAll o ForceChangePassword. Ningún usuario
  estándar debe tener permisos de escritura sobre cuentas privilegiadas.

- Segmentación de WinRM: Restringir el puerto 5985 mediante firewall
  para que solo acepte conexiones desde estaciones de administración
  privilegiada (PAWs/Jump Boxes), no desde toda la red.

🛡️ 3. Detección y Monitoreo

- Alertas de Cambio de Contraseña: Configurar alertas en el SOC para
  el Event ID 4724 (intento de reseteo de contraseña por otro usuario),
  especialmente si es iniciado por una cuenta no privilegiada.

- Monitoreo de WinRM: Alertar sobre conexiones WinRM (Event ID 6) hacia
  Domain Controllers que no provengan de subreds de administración
  autorizadas.

- EDR: Desplegar soluciones EDR capaces de detectar herramientas de
  post-explotación como WinPEAS o BloodHound en ejecución.

4\. CONCLUSIÓN

Esta operación demostró cómo una serie de \"pequeños\" errores (una
contraseña débil, un permiso mal delegado y una credencial en texto
claro) se combinaron para permitir el compromiso total del dominio.

La lección principal es que la seguridad no es solo tener los parches al
día; es la gestión rigurosa de identidades, permisos y configuraciones.
La implementación de las recomendaciones anteriores elevará
significativamente la barrera de entrada para cualquier atacante real.
