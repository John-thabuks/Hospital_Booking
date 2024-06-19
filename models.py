from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from flask_bcrypt import Bcrypt
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()
bcrypt = Bcrypt()

# Association table for many-to-many relationship between users and roles
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):        # RoleMixin: Helps in checking permissions, role assignments Admin/ Doc/ Patient/ PatientExpericeOfficer
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    _password = db.Column(db.String)
    active = db.Column(db.Boolean())

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('user', lazy='dynamic'))

    @hybrid_property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, password):
        self._password = bcrypt.generate_password_hash(password).decode('utf-8')

    def password_authetication(self, password):
        return bcrypt.check_password_hash(self._password, password).encrypt('utf-8')

class DoctorType(db.Model):     # Permanent Doctor or Consultant
    __tablename__ = 'doctortypes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String)

class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_type_id = db.Column(db.Integer, db.ForeignKey('doctor_type.id'), nullable=False)

    
    user = db.relationship('User', backref='doctor')
    doctor_type = db.relationship('DoctorType', backref='doctor')
    schedules = db.relationship('Schedule', backref='doctor')
    appointments = db.relationship('Appointment', backref='doctor')

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref='patient')
    appointments = db.relationship('Appointment', backref='patient')

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Could be a doctor or Patient Experience Officer
    

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)   
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Created by Patient Experience Officer or patient

    schedule = db.relationship('Schedule', backref='appointments')
