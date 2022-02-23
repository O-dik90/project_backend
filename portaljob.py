from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import ForeignKey, null
from sqlalchemy.orm import backref
import base64

app = Flask(__name__)
db= SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:PG_user90@localhost:5432/Portaljob?sslmode=disable'

  # class user dengan profil user relasi sudah OK
class User(db.Model):
  id= db.Column(db.Integer, primary_key = True, index= True)
  username = db.Column(db.String(30), nullable = False)
  email= db.Column(db.String(50), nullable= False)
  pas = db.Column(db.String(50), nullable= False)
  role_user = db.Column(db.String (10), nullable= False)
  user_pro= db.relationship('User_Profil', backref= 'user', uselist=False)

  def __repr__(self):
    return '<User:{}>'.format(self.name)
  
class User_Profil(db.Model):
  id= db.Column(db.Integer,db.ForeignKey('user.id'),primary_key = True, nullable = False)
  name= db.Column(db.String(50), nullable= False)
  email= db.Column(db.String(50), nullable= False, unique= True)
  telephone= db.Column(db.String(16), nullable= False)
  ttl = db.Column(db.Date, nullable= False)
  graduation= db.Column(db.String(30), nullable= False)
  majority = db.Column(db.String(30), nullable = False)
  skill = db.Column(db.String, nullable=False)

class Company(db.Model):
  id= db.Column(db.Integer, primary_key = True, index=True)
  name= db.Column(db.String(75), nullable= False, unique= True)
  email= db.Column(db.String(50), nullable= False)
  pas = db.Column(db.String(50), nullable= False)
  role_comp = db.Column(db.String (10), nullable= False)
  re_comp = db.relationship('Comp_Profil', backref= 'company')
  
class Comp_Profil(db.Model):
  id= db.Column(db.Integer,db.ForeignKey('company.id'),nullable=False, primary_key = True)
  name = db.Column(db.String(40), nullable= False)
  email = db.Column(db.String(50), nullable= False, unique= True)
  addr = db.Column(db.String(50), nullable=False)
  type= db.Column(db.String(20), nullable= False)

class Jobseeker(db.Model): 
  id = db.Column(db.Integer, primary_key= True, index= True)
  status =db.Column(db.String(15), nullable= True)
  apply_date = db.Column(db.Date, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
  job_id = db.Column(db.Integer, db.ForeignKey('job.id'),
        nullable=False)
  response_date = db.Column(db.Date, nullable=True)

class Job(db.Model):
  id = db.Column(db.Integer, primary_key=True, index=True)
  name = db.Column(db.String(120), nullable=False)
  position = db.Column(db.String(20), nullable= False)
  exp= db.Column(db.String(20), nullable = True)
  salary = db.Column(db.Integer, nullable= False)
  status = db.Column(db.String(20), nullable= False)
  company_id = db.Column(db.Integer, db.ForeignKey('company.id'),nullable=True)
  jobseeker_id = db.relationship('Jobseeker', backref='job', lazy=True)


db.create_all()
db.session.commit()

@app.route('/')
def home():
  return jsonify(
    'Backend Project SQLalchemy Portaljob'
  ),200

def aut():
  data = request.headers.get("Authorization")
  encode =data[6:].encode("ascii")
  decode= base64.b64decode(encode)
  decode=decode.decode("ascii")
  new_data= decode.split(":")
  username = new_data[0]
  password = new_data[1]

  return[username,password]

@app.route('/user_create/', methods=['POST'])
def create_user():
  data= request.get_json()
  u = User(
    email = data['email'],
    username = data['username'],
    pas = data['pas'],
    role_user = 'member'
    )
  db.session.add(u)
  db.session.commit()
  return jsonify('succes create user',{
      'email' : u.email,
      'username' : u.username
    }
  )

@app.route('/user_profil_create/', methods=['POST'])
def create_profil_user():
  parsed = aut()
  username = parsed[0]
  password= parsed[1]
  
  us = User.query.filter_by(username=username).first_or_404()
  if us.pas != password or us.username !=username :
    return{
      'error' : 'Bad Request',
      'mesage' : 'Username/Kata sandi salah'
    }
  elif us.role_user != 'member':
    return{
      'message' : 'anda bukan member user'
    }
  data = request.get_json()

  u_p = User_Profil(
    name = data['name'],
    email = us.email,
    telephone= data['telephone'],
    ttl = data['tanggal_lahir'],
    graduation= data['graduation'],
    majority = data['majority'],
    skill = data['skill'],
    id = us.id
  )
  db.session.add(u_p)
  db.session.commit()
  return jsonify(
    'succes input data user profil',{
      'name' : u_p.name,
      'email' : u_p.email,
      'telephone' : u_p.telephone,
      'tanggal_lahir' : u_p.ttl,
      'graduation' : u_p.graduation,
      'majority'  : u_p.majority,
      'skill' : u_p.skill,
    }
  )

@app.route('/company_create/', methods=['POST'])
def create_company():
  data=request.get_json()
  c = Company(
    name = data['company_name'],
    email = data['company_email'],
    pas = data['company_pas'],
    role_comp = 'company'
  )
  db.session.add(c)
  db.session.commit()
  return jsonify(
    'succes, create data user',
    {
      'email' : c.email,
      'username' : c.name
    }
  )

@app.route('/company_profil_create/', methods=['POST'])
def create_profil_company():
  parsed = aut()
  username = parsed[0]
  password= parsed[1]
  
  c = Company.query.filter_by(name=username).first_or_404()
  if c.pas != password or c.name !=username :
    return{
      'error' : 'Bad Request',
      'mesage' : 'Username/Kata sandi salah'
    } 
  elif c.role_comp != 'company':
    return{
      'message' : 'anda bukan member company'
    }
  data = request.get_json()

  c_p = Comp_Profil(
    name = data['name'],
    email = c.email,
    addr= data['addr'],
    type = data['type'],
    id = c.id
  )
  db.session.add(c_p)
  db.session.commit()
  return jsonify([
    'succes create data company',
    {
      'name' : c_p.name,
      'email' : c.email,
      'addr' : c_p.addr,
      'type' : c_p.type
    }
  ])

# Bagian update user/company
@app.route('/user_profil_update/<id>/', methods=['PUT'])
def update_user(id):
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  data = request.get_json()

  u= User.query.filter_by(id=id).first_or_404()

  if u.username != username or u.pas != password:
    return{
      'error' : 'Bad request',
      'message' : 'username/password salah '
    }
  elif u.role_user != 'member':
    return{
      'message' : 'anda bukan member user'
    }
  u_p = User_Profil.query.filter_by(id=id).first_or_404()
  
  u_p.name = data.get('name', u_p.name)
  u_p.telephone = data.get('telephone', u_p.telephone)
  u_p.ttl = data.get('tanggal_lahir', u_p.ttl)
  u_p.graduation = data.get('graduation', u_p.graduation)
  u_p.majority = data.get('majority',u_p.majority)
  u_p.skill = data.get('skill', u_p.skill)

  db.session.commit()

  return jsonify([
    'Succes update user profil',
    {
      'name' : u_p.name,
      'email' : u_p.email,
      'tanggal_lahir' : u_p.ttl,
      'telephone' : u_p.telephone,
      'graduation'  : u_p.graduation,
      'majority'  : u_p.majority,
      'skill' : u_p.skill
    }
  ])

@app.route('/company_profil_update/<id>/', methods=['PUT'])
def update_company(id):
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  data = request.get_json()

  c= Company.query.filter_by(id=id).first_or_404()

  if c.name != username or c.pas != password:
    return{
      'error' : 'Bad request',
      'message' : 'username/password salah '
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'anda bukan member company'
    }
  cp = Comp_Profil.query.filter_by(id=id).first_or_404()
  
  cp.name = data.get('name', cp.name)
  cp.addr = data.get('addr', cp.addr)
  cp.type = data.get('type', cp.type)

  db.session.commit()
  return jsonify('Succes update company profil',
    {
      'name' : cp.name,
      'email' : c.email,
      'addr' : cp.addr,
      'type' : cp.type
    }
  )

@app.route('/company_search_user/', methods=['GET'])
def search_user():
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  c = Company.query.filter_by(name=username).first_or_404()

  if c.name != username or c.pas != password:
    return{
      'error' : 'Bad Request',
      'message' : 'username/password tidak benar'
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'hanya untuk member company'
    }

  data = request.get_json()
  u_p = User_Profil.query.filter_by(graduation=data['graduation'])

  if not data or not u_p:
    return{
      'message' : 'silahkan isi category dengan benar'
    }
  elif not 'graduation' in data:
    return{
      'message' : 'user tidak ditemukan'
    }
  return jsonify('succes searching data user profile',[
    {
      'name'  : item.name
      # 'telephone' : u_p.telephone,
      # 'tanggal_lahir' : u_p.ttl,
      # 'education' : u_p.education,
      # 'skill' : u_p.skill
    }for item in User_Profil.query.filter_by(graduation=data['graduation'])
  ])

#Job management
# post, get a job, get all job, edit a job  by company
@app.route('/company_post/', methods=['POST'])
def company_post_job():

  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  c = Company.query.filter_by(name=username).first_or_404()
  if c.pas != password or c.name !=username :
    return{
      'error' : 'Bad Request',
      'mesage' : 'Username/Kata sandi salah'
    } 
  elif c.role_comp != 'company':
    return{
      'message' : 'anda bukan member company'
    }
  data= request.get_json()

  j = Job(
    name  = data['name_job'],
    position = data['position'],
    salary = data['salary'],
    exp = data['experience']+"th",
    company_id = c.id,
    status = 'available'
  )
  db.session.add(j)
  db.session.commit()
  return jsonify([
    'succes, upload job advertisment',
    {
      'name'  : j.name,
      'position' : j.position,
      'salary'  : j.salary,
      'exp' : j.exp,
      'status'  : j.status
    }
  ])

@app.route('/company_update_job/<id>/', methods=['PUT'])
def update_job(id):
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  c = Company.query.filter_by(name=username).first_or_404()

  if c.name != username or c.pas != password:
    return{
      'error' : 'Bad Request',
      'message' : 'username/password tidak benar'
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'hanya untuk member company'
    }
  data = request.get_json()
  
  j = Job.query.filter_by(id=id).first_or_404()

  j.name = data.get('name', j.name)
  j.position =  data.get('position', j.position)
  j.salary = data.get('salary', j.salary)
  j.exp = data.get('exp', j.exp)

  db.session.commit()
  return jsonify([ 
    'succes update job vacancy',
    {
      'name'  : j.name,
      'position'  : j.position,
      'salary'  : j.salary,
      'exp'  : j.exp
    }
  ])

@app.route('/company_get_job/', methods=['GET'])
def get_job_id():
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  data = request.get_json() 
  c = Company.query.filter_by(name=username).first_or_404()

  if c.name != username or c.pas != password:
    return{
      'error' : 'Bad Request',
      'message' : 'username/password tidak benar'
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'hanya untuk member company'
    }

  u =  Job.query.filter_by(name=data['name']).first_or_404()
  return jsonify('succes get job',
    {
    'name' : u.name,
    'position'  : u.position,
    'salary' : u.salary,
    'exp' : u.exp
  })

@app.route('/company_get_all_job/', methods=['GET'])
def job_get():
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  c = Company.query.filter_by(name=username).first_or_404()
  data = request.get_json()

  if c.name != username or c.pas != password:
    return{
      'eror'  : 'Bad Request',
      'message' : 'username/password salah'
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'anda bukan company member'
    }
  return jsonify(
    'succes search list job',[
    {
      'name' : item.name
    }for item in Job.query.filter_by(id=data['id'])
  ])

#Timeline job
# list all available job, search job on criteria, get a job detail, apply job
@app.route('/apply_job/', methods=['POST'])
def apply_job():
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  data = request.get_json()
  u =  User.query.filter_by(username=username).first_or_404()

  if u.username != username or u.pas != password:
    return{
      'error' : 'Bad request',
      'message' : 'username/password salah'
    }
  elif u.role_user != 'member':
    return{
      'message' : 'anda bukan member user'
    }
  elif not u :
    return{
      'message' : 'data yang dimasukkan tidak ada'
    }

  js= Jobseeker(
    user_id= u.id, 
    job_id =data['job_id'],
    apply_date = datetime.now(),
    status = 'waiting'
    )
  db.session.add(js)
  db.session.commit()

  return jsonify(
    'succes apply job',
    {
      'status'  : js.status
    }
  )

@app.route('/user_all_list_job/', methods=['GET'])
def list_job():
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  u= User.query.filter_by(username=username).first_or_404()

  if u.username != username or u.pas != password:
    return{
      'error' : 'Bad request',
      'message' : 'username/password salah '
    }
  elif u.role_user != 'member':
    return{
      'message' : 'anda bukan member user'
    }

  data =  request.get_json()

  if not data:
    return{
      'message' : 'Job sedang tidak tersedia'
    }
  return jsonify([
    {
      'name' : item.name,
      'position'  : item.position,
      'salary' : item.salary,
      'exp' : item.exp,
      'status'  : item.status
    }for item in Job.query.filter_by(status= data['status'])
  ])

@app.route('/search_job/', methods=['GET'])
def search_job():
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  u= User.query.filter_by(username=username).first_or_404()

  if u.username != username or u.pas != password:
    return{
      'error' : 'Bad request',
      'message' : 'username/password salah '
    }
  elif u.role_user != 'member':
    return{
      'message' : 'anda bukan member user'
    }

  data =  request.get_json()
  # tambahan query seperti like
  j = Job.query.filter_by(name=data['name_job']).first_or_404()

  if data == null or j == null:
    return{
      'message' : 'Job sedang tidak tersedia'
    }
  return jsonify({
    'name'  : j.name,
    'position' : j.position,
    'salary'  : j.salary,
    'exp' : j.exp,
  })

@app.route('/user_get_job/', methods=['GET'])
def user_get_job():
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  u= User.query.filter_by(username=username).first_or_404()

  if u.username != username or u.pas != password:
    return{
      'error' : 'Bad request',
      'message' : 'username/password salah '
    }
  elif u.role_user != 'member':
    return{
      'message' : 'anda bukan member user'
    }

  data =  request.get_json()

  return jsonify('succces for searching job',[
    {
    'name' : j.name,
    'position'  : j.position,
    'salary'  : j.salary
    }for j in Job.query.filter_by(id=data['id']).first_or_404()
  ]) 

#Reporting
#list apply job
#get detail user profile by company
#list all applicant on a job
@app.route('/user_list_apply_status/<id>/', methods=['GET'])
# query belum benar
def list_apply(id):
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  #data = request.get_json()
  u = User.query.filter_by(username=username).first_or_404()

  if u.username != username or u.pas != password:
    return{
      'error' : 'Bad request',
      'message' : 'username/password salah'
    }
  elif u.role_user != 'member':
    return{
      'message' :   'anda bukan member user'
    }
  
  return jsonify("list apply job status",
    [{
      'status' : item.status
    }for item in Jobseeker.query.filter_by(user_id=id)]
  )

@app.route('/company_get_profile_user/<id>/', methods=['GET'])
def get_profil_user(id): 
  parsed = aut()
  username = parsed[0]
  password= parsed[1]
  
  c = Company.query.filter_by(name=username).first_or_404()

  if c.name != username or c.pas != password:
    return{
      'error' : 'Bad request',
      'message' : 'username/password salah '
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'anda bukan member user'
    } 
  # data= request.get_json()
  u_p = User_Profil.query.filter_by(id=id).first_or_404()

  return jsonify('succes get profile user',
    {
      'nama'  : u_p.name,
      'email' : u_p.email,
      'telephone' : u_p.telephone,
      'tanggal_lahir' : u_p.ttl,
      'graduation' : u_p.graduation,
      'majority'  : u_p.majority,
      'skill' : u_p.skill
    }
  )

@app.route('/company_list_applicant/', methods=['GET'])
def list_applicant():
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  c = Company.query.filter_by(name=username).first_or_404()
  data = request.get_json()

  if c.name != username or c.pas != password:
    return{
      'eror'  : 'Bad Request',
      'message' : 'username/password salah'
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'anda bukan company member'
    }
  elif not data :
    return{
      'message' : 'data list kosong'
    }
  return jsonify('succes get applicant',[
    {
      'status': item.status
    }for item in Jobseeker.query.filter_by(job_id=data['id'])
  ])

@app.route('/company_update_status/<user_id>/<job_id>/', methods=['PUT'])
def comp_update_status(user_id,job_id):
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  c = Company.query.filter_by(name=username).first_or_404()
  if c.pas != password or c.name !=username :
    return{
      'error' : 'Bad Request',
      'mesage' : 'Username/Kata sandi salah'
    } 
  elif c.role_comp != 'company':
    return{
      'message' : 'anda bukan member company'
    }
  
  data =request.get_json()
  js = Jobseeker.query.filter_by(user_id=user_id, job_id=job_id).first_or_404()
  js.status = data.get('status_update', js.status)
  js.response_date = datetime.now()

  db.session.commit()

  return jsonify('succes update status jobseeker',
    {
      'status' : js.status,
      'response_date' : js.response_date
    }
  ) 

@app.route('/user_delete/<id>/', methods=['DELETE'])
def delete_member_user(id):
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  u = User.query.filter_by(username=username).first_or_404()

  if u.username != username or u.pas != password:
    return{
      'error' : 'Bad Request',
      'message' : 'username/password tidak benar'
    }
  elif u.role_comp != 'member':
    return{
      'message' : 'hanya untuk member company'
    }
  up = User_Profil.query.fiter_by(id=id).first_or_404()
  
  db.session.delete(up,u)
  db.session.commit()

@app.route('/company_delete/<id>/', methods=['DELETE'])
def delete_member_company(id):
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  c = Company.query.filter_by(username=username).first_or_404()

  if c.name != username or c.pas != password:
    return{
      'error' : 'Bad Request',
      'message' : 'username/password tidak benar'
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'hanya untuk member company'
    }
  cp = Comp_Profil.query.fiter_by(id=id).first_or_404()
  
  db.session.delete(cp,c)
  db.session.commit()

if __name__ == '_main_':
  app.run()
