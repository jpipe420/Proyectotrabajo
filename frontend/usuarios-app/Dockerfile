# Usar imagen de Node.js
FROM node:16-alpine

# Establecer directorio de trabajo
WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar todo el código fuente
COPY . .

# Exponer puerto 4200
EXPOSE 4200

# Comando para ejecutar la aplicación en modo desarrollo
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--poll", "2000"]