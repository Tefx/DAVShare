import subprocess
import os
import base64
import hashlib

def hash_password(password):
	return "{SHA}" + base64.b64encode(hashlib.sha1(password).digest())

def gen_User(db):
	class User(db.Model):
	    username = db.Column(db.String(80), primary_key=True)
	    password = db.Column(db.String(80), unique=False)
	    description = db.Column(db.String(120), unique=False)

	    def __init__(self, username, password, description=""):
	        self.username = username
	        self.password = password
	        self.description = description
	return User

class UserCenter(object):
	def __init__(self, root, db):
		self.session = db.session
		self.User = gen_User(db)
		self.root = root
		self.all_path = os.path.join(self.root, "all")

	def list(self):
		for user in self.User.query.all():
			yield user.username, user.description

	def add(self, username, password, description):
		user = self.User.query.get(username)
		if not user:
			user = self.User(username, hash_password(password), description)
			self.session.add(user)
			self.session.commit()
			home = os.path.join(self.root, username)
			if not os.path.exists(home):
				os.mkdir(home)
			all_mirror = os.path.join(home, "all")
			os.mkdir(all_mirror)
			subprocess.call(["sudo", "mount", "--bind", self.all_path, all_mirror])
		else:
			user.password = hash_password(password)
			user.description = description
			self.session.merge(user)
			self.session.commit()

	def chpasswd(self, username, old_passwd, new_passwd):
		user = self.User.query.get(username)
		if not user:
			return -1
		elif user.password != hash_password(old_passwd):
			return -2
		else:
			user.password = hash_password(new_passwd)
			self.session.merge(user)
			self.session.commit()
			return 0

	def delete(self, username):
		user = self.User.query.get(username)
		if not user:
			return -1
		else:
			self.session.delete(user)
			self.session.commit()
			home = os.path.join(self.root, username)
			all_mirror = os.path.join(home, "all")
			subprocess.call(["sudo", "umount", all_mirror])
			os.rmdir(all_mirror)
			os.rmdir(home)
			return 0
