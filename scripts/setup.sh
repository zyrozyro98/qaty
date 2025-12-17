#!/bin/bash

# سكريبت إعداد تطبيق قات
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

# التحقق من نظام التشغيل
check_os() {
    log_info "التحقق من نظام التشغيل..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_success "نظام Linux مدعوم"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_success "نظام macOS مدعوم"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        log_error "Windows غير مدعوم حالياً"
        exit 1
    else
        log_warning "نظام غير معروف: $OSTYPE"
    fi
}

# تثبيت Python والمتطلبات
install_python() {
    log_info "تثبيت Python والمتطلبات..."
    
    # التحقق من تثبيت Python
    if ! command -v python3 &> /dev/null; then
        log_info "تثبيت Python 3..."
        
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install python3
        fi
    fi
    
    log_success "Python مثبت"
}

# إنشاء بيئة افتراضية
create_virtualenv() {
    log_info "إنشاء بيئة Python افتراضية..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "تم إنشاء البيئة الافتراضية"
    else
        log_warning "البيئة الافتراضية موجودة بالفعل"
    fi
    
    # تفعيل البيئة
    source venv/bin/activate
}

# تثبيت متطلبات Python
install_python_requirements() {
    log_info "تثبيت متطلبات Python..."
    
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log_success "تم تثبيت المتطلبات"
}

# تثبيت Docker (اختياري)
install_docker() {
    log_info "تثبيت Docker (اختياري)..."
    
    read -p "هل ترغب في تثبيت Docker؟ (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # تثبيت Docker على Ubuntu/Debian
            sudo apt-get update
            sudo apt-get install -y \
                apt-transport-https \
                ca-certificates \
                curl \
                gnupg \
                lsb-release
            
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            
            echo \
                "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
                $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io
            
            # إضافة المستخدم الحالي لمجموعة docker
            sudo usermod -aG docker $USER
            
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            # تثبيت Docker Desktop على macOS
            brew install --cask docker
        fi
        
        log_success "تم تثبيت Docker"
    else
        log_warning "تخطي تثبيت Docker"
    fi
}

# تثبيت Docker Compose
install_docker_compose() {
    log_info "تثبيت Docker Compose..."
    
    if ! command -v docker-compose &> /dev/null; then
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
                -o /usr/local/bin/docker-compose
            
            sudo chmod +x /usr/local/bin/docker-compose
            
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install docker-compose
        fi
    fi
    
    log_success "Docker Compose مثبت"
}

# إنشاء ملفات الإعدادات
create_config_files() {
    log_info "إنشاء ملفات الإعدادات..."
    
    # ملف .env
    if [ ! -f ".env" ]; then
        cp .env.example .env
        log_warning "يرجى تعديل ملف .env بإعداداتك"
    else
        log_warning "ملف .env موجود بالفعل"
    fi
    
    # إعدادات Nginx
    if [ ! -d "nginx" ]; then
        mkdir -p nginx/ssl
        cp nginx/nginx.conf.example nginx/nginx.conf 2>/dev/null || true
        log_info "تم إنشاء مجلد Nginx"
    fi
    
    # شهادات SSL (تطوير)
    if [ ! -f "nginx/ssl/cert.pem" ]; then
        log_info "إنشاء شهادات SSL للتطوير..."
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=SA/ST=Riyadh/L=Riyadh/O=QatApp/CN=localhost"
        
        log_success "تم إنشاء شهادات SSL للتطوير"
    fi
    
    # مجلدات التطبيق
    mkdir -p logs uploads static
    
    log_success "تم إنشاء ملفات الإعدادات"
}

# تهيئة قاعدة البيانات
init_database() {
    log_info "تهيئة قاعدة البيانات..."
    
    source venv/bin/activate
    python database_init.py
    
    log_success "تم تهيئة قاعدة البيانات"
}

# تشغيل الاختبارات
run_tests() {
    log_info "تشغيل الاختبارات..."
    
    source venv/bin/activate
    
    if [ -f "run_tests.py" ]; then
        python run_tests.py
    else
        log_warning "ملف الاختبارات غير موجود"
    fi
}

# عرض معلومات التثبيت
show_installation_info() {
    echo ""
    echo -e "${GREEN}✅ تم إعداد تطبيق قات بنجاح!${NC}"
    echo ""
    echo "📋 معلومات التثبيت:"
    echo "-------------------"
    echo "📁 مجلد المشروع: $(pwd)"
    echo "🐍 بيئة Python: $(which python)"
    echo "🔑 API Key: rnd_DUomOIFZV3LldOVdqsn5eQ1TmDTj"
    echo "📞 الدعم: 771831482"
    echo ""
    echo "🚀 أوامر التشغيل:"
    echo "----------------"
    echo "1. تشغيل السيرفر: python run_server.py"
    echo "2. تشغيل التطبيق: python main.py"
    echo "3. استخدام Docker: docker-compose up"
    echo "4. نشر بالإنتاج: ./scripts/deploy.sh start"
    echo ""
    echo "🔧 معلومات الدخول:"
    echo "-----------------"
    echo "المدير: admin / admin123"
    echo "البائع: seller1 / 123456"
    echo "المشتري: buyer1 / 123456"
    echo ""
    echo "📞 للدعم: 771831482"
    echo ""
}

# الوظيفة الرئيسية
main() {
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}           إعداد تطبيق قات - بيع وتوصيل القات               ${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # تنفيذ الخطوات
    check_os
    install_python
    create_virtualenv
    install_python_requirements
    install_docker
    install_docker_compose
    create_config_files
    init_database
    run_tests
    
    show_installation_info
}

# تنفيذ الوظيفة الرئيسية
main
