from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Semesters(db.Model):
    semester_id = db.Column(db.Integer, primary_key=True)
    semester_name = db.Column(db.String(20))
    courses = db.relationship('Courses')

class Courses (db.Model):
    course_id = db.Column(db.Integer, primary_key=True)
    course_number = db.Column(db.String(5))
    section_number = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    semester_id =  db.Column(db.Integer, db.ForeignKey('semesters.semester_id'))
    gradeDistributions = db.relationship('GradesDistribution')

class GradesDistribution (db.Model):
    distribution_id = db.Column(db.Integer, primary_key=True)
    A_count = db.Column(db.Integer)
    B_count = db.Column(db.Integer)
    C_count = db.Column(db.Integer)
    D_count = db.Column(db.Integer)
    F_count = db.Column(db.Integer)
    X_count = db.Column(db.Integer)
    I_count = db.Column(db.Integer)
    CR_count = db.Column(db.Integer)
    total_count = db.Column(db.Integer)
    course_id =  db.Column(db.Integer, db.ForeignKey('courses.course_id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    semo_id = db.Column(db.String(150), unique=True)
    courses = db.relationship('Courses')
