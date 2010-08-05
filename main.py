#!/usr/bin/env python
# -*- coding: latin-1 -*-
## VERSION: Donnerstag 5 August 2010 12:03

import smtplib
#from  mechanize import Browser
import json
import urllib2
import getpass
import sqlite3
import base64
import sys



def user_pass(USERNAME="", PASSPHRASE="", EMAIL=""):
	while USERNAME=="" or PASSPHRASE=="" or EMAIL=="":
		if USERNAME=="":
			USERNAME=getpass.getuser() #for default user
			tmp_user = raw_input('Twitter username ['+str(USERNAME)+']: ')
			if tmp_user!="":
				USERNAME=tmp_user
		if PASSPHRASE=="":
			PASSPHRASE=getpass.getpass("Twitter password: ") #silent password FTW
		if EMAIL=="":
			EMAIL=getpass.getuser()+"@localhost" #for default user
			tmp_email = raw_input('Send to this Email['+ str(getpass.getuser())+'@localhost]: ')
			if tmp_email!="":
				EMAIL=tmp_email	
	return [USERNAME, PASSPHRASE, EMAIL]

def main(argv=None):
	import os.path
	if not os.path.exists(os.path.expanduser('~/.tweet2email/')):
		os.mkdir(os.path.expanduser('~/.tweet2email/'))
		[user, password, email]=user_pass()
		conn=sqlite3.connect(os.path.expanduser('~/.tweet2email/database'))
		c=conn.cursor()
		c.execute('''create table user(name text, password text, email)''')
		c.execute('''create table history(id text)''')
		c.execute('insert into user values( ? , ?, ?)', [user, password, email])
		conn.commit()
		c.close()

	conn=sqlite3.connect(os.path.expanduser('~/.tweet2email/database'))
	c=conn.cursor()
	c.execute('select * from user')
	[user,password, email]=c.fetchone()

	t=tweet2email(user, password)
	[id, name]=t.getfriendsid()
	for i in range(0,len(id)):
		[msg,msg_id]=t.get_tweets(id[i])
		print str(i)+") "+str(name[i])+" with "+str(len(msg_id))+" messages\n"
		for j in range(0,len(msg_id)):
			print "- "+str(msg_id[j])+"\n"
			c.execute('select * from history where id=?',(msg_id[j],))
			z=c.fetchone()
			if not z:
				try:
					sendmail(msg[j], email, name[i])
					c.execute('insert into history(id) values (?)', (msg_id[j],))
					conn.commit()
				except:
					print "Trouble sending and commiting\n"
					continue
			else:
				continue
	c.close()

class tweet2email:
	def __init__(self, username, password):
		self.header=self.auth_header(username,password)
	def show_friends(self):
		[id, name]=getfriendsid()
		for i in range(0,len(id)):
			print str(name[i])+" : "+ str(id[i])

	def getfriendsid(self):
		url="https://twitter.com/statuses/friends.json"
		req = urllib2.Request(url)
		req.add_header("Authorization", self.header)
		try:
			handle = urllib2.urlopen(req)
		except IOError, e:
		    # here we shouldn't fail if the username/password is right
		        print "It looks like the username or password is wrong."
			sys.exit(1)
		friendslist=json.loads(handle.read())
		friends_id=[]
		friends_name=[]
		for i in friendslist:
			friends_id.append(i['id'])
			friends_name.append(i['screen_name'])

		return [friends_id, friends_name]


	def get_tweets(self,id):
		url = 'https://twitter.com/statuses/user_timeline/'+str(id)+'.json?count=5'
		req = urllib2.Request(url)
		req.add_header("Authorization", self.header)
		try:
			handle = urllib2.urlopen(req)
		except IOError, e:
			if e.code == 401:
				print "wahrscheinlich zu viele requests\n\r"
			else:
				print str(url)+"\n"
				print "was ist hier denn passiert?"
			sys.exit(1)
		msg=json.loads(handle.read())
		txt=[]
		msg_id=[]
		if len(msg)==0:
			print "Keine rückgabe\n"
		for i in msg:
			txt.append(i['text'])
			msg_id.append(i['id'])
		return [txt, msg_id] 

	def auth_header(self, username, password):
		header=[];
		if username and password:
			basic_auth = base64.encodestring('%s:%s' % (username, password))[:-1]
			header = 'Basic %s' % basic_auth
		return header 

def sendmail(message, user, email, tweeter ):
	msg= "From: tweet2email@localhost\r\nTo: "+email+"Subject: [tweet2email]: "+tweeter+"\r\n\r\n"+message
	server = smtplib.SMTP('localhost')
	server.sendmail("tweet2email@localhost", email, msg)
	server.quit()

if __name__ == "__main__":
	main(sys.argv)
