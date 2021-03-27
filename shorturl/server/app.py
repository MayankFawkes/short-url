from flask import Flask, request, jsonify, redirect, render_template
from shorturl.utils.db import RedisDB
from shorturl.utils.helper import check, ERROR
from shorturl.utils.ratelimit import RateLimit


app = Flask(__name__)

rl = RateLimit()
db = RedisDB()

@app.route('/')
def index():
	return render_template("index.html", title="URL Shortener", domain=request.base_url[:-1])

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
	print(mydata)
	if not mydata:
		return jsonify(ERROR.INVALID_DATA)

	if res:=check(mydata, ["code", "auth"]):
		return jsonify(res)
	return db.status(mydata["code"], mydata["auth"])