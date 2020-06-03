#!/usr/bin/env python3
from flask import Flask, render_template, request, json, jsonify
from multiprocessing import Value
from time import sleep
import docker 
import threading
import requests

count=Value('i',0)#this an object of type Value(integer) initialized to 1.

no_of_containers=1#initially no. of containers are one.it represents the no. of containers currently active.

def autoscaling():
	global no_of_containers
	with count.get_lock():
		containers_to_run=int(count.value/20)+1#we are adding 1 as initially we'll have 1 container even if the requests are less than 20
		containers_to_start=containers_to_run - no_of_containers
		print("the number of containers to start are",containers_to_start)
		if(containers_to_start<0):#reducing the containers
			doc_obj2=docker.from_env()
			#the list of containers active.
			container_list_to_read=doc_obj2.containers.list()
			#as containers_to_start will be negative we are making it positive.
			container_flag=-(containers_to_start)
			#container_delete_list will have the list of containers to delete
			container_delete_list=[]
			temp=no_of_containers
			#adding the list of containers to delete to a list.
			while(container_flag!=0):
				container_delete_list.append(int(8000+temp-1))
				container_flag=container_flag-1
				temp=temp-1
			print("the containers to delete are as follows")
			print(' '.join(container_delete_list))
			for i in container_list_to_read:
				if(int(p)==int( 8000 + no_of_containers-1)==True):
					print("container:",i)
						port=i.attrs['NetworkSettings']['Ports']['80/tcp'][0]['HostPort']
						print("port :" ,port)
						print("Number of containers",no_of_containers)
						print("port number to delete", 8000+no_of_containers-1)
						if int(port) in container_delete_list:
							print("container deleted at port :",int(port))
							i.kill()
							no_of_containers=no_of_containers-1
		elif containers_to_start>0:#increasing the containers
			for i in range(containers_to_start):
				doc_obj1=docker.from_env()
				#we are creating a new container
				doc_obj1.containers.run(image='acts',detach=True,volumes={'acts': {'bind': '/app/some','mode': 'rw'}},ports={'80/tcp':8000+(no_of_containers)})
				print("container started",8000+no_of_containers)
				no_of_containers=no_of_containers+1
		else:
			print("there are no containers to start, continuing with the current number of containers")
		count.value=0

def autoscaling_thread():
	print("scaling under work")
	print("please wait!")
	while True:
		sleep(120)
		#we keep checking every 2 minutes for autoscaling.
		autoscaling()

thread2=threading.Thread(target=autoscaling_thread)

def fault_tolerence():
	global no_of_containers
	doc_obj=docker.from_env()
	#the list of containers active.
	container_list_to_read=doc_obj.containers.list()	
	x=0#just a variable to iterate.
	with count.get_lock():
		for i in container_list_to_read:
			port=i.attrs['NetworkSettings']['Ports']['80/tcp'][0]['HostPort']
				response=requests.get('http://localhost:'+str(port)+"/api/v1/_health")
				#we are checking if response code is 200, if not we'll kill the container and build it again.
				if response.status_code!=200:
					print("killing the container ",port)
					#we kill the container if it is not fit.
					i.kill()
					#creating a new container.
					doc_obj.containers.run(image='acts',detach=True,volumes={'acts': {'bind': '/app/some','mode': 'rw'}},ports={'80/tcp':p})
					print("new container created in its place.")
				x=x+1


def fault_tolerence_thread():
	print("fault tolerence thread started")
	while True:
		#we check every second if there is any fault with any active container.
		fault_tolerence()
		sleep(1)



#to check the health of the container, we check by sendind a 'get' request followed by post and then delete ,then we are returning the response from the acts.py .
@app.route("/api/v1/_health", methods=['GET'])
def health_check():
	with count.get_lock():
		port_no=count.value%no_of_containers
		response_from_acts=requests.get('http://localhost:'+str(8000+port_no)+str(request.full_path))
		try:
			data=response_from_acts.json()
			output=app.response_class(response=json.dumps(data),status=response_from_acts.status_code,mimetype='application/json')
		except:
			output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		return output

#we are just making the container crash by makking the global variable crash for that container.
#here we are returning the response from the request to the acts.py wheather it has faled to crash or a succes to crash.
@app.route("/api/v1/_crash",methods=['POST'])
def crash_server():
	with count.get_lock():
		port_no=count.value%no_of_containers
		response_from_acts=requests.get('http://localhost:'+str(8000+port_no)+str(request.full_path))
		output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		return output

#returning the count for number of requests.
@app.route("/api/v1/_count", methods=['GET'])
def return_count():
	with count.get_lock():
		port_no=count.value%no_of_containers
		response_from_acts=requests.get('http://localhost:'+str(8000+port_no)+str(request.full_path))
		output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		try:
			data=response_from_acts.json()
			output=app.response_class(response=json.dumps(data),status=response_from_acts.status_code,mimetype='application/json')
		except:
			output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		return output


#making the count to no. of requests to zero.
@app.route("/api/v1/_count", methods=['DELETE'])
def count_to_zero():
	with count.get_lock():
		port_no=count.value%no_of_containers
		response_from_acts=requests.delete("http://localhost:"+str(8000+port)+str(request.full_path))
		#if response_class doest work try with "return jsonify({}),response_from_acts.status_code"
		output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		return output


flag=0 # this flaag variable is to check if this is the first request.0 means its the first request 1 eans its not the first request.

#this returns the available categories.
@app.route('/api/v1/categories', methods = ['GET'])
def list_categories():
	global flag
	if count.value==0 and flag==0:
		thread2.start()
		flag=1
	with count.get_lock():
		count.value=count.value + 1
		port_no=count.value%no_of_containers
		response_from_acts=requests.get("http://localhost:"+str(8000+port)+str(request.full_path))
		try:
			data=response_from_acts.json()
			output=app.response_class(response=json.dumps(data),status=response_from_acts.status_code,mimetype='application/json')
		except:
			output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		return output

#this adds a category to the list of available categories.
@app.route('/api/v1/categories', methods = ['POST'])
def add_category():
	global flag
	if count.value==0 and flag==0:
		thread2.start()
		flag=1
	with count.get_lock():
		count.value=count.value+1
		port_no=count.value%no_of_containers
		response_from_acts=requests.post("http://localhost:"+str(8000+port)+str(request.full_path))
		output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		return output

@app.route('/api/v1/categories/<categoryName>', methods = ['DELETE'])
def remove_category(categoryName):
	global flag
	if count.value==0 and flag==0:
		thread2.start()
		flag=1
	with count.get_lock():
		count.value=count.value+1
		port_no=count.value%no_of_containers
		response_from_acts=requests.delete("http://localhost:"+str(8000+port)+str(request.full_path))
		#if response_class doest work try with "return jsonify({}),response_from_acts.status_code"
		output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		return output

#list the acts less than 100.
@app.route('/api/v1/categories/<categoryName>/acts', methods = ['GET'])
def list_acts_lt100(categoryName):
	global flag
	if count.value==0 and flag==0:
		thread2.start()
		flag=1
	with count.get_lock():
		count.value=count.value + 1
		port_no=count.value%no_of_containers
		response_from_acts=requests.get("http://localhost:"+str(8000+port)+str(request.full_path))
		try:
			data=response_from_acts.json()
			output=app.response_class(response=json.dumps(data),status=response_from_acts.status_code,mimetype='application/json')
		except:
			output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		return output

#list the number of acts in a particular catgeory.
@app.route('/api/v1/categories/<categoryName>/acts/size', methods = ['GET'])
def list_no_of_acts(categoryName):
	global flag
	if count.value==0 and flag==0:
		thread2.start()
		flag=1
	with count.get_lock():
		count.value=count.value + 1
		port_no=count.value%no_of_containers
		response_from_acts=requests.get("http://localhost:"+str(8000+port)+str(request.full_path))
		try:
			data=response_from_acts.json()
			output=app.response_class(response=json.dumps(data),status=response_from_acts.status_code,mimetype='application/json')
		except:
			output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		return output

#list acts in a range of size.
@app.route('/api/v1/categories/<categoryName>/acts?start=<startRange>&end=<endRange>', methods = ['GET'])
def list_acts_within_range(categoryName,startRange,endRange):
	global flag
	if count.value==0 and flag==0:
		thread2.start()
		flag=1
	with count.get_lock():
		count.value=count.value + 1
		port_no=count.value%no_of_containers
		response_from_acts=requests.get("http://localhost:"+str(8000+port)+str(request.full_path))
		try:
			data=response_from_acts.json()
			output=app.response_class(response=json.dumps(data),status=response_from_acts.status_code,mimetype='application/json')
		except:
			output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		return output

#this is to upvote an act.
@app.route('/api/v1/acts/upvote', methods = ['POST'])
def upvote():
	global flag
	if count.value==0 and flag==0:
		thread2.start()
		flag=1
	with count.get_lock():
		count.value=count.value+1
		port_no=count.value%no_of_containers
		response_from_acts=requests.post("http://localhost:"+str(8000+port)+str(request.full_path))
		output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		return output

#this is to delete an act.
@app.route('/api/v1/acts/<actid>', methods = ['DELETE'])
def delete_act(actid):
	global flag
	if count.value==0 and flag==0:
		thread2.start()
		flag=1
	with count.get_lock():
		count.value=count.value+1
		port_no=count.value%no_of_containers
		response_from_acts=requests.delete("http://localhost:"+str(8000+port)+str(request.full_path))
		#if response_class doest work try with "return jsonify({}),response_from_acts.status_code"
		output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		return output

#this is to upload an act.
@app.route('/api/v1/acts', methods = ['POST'])
def upload_act():
	global flag
	if count.value==0 and flag==0:
		thread2.start()
		flag=1
	with count.get_lock():
		count.value=count.value+1
		port_no=count.value%no_of_containers
		response_from_acts=requests.post("http://localhost:"+str(8000+port)+str(request.full_path))
		output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		return output

#returns the count of the acts
@app.route('/api/v1/acts/count',methods=['GET'])
def countacts():
	global flag
	if count.value==0 and flag==0:
		thread2.start()
		flag=1
	with count.get_lock():
		count.value=count.value + 1
		port_no=count.value%no_of_containers
		response_from_acts=requests.get("http://localhost:"+str(8000+port)+str(request.full_path))
		try:
			data=response_from_acts.json()
			output=app.response_class(response=json.dumps(data),status=response_from_acts.status_code,mimetype='application/json')
		except:
			output=app.response_class(response=json.dumps({}),status=response_from_acts.status_code,mimetype='application/json')
		return output


app=Flask(_name)
# we are starting the fault tolerence thread.
thread1=threading.Thread(target=fault_tolerence_thread)
thread1.start()
#we are running this app at port 80 in local host of acts virtual machine(VM).
#this app sends the request to app.py using 
app.run(host='0.0.0.0',port='80',debug=True)