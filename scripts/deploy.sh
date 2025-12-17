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
    export SECRET_KEY=${SECRET_KEY:-https://api.render.com/deploy/srv-d47p01e3jp1c73c5mb70?key=sdQH2xXNa_M}
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
    docker-compose up -d
    log_success "تم تشغيل التطبيق"
}

# إيقاف التطبيق
stop_application() {
    log_info "إيقاف التطبيق..."
    docker-compose down
    log_success "تم إيقاف التطبيق"
}

# إعادة تشغيل التطبيق
restart_application() {
    log_info "إعادة تشغيل التطبيق..."
    docker-compose restart
    log_success "تم إعادة تشغيل التطبيق"
}

# عرض السجلات
show_logs() {
    log_info "عرض السجلات..."
    docker-compose logs -f
}

# نسخ احتياطي للقاعدة
backup_database() {
    local backup_dir="backups"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${backup_dir}/backup_${timestamp}.sql"
    
    log_info "إنشاء نسخة احتياطية من قاعدة البيانات..."
    
    mkdir -p "$backup_dir"
    
    docker-compose exec db pg_dump -U qat_user qat_app > "$backfile"
    
    if [ $? -eq 0 ]; then
        log_success "تم إنشاء النسخة الاحتياطية: $backup_file"
        
        # حذف النسخ القديمة (احتفظ بـ 7 أيام فقط)
        find "$backup_dir" -name "backup_*.sql" -mtime +7 -delete
    else
        log_error "فشل إنشاء النسخة الاحتياطية"
        exit 1
    fi
}

# استعادة قاعدة البيانات
restore_database() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_error "يرجى تحديد ملف النسخة الاحتياطية"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "ملف النسخة الاحتياطية غير موجود: $backup_file"
        exit 1
    fi
    
    log_info "استعادة قاعدة البيانات من: $backup_file"
    
    # إيقاف التطبيق
    stop_application
    
    # بدء قاعدة البيانات فقط
    docker-compose up -d db
    
    # الانتظار حتى تكون قاعدة البيانات جاهزة
    sleep 10
    
    # استعادة النسخة الاحتياطية
    docker-compose exec -T db psql -U qat_user -d qat_app < "$backup_file"
    
    if [ $? -eq 0 ]; then
        log_success "تم استعادة قاعدة البيانات"
        
        # إعادة تشغيل التطبيق
        start_application
    else
        log_error "فشل استعادة قاعدة البيانات"
        exit 1
    fi
}

# فحص الصحة
health_check() {
    log_info "فحص صحة التطبيق..."
    
    # فحص API
    if curl -s http://localhost:5000/health | grep -q "healthy"; then
        log_success "API يعمل بشكل صحيح"
    else
        log_error "API لا يستجيب"
        exit 1
    fi
    
    # فحص قاعدة البيانات
    if docker-compose exec db pg_isready -U qat_user; then
        log_success "قاعدة البيانات تعمل بشكل صحيح"
    else
        log_error "قاعدة البيانات لا تستجيب"
        exit 1
    fi
    
    log_success "جميع الخدمات تعمل بشكل صحيح"
}

# تحديث التطبيق
update_application() {
    log_info "تحديث التطبيق..."
    
    # سحب التحديثات
    git pull
    
    # إعادة بناء الصور
    build_images
    
    # إعادة تشغيل التطبيق
    restart_application
    
    # فحص الصحة
    health_check
    
    log_success "تم تحديث التطبيق"
}

# عرض المساعدة
show_help() {
    echo -e "${BLUE}سكريبت نشر تطبيق قات${NC}"
    echo ""
    echo "الاستخدام: ./deploy.sh [COMMAND]"
    echo ""
    echo "الأوامر:"
    echo "  start        تشغيل التطبيق"
    echo "  stop         إيقاف التطبيق"
    echo "  restart      إعادة تشغيل التطبيق"
    echo "  logs         عرض السجلات"
    echo "  backup       إنشاء نسخة احتياطية من قاعدة البيانات"
    echo "  restore FILE استعادة قاعدة البيانات من ملف"
    echo "  health       فحص صحة التطبيق"
    echo "  update       تحديث التطبيق"
    echo "  help         عرض هذه المساعدة"
    echo ""
    echo "الأمثلة:"
    echo "  ./deploy.sh start"
    echo "  ./deploy.sh backup"
    echo "  ./deploy.sh restore backups/backup_20240101_120000.sql"
    echo ""
}

# التحقق من الأمر
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

# تنفيذ الأمر
case $1 in
    start)
        check_dependencies
        create_env_file
        load_env
        start_application
        health_check
        ;;
    stop)
        stop_application
        ;;
    restart)
        restart_application
        ;;
    logs)
        show_logs
        ;;
    backup)
        backup_database
        ;;
    restore)
        if [ -z "$2" ]; then
            log_error "يرجى تحديد ملف النسخة الاحتياطية"
            exit 1
        fi
        restore_database "$2"
        ;;
    health)
        health_check
        ;;
    update)
        update_application
        ;;
    help)
        show_help
        ;;
    *)
        log_error "أمر غير معروف: $1"
        show_help
        exit 1
        ;;
esac
