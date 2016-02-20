#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import re
import jinja2
from google.appengine.ext import db
import random
import hashlib
import string
import urllib2
from xml.dom import minidom
import json
import logging
import time

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

def make_salt():
	return ''.join(random.choice(string.letters) for x in xrange(5))
def make_hash(username, password, salt):
		return hashlib.sha256(username + password + salt).hexdigest()

class userDB(db.Model):
	username = db.StringProperty(required = True)
	salt = db.StringProperty(required = True)
	hashedPassword = db.StringProperty(required = True)
	firstName = db.StringProperty(required = True)
	lastName = db.StringProperty(required = True)
	email = db.StringProperty(required = True)
	phone = db.StringProperty(required = True)
	credit = db.FloatProperty(required = True)
	creat_time = db.DateTimeProperty(auto_now_add = True)

class classDB(db.Model):
	classID = db.StringProperty(required = True)
	time = db.StringProperty(required = True)
	location = db.StringProperty(required = True)
	price = db.IntegerProperty(required = True)
	capacity = db.IntegerProperty(required = True)
	occupancy = db.IntegerProperty(required = True)
	topic = db.StringProperty()
	note = db.StringProperty()
	active = db.BooleanProperty(required = True)
	creat_time = db.DateTimeProperty(auto_now_add = True)

class registerDB(db.Model):
	classID = db.StringProperty(required = True)
	username = db.StringProperty(required = True)
	creat_time = db.DateTimeProperty(auto_now_add = True)

class notificationDB(db.Model):
	title = db.StringProperty()
	contents = db.StringProperty()
	creat_time = db.DateTimeProperty(auto_now_add = True)

# classDB(classID="CSC108-0101", time="csd", location="dksdc", price=10, capacity=5, occupancy=0, topic="csbdh", note="ncdjks", active=True).put()
# notificationDB(title="bcsikjdscbskdj", contents="csndjksdbasjkdaskjfb").put()

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.write(*a, **kw)
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
class MainHandler(Handler):
	def get(self):
		classEntries = db.GqlQuery("SELECT * FROM classDB WHERE active=:1", True)
		notificationEntries = db.GqlQuery("SELECT * FROM notificationDB")
		self.render("index.html", classEntries=classEntries, notificationEntries=notificationEntries)

class signUp(Handler):
	secret = "cnsk32cds"
	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		firstName = self.request.get("firstName")
		lastName = self.request.get("lastName")
		phone = self.request.get("phone")
		email = self.request.get("email")
		if db.GqlQuery("SELECT * FROM userDB WHERE username=:1", username).count()!=0:
			self.write("1")
		else:
			salt = make_salt()
			hashedPassword = make_hash(username, password, salt)
			userDB(username=username, salt=salt, hashedPassword=hashedPassword, firstName=firstName, lastName=lastName, email=email, phone=phone, credit=0.0).put()
			cookie= str("username=" + username + '|' + hashlib.sha256(username+self.secret).hexdigest())
			self.write(cookie)
class logIn(Handler):
	secret = "cnsk32cds"
	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		cursor = db.GqlQuery("SELECT * FROM userDB WHERE username=:1", username)
		if cursor.count() == 0:
			self.write("The username does not exist!")
		else:
			entry = cursor.get()
			salt = entry.salt
			hashedPassword = make_hash(username, password, salt)
			if hashedPassword != entry.hashedPassword:
				self.write("Incorrect password!")
			else:
				cookie= str("username=" + username + '|' + hashlib.sha256(username+self.secret).hexdigest())
				self.write(cookie)

class managePage(Handler):
	secret = "cnsk32cds"
	def get(self):
		username_path = self.request.get("username")
		cookies = self.request.cookies.get('username', None)
		if not cookies:
			self.redirect('/')   #no cookies
		else:
			username_cookie = cookies.split("|")[0]
			if username_cookie != username_path:   #do not have cookies with the same username
				self.redirect('/')
			else:
				hashedUsername = cookies.split("|")[1]
				hashedUsernameMatch = str(hashlib.sha256(username_cookie+self.secret).hexdigest())
				if hashedUsername != hashedUsernameMatch:
					self.redirect('/')          #hash do not match
				else:
					cursor = db.GqlQuery("SELECT * FROM userDB WHERE username=:1", username_cookie)
					if cursor.count() == 0:   # username not in database
						self.redirect('/')
					else:
						notificationEntries = db.GqlQuery("SELECT * FROM notificationDB")
						booked = []
						registerEntries = db.GqlQuery("SELECT * FROM registerDB WHERE username=:1", username_path)
						for registerEntry in registerEntries:
							if registerEntry.username == username_path:
								booked.append(registerEntry.classID)
						classEntries = db.GqlQuery("SELECT * FROM classDB WHERE active=:1", True)
						entry = cursor.get()
						self.render("manage.html", entry=entry, classEntries=classEntries, booked = booked, notificationEntries=notificationEntries)
	def post(self):
		classID = self.request.get("classID")
		cookies = self.request.cookies.get('username', None)
		if not cookies:
			self.write("sessionExpired")
		else:
			username = cookies.split("|")[0]
			hashedUsername = cookies.split("|")[1]
			hashedUsernameMatch = str(hashlib.sha256(username+self.secret).hexdigest())
			if hashedUsername != hashedUsernameMatch:
				self.write("sessionExpired")         #hash do not match
			else:
				cursor = db.GqlQuery("SELECT * FROM userDB WHERE username=:1", username)
				if cursor.count() == 0:   # username not in database
					self.write("sessionExpired")
				else:
					if db.GqlQuery("SELECT * FROM registerDB WHERE username=:1 AND classID=:2", username, classID).count() != 0:
						self.write("alreadyReserved")   #already reserved
					else:
						classEntry = db.GqlQuery("SELECT * FROM classDB WHERE classID=:1", classID).get()
						if classEntry.occupancy >= classEntry.capacity:
							self.write("full")    #class is full
						else:
							moneyHave = cursor.get().credit
							moneyCost = db.GqlQuery("SELECT * FROM classDB WHERE classID=:1", classID).get().price
							if moneyCost - moneyHave <= 30:   #allow $30 credit  OK
								self.write("yes")
							else:
								self.write("lackMoney")   #money not enough
class makeReservation(Handler):
	secret = "cnsk32cds"
	def post(self):
		classID = self.request.get("classID")
		cookies = self.request.cookies.get('username', None)
		if not cookies:
			self.write("sessionExpired")
		else:
			username = cookies.split("|")[0]
			hashedUsername = cookies.split("|")[1]
			hashedUsernameMatch = str(hashlib.sha256(username+self.secret).hexdigest())
			if hashedUsername != hashedUsernameMatch:
				self.write("sessionExpired")         #hash do not match
			else:
				cursor = db.GqlQuery("SELECT * FROM userDB WHERE username=:1", username)
				if cursor.count() == 0:   # username not in database
					self.write("sessionExpired")
				else:
					classEntry = db.GqlQuery("SELECT * FROM classDB WHERE classID=:1", classID).get()
					price = classEntry.price
					classEntry.occupancy += 1
					classEntry.put()
					entry = cursor.get()
					entry.credit -= price
					entry.put()
					registerDB(classID=classID, username=username).put()
					self.write("You have successfully registered the class: " + classID)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/signUp', signUp),
    ('/manage', managePage),
    ('/makeReservation', makeReservation),
    ('/logIn', logIn)
], debug=True)
