# Dockerfile لتطبيق قات
FROM python:3.13-slim

# إعداد بيئة العمل
WORKDIR /app

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# نسخ متطلبات بايثون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات التطبيق
COPY . .

# إنشاء المستخدم غير الجذري
RUN useradd -m -u 1000 qatuser && chown -R qatuser:qatuser /app
USER qatuser

# إنشاء المجلدات المطلوبة
RUN mkdir -p logs uploads

# المنفذ المكشوف
EXPOSE 5000

# أمر التشغيل
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "120", "run_server:app"]
