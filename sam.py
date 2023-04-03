from flask import Flask,request, redirect,render_template,url_for,flash,session
from flask_mysqldb import MySQL
from flask_session import Session
from otp import genotp
from cmail import sendmail
import random
app=Flask(__name__)
app.secret_key='*67@hjyjhk'
app.config['SESSION_TYPE']='filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='SPM'
Session(app)
mysql=MySQL(app)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/registration',methods=['POST','GET'])
def register():
    if request.method=='POST':
        rollno=request.form['rollno']
        name=request.form['name']
        group=request.form['group']
        password=request.form['password']
        code=request.form['code']
        email=request.form['email']
        #define college code
        ccode='sai12345267890'
        if ccode==code:
            cursor=mysql.connection.cursor()
            cursor.execute('select rollno from students')
            data=cursor.fetchall()
            cursor.execute('select email from students')
            edata=cursor.fetchall()
            #print(data)
            if (rollno,) in data:
                flash('user already exists')
                return render_template('register.html')
            if (email,) in edata:
                flash('Email id already exists')
                return render_template('register.html')
            cursor.close()
            otp=genotp()
            sendmail(email,otp)
            return render_template('otp.html',otp=otp,rollno=rollno,name=name,group=group,password=password,email=email)
            return otp
        else:
            flash('Invalid college code')
            return render_template('register.html')
    return render_template('register.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method=='POST':
        rollno=request.form['id']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*) from students where rollno=%s and password=%s',[rollno,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('Invalid rollno or password')
            return render_template('login.html')
        else:
            session['user']=rollno
            return redirect(url_for('home'))
    return render_template('login.html')
@app.route('/Studenthome')
def home():
    if session.get('user'):
        return render_template('home.html')
    else:
        #implement flash
        return redirect(url_for('login'))
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('index'))
    else:
        flash('Already logged out')
        return redirect(url_for('login'))
@app.route('/otp/<otp>/<rollno>/<name>/<group>/<password>/<email>',methods=['GET','POST'])
def otp(otp,rollno,name,group,password,email):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mysql.connection.cursor()
            lst=[rollno,name,group,password,email]
            query='insert into students values(%s,%s,%s,%s,%s)'
            cursor.execute(query,lst)
            mysql.connection.commit()
            cursor.close()
            flash('Details registered')
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,rollno=rollno,name=name,group=group,password=password,email=email)
@app.route('/noteshome')
def noteshome():
    if session.get('user'):
        rollno=session.get('user')
        cursor=mysql.connection.cursor()
        cursor.execute('select * from notes where rollno=%s',[rollno])
        notes_data=cursor.fetchall()
        print(notes_data)
        cursor.close()
        return render_template('addnotetable.html',data=notes_data)
    else:
        return redirect(url_for('login'))
@app.route('/addnotes',methods=['GET','POST'])
def addnotes():
    if session.get('user'):
        if request.method=='POST':
            title=request.form['title']
            content=request.form['content']
            cursor=mysql.connection.cursor()
            rollno=session.get('user')
            cursor.execute('insert into notes(rollno,title,content) values(%s,%s,%s)',[rollno,title,content])
            mysql.connection.commit()
            cursor.close()
            flash(f'{title} added successfully')
            return redirect(url_for('noteshome'))
        return render_template('notes.html')
    else:
        return redirect(url_for('login'))
@app.route('/viewnotes/<nid>')
def viewnotes(nid):
    cursor=mysql.connection.cursor()
    cursor.execute('select title,content from notes where nid=%s',[nid])
    data=cursor.fetchone()
    return render_template('notesview.html',data=data)
@app.route('/updatenotes/<nid>',methods=['GET','POST'])
def updatenotes(nid):
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select title,content from notes where nid=%s',[nid])
        data=cursor.fetchone()
        cursor.close()
        if request.method=='POST':
            title=request.form['title']
            content=request.form['content']
            cursor=mysql.connection.cursor()
            cursor.execute('update notes set title=%s,content=%s where nid=%s',[title,content,nid])
            mysql.connection.commit()
            cursor.close()
            flash('Notes updated successfully')
            return redirect(url_for('noteshome'))
        return render_template('updatenotes.html',data=data)
    else:
        return redirect(url_for('login'))
app.run(use_reloader=True,debug=True)
