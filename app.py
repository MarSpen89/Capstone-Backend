from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash
import os
from faker import Faker

from auth import decrypt_data, encrypt_data

app = Flask(__name__)
CORS(app)
#basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] ="postgresql://ennyxfplcevzvw:956c6a148b3655ad89c612615fb2ab3e634ab8786474899623ee312049301dea@ec2-54-234-13-16.compute-1.amazonaws.com:5432/dapmtl4iufh0r0"
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'app.sqlite')
app.config['SECRET_KEY'] = 'fym-yagmm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)

fake = Faker()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ("id", "username", "password", "email")

user_schema = UserSchema()
multi_user_schema = UserSchema(many=True)

@property
def email(self):
    return decrypt_data.data(self._email)

@email.setter
def email(self, value):
    self._email = encrypt_data(value)

@app.route("/user", methods=["POST"])
def add_user():
    if request.content_type != "application/json":
        return jsonify("Error: Enter data in JSON format."), 400
    
    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")
    email = post_data.get("email")

    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    new_record = User(username, pw_hash, email)
    db.session.add(new_record)
    db.session.commit()

    return jsonify(user_schema.dump(new_record))

@app.route("/user", methods=["GET"])
def get_users():
    all_users = db.session.query(User).all()
    return jsonify(multi_user_schema.dump(all_users))

@app.route('/user/verify', methods=["POST"])
def verification():
    if request.content_type != "application/json":
        return jsonify("Error: Provide credentials in JSON format."), 400

    post_data = request.get_json()
    email = post_data.get("email")
    password = post_data.get("password")

    user = db.session.query(User).filter(User.email == email).first()
    #print(user)

    if user is None or not bcrypt.check_password_hash(user.password, password):
        return jsonify("User could not be Verified"), 401

    return jsonify("User Verified")

@app.route('/user/<id>', methods=["PUT"])
def update_usermail(id):
    if request.content_type != "application/json":
        return jsonify("Error: Enter data in JSON format."), 400

    put_data = request.get_json()
    username = put_data.get("username")
    email = put_data.get("email")

    usermail_update = db.session.query(User).filter(User.id == id).first()
    if usermail_update is None:
        return jsonify("User not found"), 404

    if username != None:
        usermail_update.username = username
    if email != None:
        usermail_update.email = email

    db.session.commit()
    return jsonify(user_schema.dump(usermail_update))

@app.route('/user/pw/<id>', methods=["PUT"])
def pw_update(id):
    if request.content_type != "application/json":
        return jsonify("Error: Enter data in JSON format."), 400

    password = request.get_json().get("password")
    user = db.session.query(User).filter(User.id == id).first()
    if user is None:
        return jsonify("User not found"), 404

    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user.password = pw_hash

    db.session.commit()
    return jsonify(user_schema.dump(user))

@app.route('/user/delete/<id>', methods=["DELETE"])
def user_delete(id):
    delete_user = db.session.query(User).filter(User.id == id).first()
    if delete_user is None:
        return jsonify("User not found"), 404

    db.session.delete(delete_user)
    db.session.commit()
    return jsonify("Another one Bites the Dust!")

def add_fake_users(count=10):
    for _ in range(count):
        username = fake.user_name()
        password = fake.password(length=10)
        email = fake.email()

        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=pw_hash, email=email)
        db.session.add(new_user)
    db.session.commit()


# if __name__ == '__main__':
    # with app.app_context():
        # db.create_all()
        # add_fake_users(20)  # Add 20 fake users comment this line out after database starts
        # app.run(debug=True)
        
if __name__ == '__main__':
    host = 'localhost'
    port = 5000
    for rule in app.url_map.iter_rules():
        print(f"HTTP Endpoint: http://{host}:{port}{rule}")
        
    with app.app_context():
        db.create_all()
        # add_fake_users(20)  # Add 20 fake users comment this line out after database starts
    app.run(debug=True, host=host, port=port)