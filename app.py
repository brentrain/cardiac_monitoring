from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cardiac_monitoring.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Patient Model
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    medical_record_number = db.Column(db.String(20), unique=True, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Vital Signs Model
class VitalSigns(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    heart_rate = db.Column(db.Integer)
    blood_pressure_systolic = db.Column(db.Integer)
    blood_pressure_diastolic = db.Column(db.Integer)
    oxygen_saturation = db.Column(db.Float)
    temperature = db.Column(db.Float)
    rhythm_status = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/patients', methods=['GET', 'POST'])
def patients():
    if request.method == 'POST':
        data = request.json
        new_patient = Patient(
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d'),
            medical_record_number=data['medical_record_number'],
            notes=data.get('notes', '')
        )
        db.session.add(new_patient)
        db.session.commit()
        return jsonify({'message': 'Patient added successfully'}), 201
    
    patients = Patient.query.all()
    return render_template('patients.html', patients=patients)

@app.route('/monitor/<int:patient_id>')
def monitor_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template('monitor.html', patient=patient)

@app.route('/api/vitals/<int:patient_id>', methods=['POST'])
def update_vitals(patient_id):
    data = request.json
    new_vitals = VitalSigns(
        patient_id=patient_id,
        heart_rate=data['heart_rate'],
        blood_pressure_systolic=data['blood_pressure_systolic'],
        blood_pressure_diastolic=data['blood_pressure_diastolic'],
        oxygen_saturation=data['oxygen_saturation'],
        temperature=data['temperature'],
        rhythm_status=data['rhythm_status']
    )
    db.session.add(new_vitals)
    db.session.commit()
    return jsonify({'message': 'Vitals updated successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 