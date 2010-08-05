#!/usr/bin/env python
# -*- coding: latin-1 -*-
## VERSION: Donnerstag 5 August 2010 12:03

import smtplib
from  mechanize import Browser
import gepass


def user_pass(USERNAME="", PASSPHRASE=""):
	while USERNAME=="" or PASSPHRASE=="":
		if USERNAME=="":
			USERNAME=getpass.getuser() #for default user
			tmp_user = raw_input('Twitter username ['+str(USERNAME)+']: ')
			if tmp_user!="":
				USERNAME=tmp_user
		if PASSPHRASE=="":
			PASSPHRASE=getpass.getpass("Twitter password: ") #silent password FTW
	return [USERNAME, PASSPHRASE]

def main(argv=None):


if __name__ == "__main__":
	main(sys.argv)

