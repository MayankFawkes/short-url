from flask import Flask, request, jsonify, redirect, render_template, abort
from shorturl.utils.db import RedisDB
from shorturl.utils.helper import check, ERROR
from shorturl.utils.ratelimit import RateLimit
from shorturl.utils.config import server_conf
from flask_cors import CORS

app = Flask(__name__)

rl = RateLimit()
db = RedisDB()

CORS(app)

'''
================
USERS REQUESTS
================
'''
@app.route('/')
def index():
	return render_template("index.html", title="URL Shortener", domain=request.base_url[:-1])

@app.route('/admin')
def admin():
	return render_template("admin.html")

@app.route('/ip')
@rl.ratelimit(rate="20 per minute")
def ip():
	return jsonify({'addr': request.remote_addr}), 200

@app.route('/<scode>')
@rl.ratelimit(rate="15 per minute")
def get(scode):
	if url:=db.get(scode):
		return redirect(url, code=302)
	return jsonify(ERROR.INVALID_SHORT_CODE)

@app.route('/create/time', methods=["POST"])
@rl.ratelimit(rate="10 per 2minute")
def time():
	mydata = request.json
	if not mydata:
		return jsonify(ERROR.INVALID_DATA)

	if res:=check(mydata, ["url", "time"]):
		return jsonify(res)
	return jsonify(db.make(fullurl=mydata["url"], time=int(mydata["time"])))

@app.route('/create/times', methods=["POST"])
@rl.ratelimit(rate="10 per 2minute")
def times():
	mydata = request.json
	if not mydata:
		return jsonify(ERROR.INVALID_DATA)

	if res:=check(mydata, ["url", "times"]):
		return jsonify(res)
	return jsonify(db.make(fullurl=mydata["url"], times=int(mydata["times"])))

@app.route('/delete', methods=["DELETE"])
@rl.ratelimit(rate="10 per 2minute")
def delete():
	mydata = request.json
	if not mydata:
		return jsonify(ERROR.INVALID_DATA)

	if res:=check(mydata, ["code", "auth"]):
		return jsonify(res)
	return db.remove(mydata["code"], mydata["auth"])

@app.route('/stats', methods=["POST"])
@rl.ratelimit(rate="20 per minute")
def stats():
	mydata = request.json
	if not mydata:
		return jsonify(ERROR.INVALID_DATA)

	if res:=check(mydata, ["code", "auth"]):
		return jsonify(res)
	return db.status(mydata["code"], mydata["auth"])



'''
===============
ADMIN REQUESTS
===============
'''

@app.route('/admin/login', methods=["POST"])
@rl.ratelimit(rate="60 per minute")
def admin_login():
	mydata = request.json
	if not mydata:
		return jsonify(ERROR.INVALID_DATA)

	if res:=check(mydata, ["admin-token"]):
		return jsonify(res)

	if mydata["admin-token"] == server_conf.admin:
		return ('', 204)

	return abort(403, description="Forbidden")

@app.route('/admin/stats', methods=["POST"])
@rl.ratelimit(rate="60 per minute")
@db.check_admin
def admin_stats():
	return jsonify({"global":db.globals(), "links": db.total_urls()})

@app.route('/admin/urlstats', methods=["POST"])
@rl.ratelimit(rate="60 per minute")
@db.check_admin
def admin_urlstats():
	mydata = request.json
	if not mydata:
		return jsonify(ERROR.INVALID_DATA), 403

	if "code" not in mydata:
		return jsonify(ERROR.INVALID_DATA), 403

	return db.status(mydata["code"])


@app.route('/admin/unblock', methods=["POST"])
@rl.ratelimit(rate="60 per minute")
@db.check_admin
def admin_unblock():
	mydata = request.json
	if not mydata:
		return jsonify(ERROR.INVALID_DATA), 403

	if "ip" not in mydata:
		return jsonify(ERROR.INVALID_DATA), 403

	return db.global_rem(mydata["ip"])


@app.route('/admin/block', methods=["POST"])
@rl.ratelimit(rate="60 per minute")
@db.check_admin
def admin_block():
	mydata = request.json
	if not mydata:
		return jsonify(ERROR.INVALID_DATA), 403

	if "ip" not in mydata:
		return jsonify(ERROR.INVALID_DATA), 403

	return db.global_add(mydata["ip"])


@app.route('/admin/delete', methods=["DELETE"])
@rl.ratelimit(rate="60 per minute")
@db.check_admin
def admin_delete():
	mydata = request.json
	if not mydata:
		return jsonify(ERROR.INVALID_DATA), 403

	if "code" not in mydata:
		return jsonify(ERROR.INVALID_DATA), 403

	return db.remove(mydata["code"])