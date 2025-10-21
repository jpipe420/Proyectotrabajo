# Usar imagen de Node.js
FROM node:16-alpine

# Argumento para la versión de Angular CLI
ARG ANGULAR_CLI_VERSION=16.2.10

# Establecer directorio de trabajo
WORKDIR /app

# Instalar Angular CLI globalmente con la versión específica
RUN npm install -g @angular/cli@${ANGULAR_CLI_VERSION}

# Copiar package.json y package-lock.json
COPY package*.json ./

# Limpiar caché de npm y instalar dependencias
RUN npm cache clean --force && npm install

# Copiar todo el código fuente
COPY . .

# Exponer puerto 4200
EXPOSE 4200

# Comando para ejecutar la aplicación en modo desarrollo
CMD ["ng", "serve", "--host", "0.0.0.0", "--poll", "2000", "--disable-host-check"]