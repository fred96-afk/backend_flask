#!/bin/bash

# Salir inmediatamente si un comando falla
set -e

# 1. Instalar dependencias del sistema necesarias para el driver
apt-get update
apt-get install -y curl apt-transport-https gnupg

# 2. Agregar la clave GPG de Microsoft
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# 3. Agregar el repositorio de Microsoft para Ubuntu 22.04 (base común de Render)
# Si falla, podrías probar cambiando '22.04' por '20.04'
curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# 4. Actualizar la lista de paquetes e instalar el driver
apt-get update
# 'ACCEPT_EULA=Y' es crucial para que la instalación no se detenga
ACCEPT_EULA=Y apt-get install -y msodbcsql18

# 5. Instalar 'unixodbc-dev', necesario para que 'pyodbc' se compile
apt-get install -y unixodbc-dev

# 6. Finalmente, instalar las dependencias de Python
pip install -r requirements.txt