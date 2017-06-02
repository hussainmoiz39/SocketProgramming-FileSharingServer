import socket                   
import os,sys
import hashlib
from datetime import *
from stat import *
import threading,time

def close():
	currtime2 = datetime.now().strftime("%I:%M%p %B %d, %Y")
	log.write(str(logcnt) + " closing at " + currtime2 + "\n")
	log.close()
	s.close()
	exit(0)


def recvdata(args):
	try:
		s.send(args)
		#print "sent"
	except:
		print "Bad Connection1"
		return
	while True:
	 	try:
	 		msg = s.recv(1024)
		except:
			print "Bad Connection2"
			close()
			break
		if msg == "done":
		 	break
		try:
			s.send("recieved")
		except:
			print "Connection Error"
			close()
		print msg		
	return	 


def filerecv(args, filename):
	inp = args.split()
	s.send(args)
	msg = s.recv(1024)


	if inp[1] != "TCP" and inp[1]!="UDP":
		print "Enter correct flags- TCP or UDP"
		return
	if msg != "recieved" :
		print msg
		return
	if inp[1] == "TCP":
		s.send("send file perm")
		perm = s.recv(1024)	
		#print "file perm are: ", perm
		#print "type of perm is", type(perm)
		s.send("recieved file perm")
		
		try:
			f = open(filename, 'wb+')
		except:
			print "check permission/space"
			return
		while True:
			data = s.recv(1024)
			if data == "done":
				break
			f.write(data)
			s.send("recieved")
		f.close()
		b = int(perm, 8)
		os.chmod(filename, b)
		#perm = oct(os.stat(filename)[ST_MODE])[-3:]
		#print "File perms are: ", perm
		
	if inp[1] == "UDP":
		new_port = int(s.recv(1024))
		new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		addr = (host, new_port)
		new_socket.sendto("recieved", addr)
		new_socket.sendto("send file perm", addr)
		data, addr = new_socket.recvfrom(1024)
		perm = data
		new_socket.sendto("recieved file perm", addr)
		#print "fileperm is ", perm
		try:
			f = open(filename, 'wb+')
		except:
			print "check permissions or space"
			return
		while True:
			data, addr = new_socket.recvfrom(1024)
			if data == "done":
				break
			f.write(data)
			new_socket.sendto("recieved", addr)
		f.close()
		b = int(perm, 8)
		os.chmod(filename, b)
		#perm = oct(os.stat(filename)[ST_MODE])[-3:]
		#print "file perm are now", perm	
		new_socket.close()	


	hrecv = s.recv(1024) #recieved hash
	f = open(filename,'rb')
	horig = hashlib.md5(f.read()).hexdigest() #original hash
	if horig != hrecv:
		print "File sent failed"
	else:
		s.send("OK")
		data = s.recv(1024)
		print data
		print "md5hash: " , hrecv
		print "Download Success"




def syncfunc():
	mtimec = {}
	for i in os.listdir('.'):
		mtimec[i] = time.ctime(os.path.getmtime(i))
	try:	
		s.send("filesync")  #call to in server
	except:
		print "bad connection.sync failed"
	
	#serverfiles = {}
	s.send("send files")
	flg = 0
	cnt = 0
	while flg == 0:
		t = s.recv(1024)
		if t == "files sent":
			flg = 1
			break
		cnt = cnt + 1	
		#serverfiles.append(t)
		s.send("file recieved")
		
	'''str x
	x = s.recv(1024)
	print x
	x = int(x)
	s.send("recieved cnt")'''

	mtimes = {}
	name = {}
	
	for i in range(cnt):
		name[i] = s.recv(1024)
		s.send("recieved name")
		mtimes[name[i]] = s.recv(1024)
		s.send("recieved mtime")
	
	for i in range(cnt):
		if (str(name[i]) not in mtimec) or comp(mtimec[name[i]], mtimes[name[i]]) == 0:
			s.send("TCP Send")
			s.recv(1024)
			s.send(name[i])
			s.recv(1024)
			s.send("hi")
			f = open(name[i], 'wb+')
			
			while True:
				l = s.recv(1024)
				if l == done:
					break
				print "Updating file"
				f.write(l)
				s.send("recieved")
			f.close()
			print "File updated"
		

			s.send("send file perm")
			perm = s.recv(1024)
			b = int(perm, 8)
			os.chmod(name[i], b)

	print "Sync Complete"	
	threading.Timer(20, syncfunc).start()
















s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)             
host = ""
port = 60015
s.connect((host,port))
logcnt = 0
log = open("client.log", "a+")
currtime = datetime.now().strftime("%I:%M%p %B %d, %Y")
log.write(str(logcnt) + "Started at " + currtime + "\n")



while True:
	logcnt += 1
	#syncfunc()
	cmd = raw_input("Enter your request: ")
	inp = cmd.split(" ")
	log.write(str(logcnt) + "   " + cmd + "\n")
	if len(inp) == 0 or inp[0] == "close":
		s.send(cmd)
		currtime2 = datetime.now().strftime("%I:%M%p %B %d, %Y")
		log.write(str(logcnt) + " closing at " + currtime2 + "\n")
		close()
	elif inp[0] == "index" or inp[0] == "hash":
		recvdata(cmd)


	elif inp[0] == "download":
		filename = " ".join(inp[2:])
		filerecv(cmd, filename)
	else:
		print "Invalid request"
s.close()	




