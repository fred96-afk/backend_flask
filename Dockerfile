# Use an official Python runtime as a parent image
FROM python:3.11-slim

# --- INICIO DE SECCIÓN DEL DRIVER ---
# 1. Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc-dev \
    apt-transport-https \
    && echo "Dependencias de sistema instaladas"

# 2. Registrar la clave GPG de Microsoft
RUN mkdir -p /usr/share/keyrings \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

# 3. Registrar el repositorio de Microsoft
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list

# 4. Instalar el driver
RUN apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*
# --- FIN DE SECCIÓN DEL DRIVER ---


# Set the working directory in the container
WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# --- ¡NUEVA LÍNEA! ---
# Crea el directorio de 'uploads' para que 'image.save()' funcione
RUN mkdir -p /app/instance/uploads
# --------------------

# Make port 5000 available
EXPOSE 5000

# Usamos gunicorn para producción
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]