# pip install redis flask pytz
# FLASK_APP=main.py flask run

from flask import Flask, request, redirect
from redis import Redis
import uuid
import hmac
import calendar
import datetime
import urllib.parse
import pytz
import re
from xml.sax import saxutils

app = Flask(__name__)
redis = Redis(host="localhost", port=6379)
server_timezone = pytz.timezone("Asia/Tokyo")


def unix_now():
    return calendar.timegm(datetime.datetime.utcnow().timetuple())


def is_valid_session_id(session_id):
    if not isinstance(session_id, str):
        return False
    if not re.match(r"^[a-zA-Z0-9\-]+$", session_id):
        return False
    return True


def is_valid_username(username):
    if not isinstance(username, str):
        return False
    if not re.match(r"^[a-zA-Z0-9]+$", username):
        return False
    return True


def is_valid_password(password):
    if not isinstance(password, str):
        return False
    if not re.match(r"^[a-zA-Z0-9]+$", password):
        return False
    return True


def get_user_posts(username):
    if not is_valid_username(username):
        return []
    posts_db = redis.lrange("posts:{}".format(username), 0, -1)
    posts = []
    for post_bin in posts_db:
        try:
            unixtime, text = post_bin.decode("ascii").split("\t")
            unixtime = int(unixtime)
            text = urllib.parse.unquote(text)
        except Exception as e:
            continue
        datetime_text = datetime.datetime.fromtimestamp(
            unixtime, tz=server_timezone
        ).strftime("%Y/%m/%d %H:%M:%S")
        posts.append({
            "datetime": datetime_text,
            "text": text
        })
    return posts


def get_user_session(session_id):
    if not is_valid_session_id(session_id):
        return None

    result = redis.get("session:{}".format(session_id))
    if result is None:
        return None

    try:
        username = result.decode("ascii")
    except Exception as e:
        return None

    return username


def delete_user_session(session_id):
    if not is_valid_session_id(session_id):
        return False

    success = redis.delete("session:{}".format(session_id))
    return bool(success)


def valid_login(username, password):
    if not (is_valid_username(username) and is_valid_password(password)):
        return False

    password_bin = password.encode("ascii")

    result = redis.get("login:{}".format(username))
    if result is None:
        return False

    try:
        hmac_key, db_hmac_value = result.decode("ascii").split(":")
    except Exception as e:
        print(e)
        return False

    hmac_key_bin = hmac_key.encode("ascii")
    input_hmac_value = hmac.new(hmac_key_bin, password_bin, "sha256").hexdigest()

    return input_hmac_value == db_hmac_value


def valid_create_account(username, password):
    if not (is_valid_username(username) and is_valid_password(password)):
        return False

    password_bin = password.encode("ascii")
    hmac_key = str(uuid.uuid4())
    hmac_key_bin = hmac_key.encode("ascii")
    hmac_value = hmac.new(hmac_key_bin, password_bin, "sha256").hexdigest()

    result = redis.set("login:{}".format(username), "{}:{}".format(hmac_key, hmac_value))

    return bool(result)


def create_session(username, session_id):
    redis.set("session:{}".format(session_id), username)


@app.route('/')
def hello():
    username = get_user_session(request.cookies.get('redisapp_sessionid', None))
    if username:
        logged_in_message = "Hello, {}!".format(username)
        posts = get_user_posts(username)
    else:
        logged_in_message = ""
        posts = []

    tmpl = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
    <meta charset="UTF-8" />
    </head>
    <body>

    <div>{}</div>

    <h3>login</h3>
    <form action="/login" method="post">
    <span>username</span><input type="text" name="username">
    <span>password</span><input type="password" name="password">
    <input type="submit">
    </form>

    <h3>create account</h3>
    <form action="/createaccount" method="post">
    <span>username</span><input type="text" name="username">
    <span>password</span><input type="password" name="password">
    <input type="submit">
    </form>

    <h3>logout</h3>
    <form action="/logout" method="post">
    <input type="submit">
    </form>

    <h3>post</h3>
    <form action="/post" method="post">
    <div>
    <textarea name="text" style="width:90%; height:40px;"></textarea>
    </div>
    <input type="submit">
    </form>
    
    <h3>your posts</h3>
    <table>
    {}
    </table>      
    </body>
    </html>
    """.format(
        logged_in_message,
        "\n".join([
            "<tr><td>{}</td><td>{}</td></tr>".format(_p["datetime"], saxutils.escape(_p["text"]))
            for _p in posts
        ])
    )
    return tmpl


@app.route('/login', methods=["POST"])
def login():
    username = request.form.get('username')
    valid = valid_login(username, request.form.get('password'))
    if valid:
        response = redirect("/", code=302)
        session_id = str(uuid.uuid4())
        create_session(username, session_id)
        response.headers['Set-Cookie'] = 'redisapp_sessionid={}'.format(session_id)
        return response
    else:
        return "invalid", 400


@app.route('/logout', methods=["POST"])
def logout():
    valid = delete_user_session(request.cookies.get('redisapp_sessionid', None))
    if valid:
        return redirect("/", code=302)
    else:
        return "failed", 400


@app.route('/createaccount', methods=["POST"])
def create_account():
    valid = valid_create_account(request.form.get('username'), request.form.get('password'))
    if valid:
        return redirect("/", code=302)
    else:
        return "invalid", 400


@app.route('/post', methods=["POST"])
def post_article():
    username = get_user_session(request.cookies.get('redisapp_sessionid', None))
    if not username:
        return "invalid", 400

    text = request.form.get('text')
    if not isinstance(text, str):
        return "invalid", 400

    elem_num = redis.lpush(
        "posts:{}".format(username),
        "{}\t{}".format(unix_now(), urllib.parse.quote(text))
    )
    if elem_num:
        return redirect("/", code=302)
    else:
        return "invalid", 400
