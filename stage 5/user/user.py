from flask import Flask, render_template , request ,jsonify
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

app=Flask(__name__)

@app.route('/')

@app.route("/api/v1/users",methods=['POST'])
def add_users():
	global count
	count = count + 1
	r={}
	ip=request.get_json()
	if request.method != 'POST':
		return jsonify(r),405
	name=ip['username']
	pas=ip['password']

	f = open("/app/some/users.txt",'r')
	user = json.load(f)
	if name in user.keys():
		return jsonify(r),400

	if len(pas) != 40:
		return jsonify(r),400
	try:
		sha_int = int(pas, 16)
	except ValueError:
		return jsonify(r),400

	user[name] = pas
	f = open("/app/some/users.txt",'w')
	json.dump(user,f)
	f.close()

	return jsonify(r),201



@app.route("/api/v1/users/<username>",methods=['DELETE'])
def remove(username):
	global count
	count = count + 1
	r={}
	if request.method != 'DELETE':
		return jsonify(r),405

	f = open("/app/some/users.txt",'r')
	user=json.load(f)
	f.close()
	if username in user.keys():
		del user[username]
		f=open("/app/some/users.txt",'w')
		json.dump(user,f)
		f.close()
		return jsonify(r),200
	else:
		return jsonify(r),400

@app.route("/api/v1/users",methods=['GET'])
def list_users():
	global count
	r=[]
	count=count + 1
	if request.method != 'GET':
		return jsonify(r),405

	fp=open("/app/some/users.txt","r")
	temp=json.load(fp)
	fp.close()

	if not temp:
		return jsonify(r),204

	for i in temp.keys():
		r.append(i)

	return jsonify(r),200

@app.route("/api/v1/_count",methods=['GET','DELETE'])
def total_count():
	global count
	r={}
	x=[]
	if request.method not in ['GET','DELETE'] :
		return jsonify(r),405

	if request.method == 'GET':
		x.append(count)
		return jsonify(x),200

	if request.method == 'DELETE':
		count=0
		return jsonify(r),200


if __name__=='__main__':
	app.run(host='0.0.0.0',port=80,debug=True)
