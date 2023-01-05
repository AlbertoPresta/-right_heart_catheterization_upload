import os
from datetime import datetime

from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = "secret_key"  # for encrypting the session

UPLOAD_FOLDER_ROOT =  "/Users/albertopresta/Desktop/Tavi_regurgitation_upload/src/tavi"
#UPLOAD_FOLDER_ROOT = os.path.join("/","data", "exports", "sshfs", "tavi_regurgitation")
DB_PATH = os.path.join(UPLOAD_FOLDER_ROOT, "site.db")

# TODO change DB dir to /data/...
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"

db = SQLAlchemy(app)


class Patient(db.Model):
    # TODO set nullable=False as needed
    id = db.Column(db.Text, unique=True, nullable=False, primary_key=True)
    sex = db.Column(db.Text, nullable=False)
    birth = db.Column(db.DateTime)

    ct_date = db.Column(db.DateTime)
    
    tavi_score = db.Column(db.Integer)

    
    other = db.Column(db.Text)
    
    def __repr__(self):
        return f"{self.id} {self.id} {self.sex} {self.birt}  {self.ct_date} {self.tavi_score}"


# Make root directory and db if not existing
if not os.path.isdir(UPLOAD_FOLDER_ROOT):
    os.makedirs(UPLOAD_FOLDER_ROOT, exist_ok=True)
if not os.path.isfile(DB_PATH):
    with app.app_context():
        db.create_all()


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        
        # Collect all the form data
        patient_id = request.form["patient"]
        patient_sex = request.form["sex"]
        patient_birth = request.form['birth']
        patient_birth = datetime.strptime(patient_birth, "%Y-%m-%d")
        

        ct_files = request.files.getlist('ct[]')
        ct_files = [f for f in ct_files if f]
        ct_date = None
        if len(ct_files) > 0:
            ct_date = request.form['ctdate']
            ct_date = datetime.strptime(ct_date, "%Y-%m-%d")
        
        tavi_score = float(request.form['tavi'])

        
        other_info = request.form['other_text']
        
        # Create the Patient instance
        patient = Patient(id=patient_id, sex=patient_sex, birth=patient_birth, tavi_score=tavi_score,
                          other=other_info)

        if ct_date:
            patient.ct_date = ct_date

        
        # Add the Patient to the DB
        db.session.add(patient)
        
        try:
            db.session.commit()
        except IntegrityError:
            flash("Patient already uploaded", "error")
            return redirect('/')
        
        # Save the files
        patient_dir = os.path.join(UPLOAD_FOLDER_ROOT, patient_id)
        
        if os.path.isdir(patient_dir):
            flash('Patient already uploaded', "error")
            return redirect('/')
        
        os.makedirs(os.path.join(patient_dir, "ct"), exist_ok=False)
        

        
        for file in ct_files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(patient_dir, "ct", filename))
        
        flash('Data successfully uploaded', "success")
        return redirect('/')


if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 1339, debug=True)