import json, os
from urllib.parse import urlparse


class worker:
	_SERVER_PORT = 0
	_THREADS = 0
	_WORKERS = 0

	_REDIS_URL = 0

	def __init__(self):
		with open("config.json", "r") as file:
			data = json.loads(file.read())
			if "threads" in data.keys():
				self.__class__._THREADS = data["threads"]

			if "workers" in data.keys():
				self.__class__._WORKERS = data["workers"]

		try:
			self.__class__._SERVER_PORT = os.environ["PORT"]
		except:
			pass

		try:
			self.__class__._REDIS_URL = urlparse(os.environ["REDIS_URL"])
		except:
			pass


	@property
	def SERVER_PORT(self):
		return self._SERVER_PORT

	@property
	def THREADS(self):
		return self._THREADS

	@property
	def WORKERS(self):
		return self._WORKERS

	@property
	def REDIS_HOSTNAME(self):
		if self._REDIS_URL:
			return self._REDIS_URL.hostname
	
	@property
	def REDIS_PORT(self):
		if self._REDIS_URL:
			return self._REDIS_URL.port

	@property
	def REDIS_PASSWORD(self):
		if self._REDIS_URL:
			return self._REDIS_URL.password


work = worker()

class redis_conf:
	hostname = work.REDIS_HOSTNAME or "localhost"
	port = work.REDIS_PORT or 6379
	password = work.REDIS_PASSWORD or ""

class server_conf:
	admin = os.environ.get("ADMIN_TOKEN") or "admin"
	hostname = "0.0.0.0"
	port = work.SERVER_PORT or 8000
	threads = work.THREADS or 2
	workers = work.WORKERS or 2
