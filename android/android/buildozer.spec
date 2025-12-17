[app]

# عنوان التطبيق
title = تطبيق قات

# اسم الحزمة (يجب أن يكون فريداً)
package.name = com.qatapp.qat

# اسم المجال
package.domain = com.qatapp

# مصدر التطبيق
source.dir = .

# دالة التشغيل الرئيسية
source.main = main.py

# إصدار التطبيق
version = 1.0.0

# متطلبات بايثون
requirements = python3,kivy==2.3.0,kivymd==1.1.1,Pillow,requests,plyer,android

# اسم APK الناتج
fullname = QatApp

# إعدادات النظام
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.3.0

# صلاحيات الاندرويد
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,WAKE_LOCK,VIBRATE

# ميزات الاندرويد
android.features = android.hardware.location, android.hardware.location.gps

# إصدارات SDK
android.api = 31
android.minapi = 21
android.sdk = 24
android.ndk = 23b
android.ndk_api = 21

# إعدادات البناء
android.arch = arm64-v8a, armeabi-v7a
p4a.branch = develop
android.accept_sdk_license = True

# إعدادات التوقيع (تغييرها لبياناتك)
android.keystore = qat.keystore
android.keystorepass = qat123456
android.keyalias = qatalias
android.keyaliaspass = qat123456

# لغات التطبيق
android.allow_backup = True
android.default_language = ar
android.local_props = True

# إعدادات التصميم
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-3940256099942544~3347511713
android.gradle_dependencies = 'com.google.android.gms:play-services-ads:22.4.0'

# مكتبات C
android.add_libs_armeabi_v7a = libs/armeabi-v7a/*.so
android.add_libs_arm64_v8a = libs/arm64-v8a/*.so
android.add_libs_x86 = libs/x86/*.so
android.add_libs_x86_64 = libs/x86_64/*.so

# مخرجات التطبيق
android.wakelock = True
android.manifest.intent_filters = android.intent.action.MAIN+android.intent.category.LAUNCHER

# إعدادات التطبيق
presplash.filename = %(source.dir)s/app/assets/images/splash.png
icon.filename = %(source.dir)s/app/assets/images/icon.png
icon.adaptive_foreground.filename = %(source.dir)s/app/assets/images/adaptive-icon.png
icon.adaptive_background.filename = %(source.dir)s/app/assets/images/adaptive-background.png

# اللغات المدعومة
android.manifest.placeholders = [['android:usesCleartextTraffic', 'true']]
android.manifest.placeholders += [['android:requestLegacyExternalStorage', 'true']]
android.manifest.placeholders += [['android:largeHeap', 'true']]

# تحسين الأداء
android.manifest.placeholders += [['android:hardwareAccelerated', 'true']]
android.manifest.placeholders += [['android:supportsRtl', 'true']]
android.manifest.placeholders += [['android:allowBackup', 'true']]
android.manifest.placeholders += [['android:fullBackupContent', '@xml/backup_rules']]

# مكتبات بايثون الإضافية
android.add_src = 

# الحجم النهائي
android.no-compress-png = True

[buildozer]

# إعدادات Buildozer
log_level = 2
warn_on_root = 1
build_dir = .buildozer
bin_dir = .bin
