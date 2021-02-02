# python
import hashlib
from json.decoder import JSONDecodeError
from urllib.parse import urlparse
import json
import time
import os
import sys
from shutil import copyfile

# flask
from flask import Flask, jsonify, request

# requests
import requests

auth_file = open("auth.json", "r").read()
auth_data = json.loads(auth_file)

type = "notification"

url = f"https://onlyfans.com/api2/v2/users/notifications?limit=10&offset=0&type={type}&skip_users_dups=1&app-token={auth_data['app_token']}"

session = requests.Session()
ctime = str(int(round(time.time() * 1000 - 301000)))

path = urlparse(url).path
query = urlparse(url).query

path = path + "?" + query
a = [auth_data["sess"], ctime, path, auth_data["user_agent"], "onlyfans"]

msg = "\n".join(a)
message = msg.encode("utf-8")
hash_object = hashlib.sha1(message)
sha_1 = hash_object.hexdigest()

session.headers["access-token"] = auth_data["sess"]
session.headers["sign"] = sha_1
session.headers["time"] = ctime
session.headers["accept"] = "application/json, text/plain, */*"
session.headers["user-agent"] = auth_data["user_agent"]
session.headers["referer"] = "https://onlyfans.com/"

auth_cookies = [
    {"name": "auth_id", "value": auth_data["auth_id"]},
    {"name": "sess", "value": auth_data["sess"]},
    {"name": "auth_hash", "value": ""},
    {"name": f'auth_uniq_{auth_data["auth_id"]}', "value": None},
    {"name": f'auth_uid_{auth_data["auth_id"]}', "value": None},
]

for auth_cookie in auth_cookies:
    session.cookies.set(**auth_cookie)

if getattr(sys, "frozen", False):
    static_folder = os.path.join(sys._MEIPASS, "static")
    app = Flask(__name__, static_folder=static_folder)
else:
    app = Flask(__name__, static_folder="static", static_url_path="/")


@app.route("/")
def send_index():
    return app.send_static_file("index.html")

@app.route("/notifications")
def send_notifications():
    resp = session.get(url).json()

    return jsonify(resp)


@app.route("/ignore/<username>", methods=["POST", "GET"])
def ignore_username(username):
    if request.method == "GET":
        with open("ignore.json", "r") as file:
            try:
                ignore_file = json.loads(file.read())
                for user in ignore_file["ignore"]:
                    if user == username:
                        file.close()
                        return jsonify({"ignore": True})
                file.close()
                return jsonify({"ignore": False})
            except JSONDecodeError as e:
                copyfile("ignore.json", "ignore.json.bak")
                with open("ignore.json", "w") as new_file:
                    obj = {"ignore": []}
                    json.dump(obj, new_file)
                return jsonify({"ignore": False})
    elif request.method == "POST":
        try:
            new_usernames = []
            with open("ignore.json", "r") as file:
                ignore_file = json.load(file)
                new_usernames = ignore_file["ignore"]
                if username not in new_usernames:
                    new_usernames.append(username)
                file.close()

            with open("ignore.json", "w") as file:
                data = {"ignore": new_usernames}
                json.dump(data, file)
                file.close()
                return jsonify({"saved": True})

        except Exception as e:
            print(e)
            return jsonify({"saved": False})


app.run()
