#!/bin/sh
set -e

export PORT="${PORT:-80}"
export BACKEND_URL="${BACKEND_URL:-http://backend:8000}"

# Quitar trailing slash si fue colocado por error (ej: https://host.com/)
BACKEND_URL=$(echo "$BACKEND_URL" | sed 's/\/$//')
export BACKEND_URL

echo "=========================================================="
echo " ==> SIGEPSI FRONTEND NGINX"
echo " ==> Puerto de escucha: ${PORT}"
echo " ==> Proxy /api/ hacia: ${BACKEND_URL}/api/"
echo "=========================================================="

# Sustituir EXCLUSIVAMENTE $PORT y $BACKEND_URL
# Las variables de Nginx ($uri, $proxy_host, $remote_addr, etc.) se preservan intactas
envsubst '${PORT} ${BACKEND_URL}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf

# Validar la configuración generada
nginx -t

exec "$@"
