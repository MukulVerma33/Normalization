from flask import Flask, render_template, redirect,url_for, request,flash, send_file
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import FileField,SubmitField
import pandas as pd
import numpy as np
import os
import sendgrid
from sendgrid.helpers.mail import *
import base64
UPLOAD_FOLDER = '/app'                  # /app

SENDGRID_API_KEY = 'Your-API-KEY'
app = Flask(__name__)
app.config['SECRET_KEY']='pass'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['xlsx'])
class Form(FlaskForm):
    file=FileField('Upload your xlsx file')
    submit=SubmitField('submit')


@app.route('/',methods=['GET', 'POST'])
def index():
    try:
        form=Form()
        FinalMarks = []
        RollNo=[]
        Name=[]
        marks=[]
        #try:
        if form.validate_on_submit():

            file=form.file.data
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'data.xlsx'))
            file_name1='data.xlsx'

    #Logic 

            file_errors_location = file_name1     
            df = pd.read_excel(file_errors_location)


            x = df['Group'].tolist()

            x = set(x)
            mean=[]
            std=[]

            for i in x:
                mean.append(np.mean(df[df.Group == i][['Mark']]))
                std.append(np.std(df[df.Group == i][['Mark']]))


            avg=np.mean(mean)
            sd=np.mean(std)

            x=list(x)

            dict_mean = dict()

            for i,j in enumerate(mean):
                dict_mean[x[i]]=j 

            dict_sd = dict()

            for i,j in enumerate(std):
                dict_sd[x[i]]=j 

            marks = df['Mark'].tolist()
            group = df['Group'].tolist()
            RollNo = df['RollNo'].tolist()
            Name = df['Name'].tolist()


            norm=list()

            for i,j in enumerate(group):
                norm.append((marks[i]-dict_mean[j])/dict_sd[j])

            NormalizedMarks = list()

            for i in norm:
                NormalizedMarks.append((sd*i)+avg)


            FinalMarks = list()

            for i in NormalizedMarks:
                FinalMarks.append(round(i,0))


            FinalMarks = pd.DataFrame(FinalMarks) 

            FinalMarks = FinalMarks['Mark'].tolist()

            writefp = open('Marks.csv','w')
            writefp.write('RollNo'+','+'Name'+','+'Original Marks'+','+'Group'+','+'Final Marks'+'\n')
            for i,j in enumerate(FinalMarks):
                writefp.write(str(RollNo[i])+','+str(Name[i])+','+str(marks[i])+','+str(group[i])+','+str(j)+'\n')
            writefp.close()


        #if request.method == "POST":
            sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
            from_email = Email('normalisation33@gmail.com')
            to_email = Email(request.form.get("to_email"))
            subject = 'Here are your normalized marks'
            content = Content("text/plain", 'Here are your results')

            file_path = "/app\\Marks.csv"

            with open(file_path, 'rb') as f:
                data = f.read()

            # Encode contents of file as Base 64
            encoded = base64.b64encode(data).decode()

            """Build attachment"""
            attachment = Attachment()
            attachment.content = encoded
            attachment.type = "text/csv"
            attachment.filename = "Marks.csv"
            attachment.disposition = "attachment"
            attachment.content_id = "PDF Document file"

            mail = Mail(from_email, subject, to_email, content)
            mail.add_attachment(attachment)

            response = sg.client.mail.send.post(request_body=mail.get())

            if response.status_code == 202:
                #return "Email sent successfully!"
                flash("Email sent successfully! Don't forget the spam folder")
                return redirect(url_for('index'))
            else:
                return "Status Code: " + str(response.status_code)
        #except:
            #flash("Please Check the instructions again!!")    
    except:
        flash("Please Check the instructions again!!")

    return render_template('index.html',form=form)


@app.route('/download')
def download():
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = "/app/data.xlsx"
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
  app.run(debug=True)
 
