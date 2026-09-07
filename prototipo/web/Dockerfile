# ==============================================================================
# ETAPA 1: Compilación de la aplicación Angular 17
# ==============================================================================
FROM node:20-alpine AS build

WORKDIR /app

# Instalar dependencias
COPY package*.json ./
RUN npm ci

# Copiar código fuente y compilar bundle para producción
COPY . .
RUN npm run build -- --configuration production

# ==============================================================================
# ETAPA 2: Servidor Nginx de Alto Rendimiento con Proxy Inverso
# ==============================================================================
FROM nginx:1.25-alpine

# Variables de entorno por defecto (Render inyecta PORT automáticamente)
ENV PORT=80 \
    BACKEND_URL=http://backend:8000

# Copiar bundle compilado de Angular a la raíz web de Nginx
COPY --from=build /app/dist/sigepsi-web/browser /usr/share/nginx/html

# Copiar plantilla Nginx (envsubst la compila automáticamente al arrancar el contenedor)
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80 10000

CMD ["nginx", "-g", "daemon off;"]
