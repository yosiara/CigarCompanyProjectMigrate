#!/bin/bash
set -e

# ============================================
# Configuración de base de datos
# ============================================
if [ -v PASSWORD_FILE ]; then
    PASSWORD="$(< $PASSWORD_FILE)"
fi

: ${HOST:=${DB_PORT_5432_TCP_ADDR:='db'}}
: ${PORT:=${DB_PORT_5432_TCP_PORT:=5432}}
: ${USER:=${DB_ENV_POSTGRES_USER:=${POSTGRES_USER:='odoo'}}}
: ${PASSWORD:=${DB_ENV_POSTGRES_PASSWORD:=${POSTGRES_PASSWORD:='odoo'}}}

DB_ARGS=()
function check_config() {
    param="$1"
    value="$2"
    if grep -q -E "^\s*\b${param}\b\s*=" "$ODOO_RC" ; then       
        value=$(grep -E "^\s*\b${param}\b\s*=" "$ODOO_RC" |cut -d " " -f3|sed 's/["\n\r]//g')
    fi;
    DB_ARGS+=("--${param}")
    DB_ARGS+=("${value}")
}
check_config "db_host" "$HOST"
check_config "db_port" "$PORT"
check_config "db_user" "$USER"
check_config "db_password" "$PASSWORD"

# Esperar a que PostgreSQL esté listo
wait-for-psql.py ${DB_ARGS[@]} --timeout=30

# ============================================
# WRAPPER para mantener vivo
# ============================================
DEBUGPY_ENABLE=${DEBUGPY_ENABLE:-false}
DEBUGPY_PORT=${DEBUGPY_PORT:-5678}

while true; do
    if [ "$DEBUGPY_ENABLE" = "true" ]; then
        echo "Starting Odoo with debugpy (port $DEBUGPY_PORT) - PID $$"
        # Usamos /usr/bin/odoo directamente (no -m odoo) para evitar errores de importación en workers
        python3 -m debugpy \
            --listen "0.0.0.0:$DEBUGPY_PORT" \
            /usr/bin/odoo \
            "$@" "${DB_ARGS[@]}" \
            || echo "Odoo terminated with code $?. Restarting in 1 second..."
    else
        echo "Starting Odoo without debugpy"
        odoo "$@" "${DB_ARGS[@]}" \
        || echo "Odoo terminated with code $?. Restarting in 1 second..."
    fi
    sleep 1
done