from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os
from arrhythmia_detector import ArrhythmiaDetector
from simulator_connection import ProSim8Connection
import threading
import time
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-development')
db = SQLAlchemy(app)

# Register the simulator blueprint
from simulator_connection import simulator_bp
app.register_blueprint(simulator_bp)

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    subscription_plan = db.Column(db.String(20), nullable=False, default='free')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    patients = db.relationship('Patient', backref='tenant', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Tenant {self.name}>'

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    room = db.Column(db.String(10), nullable=False)
    admission_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    vitals = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Patient {self.name}>'

# Initialize arrhythmia detector
arrhythmia_detector = ArrhythmiaDetector()

@app.route('/')
def index():
    if 'tenant_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Hardcoded test credentials
        if email == 'user@cardiacmonitor.com' and password == 'Test12345':
            session['tenant_id'] = 1
            session['tenant_name'] = 'Test User'
            return redirect(url_for('dashboard'))
        
        # Original login logic as fallback
        tenant = Tenant.query.filter_by(email=email).first()
        if tenant and tenant.check_password(password):
            session['tenant_id'] = tenant.id
            session['tenant_name'] = tenant.name
            return redirect(url_for('dashboard'))
        
        return render_template('login.html', error="Invalid email or password")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        if Tenant.query.filter_by(email=email).first():
            return render_template('register.html', error="Email already registered")
        
        tenant = Tenant(name=name, email=email)
        tenant.set_password(password)
        db.session.add(tenant)
        db.session.commit()
        
        session['tenant_id'] = tenant.id
        session['tenant_name'] = tenant.name
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('tenant_id', None)
    session.pop('tenant_name', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'tenant_id' not in session:
        return redirect(url_for('login'))
    
    tenant = Tenant.query.get(session['tenant_id'])
    return render_template('dashboard.html', tenant=tenant)

@app.route('/patients')
def patients():
    if 'tenant_id' not in session:
        return redirect(url_for('login'))
    
    patients = Patient.query.filter_by(tenant_id=session['tenant_id']).all()
    return render_template('patients.html', patients=patients)

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if 'tenant_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        room = request.form['room']
        
        patient = Patient(
            name=name, 
            age=age, 
            room=room,
            tenant_id=session['tenant_id']
        )
        db.session.add(patient)
        db.session.commit()
        
        return redirect(url_for('patients'))
    
    return render_template('add_patient.html')

@app.route('/monitor/<int:patient_id>')
def monitor_patient(patient_id):
    if 'tenant_id' not in session:
        return redirect(url_for('login'))
    
    patient = Patient.query.get_or_404(patient_id)
    if patient.tenant_id != session['tenant_id']:
        return redirect(url_for('patients'))
    
    return render_template('monitor.html', patient=patient)

@app.route('/api/patient/<int:patient_id>/vitals')
def update_vitals(patient_id):
    if 'tenant_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
        
    patient = Patient.query.get_or_404(patient_id)
    
    # Generate realistic ECG data
    t = np.linspace(0, 10, 2500)
    heart_rate = np.random.normal(75, 5)  # Normal heart rate with some variation
    ecg_data = generate_ecg(t, heart_rate)
    
    # Detect arrhythmia
    detector = ArrhythmiaDetector()
    arrhythmia_result = detector.detect_arrythmia(ecg_data)
    
    # Calculate other vitals with realistic variations
    systolic = int(np.random.normal(120, 5))
    diastolic = int(np.random.normal(80, 3))
    spo2 = int(np.random.normal(98, 1))
    resp_rate = int(np.random.normal(16, 1))
    temp = round(np.random.normal(37.0, 0.2), 1)
    
    # Update patient's vitals in database
    vitals_data = {
        'heart_rate': heart_rate,
        'systolic': systolic,
        'diastolic': diastolic,
        'spo2': spo2,
        'resp_rate': resp_rate,
        'temp': temp,
        'ecg_data': ecg_data.tolist(),
        'arrhythmia': arrhythmia_result
    }
    
    patient.vitals = json.dumps(vitals_data)
    db.session.commit()
    
    return jsonify(vitals_data)

@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    if 'tenant_id' not in session:
        return redirect(url_for('login'))
        
    patient = Patient.query.get_or_404(patient_id)
    if patient.tenant_id != session['tenant_id']:
        return redirect(url_for('patients'))
        
    db.session.delete(patient)
    db.session.commit()
    
    return redirect(url_for('patients'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8081) 