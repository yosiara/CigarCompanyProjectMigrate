#!/bin/bash
# restore-odoo.sh - Restaura SOLO imágenes y volúmenes Docker
# Uso: ./restore-odoo.sh <backup.tar.gz> [volumen_odoo] [volumen_postgres] 

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
if [ $# -lt 1 ]; then
    echo "Uso: $0 <backup.tar.gz> [volumen_odoo] [volumen_postgres]"
    echo ""
    echo "Ejemplo:"
    echo "  $0 backup.tar.gz mi_odoo_volume mi_postgres_volume"
    echo ""
    echo "Archivos disponibles:"
    ls -la *.tar.gz 2>/dev/null || echo "No hay archivos .tar.gz"
    exit 1
fi

BACKUP_FILE="$1"
ODOO_VOLUME="${2:-odoo_volume}"
POSTGRES_VOLUME="${3:-postgres_volume}"

# Validar archivo
if [ ! -f "$BACKUP_FILE" ]; then
    log_error "Archivo '$BACKUP_FILE' no encontrado"
    exit 1
fi

# Extraer nombre base
BACKUP_BASENAME=$(basename "$BACKUP_FILE" .tar.gz)
RESTORE_DIR="restore_${BACKUP_BASENAME}"

echo "========================================"
echo "  RESTAURACIÓN DATOS ODOO - $(date)"
echo "========================================"
echo "Backup:             $BACKUP_FILE"
echo "Volumen Odoo:       $ODOO_VOLUME"
echo "Volumen PostgreSQL: $POSTGRES_VOLUME"
echo "Directorio:         $RESTORE_DIR"
echo "========================================"

# ========== EXTRAER BACKUP ========== #
log_info "1. Extrayendo backup..."
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR" --strip-components=1

cd "$RESTORE_DIR"

# Validar archivos esenciales
if [ ! -f "postgres-volume.tar.gz" ] || [ ! -f "odoo-volume.tar.gz" ]; then
    log_error "Archivos de volumen no encontrados en el backup"
    echo "Contenido del backup:"
    ls -la
    exit 1
fi

# Opcional: validar imágenes
if [ -f "odoo-image.tar" ] && [ -f "postgres-image.tar" ]; then
    log_info "  ✓ Imágenes Docker incluidas en backup"
    HAS_IMAGES=true
else
    log_warn "  ⚠️  No se encontraron imágenes Docker en el backup"
    HAS_IMAGES=false
fi

# ========== OPCIONAL: CARGAR IMÁGENES ========== #
if [ "$HAS_IMAGES" = true ]; then
    log_info "2. Cargando imágenes Docker (opcional)..."
    
    log_info "  - Cargando imagen Odoo..."
    docker load -i odoo-image.tar
    ODOO_IMAGE=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "odoo-backup" | head -1)
    
    log_info "  - Cargando imagen PostgreSQL..."
    docker load -i postgres-image.tar
    POSTGRES_IMAGE=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "postgres-backup" | head -1)
    
    log_info "  ✓ Imágenes cargadas"
else
    log_info "2. Saltando carga de imágenes..."
fi

# ========== CREAR VOLÚMENES ========== #
log_info "3. Creando/preparando volúmenes Docker..."

# Odoo
log_info "  - Volumen Odoo: $ODOO_VOLUME"
if docker volume inspect "$ODOO_VOLUME" >/dev/null 2>&1; then
    log_warn "    ⚠️  Volumen ya existe"
    read -p "    ¿Sobrescribir? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        log_info "    Saltando Odoo..."
        SKIP_ODOO=true
    else
        log_info "    Limpiando volumen existente..."
        docker run --rm -v "$ODOO_VOLUME:/target" alpine sh -c "rm -rf /target/*"
        SKIP_ODOO=false
    fi
else
    docker volume create "$ODOO_VOLUME"
    SKIP_ODOO=false
fi

# PostgreSQL
log_info "  - Volumen PostgreSQL: $POSTGRES_VOLUME"
if docker volume inspect "$POSTGRES_VOLUME" >/dev/null 2>&1; then
    log_warn "    ⚠️  Volumen ya existe"
    read -p "    ¿Sobrescribir? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        log_info "    Saltando PostgreSQL..."
        SKIP_POSTGRES=true
    else
        log_info "    Limpiando volumen existente..."
        docker run --rm -v "$POSTGRES_VOLUME:/target" alpine sh -c "rm -rf /target/*"
        SKIP_POSTGRES=false
    fi
else
    docker volume create "$POSTGRES_VOLUME"
    SKIP_POSTGRES=false
fi

# ========== RESTAURAR VOLÚMENES ========== #
log_info "4. Restaurando datos en volúmenes..."

# Odoo
if [ "$SKIP_ODOO" = false ]; then
    log_info "  - Restaurando Odoo en volumen: $ODOO_VOLUME"
    docker run --rm \
        -v "$ODOO_VOLUME:/target" \
        -v "$(pwd):/backup" \
        alpine \
        tar -xzf /backup/odoo-volume.tar.gz -C /target
    
    # Verificar restauración
    FILE_COUNT=$(docker run --rm -v "$ODOO_VOLUME:/data" alpine sh -c "find /data -type f | wc -l")
    log_info "    ✓ Restaurado: $FILE_COUNT archivos"
else
    log_info "  - ⏭️  Saltando Odoo (volumen existente preservado)"
fi

# PostgreSQL
if [ "$SKIP_POSTGRES" = false ]; then
    log_info "  - Restaurando PostgreSQL en volumen: $POSTGRES_VOLUME"
    docker run --rm \
        -v "$POSTGRES_VOLUME:/target" \
        -v "$(pwd):/backup" \
        alpine \
        tar -xzf /backup/postgres-volume.tar.gz -C /target
    
    # Verificar restauración
    FILE_COUNT=$(docker run --rm -v "$POSTGRES_VOLUME:/data" alpine sh -c "find /data -type f | wc -l")
    log_info "    ✓ Restaurado: $FILE_COUNT archivos"
else
    log_info "  - ⏭️  Saltando PostgreSQL (volumen existente preservado)"
fi

# ========== LIMPIAR ========== #
log_info "5. Limpiando temporal..."
cd ..
rm -rf "$RESTORE_DIR"

# ========== RESUMEN FINAL ========== #
echo ""
echo "========================================"
echo "  ✅ RESTAURACIÓN DE DATOS COMPLETADA"
echo "========================================"
echo "Volúmenes Docker listos:"
echo ""
echo "Odoo:"
echo "  Nombre: $ODOO_VOLUME"
echo "  Estado: $(if [ "$SKIP_ODOO" = false ]; then echo "✅ Restaurado"; else echo "⏭️  Preservado"; fi)"
docker volume inspect "$ODOO_VOLUME" --format '  Driver: {{.Driver}}  Ruta: {{.Mountpoint}}' 2>/dev/null || echo "  ❌ No disponible"
echo ""
echo "PostgreSQL:"
echo "  Nombre: $POSTGRES_VOLUME"
echo "  Estado: $(if [ "$SKIP_POSTGRES" = false ]; then echo "✅ Restaurado"; else echo "⏭️  Preservado"; fi)"
docker volume inspect "$POSTGRES_VOLUME" --format '  Driver: {{.Driver}}  Ruta: {{.Mountpoint}}' 2>/dev/null || echo "  ❌ No disponible"
echo ""

if [ "$HAS_IMAGES" = true ]; then
    echo "Imágenes Docker listas:"
    echo ""
    docker images | grep -E "(odoo-backup|postgres-backup)"
    echo ""
fi

log_info "✅ Proceso completado"