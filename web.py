from flask import Flask, request, render_template
from wtforms import Form, TextField, TextAreaField, PasswordField, validators
from flask.ext.sqlalchemy import SQLAlchemy
from usercenter import UserCenter

app = Flask(__name__)
app.debug=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DAVShare.db'
db = SQLAlchemy(app)
uc = UserCenter("/var/www/webdav/", db)

class ChangePasswdForm(Form):
	username = TextField("Username", [validators.Required()])
	old_password = PasswordField("Old Password", [validators.Required()])
	new_password = PasswordField('New Password', [
		validators.Required(),
		validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = PasswordField('Repeat Password')

class AddUserForm(Form):
	users = TextAreaField("Users", [validators.Required()])

class DeleteUserForm(Form):
	users = TextField("Users", [validators.Required()])

@app.route("/", methods=["GET"])
def index():
	return render_template("davshare.html")

@app.route("/chpasswd", methods=["GET", "POST"])
def changePasswd():
	form = ChangePasswdForm(request.form)
	if request.method == "POST" and form.validate():
		error = uc.chpasswd(form.username.data, form.old_password.data, form.new_password.data)
		if error == 0:
			return "Succeed!"
		elif error == -1:
			return "No such user!"
		elif error == -2:
			return "Old password is wrong!"
	return render_template("chpasswd.html", form=form)

@app.route("/useradmin", methods=["GET"])
@app.route("/useradmin/<method>", methods=["POST"])
def useradmin(method=None):
	add_form = AddUserForm(request.form)
	delete_form = DeleteUserForm(request.form)
	if request.method == "POST":
		if method == "add" and add_form.validate():
			for line in add_form.users.data.splitlines():
				line = line.strip()
				if not line:
		 			continue
				userinfo = line.split()
				if len(userinfo) != 3:
					continue
				username, password, description = userinfo
				uc.add(username, password, description)
		elif method == "delete" and delete_form.validate():
			users = delete_form.users.data.split(",")
			for user in users:
				uc.delete(user)
	return render_template("useradmin.html", add_form=add_form, del_form=delete_form, users=uc.list())

if __name__ == '__main__':
	if not os.path.exists("/var/www/DAVShare/DAVShare.db"):
		db.create_all()
	uc.add("admin", "admin", "admin")
