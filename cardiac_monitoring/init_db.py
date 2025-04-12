from app import app, db, Tenant, Patient
from datetime import datetime

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        
        # Create a test tenant
        test_tenant = Tenant(
            name='Test Hospital',
            email='test@hospital.com',
            subscription_plan='premium'
        )
        test_tenant.set_password('password123')
        db.session.add(test_tenant)
        db.session.commit()
        
        # Create a test patient
        test_patient = Patient(
            tenant_id=test_tenant.id,
            name='John Doe',
            age=45,
            room='101'
        )
        db.session.add(test_patient)
        db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db() 