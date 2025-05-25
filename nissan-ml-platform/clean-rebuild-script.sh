#!/bin/bash
# Script de limpieza y reconstrucción para resolver problemas de dependencias
# Autor: Sistema de ML Nissan
# Este script limpia completamente el entorno y reconstruye con configuraciones optimizadas

set -e  # Salir si hay errores
set -u  # Error si se usan variables no definidas

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con formato
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    log_error "No se encontró docker-compose.yml. Asegúrate de ejecutar este script desde la raíz del proyecto."
    exit 1
fi

log_info "Iniciando proceso de limpieza y reconstrucción..."

# Paso 1: Detener y eliminar contenedores existentes
log_info "Deteniendo contenedores existentes..."
docker-compose down -v 2>/dev/null || log_warning "No había contenedores ejecutándose"

# Paso 2: Eliminar imágenes del proyecto
log_info "Eliminando imágenes Docker del proyecto..."
docker images | grep "nissan-ml-platform" | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || log_warning "No se encontraron imágenes para eliminar"

# Paso 3: Limpiar volúmenes no utilizados
log_info "Limpiando volúmenes Docker no utilizados..."
docker volume prune -f

# Paso 4: Limpiar cache de Docker
log_info "Limpiando cache de Docker build..."
docker builder prune -f

# Paso 5: Limpiar node_modules y archivos de cache del frontend
log_info "Limpiando archivos de cache del frontend..."
if [ -d "frontend/node_modules" ]; then
    rm -rf frontend/node_modules
    log_success "node_modules del frontend eliminado"
fi

if [ -f "frontend/package-lock.json" ]; then
    rm -f frontend/package-lock.json
    log_success "package-lock.json eliminado"
fi

if [ -f "frontend/.eslintcache" ]; then
    rm -f frontend/.eslintcache
fi

# Paso 6: Actualizar archivos según las correcciones
log_info "Verificando actualizaciones de archivos..."

# Crear backup del Dockerfile original si no existe
if [ ! -f "frontend/Dockerfile.backup" ]; then
    cp frontend/Dockerfile frontend/Dockerfile.backup
    log_info "Backup del Dockerfile original creado"
fi

# Crear backup del package.json original si no existe
if [ ! -f "frontend/package.json.backup" ]; then
    cp frontend/package.json frontend/package.json.backup
    log_info "Backup del package.json original creado"
fi

# Paso 7: Crear archivo .dockerignore optimizado si no existe
if [ ! -f "frontend/.dockerignore" ]; then
    cat > frontend/.dockerignore << EOF
node_modules
npm-debug.log
build
.dockerignore
.git
.gitignore
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
coverage
.eslintcache
.DS_Store
*.log
EOF
    log_success "Archivo .dockerignore creado"
fi

# Paso 8: Reconstruir con Docker Compose
log_info "Iniciando reconstrucción con Docker Compose..."

# Usar build sin cache para asegurar limpieza completa
docker-compose build --no-cache --progress=plain

if [ $? -eq 0 ]; then
    log_success "¡Build completado exitosamente!"
    
    # Paso 9: Iniciar servicios
    log_info "Iniciando servicios..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        log_success "¡Servicios iniciados correctamente!"
        
        # Mostrar estado de los servicios
        echo -e "\n${GREEN}Estado de los servicios:${NC}"
        docker-compose ps
        
        echo -e "\n${GREEN}URLs de acceso:${NC}"
        echo -e "  Frontend: ${BLUE}http://localhost:3000${NC}"
        echo -e "  Backend API: ${BLUE}http://localhost:8000/api/v1/docs${NC}"
        echo -e "  PostgreSQL: ${BLUE}localhost:5432${NC}"
        echo -e "  Redis: ${BLUE}localhost:6379${NC}"
        
        # Mostrar logs del frontend para verificar
        echo -e "\n${YELLOW}Mostrando logs del frontend (Ctrl+C para salir):${NC}"
        sleep 3
        docker-compose logs -f frontend
    else
        log_error "Error al iniciar los servicios"
        exit 1
    fi
else
    log_error "Error durante el build. Revisa los logs anteriores."
    
    # Intentar build solo del backend para verificar si el problema es solo del frontend
    log_info "Intentando construir solo el backend para diagnóstico..."
    docker-compose build backend worker
    
    if [ $? -eq 0 ]; then
        log_warning "El backend se construyó correctamente. El problema está aislado al frontend."
        log_info "Por favor, verifica que hayas actualizado los archivos:"
        echo "  1. frontend/Dockerfile"
        echo "  2. frontend/package.json"
        echo "  3. frontend/nginx.conf (opcional)"
    fi
    
    exit 1
fi