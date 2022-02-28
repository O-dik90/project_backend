from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import base64

from sqlalchemy import or_

app = Flask(__name__) 
db= SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:PG_user90@localhost:5432/Job?sslmode=disable'

class User(db.Model):
  id= db.Column(db.Integer, primary_key = True, index= True)
  username = db.Column(db.String(50), nullable= True, unique= True)
  name = db.Column(db.String(30), nullable = True)
  email= db.Column(db.String(50), nullable= True)
  pas = db.Column(db.String(50), nullable= True)
  telephone= db.Column(db.String(16), nullable= True)
  ttl = db.Column(db.Date, nullable= True)
  graduation= db.Column(db.String(30), nullable= True)
  majority = db.Column(db.String(30), nullable = True)
  skill = db.Column(db.String, nullable=True)
  role_user = db.Column(db.String (10), nullable= False)

class Company(db.Model):
  id= db.Column(db.Integer, primary_key = True, index=True)
  username= db.Column(db.String(75), nullable= True)
  name= db.Column(db.String(75), nullable= True)
  email= db.Column(db.String(50), nullable= True)
  pas = db.Column(db.String(50), nullable= True)
  addr = db.Column(db.String(50), nullable=True)
  type= db.Column(db.String(20), nullable= True)
  role_comp = db.Column(db.String (10), nullable= False)
  
class Job_Application(db.Model): 
  id = db.Column(db.Integer, primary_key= True, index= True)
  status =db.Column(db.String(15), nullable= True)
  apply_date = db.Column(db.Date, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
  job_id = db.Column(db.Integer, db.ForeignKey('job.id'),
        nullable=False)
  response_date = db.Column(db.Date, nullable=True)
  jobapp_id = db.relationship('Job', backref='jobapp_id', lazy=True)
  user_app_id = db.relationship('User', backref='user_app_id', lazy=True)

class Job(db.Model):
  id = db.Column(db.Integer, primary_key=True, index=True)
  name = db.Column(db.String(120), nullable=False)
  position = db.Column(db.String(20), nullable= False)
  exp= db.Column(db.String(20), nullable = True)
  salary = db.Column(db.Integer, nullable= False)
  status = db.Column(db.String(20), nullable= False)
  company_id = db.Column(db.Integer, db.ForeignKey('company.id'),nullable=True)
  job_id = db.relationship('Company', backref='job' ,lazy=True)

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
    username= data['username'],
    pas = data['pas'],
    role_user = 'member'
    )
  db.session.add(u)
  db.session.commit()
  return{
    'message' : 'succes create user',
    'data'  : {
      'email' : u.email,
      'username'  : u.username,
      'id_user' : u.id
    }
  }

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
  
  u.name = data.get('name', u.name),
  u.email = data.get('email', u.email),
  u.telephone = data.get('telephone', u.telephone)
  u.ttl = data.get('tanggal_lahir', u.ttl)
  u.graduation = data.get('graduation', u.graduation)
  u.majority = data.get('majority',u.majority)
  u.skill = data.get('skill', u.skill)

  db.session.commit()

  return jsonify([
    'Succes update user profil',
    {
      'name' : u.name,
      'email' : u.email,
      'tanggal_lahir' : u.ttl,
      'telephone' : u.telephone,
      'graduation'  : u.graduation,
      'majority'  : u.majority,
      'skill' : u.skill
    }
  ])

@app.route('/user_delete/', methods=['DELETE'])
def delete_member_user():
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
  db.session.delete(u)
  db.session.commit()
  return{
    'User Berhasil Di hapus'
  }

@app.route('/company_create/', methods=['POST'])
def create_company():
  data=request.get_json()
  c = Company(
    username = data['company_name'],
    email = data['company_email'],
    pas = data['company_pas'],
    role_comp = 'company'
  )
  db.session.add(c)
  db.session.commit()
  return {
    'message' : 'succes, create data user',
    'data'  : {
      'email' : c.email,
      'username' : c.username,
      'company_id'  : c.id
    }
  }

@app.route('/company_profil_update/<id>/', methods=['PUT'])
def update_company(id):
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  data = request.get_json()

  c= Company.query.filter_by(id=id).first_or_404()

  if c.username != username or c.pas != password:
    return{
      'error' : 'Bad request',
      'message' : 'username/password salah '
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'anda bukan member company'
    }
  cp = Company.query.filter_by(id=id).first_or_404()
  
  cp.name = data.get('name', cp.name)
  cp.addr = data.get('addr', cp.addr)
  cp.type = data.get('type', cp.type)

  db.session.commit()
  return {
    'message'  : 'Succes update company profil',
    'data'  :
      {
        'name' : cp.name,
        'email' : c.email,
        'addr' : cp.addr,
        'type' : cp.type
      }
    }

@app.route('/company_delete/', methods=['DELETE'])
def delete_member_company():
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
  
  db.session.delete(c)
  db.session.commit()
  return{
    'user Company berhasil di Hapus'
  }

@app.route('/company_search_user/', methods=['GET'])
def search_user():
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  c = Company.query.filter_by(username=username).first_or_404()

  if c.username != username or c.pas != password:
    return{
      'error' : 'Bad Request',
      'message' : 'username/password tidak benar'
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'hanya untuk member company'
    }

  data = request.get_json()

  if not data :
    return{
      'message' : 'silahkan isi category dengan benar'
    }
  elif not 'search_key' in data:
    return{
      'message' : 'user tidak ditemukan'
    }
  return {'messsage'  : 'Data user ditemukan',
    'Data'  :[{
    'name'  : u.name,
    'email'  : u.email,
    'salary'  : u.graduation,
    'majority'  : u.majority
  } for u in User.query.filter(or_(User.name.like("%"+ data['search_key']+ "%"),
    User.graduation.like("%"+data['search_key']+"%"),
    User.skill.like("%"+ data['search_key']+"%"))).all()]}
  # return{
  #   'message' : 'succes searching data user profile',
  #   'Data'  : [{
  #     'nama'  : u.name,
  #     'email' : u.email
  #   }for u in User.query.filter_by(graduation=data['graduation'])]
  # }

#Job management
@app.route('/company_post/', methods=['POST'])
def company_post_job():

  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  c = Company.query.filter_by(username=username).first_or_404()
  if c.pas != password or c.username !=username :
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
  return{
    'Message'  : 'succes, upload job advertisment',
    'Company' : c.name,
    'Data'  : {
      'name'  : j.name,
      'position' : j.position,
      'salary'  : j.salary,
      'exp' : j.exp,
      'status'  : j.status
    }
  }

@app.route('/company_get_job/', methods=['GET'])
def get_job_id():
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  data = request.get_json() 
  c = Company.query.filter_by(username=username).first()
  j =  Job.query.filter_by(name=data['name']).first()

  if c.username != username or c.pas != password:
    return{
      'error' : 'Bad Request',
      'message' : 'username/password tidak benar'
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'hanya untuk member company'
    }
  elif not j :
    return "Data tidak ditemukan"
  
  return{'message'  : 'succes get job',
    'Data'  :{
    'name' : j.name,
    'position'  : j.position,
    'salary' : j.salary,
    'exp' : j.exp,
    'job_id' : j.id,
    'company_id'  : j.company_id
    }
  }

@app.route('/company_get_all_job/', methods=['GET'])
def job_get():
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  data = request.get_json()
  c = Company.query.filter_by(username=username).first_or_404()
  
  if c.username != username or c.pas != password:
    return{
      'eror'  : 'Bad Request',
      'message' : 'username/password salah'
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'anda bukan company member'
    }
  return{
    'message' : 'succes search list job',
    'Data'  :[{
        'name'  : item.name,
        'position'  : item.position,
        'status'  : item.status,
        'job_id'  : item.id
      }for item in Job.query.filter_by(company_id=data['company_id'])]
    }

@app.route('/company_update_job/<id>/', methods=['PUT'])
def update_job(id):
  parsed = aut()
  username = parsed[0]
  password= parsed[1]
  data = request.get_json()
  c = Company.query.filter_by(username=username).first_or_404()

  j = Job.query.filter_by(id=id).first_or_404()

  if c.username != username or c.pas != password:
    return{
      'error' : 'Bad Request',
      'message' : 'username/password tidak benar'
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'hanya untuk member company'
    }
  elif c.id != j.company_id:
    return{
      'error' : 'id company salah'
    }

  j.name = data.get('name', j.name)
  j.position =  data.get('position', j.position)
  j.salary = data.get('salary', j.salary)
  j.exp = data.get('exp', j.exp)
  j.status = data.get('status', j.status)

  db.session.commit()
  return{'message'  : 'succes update job vacancy',
    'Data'  :{
      'name'  : j.name,
      'position'  : j.position,
      'salary'  : j.salary,
      'exp'  : j.exp,
      'status'  : j.status
    }
  }

@app.route('/company_delete_job/<job_id>', methods=['DELETE'])
def company_delete_job(job_id):
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  c = Company.query.filter_by(username=username).first_or_404()

  if c.username != username or c.pas != password:
    return{
      'error' : 'Bad Request',
      'message' : 'username/password tidak benar'
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'hanya untuk member company'
    }
  up = Job.query.fiter_by(id=job_id).first_or_404()
  db.session.delete(up)
  db.session.commit()
  return{
    'User Berhasil Di hapus'
  }

#Timeline job
# list all available job, search job on criteria, get a job detail, apply job
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

  if not data or not Job:
    return{
      'message' : 'Job sedang tidak tersedia'
    }
  return {'message' : 'succes list job',
    'Data'  : [{
      'name' : item.name,
      'position'  : item.position,
      'salary' : item.salary,
      'exp' : item.exp,
      'status'  : item.status,
      'job_id'  : item.id,
      'company' : item.job_id.name
    }for item in Job.query.filter_by(status= data['status'])
  ]}

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

  js= Job_Application(
    user_id= u.id, 
    job_id =data['job_id'],
    apply_date = datetime.now(),
    status = 'waiting'
    )
  db.session.add(js)
  db.session.commit()

  return{
    'message' : 'succes apply job',
    'Data'  : {
      'status'  : js.status,
      'name'  : u.username,
      'email' : u.email,
      'company' : js.jobapp_id.job_id.name,
      'job_name'  : js.jobapp_id.name
    }
  }

@app.route('/search_job/', methods=['GET'])
def search_job():
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  u= User.query.filter_by(username=username).first()

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
  # j=Job.query.filter_by(name=data['name_job']).first()
  if not data:
    return{
      'message' : 'Job sedang tidak tersedia'
    }
  return {'messsage'  : 'Data ditemukan',
    'Data'  :[{
    'name'  : m.name,
    'position'  : m.position,
    'salary'  : m.salary
  } for m in Job.query.filter(or_(Job.name.like("%"+ data['search']+ "%"),Job.position.like("%"+data['search']+"%"))).all()]}
  # return{'message'  : 'succes',
  #   'Data'  : {
  #     'name'  : j.name,
  #     'position' : j.position,
  #     'salary'  : j.salary,
  #     'exp' : j.exp,
  #     }
  #   }

@app.route('/user_get_job/<id>/', methods=['GET'])
def user_get_job(id):
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
  j= Job.query.filter_by(id=id).first()
  return{'message'  : 'succces for searching job',
  'Data'  : {
      'job_name'  : j.name,
      'company' : j.job_id.name,
      'email' :j.job_id.email,
      'addr'  : j.job_id.addr
    }
  }

@app.route('/user_list_apply_status/<id>/', methods=['GET'])
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
  
  return{'message'  : 'list apply job status',
    'Data'  :[{
      'status' : item.status,
      'job_name' : item.jobapp_id.name,
      'company' : item.jobapp_id.job_id.name,
      'date'  : item.response_date
    }for item in Job_Application.query.filter_by(user_id=id)]
  }

@app.route('/company_get_profile_user/<id>/', methods=['GET'])
def get_profil_user(id): 
  parsed = aut()
  username = parsed[0]
  password= parsed[1]
  
  c = Company.query.filter_by(username=username).first_or_404()

  if c.username != username or c.pas != password:
    return{
      'error' : 'Bad request',
      'message' : 'username/password salah '
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'anda bukan member user'
    } 
  # data= request.get_json()
  u_p = User.query.filter_by(id=id).first_or_404()

  return{'message'  : 'succes get profile user',
    'Data'  :{
      'nama'  : u_p.name,
      'email' : u_p.email,
      'telephone' : u_p.telephone,
      'tanggal_lahir' : u_p.ttl,
      'graduation' : u_p.graduation,
      'majority'  : u_p.majority,
      'skill' : u_p.skill
    }
  }

@app.route('/company_list_applicant/', methods=['GET'])
def list_applicant(): 
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  data = request.get_json()

  c = Company.query.filter_by(username=username).first_or_404()
  j = Job.query.filter_by(id=data['job_id']).first()

  if c.username != username or c.pas != password:
    return{
      'error' : 'Bad request',
      'message' : 'username/password salah '
    }
  elif c.role_comp != 'company':
    return{
      'message' : 'anda bukan member user'
    }
  elif  not j:
    return{
      'message' : 'lowongan tidak sesuai'
    }
  return{'message'  : 'succes get user applicant',
    'data'  : [{
      'status'  : ja.status,
      'user_applicant' : ja.user_app_id.name,
      'email_applicant' : ja.user_app_id.email,
      'job_apply' : ja.jobapp_id.name,
      'position_apply'  : ja.jobapp_id.position
    }for ja in Job_Application.query.filter_by(job_id=data['job_id'])]
  }

@app.route('/company_update_status/user/<user_id>/job/<job_id>/', methods=['PUT'])
def comp_update_status(user_id,job_id):
  parsed = aut()
  username = parsed[0]
  password= parsed[1]

  c = Company.query.filter_by(username=username).first_or_404()
  if c.pas != password or c.username !=username :
    return{
      'error' : 'Bad Request',
      'mesage' : 'Username/Kata sandi salah'
    } 
  elif c.role_comp != 'company':
    return{
      'message' : 'anda bukan member company'
    }
  
  data =request.get_json()
  js = Job_Application.query.filter_by(user_id=user_id, job_id=job_id).first_or_404()
  js.status = data.get('status_update', js.status)
  js.response_date = datetime.now()

  db.session.commit()

  return{'message'  : 'succes update status job application',
    'Data'  : {
      'status' : js.status,
      'response_date' : js.response_date,
      'user_apply'  : js.user_app_id.name,
      'job_apply' : js.jobapp_id.name,
      'job_position'  : js.jobapp_id.position
    }
  } 

if __name__ == '_main_':
  app.run()
  