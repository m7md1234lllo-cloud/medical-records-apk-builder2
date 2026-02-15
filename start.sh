#!/bin/bash

# نظام إدارة الملفات الطبية
# Medical Records Management System Launcher

echo "========================================="
echo "🏥 نظام إدارة الملفات الطبية"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python غير مثبت!"
    echo "قم بتثبيته باستخدام: pkg install python"
    exit 1
fi

echo "✅ Python مثبت"

# Check if Flask is installed
if ! python -c "import flask" &> /dev/null; then
    echo "📦 تثبيت المكتبات المطلوبة..."
    pip install -r requirements.txt
fi

echo "✅ جميع المكتبات مثبتة"
echo ""

# Get IP address
IP=$(ifconfig 2>/dev/null | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -1)

echo "========================================="
echo "🚀 بدء التشغيل..."
echo "========================================="
echo ""
echo "📱 افتح المتصفح واذهب إلى:"
echo "   http://localhost:5000"
echo ""

if [ ! -z "$IP" ]; then
    echo "🌐 أو من أي جهاز على نفس الشبكة:"
    echo "   http://$IP:5000"
    echo ""
fi

echo "⏹️  لإيقاف التطبيق اضغط Ctrl+C"
echo "========================================="
echo ""

# Start the app
python app.py
