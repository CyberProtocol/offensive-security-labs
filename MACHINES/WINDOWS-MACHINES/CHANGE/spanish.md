# Informe técnico – Operación Red Team

## Compromiso completo de Active Directory: de usuario estándar a Domain Administrator  
**Estado:** Completado (Root obtenido)

## 1. Resumen ejecutivo

Esta evaluación de seguridad ofensiva simuló un ataque realista contra un entorno de Active Directory. El objetivo fue demostrar el impacto de una cadena de malas configuraciones comunes. Partiendo sin acceso inicial, se logró un compromiso completo como Domain Administrator en un corto periodo de tiempo.

La cadena de ataque aprovechó las siguientes debilidades:

1. Contraseñas débiles en cuentas de usuario estándar.
2. Permisos delegados mal configurados (`GenericWrite`).
3. Almacenamiento inseguro de credenciales privilegiadas (`AutoLogon`).

Este documento proporciona una narrativa técnica completa, paso a paso, que sirve tanto como evidencia de las vulnerabilidades identificadas como guía de remediación.

## 2. Narrativa técnica detallada (Kill Chain)

### Fase 1: Reconocimiento inicial y confirmación de disponibilidad del host

La operación comenzó verificando la conectividad básica con el objetivo en `192.168.0.19`. Una respuesta ICMP exitosa confirmó que el activo estaba en línea y era alcanzable desde la posición del atacante dentro de la red.

- Hallazgo: `TTL=128` indicó un sistema Windows Server.
- Decisión: Continuar con el escaneo de puertos para identificar los servicios expuestos.

![Figura 1: Confirmación inicial de conectividad](https://github.com/user-attachments/assets/150e6a63-e96a-4127-ad68-1ac91084e1c3)

### Fase 2: Enumeración de servicios e identificación del rol del objetivo

Se realizó un escaneo completo con Nmap para identificar puertos abiertos y versiones de servicios. El resultado fue crítico: el objetivo no era un servidor cualquiera, sino el Controlador de Dominio (DC) del dominio `megachange.nyx`.

- Servicios clave: DNS (53), Kerberos (88), LDAP (389), SMB (445) y WinRM (5985).
- Análisis: La presencia de WinRM expuesto se convertiría en un vector de ataque crucial más adelante.

![Identificación del Controlador de Dominio y servicios expuestos](https://github.com/user-attachments/assets/9cc967af-c45a-4862-9cca-165b787014b8)

### Fase 3: Mapeo del dominio mediante DNS

Antes de continuar con ataques activos, fue necesario comprender la estructura del dominio. Usando `dig` y `fierce`, se consultó el servicio DNS.

- Hallazgo: Se confirmó el dominio `megachange.nyx` y su delegación. No se descubrieron subdominios ocultos, lo que indicó que la superficie de ataque externa estaba bien contenida.
- Pivot: Sin vectores de ataque basados en DNS, el siguiente paso lógico fue la enumeración no autenticada mediante SMB y LDAP.

![Mapeo inicial de la estructura del dominio](https://github.com/user-attachments/assets/7dd44797-3c59-44a7-b154-cbf9688192ed)

<img width="1040" height="441" alt="image" src="https://github.com/user-attachments/assets/b5ecce73-40b9-462c-3e3c-5e3e3e3e3e3e" />

### Fase 4: Intentos de enumeración anónima (fallidos)

Se probaron vectores clásicos de mala configuración:

1. Sesiones nulas SMB: Bloqueadas (`STATUS_ACCESS_DENIED`).
2. Cuenta Guest: Correctamente deshabilitada.
3. RID Brute Force: Bloqueado por permisos insuficientes.

- Observación defensiva: El endurecimiento básico del Controlador de Dominio estaba correctamente implementado contra accesos anónimos.
- Conclusión: Se requerían credenciales válidas para continuar.

![Resultados de los intentos fallidos de enumeración con nxc/netexec](https://github.com/user-attachments/assets/cdd56a93-e6a8-4ca5-a73f-8d352e2cbdf1)

### Fase 5: Enumeración de usuarios mediante Kerberos

Dado que no era posible la enumeración no autenticada, se utilizó Kerbrute para identificar usuarios válidos sin provocar bloqueos de cuenta (técnica sigilosa).

- Usuarios descubiertos: `alfredo`, `administrator`, `change`.
- Estrategia: `alfredo` parecía ser un usuario estándar, por lo que se eligió como objetivo inicial para fuerza bruta.

![Identificación silenciosa de usuarios válidos mediante Kerberos](https://github.com/user-attachments/assets/b9f54ff0-b193-411b-815e-d5876b58cb0c)

### Fase 6: Fuerza bruta y acceso inicial

Usando los nombres de usuario descubiertos, se ejecutó un ataque de fuerza bruta contra `alfredo` mediante SMB con la wordlist `rockyou.txt`.

- Hallazgo crítico: La contraseña era `Password1`.
- Impacto: Se obtuvo acceso inicial en menos de 25 intentos, lo que demuestra una política de contraseñas débil o mal aplicada.

**Nota técnica – Exhaustividad de vectores alternativos:**

Antes de depender únicamente de la fuerza bruta, se probaron vectores Kerberos más avanzados:

- AS-REP Roasting: `GetNPUsers` se ejecutó contra `alfredo`, pero la cuenta no era vulnerable (la preautenticación estaba habilitada).
- Kerberoasting: `GetUserSPNs` se ejecutó para identificar SPNs explotables, pero no se encontraron entradas.

Estos resultados confirmaron que Kerberos estaba correctamente configurado, dejando como única vía práctica las malas prácticas humanas en contraseñas.

![Compromiso inicial logrado debido a credenciales débiles](https://github.com/user-attachments/assets/1a80c866-d730-4f27-881c-c047b532fa46)

![Compromiso inicial logrado debido a credenciales débiles](https://github.com/user-attachments/assets/4d4320a9-ae0d-4536-8c9b-1e84604f3d9c)

### Fase 7: Enumeración interna con credenciales válidas

Con acceso como `alfredo`, se enumeraron recursos internos.

- Shares: Acceso de lectura a `SYSVOL` y `NETLOGON` (esperado), sin archivos sensibles obvios.
- Usuarios: Se confirmó la existencia de una cuenta `sysadmin`, creada el mismo día que `alfredo`.
- Hipótesis: La creación simultánea sugería una posible relación de permisos entre ambas cuentas.

![Enumeración interna posterior al compromiso](https://github.com/user-attachments/assets/eccd01fc-d8c8-4832-bc98-e4d3bf5a9ca0)

### Fase 8: Descubrimiento del camino de escalada de privilegios (BloodHound)

Para validar la hipótesis, se utilizó BloodHound (mediante `bloodhound-python`) para mapear relaciones de confianza dentro de Active Directory.

- Hallazgo crítico: `alfredo` tenía permisos `GenericWrite` sobre `sysadmin`.
- Significado: Esto permite modificar atributos sensibles de otro usuario, incluyendo forzar un restablecimiento de contraseña, un permiso delegable extremadamente peligroso.

![Relación de confianza crítica identificada para escalada de privilegios](https://github.com/user-attachments/assets/ba2308d3-0481-4444-936a-2d900e7af66c)

![Relación de confianza crítica identificada para escalada de privilegios](https://github.com/user-attachments/assets/9f7e6827-6db5-4ac8-99a9-476ce5321851)

### Fase 9: Explotación y movimiento lateral

El permiso `GenericWrite` se explotó usando `rpcclient` para restablecer la contraseña de `sysadmin` sin conocer la original.

- Acción: `setuserinfo2 sysadmin 23 NewPassword123!`
- Resultado: Éxito silencioso (sin errores devueltos por `rpcclient`).
- Verificación: Se confirmó el acceso con `netexec`, mostrando el indicador `(Pwn3d!)`, lo que significó que `sysadmin` tenía privilegios de administrador local en el Controlador de Dominio.

![Movimiento lateral exitoso hacia una cuenta privilegiada](https://github.com/user-attachments/assets/032c59cc-db63-4bcd-a302-0e1592d47430)

### Fase 10: Acceso remoto y post-explotación (WinRM)

Como `sysadmin` tenía privilegios administrativos y WinRM (puerto 5985) estaba expuesto, se estableció una shell interactiva completa usando Evil-WinRM.

- Ventaja: Ejecución completa de PowerShell en el sistema objetivo, mucho más potente que el acceso SMB.
- Preparación: Se subieron herramientas de post-explotación (`winPEASx64.exe` y `SharpHound.zip`) al escritorio del usuario para un análisis más profundo.

![Shell remota establecida y herramientas desplegadas](https://github.com/user-attachments/assets/30e8407f-8061-4562-8378-93b6f1dd1952)

### Fase 11: Análisis automatizado con WinPEAS

Se ejecutó WinPEAS para identificar malas configuraciones, credenciales almacenadas y vectores de escalada local.

- Proceso: La herramienta analizó el registro, tareas programadas, servicios y políticas.
- Resultado inicial: No se encontraron vulnerabilidades del kernel ni servicios mal configurados; el sistema estaba correctamente parcheado.

![Ejecución de enumeración automatizada con WinPEAS](https://github.com/user-attachments/assets/bfcdc528-0daf-4879-b832-ef7cdc3d30be)

### Fase 12: Descubrimiento crítico – AutoLogon

Durante el análisis profundo, WinPEAS identificó una configuración crítica en el registro de Windows: AutoLogon habilitado para la cuenta `administrator`.

- Hallazgo máximo crítico: La contraseña del Domain Administrator (`d0m@in_c0ntr0ll3r`) estaba almacenada en texto claro en el registro.
- Impacto: Esto proporciona control inmediato y completo sobre todo el bosque de Active Directory. Esta práctica está estrictamente prohibida por su riesgo extremo.

![Exposición catastrófica de credenciales de Domain Admin en texto claro](https://github.com/user-attachments/assets/d98beed7-6307-4ba9-91df-f9486a6e162d)

![Exposición catastrófica de credenciales de Domain Admin en texto claro](https://github.com/user-attachments/assets/107a78a1-99f7-4064-a05e-6da6d3c9a3f9)

### Fase 13: Compromiso total del dominio

Usando las credenciales recuperadas, se estableció una nueva sesión como `administrator`.

- Verificación: El comando `whoami /groups` confirmó pertenencia a `Domain Admins`, `Enterprise Admins` y `Schema Admins`.
- Estado: Control total de la infraestructura, incluyendo la capacidad de modificar el esquema, crear Golden Tickets y acceder a cualquier dato.

![Confirmación del máximo nivel de privilegio (Domain Admin)](https://github.com/user-attachments/assets/d46506cd-579c-427d-ae85-828d6641f0b8)

![Confirmación del máximo nivel de privilegio (Domain Admin)](https://github.com/user-attachments/assets/ddb7d64c-2d7e-4b49-a376-2d2d18d3924a)

### Fase 14: Cumplimiento del objetivo (Root)

Para finalizar la operación, se accedió al escritorio del administrador y se recuperó el indicador `root.txt`.

- Resultado: Se obtuvieron `user.txt` (como `sysadmin`) y `root.txt` (como `administrator`).
- Conclusión: La cadena de ataque quedó completa y totalmente exitosa.

## 3. Recomendaciones defensivas (Blue Team)

Para evitar que esta cadena de ataque vuelva a producirse, se recomiendan las siguientes mejoras de seguridad, priorizadas por impacto:

### 1. Higiene de credenciales (prioridad crítica)

- Política de contraseñas: Exigir una longitud mínima de 14+ caracteres e implementar listas de contraseñas prohibidas para evitar combinaciones débiles como `Password1`.
- Deshabilitar AutoLogon: Auditar y eliminar de inmediato cualquier clave `DefaultPassword` ubicada en `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon`. Las credenciales privilegiadas nunca deben almacenarse en texto claro.
- LAPS: Implementar Local Administrator Password Solution (LAPS) para administrar y rotar de forma segura las contraseñas de administradores locales.

### 2. Endurecimiento de Active Directory

- Auditoría de ACLs: Revisar periódicamente permisos delegados como `GenericWrite`, `GenericAll` o `ForceChangePassword`. Los usuarios estándar nunca deben tener permisos de escritura sobre cuentas privilegiadas.
- Segmentación de WinRM: Restringir el puerto 5985 mediante reglas de firewall para permitir conexiones solo desde estaciones administrativas privilegiadas (PAWs/Jump Boxes), no desde toda la red.

### 3. Detección y monitorización

- Alertas de restablecimiento de contraseña: Configurar alertas del SOC para el Event ID 4724 (intentos de cambio de contraseña), especialmente si son iniciados por cuentas no privilegiadas.
- Monitorización de WinRM: Alertar sobre conexiones WinRM (Event ID 6) a Controladores de Dominio originadas en subredes no autorizadas.
- Despliegue de EDR: Implementar soluciones EDR capaces de detectar herramientas de post-explotación como WinPEAS o BloodHound.

### 4. Conclusión

Esta operación demostró cómo una cadena de problemas aparentemente menores —una contraseña débil, permisos mal configurados y almacenamiento de credenciales en texto claro— puede combinarse para permitir un compromiso total del dominio.

La conclusión clave es que la seguridad no consiste solo en parchear sistemas; requiere una gestión rigurosa de identidades, permisos y configuraciones. Implementar las recomendaciones anteriores incrementará significativamente la dificultad para cualquier atacante real.
