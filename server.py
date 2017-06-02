import socket
import os,sys,re
from datetime import *
import random
from stat import *
import threading,time
def longlist(conn):

	files = [f for f in os.listdir('.') if os.path.isfile(f)] #select files in folder
	
	try:
		for i in files:
			if os.stat(i).st_size != 0:   #file size is finite,non zero
				command = "stat --printf 'Name: %n \t Type: %F \t  Size: %s bytes \t  Timestamp: %z\n' " + i
				myres = os.popen(command).read()
				conn.send(myres)
				if conn.recv(1024) != "recieved":
					break
		conn.send(" ")
		conn.recv(1024)
		conn.send("done")
	except:
		print "Bad Connec. @ longlist()"
		return
	

def shortlist(conn, args):
	inp = args.split()
	t1 = float(inp[2])
	t2 = float(inp[3])
	
	cmd = "stat --printf 'Name: %n \t Type: %F \t  Size: %s bytes \t  Timestamp: %z\n' "
	files = [f for f in os.listdir('.') if os.path.isfile(f)]  #select files in folder
	
	try:
		for i in files:
			if os.stat(i).st_size != 0:
				t = os.stat(i).st_mtime
				tstamp = str(datetime.fromtimestamp(t))
				if t >= t1 and t <= t2:
					command = cmd + i
					myres = os.popen(command).read()
					conn.send(myres)
					if conn.recv(1024) != "recieved":
						break
		conn.send(" ")
		conn.recv(1024)
		conn.send("done")
	except:
		print "Bad Connec @ shortlist() "
		return
					
		
def regex(conn, args):
	inp = args.split()
	pattern = str(inp[2])
	print pattern
	cmd = "stat --printf 'Name: %n \t Type: %F \t  Size: %s bytes \t  Timestamp: %z\n' "
	files = [f for f in os.listdir('.') if os.path.isfile(f)]  #select files in folder
	flag = True   #assuming no matching file is present
	try:
		for i in files:
			if os.stat(i).st_size != 0:
				name = str(i)
				print name
				mat = re.search(pattern, name)
				print mat
				if mat:
					command = cmd + i
					myres = os.popen(command).read()
					conn.send(myres)
					flag = False
					if conn.recv(1024) != "recieved":
						break
		
		if flag == True:
			conn.send("No Files found")
		conn.send(" ")
		conn.recv(1024)
		conn.send("done")
	except:
		print "Bad Connec @ regex() "
		return
					
				

def verify(flag, conn, filename):
	
	fname = filename 
	cmd = "stat --printf '%z\n' "
	command1 = cmd + fname
	check = os.popen(command1).read().split('\n')
	b = check[0]  #eg::  b = '2017-03-22 00:00:00.55664 + 0530'
			
	if b == "":
		conn.send("File doesn't exist")
			
	else:
		try:
			command2 = "cksum " + fname
			h = os.popen(command2).read().split('\n')
			h = h[0].split()
			h = "checksum: " + h[0] + "\n"
			string = "File: " + fname
			t = "Last Modified: " + b
			res = [string, t, h]
			for j in res:
				conn.send(j)
				if conn.recv(1024) != "recieved":
					break
		except:
			print "Bad Connec @ verify() "
			return
		if flag == True:
			conn.send(" ")
			conn.recv(1024)
			conn.send("done")
		
def checkall(conn, args):
	files = [f for f in os.listdir('.') if os.path.isfile(f)]  #select files in folder
	for i in files:
		if i != "":
			verify(False , conn, i)
	conn.send("done")




def newport(socket):
	new_port = random.randint(1000, 9000)
	try:
		socket.bind((host, new_port))
	except:
		newport(socket)
	
	return new_port	




	

def filesend(flg, conn, args):
	inp = args.split()
	filename = " ".join(inp[2:])
	perm = oct(os.stat(filename)[ST_MODE])[-3:]

	cmd = "stat --printf 'Name: %n \t Type: %F \t  Size: %s bytes \t  Timestamp: %z\n' "
	t = os.popen('ls "' + filename + '"').read().split('\n')
	if t[0] == "":
		conn.send("File doesn't exist")
		return
	conn.send("recieved")
	
	if flg == "TCP":
		try:
			if conn.recv(1024) == "send file perm":
				conn.send(perm)
			else:
				print "file perm not sent"
			message = conn.recv(1024)
			if message == "recieved file perm":
				print "recieved at client"
			else:	
				print "not recieved at client"
			
			
			f = open(filename, 'rb')
			l = f.read(1024)
			while l:
				conn.send(l)
				if conn.recv(1024) != "recieved":
					break
				l = f.read(1024)
			conn.send("done")
		except:
			print "Bad Connec @ TCP filesend() "
			return

	elif flg == "UDP":
		new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		new_port = newport(new_socket)
		conn.send(str(new_port))
		data, addr = new_socket.recvfrom(1024)
		if data == "recieved":
			try:
				data, addr = new_socket.recvfrom(1024)
				if data == "send file perm":
					new_socket.sendto(perm, addr)
				else:
					print "file perm not sent"

				data, addr = new_socket.recvfrom(1024)
				if data == "recieved file perm":
					print "recieved at client"
				else:
					print "not recieved at client"	 


				f = open(filename, 'rb')
				l = f.read(1024)
				while l:
					new_socket.sendto(l, addr)
					data, addr = new_socket.recvfrom(1024)
					if data != "recieved":
						break
					l = f.read(1024)
				new_socket.sendto("done", addr)
			except:
				print "Bad Connec @ filesendUDP() "
				return
	else:
		print "Check arguments passed"
		return

	#print "PArt DOne"			
	h = os.popen(" md5sum " + filename + " ").read().split()
	h = h[0]
	conn.send(h)
	command2 = cmd + filename
	myres = os.popen(command2).read()
	print "myres is ", myres
	if conn.recv(1024) == 'OK':
		conn.send(myres)
		print "done"

		

def filesync(conn):
	msg = conn.recv(1024)
	files = [f for f in os.listdir('.') if os.path.isfile(f)] #select files in folder
	cnt = 0
	for i in files:
		cnt = cnt + 1

	cnt = str(cnt)
	print "cnt is ", cnt
	if msg == "send files":
		try:
			for i in files:
				conn.send(i)
				if conn.recv(1024) != "file recieved":
					break
			conn.send("files sent")		 
		
		except:
			print "bad connection"
			return
		if conn.recv(1024) == "recieved cnt":
			try:
				for i in files:
					conn.send(i)
					conn.recv(1024)
					t = time.ctime(os.path.getmtime(i))
					conn.send(t)
					conn.recv(1024)					
				conn.send("done")
			except:
				print "bad connection"
				return

		
		flg = 0
		while flg == 0:
			if s.recv(1024) == "TCP Send":
				conn.send("send file name")
				filename = conn.recv(1024)
				conn.send("file recieved")
				conn.recv(1024)
				
				f = open(filename, 'rb')
				l = f.read(1024)
				while l:
					conn.send(l)
					if conn.recv(1024) != "recieved":
						break
					f.write(l)	
				f.close()
				conn.send("done")
				conn.recv(1024)
				perm = oct(os.stat(filename)[ST_MODE])[-3:]
				conn.send(perm)
				if conn.recv(1024) == "flag":
					flg = 1
					break
			
	else:
		print "bad connection"
		return
			








port= 60015
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ""

s.bind((host, port))
s.listen(5)

log = open("server.log", "a+")

print 'Server listening....'
currtime = datetime.now().strftime("%I:%M%p %B %d, %Y")
log.write("Start Time: " + currtime + "\n")
logcnt = 0



while True:
	logcnt += 1
	try:
		conn, addr = s.accept() #conn->new socket object to send/recive data. addr->address bound to socket on other end of connec.
		log.write("connection-> " + str(addr) + "\n")
	except:
		s.close()
		currtime3 = datetime.now().strftime("%I:%M%p %B %d, %Y")
		log.write("Close Time " + currtime3  +  "\n")
		log.close()
		exit(0)

	while True:
		print 'Got connection from', addr
    		
		try:
			data = conn.recv(1024)     #msg from client

    		except:
			print "Connection to client closed"
			break

		p = data.split(" ")
		
		if len(p) == 0:                       #no arguments passed
			conn.close()
			currtime1 = datetime.now().strftime("%I:%M%p %B %d, %Y")
			log.write( "Close time is" + currtime1 + "connection closed\n")
			log.close()
			print "Connec. to client closed"
			break
		
		elif p[0] == "index":
			if p[1] == "longlist":
				longlist(conn)
				log.write("called index longlist \n")
			elif p[1] == "shortlist":
				shortlist(conn, data )
				log.write("called index shortlist \n")
			elif p[1] == "regex":
				regex(conn, data)
				log.write("called index regex \n")
		
		elif p[0] == "hash":
			if p[1] == "verify":
				verify(True, conn, p[2])
				log.write("called hash verify \n")
			elif p[1] == "checkall":
				checkall(conn, data)
				log.write("called hash checkall \n")
		
		elif p[0] == "download":
			if p[1] == "TCP":
				filename = " ".join(p[2:])
				log.write("called download TCP \n")
				filesend("TCP", conn, data)
			elif p[1] == "UDP":
				filesend("UDP", conn, data)
				log.write("called download UDP \n")

		elif p[0] == "filesync":
			filesync(conn)
				
		else:
			break
	conn.close()
	currtime2 = datetime.now().strftime("%I:%M%p %B %d, %Y")
	log.write("Close Time: " + currtime2 + "\n")
	log.close()
    









