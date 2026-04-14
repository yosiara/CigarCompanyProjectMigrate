#!/bin/bash
# backup-odoo.sh - Backup SOLO de imágenes y volúmenes Docker
# Uso: ./backup-odoo.sh <contenedor_odoo> <contenedor_postgres> [nombre_backup]

set -euo pipefail

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Validar argumentos
if [ $# -lt 2 ]; then
    echo "Uso: $0 <contenedor_odoo> <contenedor_postgres> [nombre_backup]"
    echo ""
    echo "Ejemplos:"
    echo "  $0 odoo-18.0 odoo-db-18.0"
    echo "  $0 odoo-18.0 odoo-db-18.0 produccion"
    echo ""
    echo "Contenedores disponibles:"
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
    exit 1
fi

ODOO_CONTAINER="$1"
POSTGRES_CONTAINER="$2"
BACKUP_PREFIX="${3:-odoo-backup}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_PREFIX}_${TIMESTAMP}"

# Crear directorio de backup
mkdir -p "$BACKUP_DIR"
cd "$BACKUP_DIR"

echo "========================================"
echo "  BACKUP DOCKER ODOO - $(date)"
echo "========================================"
echo "Odoo:          $ODOO_CONTAINER"
echo "PostgreSQL:    $POSTGRES_CONTAINER"
echo "Directorio:    $BACKUP_DIR"
echo "========================================"

# ========== VALIDAR CONTENEDORES ==========
log_info "1. Validando contenedores..."

for container in "$ODOO_CONTAINER" "$POSTGRES_CONTAINER"; do
    if ! docker inspect "$container" >/dev/null 2>&1; then
        log_error "Contenedor '$container' no existe"
        exit 1
    fi
done

log_info "  ✓ Contenedores validados"

# ========== DETECTAR VOLÚMENES DOCKER (EXCLUIR BIND MOUNTS) ==========
log_info "2. Detectando volúmenes..."

get_volume() {
    docker inspect "$1" | grep -B1 -A8 '"Type": "volume"' | grep '"Name"' | cut -d'"' -f4
}

ODOO_VOLUME=$(get_volume "$ODOO_CONTAINER")
POSTGRES_VOLUME=$(get_volume "$POSTGRES_CONTAINER")

if [ -z "$ODOO_VOLUME" ] || [ -z "$POSTGRES_VOLUME" ]; then
    log_error "No se pudieron detectar volúmenes"
    exit 1
fi

log_info "  ✓ Volumen Odoo: $ODOO_VOLUME"
log_info "  ✓ Volumen PostgreSQL: $POSTGRES_VOLUME"

# ========== BACKUP IMÁGENES ==========
log_info "3. Backup de imágenes Docker..."

# Odoo
log_info "  - Creando imagen de $ODOO_CONTAINER..."
docker commit "$ODOO_CONTAINER" "odoo-backup:$TIMESTAMP"
docker save "odoo-backup:$TIMESTAMP" -o odoo-image.tar
log_info "    ✓ Tamaño: $(du -h odoo-image.tar | cut -f1)"

# PostgreSQL
log_info "  - Creando imagen de $POSTGRES_CONTAINER..."
docker commit "$POSTGRES_CONTAINER" "postgres-backup:$TIMESTAMP"
docker save "postgres-backup:$TIMESTAMP" -o postgres-image.tar
log_info "    ✓ Tamaño: $(du -h postgres-image.tar | cut -f1)"

# ========== BACKUP VOLÚMENES ==========
log_info "4. Backup de volúmenes Docker..."

# Odoo
log_info "  - Backup volumen: $ODOO_VOLUME"
docker run --rm \
    -v "$ODOO_VOLUME:/source:ro" \
    -v "$(pwd):/backup" \
    alpine \
    tar -czf /backup/odoo-volume.tar.gz -C /source .
log_info "    ✓ Tamaño: $(du -h odoo-volume.tar.gz | cut -f1)"

# PostgreSQL
log_info "  - Backup volumen: $POSTGRES_VOLUME"
docker run --rm \
    -v "$POSTGRES_VOLUME:/source:ro" \
    -v "$(pwd):/backup" \
    alpine \
    tar -czf /backup/postgres-volume.tar.gz -C /source .
log_info "    ✓ Tamaño: $(du -h postgres-volume.tar.gz | cut -f1)"

# ========== CREAR ARCHIVO ÚNICO ==========
log_info "5. Creando paquete final..."

cd ..
tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
BACKUP_SIZE=$(du -h "${BACKUP_DIR}.tar.gz" | cut -f1)

# ========== LIMPIAR ==========
log_info "6. Limpiando temporales..."

# Eliminar directorio temporal
rm -rf "$BACKUP_DIR"

# Eliminar imágenes temporales
docker rmi "odoo-backup:$TIMESTAMP" "postgres-backup:$TIMESTAMP" 2>/dev/null || true

# ========== RESUMEN ==========
echo ""
echo "========================================"
echo "  ✅ BACKUP COMPLETADO"
echo "========================================"
echo "Archivo:   ${BACKUP_DIR}.tar.gz"
echo "Tamaño:    $BACKUP_SIZE"
echo ""
echo "CONTENIDO:"
echo "  📦 ${BACKUP_DIR}.tar.gz"
echo "    ├── 📷 odoo-image.tar          (Imagen Odoo)"
echo "    ├── 📷 postgres-image.tar      (Imagen PostgreSQL)"
echo "    ├── 💾 odoo-volume.tar.gz      (Volumen Odoo)"
echo "    └── 💾 postgres-volume.tar.gz  (Volumen PostgreSQL)"
echo ""
echo "PARA RESTAURAR:"
echo "  ./restore-odoo.sh ${BACKUP_DIR}.tar.gz"
echo ""
echo "========================================"
