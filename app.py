#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة الملفات الطبية الإلكترونية
Medical Records Management System
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'medical-records-2024'

# Database setup
DATABASE = 'medical_records.db'

def get_db():
    """إنشاء اتصال بقاعدة البيانات"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """إنشاء جداول قاعدة البيانات"""
    conn = get_db()
    cursor = conn.cursor()
    
    # حذف الجدول القديم إذا كان موجوداً وإعادة إنشائه
    # هذا يحل مشكلة الأعمدة الناقصة
    try:
        # التحقق من وجود الجدول القديم
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patients'")
        if cursor.fetchone():
            # الجدول موجود، نتحقق من الأعمدة
            cursor.execute("PRAGMA table_info(patients)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # إذا كانت الأعمدة ناقصة، نعيد إنشاء الجدول
            required_columns = ['email', 'national_id', 'blood_type', 'allergies']
            if not all(col in columns for col in required_columns):
                print("تحديث جدول المرضى...")
                # نسخ البيانات القديمة
                cursor.execute('''
                    CREATE TABLE patients_backup AS 
                    SELECT * FROM patients
                ''')
                # حذف الجدول القديم
                cursor.execute('DROP TABLE patients')
    except:
        pass
    
    # جدول المرضى - موسع بمعلومات طبية
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            phone TEXT,
            address TEXT,
            email TEXT,
            national_id TEXT,
            blood_type TEXT,
            allergies TEXT,
            chronic_diseases TEXT,
            current_medications TEXT,
            emergency_contact TEXT,
            emergency_phone TEXT,
            insurance_company TEXT,
            insurance_number TEXT,
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # استعادة البيانات القديمة إذا كانت موجودة
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patients_backup'")
        if cursor.fetchone():
            cursor.execute('''
                INSERT INTO patients (id, name, age, gender, phone, address, created_date)
                SELECT id, name, age, gender, phone, address, created_date
                FROM patients_backup
            ''')
            cursor.execute('DROP TABLE patients_backup')
            print("تم استعادة البيانات القديمة بنجاح!")
    except:
        pass
    
    
    # جدول الأطباء
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT,
            phone TEXT,
            email TEXT,
            license_number TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول ربط الزيارات بالأطباء (Many-to-Many)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visit_doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visit_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            role TEXT DEFAULT 'مشارك',
            is_primary INTEGER DEFAULT 0,
            notes TEXT,
            FOREIGN KEY (visit_id) REFERENCES visits (id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES doctors (id),
            UNIQUE(visit_id, doctor_id)
        )
    ''')
    
    # جدول إعدادات العيادة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clinic_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            clinic_name TEXT DEFAULT 'العيادة الطبية',
            clinic_address TEXT,
            clinic_phone TEXT,
            clinic_email TEXT,
            header_text TEXT DEFAULT 'عيادة طبية متخصصة',
            footer_text TEXT DEFAULT 'نتمنى لكم دوام الصحة والعافية',
            logo_path TEXT
        )
    ''')
    
    # إضافة إعدادات افتراضية إذا لم تكن موجودة
    cursor.execute('INSERT OR IGNORE INTO clinic_settings (id) VALUES (1)')
    
    # التحقق من جدول الزيارات وتحديثه
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='visits'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(visits)")
            columns = [col[1] for col in cursor.fetchall()]
            
            required_columns = ['symptoms', 'vital_signs', 'prescriptions', 'lab_tests', 'doctor_id']
            if not all(col in columns for col in required_columns):
                print("تحديث جدول الزيارات...")
                cursor.execute('CREATE TABLE visits_backup AS SELECT * FROM visits')
                cursor.execute('DROP TABLE visits')
    except:
        pass
    
    # جدول الزيارات الطبية
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER,
            visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            diagnosis TEXT,
            symptoms TEXT,
            treatment TEXT,
            prescriptions TEXT,
            lab_tests TEXT,
            vital_signs TEXT,
            notes TEXT,
            total_cost REAL DEFAULT 0,
            paid_amount REAL DEFAULT 0,
            next_visit_date TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (id)
        )
    ''')
    
    # استعادة بيانات الزيارات القديمة
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='visits_backup'")
        if cursor.fetchone():
            cursor.execute('''
                INSERT INTO visits (id, patient_id, visit_date, diagnosis, treatment, 
                                  notes, total_cost, paid_amount)
                SELECT id, patient_id, visit_date, diagnosis, treatment, 
                       notes, total_cost, paid_amount
                FROM visits_backup
            ''')
            cursor.execute('DROP TABLE visits_backup')
            print("تم استعادة بيانات الزيارات بنجاح!")
    except:
        pass
    
    # جدول المواعيد
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'مجدول',
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
    ''')
    
    # جدول المدفوعات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visit_id INTEGER NOT NULL,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            amount REAL NOT NULL,
            payment_method TEXT,
            notes TEXT,
            FOREIGN KEY (visit_id) REFERENCES visits (id)
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')

@app.route('/patients')
def patients_list():
    """قائمة المرضى"""
    conn = get_db()
    cursor = conn.cursor()
    
    # جلب جميع المرضى مع معلومات الديون
    cursor.execute('''
        SELECT p.*, 
               COALESCE(SUM(v.total_cost), 0) as total_charges,
               COALESCE(SUM(v.paid_amount), 0) as total_paid,
               COALESCE(SUM(v.total_cost - v.paid_amount), 0) as total_debt
        FROM patients p
        LEFT JOIN visits v ON p.id = v.patient_id
        GROUP BY p.id
        ORDER BY p.created_date DESC
    ''')
    
    patients = cursor.fetchall()
    conn.close()
    
    return render_template('patients.html', patients=patients)

@app.route('/patient/new', methods=['GET', 'POST'])
def new_patient():
    """إضافة مريض جديد"""
    if request.method == 'POST':
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO patients (
                name, age, gender, phone, address, email, national_id,
                blood_type, allergies, chronic_diseases, current_medications,
                emergency_contact, emergency_phone, insurance_company, 
                insurance_number, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'], 
            data.get('age'), 
            data.get('gender'), 
            data.get('phone'), 
            data.get('address'),
            data.get('email'),
            data.get('national_id'),
            data.get('blood_type'),
            data.get('allergies'),
            data.get('chronic_diseases'),
            data.get('current_medications'),
            data.get('emergency_contact'),
            data.get('emergency_phone'),
            data.get('insurance_company'),
            data.get('insurance_number'),
            data.get('notes')
        ))
        
        patient_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'patient_id': patient_id})
    
    return render_template('new_patient.html')

@app.route('/patient/<int:patient_id>')
def patient_details(patient_id):
    """تفاصيل المريض"""
    conn = get_db()
    cursor = conn.cursor()
    
    # بيانات المريض
    cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
    patient = cursor.fetchone()
    
    if not patient:
        conn.close()
        return "المريض غير موجود", 404
    
    # زيارات المريض
    cursor.execute('''
        SELECT v.*, 
               (v.total_cost - v.paid_amount) as remaining_debt
        FROM visits v
        WHERE v.patient_id = ?
        ORDER BY v.visit_date DESC
    ''', (patient_id,))
    
    visits = cursor.fetchall()
    
    # إجمالي الديون
    cursor.execute('''
        SELECT 
            COALESCE(SUM(total_cost), 0) as total_charges,
            COALESCE(SUM(paid_amount), 0) as total_paid,
            COALESCE(SUM(total_cost - paid_amount), 0) as total_debt
        FROM visits
        WHERE patient_id = ?
    ''', (patient_id,))
    
    summary = cursor.fetchone()
    conn.close()
    
    return render_template('patient_details.html', 
                         patient=patient, 
                         visits=visits,
                         summary=summary)

@app.route('/visit/new/<int:patient_id>', methods=['GET', 'POST'])
def new_visit(patient_id):
    """إضافة زيارة طبية جديدة"""
    if request.method == 'POST':
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.cursor()
        
        # إضافة الزيارة
        cursor.execute('''
            INSERT INTO visits (
                patient_id, doctor_id, diagnosis, symptoms, treatment, prescriptions,
                lab_tests, vital_signs, notes, total_cost, paid_amount, next_visit_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            patient_id,
            data.get('doctor_id'),  # الطبيب الرئيسي (للتوافق مع النظام القديم)
            data.get('diagnosis'), 
            data.get('symptoms'),
            data.get('treatment'),
            data.get('prescriptions'),
            data.get('lab_tests'),
            data.get('vital_signs'),
            data.get('notes'), 
            float(data.get('total_cost', 0)),
            float(data.get('paid_amount', 0)),
            data.get('next_visit_date')
        ))
        
        visit_id = cursor.lastrowid
        
        # إضافة الأطباء المشاركين
        primary_doctor_id = data.get('doctor_id')
        participating_doctors = data.get('participating_doctors', [])
        
        # إضافة الطبيب الرئيسي
        if primary_doctor_id:
            cursor.execute('''
                INSERT INTO visit_doctors (visit_id, doctor_id, role, is_primary)
                VALUES (?, ?, ?, ?)
            ''', (visit_id, primary_doctor_id, 'طبيب رئيسي', 1))
        
        # إضافة الأطباء المشاركين
        for doc in participating_doctors:
            if doc.get('doctor_id') and doc['doctor_id'] != primary_doctor_id:
                cursor.execute('''
                    INSERT INTO visit_doctors (visit_id, doctor_id, role, is_primary, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (visit_id, doc['doctor_id'], doc.get('role', 'طبيب مشارك'), 0, doc.get('notes')))
        
        # إذا في دفعة، سجلها في جدول المدفوعات
        if float(data.get('paid_amount', 0)) > 0:
            cursor.execute('''
                INSERT INTO payments (visit_id, amount, payment_method, notes)
                VALUES (?, ?, ?, ?)
            ''', (visit_id, float(data['paid_amount']), 
                  data.get('payment_method', 'نقدي'), 
                  'دفعة أولية'))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'visit_id': visit_id})
    
    conn = get_db()
    cursor = conn.cursor()
    
    # بيانات المريض
    cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
    patient = cursor.fetchone()
    
    # قائمة الأطباء
    cursor.execute('SELECT * FROM doctors ORDER BY name')
    doctors = cursor.fetchall()
    
    conn.close()
    
    if not patient:
        return "المريض غير موجود", 404
    
    return render_template('new_visit.html', patient=patient, doctors=doctors)

@app.route('/payment/add/<int:visit_id>', methods=['POST'])
def add_payment(visit_id):
    """إضافة دفعة جديدة"""
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # إضافة الدفعة
    cursor.execute('''
        INSERT INTO payments (visit_id, amount, payment_method, notes)
        VALUES (?, ?, ?, ?)
    ''', (visit_id, float(data['amount']), 
          data.get('payment_method', 'نقدي'),
          data.get('notes', '')))
    
    # تحديث المبلغ المدفوع في الزيارة
    cursor.execute('''
        UPDATE visits
        SET paid_amount = paid_amount + ?
        WHERE id = ?
    ''', (float(data['amount']), visit_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/search')
def search():
    """البحث عن المرضى"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify([])
    
    conn = get_db()
    cursor = conn.cursor()
    
    # البحث في حقول متعددة
    cursor.execute('''
        SELECT p.*, 
               COALESCE(SUM(v.total_cost - v.paid_amount), 0) as total_debt
        FROM patients p
        LEFT JOIN visits v ON p.id = v.patient_id
        WHERE p.name LIKE ? 
           OR p.phone LIKE ? 
           OR p.national_id LIKE ?
           OR p.email LIKE ?
        GROUP BY p.id
        ORDER BY p.name
        LIMIT 20
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    
    results = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in results])

@app.route('/reports')
def reports():
    """التقارير المالية"""
    conn = get_db()
    cursor = conn.cursor()
    
    # إحصائيات عامة
    cursor.execute('''
        SELECT 
            COUNT(DISTINCT p.id) as total_patients,
            COUNT(v.id) as total_visits,
            COALESCE(SUM(v.total_cost), 0) as total_revenue,
            COALESCE(SUM(v.paid_amount), 0) as total_collected,
            COALESCE(SUM(v.total_cost - v.paid_amount), 0) as total_outstanding
        FROM patients p
        LEFT JOIN visits v ON p.id = v.patient_id
    ''')
    
    stats = cursor.fetchone()
    
    # أكبر الديون
    cursor.execute('''
        SELECT p.name, p.phone,
               COALESCE(SUM(v.total_cost - v.paid_amount), 0) as debt
        FROM patients p
        LEFT JOIN visits v ON p.id = v.patient_id
        GROUP BY p.id
        HAVING debt > 0
        ORDER BY debt DESC
        LIMIT 10
    ''')
    
    top_debtors = cursor.fetchall()
    conn.close()
    
    return render_template('reports.html', stats=stats, top_debtors=top_debtors)

@app.route('/api/dashboard-stats')
def dashboard_stats():
    """إحصائيات لوحة التحكم"""
    conn = get_db()
    cursor = conn.cursor()
    
    # إحصائيات عامة
    cursor.execute('''
        SELECT 
            COUNT(DISTINCT p.id) as total_patients,
            COUNT(v.id) as total_visits,
            COALESCE(SUM(v.total_cost), 0) as total_revenue,
            COALESCE(SUM(v.paid_amount), 0) as total_collected,
            COALESCE(SUM(v.total_cost - v.paid_amount), 0) as total_debt
        FROM patients p
        LEFT JOIN visits v ON p.id = v.patient_id
    ''')
    
    stats = dict(cursor.fetchone())
    
    # إيرادات اليوم
    cursor.execute('''
        SELECT COALESCE(SUM(paid_amount), 0) as today_revenue
        FROM visits
        WHERE DATE(visit_date) = DATE('now')
    ''')
    
    stats['today_revenue'] = cursor.fetchone()[0]
    
    # مواعيد اليوم
    cursor.execute('''
        SELECT COUNT(*) as today_appointments
        FROM appointments
        WHERE appointment_date = DATE('now')
        AND status = 'مجدول'
    ''')
    
    stats['today_appointments'] = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify(stats)

# ===== إدارة الأطباء =====

@app.route('/doctors')
def doctors_list():
    """قائمة الأطباء"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM doctors ORDER BY name')
    doctors = cursor.fetchall()
    conn.close()
    
    return render_template('doctors.html', doctors=doctors)

@app.route('/doctor/new', methods=['GET', 'POST'])
def new_doctor():
    """إضافة طبيب جديد"""
    if request.method == 'POST':
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO doctors (name, specialization, phone, email, license_number)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['name'], data.get('specialization'), data.get('phone'),
              data.get('email'), data.get('license_number')))
        
        doctor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'doctor_id': doctor_id})
    
    return render_template('new_doctor.html')

@app.route('/doctor/delete/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    """حذف طبيب"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM doctors WHERE id = ?', (doctor_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# ===== التصدير والنسخ الاحتياطي =====

@app.route('/patient/<int:patient_id>/export')
def export_patient(patient_id):
    """تصدير ملف المريض كـ PDF"""
    conn = get_db()
    cursor = conn.cursor()
    
    # إعدادات العيادة
    cursor.execute('SELECT * FROM clinic_settings WHERE id = 1')
    clinic = cursor.fetchone()
    
    # بيانات المريض
    cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
    patient = cursor.fetchone()
    
    if not patient:
        return "المريض غير موجود", 404
    
    # زيارات المريض
    cursor.execute('''
        SELECT v.*, d.name as doctor_name, d.specialization as doctor_spec
        FROM visits v
        LEFT JOIN doctors d ON v.doctor_id = d.id
        WHERE v.patient_id = ?
        ORDER BY v.visit_date DESC
    ''', (patient_id,))
    
    visits = cursor.fetchall()
    conn.close()
    
    return render_template('export_patient.html', patient=patient, visits=visits, clinic=clinic)

@app.route('/visit/<int:visit_id>/export')
def export_visit(visit_id):
    """تصدير زيارة واحدة"""
    conn = get_db()
    cursor = conn.cursor()
    
    # إعدادات العيادة
    cursor.execute('SELECT * FROM clinic_settings WHERE id = 1')
    clinic = cursor.fetchone()
    
    # بيانات الزيارة
    cursor.execute('''
        SELECT v.*, p.*, d.name as doctor_name, d.specialization as doctor_spec,
               p.name as patient_name, p.age as patient_age, p.gender as patient_gender
        FROM visits v
        JOIN patients p ON v.patient_id = p.id
        LEFT JOIN doctors d ON v.doctor_id = d.id
        WHERE v.id = ?
    ''', (visit_id,))
    
    visit = cursor.fetchone()
    conn.close()
    
    if not visit:
        return "الزيارة غير موجودة", 404
    
    return render_template('export_visit.html', visit=visit, clinic=clinic)

@app.route('/settings', methods=['GET', 'POST'])
def clinic_settings():
    """إعدادات العيادة"""
    if request.method == 'POST':
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE clinic_settings
            SET clinic_name = ?,
                clinic_address = ?,
                clinic_phone = ?,
                clinic_email = ?,
                header_text = ?,
                footer_text = ?
            WHERE id = 1
        ''', (
            data.get('clinic_name'),
            data.get('clinic_address'),
            data.get('clinic_phone'),
            data.get('clinic_email'),
            data.get('header_text'),
            data.get('footer_text')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clinic_settings WHERE id = 1')
    settings = cursor.fetchone()
    conn.close()
    
    return render_template('settings.html', settings=settings)

@app.route('/patient/<int:patient_id>/delete', methods=['POST'])
def delete_patient(patient_id):
    """حذف المريض وجميع بياناته المرتبطة"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # حذف المدفوعات المرتبطة بزيارات المريض
        cursor.execute('''
            DELETE FROM payments 
            WHERE visit_id IN (SELECT id FROM visits WHERE patient_id = ?)
        ''', (patient_id,))
        
        # حذف الزيارات
        cursor.execute('DELETE FROM visits WHERE patient_id = ?', (patient_id,))
        
        # حذف المواعيد
        cursor.execute('DELETE FROM appointments WHERE patient_id = ?', (patient_id,))
        
        # حذف المريض
        cursor.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'تم حذف المريض وجميع بياناته بنجاح'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/backup/database')
def backup_database():
    """تصدير نسخة احتياطية من قاعدة البيانات"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'backup_{timestamp}.db'
    backup_path = os.path.join('/tmp', backup_filename)
    
    try:
        shutil.copy2(DATABASE, backup_path)
        
        from flask import send_file
        return send_file(backup_path, 
                        as_attachment=True,
                        download_name=backup_filename,
                        mimetype='application/x-sqlite3')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/search/advanced')
def advanced_search():
    """البحث المتقدم بالتاريخ"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    query = request.args.get('q', '').strip()
    
    conn = get_db()
    cursor = conn.cursor()
    
    sql = '''
        SELECT DISTINCT p.*, 
               COALESCE(SUM(v.total_cost - v.paid_amount), 0) as total_debt
        FROM patients p
        LEFT JOIN visits v ON p.id = v.patient_id
        WHERE 1=1
    '''
    
    params = []
    
    if query:
        sql += ' AND (p.name LIKE ? OR p.phone LIKE ? OR p.national_id LIKE ?)'
        params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
    
    if start_date:
        sql += ' AND DATE(v.visit_date) >= ?'
        params.append(start_date)
    
    if end_date:
        sql += ' AND DATE(v.visit_date) <= ?'
        params.append(end_date)
    
    sql += ' GROUP BY p.id ORDER BY p.name LIMIT 50'
    
    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in results])

@app.route('/appointments')
def appointments_list():
    """قائمة المواعيد"""
    conn = get_db()
    cursor = conn.cursor()
    
    # جلب جميع المواعيد مع بيانات المرضى
    cursor.execute('''
        SELECT a.*, p.name as patient_name, p.phone
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        ORDER BY a.appointment_date, a.appointment_time
    ''')
    
    appointments = cursor.fetchall()
    conn.close()
    
    return render_template('appointments.html', appointments=appointments)

@app.route('/appointment/new/<int:patient_id>', methods=['GET', 'POST'])
def new_appointment(patient_id):
    """إضافة موعد جديد"""
    if request.method == 'POST':
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO appointments (patient_id, appointment_date, appointment_time, 
                                    reason, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (patient_id, data['appointment_date'], data['appointment_time'],
              data.get('reason'), data.get('status', 'مجدول'), data.get('notes')))
        
        appointment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'appointment_id': appointment_id})
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    
    if not patient:
        return "المريض غير موجود", 404
    
    return render_template('new_appointment.html', patient=patient)

@app.route('/appointment/update/<int:appointment_id>', methods=['POST'])
def update_appointment_status(appointment_id):
    """تحديث حالة الموعد"""
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE appointments
        SET status = ?
        WHERE id = ?
    ''', (data['status'], appointment_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/appointment/delete/<int:appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    """حذف موعد"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM appointments WHERE id = ?', (appointment_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    # استخدم 0.0.0.0 ليكون متاح على الشبكة
    app.run(host='0.0.0.0', port=5000, debug=True)
