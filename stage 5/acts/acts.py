from flask import Flask,url_for, render_template , request ,jsonify
import hashlib
import json
import os
import shutil
import datetime
import base64
import binascii
import re
from werkzeug import secure_filename
from flask import request
import requests

count = 0
crash = 0
app= Flask(__name__)

@app.route('/')

@app.route("/api/v1/_health",methods=['GET'])
def health_check():
	r={}
	global crash
	a=crash
	if a==1:
		return jsonify(r),500
	else:
		return jsonify(r),200

@app.route("/api/v1/_crash",methods=['POST'])
def crash_server():
	r={}
	global crash
	crash = 1
	return jsonify(r),200

@app.route("/api/v1/categories",methods=['GET'])
def list_cat():
	r={}
	global crash
	a=crash
	if a==1:
		return jsonify(r),500
	global count
	count =count +1
	if request.method =='GET':
		f=open("/app/some/category.txt",'r')
		r=json.load(f)
		if bool(r)==False:
			return jsonify(r),204
		return jsonify(r),200
	else:
		return jsonify(r),405

@app.route("/api/v1/categories",methods=['POST'])
def add_cat():
	r={}
	global crash
	a=crash
	if a==1:
		return jsonify(r),500
	global count
	count =count +1
	r={}
	if request.method == 'POST':
		f=open("/app/some/category.txt",'r')
		a=json.load(f)
		f.close()
		ip=request.get_json()
		if ip[0] in a.keys():
			return jsonify(r),400
		else:
			cn=ip[0]
			os.mkdir("/app/some/categories/"+cn)
			fp=open("/app/some/categories/"+cn+"/act.txt",'w')
			d=[]
			json.dump(d,fp)
			fp.close()
			n=open("/app/some/category.txt",'r')
			temp=json.load(n)
			temp[cn]=0
			n.close()
			n=open("/app/some/category.txt",'w')
			json.dump(temp,n)
			n.close()
			return jsonify(r),201
	else:
		return jsonify(r),405

@app.route("/api/v1/categories/<categoryName>",methods=['DELETE'])
def rem_cat(categoryName):
	r={}
	global crash
	a=crash
	if a==1:
		return jsonify(r),500
	global count
	count =count +1
	r={}
	if request.method != 'DELETE':
		return jsonify(r),405
	fp=open("/app/some/category.txt",'r')
	temp=json.load(fp)
	fp.close()

	if categoryName not in temp.keys():
		return jsonify(r),400

	del temp[categoryName]

	fp=open("/app/some/category.txt",'w')
	json.dump(temp,fp)
	fp.close()
	shutil.rmtree('/app/some/categories/'+categoryName)
	return jsonify(r),200


@app.route("/api/v1/acts",methods=['POST'])
def upload_act():
	r={}
	global crash
	a=crash
	if a==1:
		return jsonify(r),500
	global count
	count =count +1
	r={}
	if request.method !='POST':
		return jsonify(r),405
	fp=open("/app/some/acts.txt",'r')
	temp=json.load(fp)
	fp.close()

	ip=request.get_json()
	if str(ip['actId']) in temp.keys():
		return jsonify(r),4001

	url="http://3.93.30.59:80/api/v1/users"
	ran=requests.get(url)
	data=ran.json()

	if ip['username'] not in data:
		return jsonify(r),4002

	try:
		datetime.datetime.strptime(ip['timestamp'],'%d-%m-%Y:%S-%M-%H')
	except:
		return jsonify(r),4003

#	if not re.match("^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$",ip['imgB64']):
#		return jsonify(r),4004

	if "upvote" in ip.keys():
		return jsonify(r),4005

	fp=open("/app/some/category.txt",'r')
	temp=json.load(fp)
	fp.close()
	if ip['categoryName'] not in temp.keys():
		return jsonify(r),400

	fp=open("/app/some/acts.txt",'r')
	temp=json.load(fp)
	fp.close()
	actId=ip['actId']
	temp[actId]=ip['categoryName'];
	fp=open("/app/some/acts.txt",'w')
	json.dump(temp,fp)
	fp.close()

	fp=open("/app/some/categories/"+ip['categoryName']+"/act.txt",'r')
	temp=json.load(fp)
	fp.close()
	d={}
	d["actId"]=ip['actId']
	d["username"]=ip['username']
	d["timestamp"]=ip['timestamp']
	d["caption"]=ip['caption']
	d["upvotes"]=0
	d["imgB64"]=ip['imgB64']
	temp.append(d)
	fp=open("/app/some/categories/"+ip['categoryName']+"/act.txt",'w')
	json.dump(temp,fp)
	fp.close()

	fp=open("/app/some/category.txt",'r')
	temp=json.load(fp)
	fp.close()

	temp[ip['categoryName']]=temp[ip['categoryName']]+1
	fp=open("/app/some/category.txt",'w')
	json.dump(temp,fp)
	fp.close()

	return jsonify(r),200

@app.route("/api/v1/categories/<categoryName>/acts",methods=['GET'])
def list_acts_lt100(categoryName):
	r={}
	global crash
	a=crash
	if a==1:
		return jsonify(r),500
	global count
	count =count +1
	r=[]
	if request.method !='GET':
		return jsonify(r),405
	fp=open("/app/some/category.txt",'r')
	temp=json.load(fp)
	fp.close()

	if categoryName not in temp.keys():
		return jsonify(r),204

	print(request.args.get('start'))
	if request.args.get('start') is not None:
		st= int(request.args.get('start'))
		ed= int(request.args.get('end'))
		fp=open("/app/some/categories/"+categoryName+"/act.txt",'r')
		s=json.load(fp)
		fp.close()
		if len(s)<ed or st<0:
			return jsonify(r),413
		elif len(s) == 0:
			return jsonify(r),204
		else:
			s.sort(key=lambda x:x['timestamp'], reverse = True)
			t1=[]
			for i in range(st-1,ed):
				t1.append(s[i])
			print("first")
			return jsonify(t1),200
	elif request.args.get('start') is None:
		fp=open("/app/some/categories/"+categoryName+"/act.txt",'r')
		temp=json.load(fp)
		if len(temp) >= 100 :
			return jsonify(r),413
		elif len(temp) == 0:
			return jsonify(r),204
		else:
			r=temp
			print("hello")
			return jsonify(r),200

@app.route("/api/v1/categories/<categoryName>/acts/size",methods=['GET'])
def list_no_of_acts(categoryName):
	r={}
	global crash
	a=crash
	if a==1:
		return jsonify(r),500
	global count
	count =count +1
	r=[]
	if request.method !='GET':
		return json.dumps(r),405
	fp=open("/app/some/category.txt",'r')
	temp=json.load(fp)
	fp.close()

	if categoryName not in temp.keys():
		return json.dumps(r),204



	fp=open("/app/some/categories/"+categoryName+"/act.txt",'r')
	temp=json.load(fp)
	r.append(len(temp))
	return jsonify(r),200


@app.route("/api/v1/acts/upvote",methods=['POST'])
def upvote():
	r={}
	global crash
	a=crash
	if a==1:
		return jsonify(r),500
	global count
	count =count +1
	r={}

	if request.method!='POST':
		return jsonify(r),405

	fp=open("/app/some/acts.txt",'r')
	temp=json.load(fp)
	fp.close()
	ip=request.get_json()

	x=ip[0]
	z=str(x)
	y=temp[z]

	if str(x) not in temp.keys():
		return jsonify(r),400

	fp=open("/app/some/categories/"+y+"/act.txt",'r')
	t1=json.load(fp)
	fp.close()
	for i in range(len(t1)):
		ab=t1[i]
		if ab['actId']==x:
			ab['upvotes']+=1

	fp=open("/app/some/categories/"+y+"/act.txt",'w')
	json.dump(t1,fp)
	fp.close()
	return jsonify(r),200

@app.route("/api/v1/acts/<actId>",methods=['DELETE'])
def del_act(actId):
	r={}
	global crash
	a=crash
	if a==1:
		return jsonify(r),500
	global count
	count =count +1
	r={}
	if request.method != 'DELETE':
		return jsonify(r),405

	fp=open("/app/some/acts.txt",'r')
	temp=json.load(fp)
	fp.close()

	if actId not in temp.keys():
		return jsonify(r),400

	catn=temp[actId]
	fp=open("/app/some/categories/"+catn+"/act.txt",'r')
	t1=json.load(fp)

	fp.close()

	for i in range(len(t1)):
		ab=t1[i]
		if ab['actId'] == int(actId):
			t1.remove(t1[i])
			fp=open("/app/some/categories/"+catn+"/act.txt",'w')
			json.dump(t1,fp)
			fp.close()
			fp=open("/app/some/acts.txt",'r')
			q=json.load(fp)
			fp.close()
			del q[actId]
			fp=open("/app/some/acts.txt",'w')
			json.dump(q,fp)
			fp.close()
			fp=open("/app/some/category.txt",'r')
			w=json.load(fp)
			fp.close()
			temp=w[catn]
			w[catn]=temp-1
			fp=open("/app/some/category.txt",'w')
			json.dump(w,fp)
			fp.close()
			return jsonify(r),200


@app.route("/api/v1/_count",methods=['GET','DELETE'])
def total_count():
	r={}
	global crash
	a=crash
	if a==1:
		return jsonify(r),500
	global count
	r={}
	x=[]
	if request.method not in ['GET','DELETE'] :
		return jsonify(r),405

	if request.method == 'GET':
		x.append(count)
		return jsonify(x),200

	elif request.method == 'DELETE':
		count =0
		return jsonify(r),200

@app.route("/api/v1/acts/count",methods=['GET'])
def countacts():
	r={}
	global crash
	a=crash
	if a==1:
		return jsonify(r),500
	global count
	count = count + 1
	r=[]
	if request.method !='GET':
		return jsonify(r),405

	fp=open("/app/some/acts.txt",'r')
	temp=json.load(fp)
	fp.close()

	r.append(len(temp))
	return jsonify(r),200

if __name__=='__main__':
	app.run(host='0.0.0.0',port=80,debug=True)
