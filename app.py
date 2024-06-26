from flask import Flask, render_template, request,url_for,redirect
from werkzeug.utils import secure_filename
import mysql.connector
import json
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from dotenv import load_dotenv
load_dotenv()
import os
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
import google.generativeai as genai

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

genai.configure(api_key="AIzaSyDa24HHUaKSxgyvg7FgLolrZOSR8LKXYtk")

app = Flask(__name__)

# MySQL Configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shri@2023',
    'database': 'GenQuest'
}


def generate_question_pdf(response):
    # Create a PDF canvas
    c = canvas.Canvas("ques.pdf", pagesize=letter)

    # Set up fonts and styles
    c.setFont("Helvetica", 12)

    # Add the generated question to the PDF
    c.drawString(100, 750, response)

    # Save the PDF
    c.save()


@app.route('/profile',methods=['POST','GET'])
def profile():
    if request.method == 'GET':
        conn = connect_to_mysql()  # Assuming you have a function connect_to_mysql() to establish a database connection
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM users where id="SREC_IT_1" """)
        user = cursor.fetchone()  
        print(user)# Use fetchall() to retrieve all rows
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('profile.html',user=user)
    elif request.method == 'POST':
        name = request.form['name']
        id = request.form['id']
        dept = request.form['dept']
        college = request.form['college']
        email = request.form['email']
        password = request.form['password']
        conn = connect_to_mysql()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET name = %s, dept = %s,college=%s,email=%s,password=%s WHERE id=%s",(name, dept, college, email, password,id))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('profile.html',flag=1)
   
    return render_template('profile.html')


# Function to connect to MySQL database
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/p1')
def p1():
    return render_template('p1.html')



@app.route('/home')
def home():
    conn = connect_to_mysql()  # Assuming you have a function connect_to_mysql() to establish a database connection
    cursor = conn.cursor()
    cursor.execute("SELECT sub_code,sub_name,batch,test_name,test,date FROM subjects")
    subjects = cursor.fetchall()  
    print(subjects)# Use fetchall() to retrieve all rows
    
    cursor.execute("SELECT COUNT(*) FROM subjects")
    row_count = cursor.fetchone()[0]
    cursor.execute("""SELECT COUNT(*) FROM subjects where test="Internal" """)
    internal=cursor.fetchone()[0]
    cursor.execute("""SELECT COUNT(*) FROM subjects where test="Assignment Test" """)
    assign = cursor.fetchone()[0]
    cursor.execute("""SELECT COUNT(*) FROM subjects where test="Quiz" """)
    quiz= cursor.fetchone()[0]
    cursor.execute("""SELECT COUNT(DISTINCT sub_name) FROM subjects """)
    sub= cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    

    return render_template('home.html', subjects=subjects,row_count=row_count,internal=internal,assign=assign,quiz=quiz,sub=sub)

def connect_to_mysql():
    return mysql.connector.connect(**mysql_config)
def get_gemini_resp(ques):
    prompt = """\n\n
    Your task is to generate answers for the given questions {0} .Output the answers in html format.
   Maintain the standards which corresponds to university level.For long answer type of question generate a long paragraph.
     """.format(ques)
    #template = PromptTemplate(template=prompt,input_variables=['diff','topic','material'])
    model=genai.GenerativeModel('gemini-1.0-pro-latest')
    response=model.generate_content(prompt)
    print(response)
    return response.text


def get_gem(diff,topic,type,bloom,co):
    prompt = """\n\n
    Your task is to generate 1 {2} of  {0} difficulty on the topic:{1} based on the course outcome : {4} by following the blooms taxonomy level:{3} .Output the questions as a json array.
   Maintain the standards which corresponds to university level.For long answer type of question generate a long paragraph.
     """.format(diff,topic,type,bloom,co)
    #template = PromptTemplate(template=prompt,input_variables=['diff','topic','material'])
    model=genai.GenerativeModel('gemini-1.0-pro-latest')
    response=model.generate_content(prompt)
    print(response)
    return response.text
def get_gemini_response(diff,topic,type,bloom,co):
    prompt = """\n\n
    Your task is to generate 10 {2} of  {0} difficulty on the topic:{1} based on the course outcome : {4} by following the blooms taxonomy level:{3} .Output the questions in html format.
   Maintain the standards which corresponds to university level.For long answer type of question generate a long paragraph.
     """.format(diff,topic,type,bloom,co)
    #template = PromptTemplate(template=prompt,input_variables=['diff','topic','material'])
    model=genai.GenerativeModel('gemini-1.0-pro-latest')
    response=model.generate_content(prompt)
    print(response)
    return response.text

@app.route('/analyze',methods=['POST','GET'])
def analyze():
    if request.method == 'POST':
        if 'code' in request.form:
            code= request.form['code']
            name= request.form['name']
            fac_id=request.form['id']
            fac_name=request.form['fac_name']
            sem=request.form['sem']
            batch=request.form['batch']
            year=request.form['year']
            test=request.form['test']
            test_name=request.form['test_name']
            marks=request.form['marks']
            date=request.form['date']
            conn = connect_to_mysql()
            cursor = conn.cursor()
       
            # Insert data into MySQL
            query = "INSERT INTO subjects (sub_code, sub_name, fac_id, fac_name, batch, year, sem, test,test_name, marks, date) VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s)"
            values = (code, name, fac_id, fac_name, batch, year, sem, test,test_name, marks, str(date))

            cursor.execute(query, values)
        
        # Commit changes and close connections
            conn.commit()
            cursor.close()
            conn.close()
            
            return render_template('question.html')
        elif 'topic' in request.form:
            diff= request.form['difficulty']
            topic= request.form['topic']
            type=request.form['type']
            co=request.form['co']
            bloom=request.form['bloom']
            

            r=get_gem(diff,topic,type,bloom,co)
            print(r)
            response=get_gemini_response(diff,topic,type,bloom,co)
            ans=get_gemini_resp(response)
            generate_question_pdf(response)

            c = canvas.Canvas("questions.pdf", pagesize=letter)

        # Set up fonts and styles
            c.setFont("Helvetica", 12)

        # Add content to the PDF
            c.drawString(100, 750, response)

        # Save the PDF
            c.save()
        
    
            return render_template('question.html',response=response,ans=ans,r=r)
    return render_template('question.html')


@app.route('/signup', methods=['POST','GET'])
def signup_post():
    if request.method == 'POST':
        name = request.form['name']
        dept = request.form['dept']
        college = request.form['college']
        email = request.form['email']
        password = request.form['password']
        conn = connect_to_mysql()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE college=%s and dept=%s",(college,dept))
        
        # Fetch the result
        result = cursor.fetchone()

        # Extract the count value from the result
        count_value = result[0]
        # Insert user data into database
        cursor.execute("INSERT INTO users (id,name, dept, college, email, password) VALUES (%s,%s, %s, %s, %s, %s)",
                       (college+"_"+dept+"_"+str(count_value+1),name, dept, college, email, password))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('home.html',flag=1)
    return render_template('user_creation.html')


@app.route('/login', methods=['POST'])
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = connect_to_mysql()
        cursor = conn.cursor()
        # Check if email and password match in the database
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        if user:
            # Login successful
            return redirect(url_for('home'))
        else:
            # Login failed
            return "Invalid email or password"


# Route for subject creation form
@app.route('/subject', methods=['GET', 'POST'])
def subject_create():
    if request.method == 'POST':
        
        sub_name = request.form['name']
        fac_name= request.form['fac_name']
        fac_id=request.form['fac_id']
        year = request.form['year']
        batch = request.form['batch']
        sem = request.form['sem']
        subject_code = request.form['sub_code']
        
        conn = connect_to_mysql()
        cursor = conn.cursor()
       
        # Insert data into MySQL
        query = "INSERT INTO subjects (sub_code,sub_name, fac_id, fac_name, batch, year, sem) VALUES (%s, %s, %s, %s, %s, %s,%s)"
        values = (subject_code,sub_name, fac_id, fac_name, batch, year, sem)
        cursor.execute(query, values)
        
        # Commit changes and close connections
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('home.html')
    return render_template('sub_creation.html')

if __name__ == '__main__':
    app.run(debug=True)



