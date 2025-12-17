#!/usr/bin/env python3
"""
تشغيل سيرفر API
"""
import os
from app import create_app
from app.config import Config

# إنشاء التطبيق
app = create_app(Config)

@app.route('/')
def index():
    return {
        'success': True,
        'message': 'مرحباً بك في تطبيق قات API',
        'version': '1.0.0',
        'support': '771831482'
    }

@app.route('/health')
def health():
    return {
        'success': True,
        'status': 'healthy',
        'timestamp': '2024-01-01T00:00:00Z'
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 تشغيل سيرفر تطبيق قات...")
    print(f"🌐 العنوان: http://0.0.0.0:{port}")
    print(f"🔧 الوضع: {'تطوير' if debug else 'إنتاج'}")
    print(f"🔑 API Key: {Config.API_KEY}")
    print(f"📞 الدعم: {Config.SUPPORT_PHONE}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
