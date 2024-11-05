from flask import Blueprint, render_template, request, flash, jsonify, send_file
from flask_login import login_required, current_user
from .models import Semesters,Courses,GradesDistribution, User
from . import db
import json
import pandas as pd
from datetime import datetime
import os
from werkzeug.utils import secure_filename

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if current_user.email == 'admin@semo.edu':
        semesters = Semesters.query.all()
        return render_template("home2.html", user=current_user, Semesters = semesters)
    if request.method == 'POST': 
        semester = request.form.get('semester')
        sec_no = request.form.get('section_number[]')
        course_no = request.form.get('course_number[]')
        A_count = int(request.form.get('A_count[]'))
        B_count = int(request.form.get('B_count[]'))
        C_count = int(request.form.get('C_count[]'))
        D_count = int(request.form.get('D_count[]'))
        F_count = int(request.form.get('F_count[]'))
        X_count = int(request.form.get('X_count[]'))
        I_count = int(request.form.get('I_count[]'))
        CR_count = int(request.form.get('CR_count[]'))
        total_count = int(request.form.get('total[]'))


        if len(semester) < 6:
            flash('Semester be greater than 3 characters.', category='error')
        elif len(course_no) != 5 :
            flash('Couse number shoubld be 5 characters. For example: MA440', category='error')
        elif len(sec_no) > 3 :
            flash('Section number cannot be greater than 3 characters.', category='error')
        elif int(total_count) != int(A_count) + int(B_count) + int(C_count) + int(D_count) + int(F_count) + int(X_count) + int(I_count) + int(CR_count):
            flash('Total does not match the sum of the grades', category='error')
        else:
            semesterName = Semesters.query.filter_by(semester_name=semester).first()
            if not semesterName:
                semesterName = Semesters(semester_name=semester)
                db.session.add(semesterName) 
                db.session.commit()

            course_Name = Courses.query.filter_by(course_number=course_no , section_number = sec_no).first()
            if not course_Name:
                course_Name = Courses(course_number=course_no, section_number = int(sec_no), semester_id = semesterName.semester_id, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(course_Name) #adding the note to the database 
            db.session.commit()
            new_grade_distribution= GradesDistribution(A_count = A_count, B_count = B_count, C_count = C_count, D_count = D_count, F_count = F_count, X_count = X_count, I_count = I_count, CR_count = CR_count, total_count = total_count, course_id = course_Name. course_id)
            db.session.add(new_grade_distribution) #adding the note to the database 
            db.session.commit()
            flash('Form Sumbitted', category='success')


    return render_template("home.html", user=current_user, Semesters = Semesters)

@views.route('/delete-distribution', methods=['POST'])
def delete_distribution():  
    distribution = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    distribution_id = distribution['distribution_id']
    distribution = GradesDistribution.query.get(distribution_id)
    if distribution:
        course_id = distribution.course_id
        course = Courses.query.get(course_id)
        if course.user_id == current_user.id:
            db.session.delete(distribution)
            db.session.commit()
        distributions = [gradeDistributions for gradeDistributions in  course]
        if len(distributions) == 0:
            db.session.delete(course)
            db.session.commit()

    return jsonify({})

@views.route('/download_csv/<semester_name>')
def download_csv(semester_name):
    semester = Semesters.query.filter_by(semester_name = semester_name).first()
    distribution_dict= {'Course Number':[], 'Section Number': [], 'Professor':[], 'A':[], 'B':[], 'C':[], 'D':[], 'F':[], 'X':[], 'I':[], 'CR':[], 'Total':[], 'Pass Rate':[]}
    for course in semester.courses:
        for gradeDistribution in course.gradeDistributions:
            distribution_dict['Course Number'].append(course.course_number)
            distribution_dict['Section Number'].append(course.section_number)
            distribution_dict['Professor'].append(User.query.get(course.user_id).first_name + " " + User.query.get(course.user_id).last_name)
            distribution_dict['A'].append(gradeDistribution.A_count)
            distribution_dict['B'].append(gradeDistribution.B_count)
            distribution_dict['C'].append(gradeDistribution.C_count)
            distribution_dict['D'].append(gradeDistribution.D_count)
            distribution_dict['F'].append(gradeDistribution.F_count)
            distribution_dict['X'].append(gradeDistribution.X_count)
            distribution_dict['I'].append(gradeDistribution.I_count)
            distribution_dict['CR'].append(gradeDistribution.CR_count)
            distribution_dict['Total'].append(gradeDistribution.total_count)
            pass_rate = ((gradeDistribution.A_count + gradeDistribution.B_count + gradeDistribution.C_count + gradeDistribution.CR_count) / gradeDistribution.total_count) * 100
            distribution_dict['Pass Rate'].append(round(pass_rate, 2))
    
    distribution_df = pd.DataFrame(distribution_dict)
    file_name = f'{semester.semester_name}_grade_distributions_{str(datetime.now())}.csv'
    file_name = secure_filename(file_name)
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    path = f'{output_dir}/{file_name}'
    distribution_df.to_csv(path , index=False)
    print("Checking path:", path)
    print("Path exists:", os.path.exists(path))

    current_path= str(os.getcwd())
    current_path = str(os.getcwd())
    safe_path = current_path.replace('\\', '/')

    
    
    return send_file(safe_path+'/'+ path, as_attachment= True)


