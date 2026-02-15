[app]

# نظام إدارة الملفات الطبية
title = Medical Records
package.name = medicalrecords
package.domain = org.clinic

# Source code
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,html,css,js,md

# Version
version = 1.0.0

# Requirements
requirements = python3,flask,werkzeug,kivy,sqlite3,jnius,android

# Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WAKE_LOCK

# Android API
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31

# Orientation
orientation = portrait

# Icon (optional - will use default if not provided)
#icon.filename = %(source.dir)s/icon.png

# Presplash (optional)
#presplash.filename = %(source.dir)s/presplash.png

# Android arch
android.archs = arm64-v8a,armeabi-v7a

# Services
services = flask_service:service.py

# Copy files
android.add_src = ../app.py,../templates,../static,../requirements.txt

# Gradle dependencies
android.gradle_dependencies = 

# Android app theme
android.apptheme = "@android:style/Theme.NoTitleBar"

# Allow backup
android.allow_backup = True

[buildozer]

# Log level
log_level = 2

# Display warning if buildozer is run as root
warn_on_root = 1

# Build directory
build_dir = ./.buildozer

# Bin directory
bin_dir = ./bin
