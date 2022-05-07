import psycopg2
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from marshmallow import Schema, fields, INCLUDE,  validate

book = Blueprint(name="book", import_name=__name__)
conn = psycopg2.connect(database="test", user="postgres", password="50608184", host="127.0.0.1",
                        port="5432")
cur = conn.cursor()
cur.execute(
    'CREATE TABLE if not exists USERS (id INT,USERNAME varchar (50) NOT NULL,PASSWORD varchar (150) NOT NULL,EMAIL varchar (50) NOT NULL) ;')


@book.route('/register', methods=['POST'])
def register():
    a = PackageSchema()
    b = a.load(request.get_json())
    print(b["password"])
    pwd_hash = generate_password_hash(b["password"])
    cur.execute(
        f"INSERT INTO users (id,username,password,email) VALUES ( {b['id']},'{b['username']}','{pwd_hash}','{b['email']}');")
    conn.commit()
    return jsonify({"user": {"id": b['id'], "username": b['username'], "password": pwd_hash, "email": b['email']}})


@book.route("/login", methods=['POST'])
def login():
    c = loginSchema()
    d = c.load(request.get_json())
    cur.execute(f"select id,password from users where username='{d['username']}' or email='{d['email']}';")
    pws = cur.fetchall()
    if len(pws) != 0:
        if check_password_hash(pws[0][1], d['password']):
            refresh = create_refresh_token(identity=int(pws[0][0]))
            access = create_access_token(identity=int(pws[0][0]))
            return jsonify(
                {"user": {"refresh": refresh, "access": access, "username": d['username'], "email": d['email']}}), 200
    else:
        return jsonify({"message": "not found email and user name"}), 401


@book.route("/me", methods=['GET'])
@jwt_required()
def me():
    id = get_jwt_identity()
    cur.execute(f"select * from users where id={id}")
    user = cur.fetchall()
    t = loginSchema()
    o = t.load({"username": user[0][1], "password": user[0][2], "email": user[0][3]})

    return jsonify({"user": {"id": id, "username": o["username"], "password": o["password"], "email": o["email"]}}), 200


@book.route("/token/refresh", methods=['GET'])
@jwt_required(refresh=True)
def refresh_token():
    id = get_jwt_identity()
    access = create_access_token(identity=id)
    return jsonify({"access": access})


@book.route("/edit", methods=['PUT'])
@jwt_required()
def edit():
    id = get_jwt_identity()
    y = EditSchema()
    p = y.load(request.get_json())
    if 'username' in request.json:
        cur.execute(f"UPDATE users SET username = '{p['username']}' WHERE id={id};")
    if "email" in request.json:
        cur.execute(f"UPDATE users SET email = '{p['email']}' WHERE id={id};")
    if "password" in request.json:
        cur.execute(f"UPDATE users SET password = '{p['password']}' WHERE id={id};")
    conn.commit()
    return {"message": "updata successfully"}


@book.route("/delete", methods=['delete'])
@jwt_required()
def delete():
    id = get_jwt_identity()
    cur.execute(f"delete from users where id={id};")
    conn.commit()
    return {"message": f"deleted {id}"}


class PackageSchema(Schema):
    id = fields.Integer(required=True)
    username = fields.Str(required=True, validate=[validate.Length(min=3)])
    password = fields.Str(required=True, validate=[validate.Length(min=6)])
    email = fields.Str(required=False, validate=validate.Email(error="Not a valid email address"))

    class Meta:
        # Include unknown fields in the deserialized output
        unknown = INCLUDE


class loginSchema(Schema):
    username = fields.Str(required=True, validate=[validate.Length(min=3)])
    password = fields.Str(required=True, validate=[validate.Length(min=6)])
    email = fields.Str(required=False, validate=validate.Email(error="Not a valid email address"))

    class Meta:
        # Include unknown fields in the deserialized output
        unknown = INCLUDE


class EditSchema(Schema):
    username = fields.Str(required=False, validate=[validate.Length(min=3)])
    password = fields.Str(required=False, validate=[validate.Length(min=6)])
    email = fields.Str(required=False, validate=validate.Email(error="Not a valid email address"))

    class Meta:
        # Include unknown fields in the deserialized output
        unknown = INCLUDE