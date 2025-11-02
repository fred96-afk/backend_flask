# Use an official Python runtime as a parent image
FROM python:3.11-slim

# --- NUEVO: Instalar el driver ODBC de SQL Server ---
# 1. Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc-dev \
    apt-transport-https \
    && echo "Dependencias de sistema instaladas"

# 2. Registrar la clave GPG de Microsoft
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# 3. Registrar el repositorio de Microsoft para Debian 12 (la base de python:3.11-slim)
RUN curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list

# 4. Instalar el driver (y limpiar la caché)
RUN apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*
# --- FIN DE SECCIÓN NUEVA ---


# Set the working directory in the container
WORKDIR /app

# Copy and install Python requirements
# El driver ODBC debe estar instalado ANTES de pip install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make port 5000 available (Gunicorn usará este puerto)
EXPOSE 5000

# --- MODIFICADO: Usar Gunicorn para producción ---
# Los ENV FLASK_APP y FLASK_RUN_HOST ya no son necesarios
# El comando CMD ["flask", "run"] es SOLO para desarrollo.
# Usamos gunicorn para producción:
# (Asegúrate de agregar 'gunicorn' a tu requirements.txt)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]