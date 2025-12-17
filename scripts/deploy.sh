#!/bin/bash

# سكريبت نشر تطبيق قات
set -e

# الألوان للطرفية
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# وظائف مساعدة
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

# التحقق من وجود Docker و Docker Compose
check_dependencies() {
    log_info "التحقق من التبعيات..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker غير مثبت!"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose غير مثبت!"
        exit 1
    fi
    
    log_success "جميع التبعيات مثبتة"
}

# إنشاء ملف .env إذا لم يكن موجوداً
create_env_file() {
    if [ ! -f .env ]; then
        log_info "إنشاء ملف .env من القالب..."
        cp .env.example .env
        log_warning "يرجى تعديل ملف .env بإعداداتك"
        exit 1
    fi
    
    log_success "ملف .env موجود"
}

# تحميل متغيرات البيئة
load_env() {
    log_info "تحميل متغيرات البيئة..."
    
    if [ -f .env ]; then
        set -a
        source .env
        set +a
    fi
    
    # القيم الافتراضية
    export APP_ENV=${APP_ENV:-production}
    export DB_PASSWORD=${DB_PASSWORD:-qat_password123}
    export SECRET_KEY=${SECRET_KEY:-rnd_DUomOIFZV3LldOVdqsn5eQ1TmDTj}
    export API_KEY=${API_KEY:-rnd_DUomOIFZV3LldOVdqsn5eQ1TmDTj}
    
    log_success "تم تحميل متغيرات البيئة"
}

# بناء الصور
build_images() {
    log_info "بناء صور Docker..."
    docker-compose build
    log_success "تم بناء الصور"
}

# تشغيل التطبيق
start_application() {
    log_info "تشغيل التطبيق..."
   
