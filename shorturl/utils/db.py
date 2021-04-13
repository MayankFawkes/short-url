import redis
from flask import request
from string import ascii_lowercase, ascii_uppercase, digits
from random import choice
from time import time as timestamp
from typing import Union, Dict, Any
from shorturl.utils.helper import ERROR, valid_ip
from uuid import uuid4
from collections import deque
from itertools import count
from functools import wraps
from shorturl.utils.config import redis_conf, server_conf


class RedisDB:
	def __init__(self):
		self.redis = redis.Redis(host=redis_conf.hostname, port=redis_conf.port, password=redis_conf.password)

		self.MIN_LEN_SURL = 6
		self.MAX_RETRIES = 5

	def make(self, fullurl:str, time:int=15*60, times:int=0) -> Union[None, str]:
		count = 0
		while True:
			if count == self.MAX_RETRIES:
				self.MIN_LEN_SURL+=1
			if scode:=self._check_short_url(self._make_short_code()):
				auth = str(uuid4())
				if not self.redis.hmset(f"URL:{scode}", {
					"fullurl": fullurl,
					"created at": timestamp(),
					"auth": auth,
					}):
					return print("Error while creating ")
				if times:
					if not self.redis.hmset(f"URL:{scode}", {
						"times": times
						}):
						return print("Error while creating 'times' in HashMap")
				else:
					if not self.redis.expire(f"URL:{scode}", time):
						return print("Error while creating ")

				return self.status(scode, auth)

	def get(self, scode:str) -> Union[None, str]:
		scode = f"URL:{scode}"
		if data:=self.redis.hgetall(scode):
			self.redis.hmset(scode, {
				"last visit": timestamp(),
				})
			self.redis.hincrby(scode, "access", 1)
			if self.redis.hexists(scode, "times"):
				if 0 >= self.redis.hincrby(scode, "times", -1):
					self.redis.delete(scode)
			return data[b"fullurl"].decode()

	def status(self, scode:str, auth:str=False) -> Dict[str, str]:
		scode = f"URL:{scode}"
		if auth:
			if data:=self._auth(scode, auth):
				if isinstance(data, tuple):
					return data
			else:
				return ERROR.AUTH_FAILED, 403

		if data:=self.redis.hgetall(scode):
			data[b"code"] = scode.split(":")[-1].encode()
			if not self.redis.hexists(scode, "times"):
				data[b"ttl in seconds"] = f"{self.redis.ttl(scode)}".encode()
			return {k.decode():v.decode() for k, v in data.items()}

		return ERROR.INVALID_SHORT_CODE, 404

	def remove(self, scode:str, auth:str=False) -> Dict[str, str]:
		scode = f"URL:{scode}"
		if auth:
			if data:=self._auth(scode, auth):
				if isinstance(data, tuple):
					return data
			else:
				return ERROR.AUTH_FAILED, 403

		if self.redis.delete(scode):
			return ERROR.SUCCESS, 204

		return ERROR.INVALID_SHORT_CODE, 404

	def check_admin(self, func):
		@wraps(func)
		def inner(*args, **kwargs):
			if admin_token:=request.headers.get('X-ADMIN-TOKEN'):
				if admin_token == server_conf.admin:
					return func(*args, **kwargs)
			return ERROR.AUTH_FAILED, 403

		return inner

	def _auth(self, scode:str, auth:str) -> bool:
		if self.redis.exists(scode):
			if self.redis.hget(scode, "auth").decode() == auth or server_conf.admin == auth:
				return True
			return False
		return ERROR.INVALID_SHORT_CODE, 404

	def _check_short_url(self, scode:str) -> Union[None, str]:
		if not self.redis.keys(f"URL:{scode}"):
			return scode

	def total_urls(self) -> int:
		return self._ilen(self.redis.scan_iter(match="URL:*"))

	def global_rem(self, value:str, list_name:str="GLOBAL") -> bool:
		if not valid_ip(value):
			return ERROR.INVALID_DATA, 403
		if check:= self.redis.srem(list_name, value):
			return ERROR.SUCCESS, 200
		return ERROR.ALREADY_UNBLOCKED, 404

	def global_add(self, value:str, list_name:str="GLOBAL") -> bool:
		if not valid_ip(value):
			return ERROR.INVALID_DATA, 403
		if check:=self.redis.sadd(list_name, value):
			return ERROR.SUCCESS, 200
		return ERROR.ALREADY_BLOCKED, 404

	def globals(self) -> int:
		if s:=self.redis.smembers("GLOBAL"):
			return len(s)
		return 0

	def _ilen(self, it):
		cnt = count()
		deque(zip(it, cnt), 0)
		return next(cnt)

	def _make_short_code(self) -> str:
		return "".join(choice(ascii_lowercase + ascii_uppercase + digits) for _ in range(self.MIN_LEN_SURL))

class RateLimitList:
	def __init__(self):
		self.redis = redis.Redis(host=redis_conf.hostname, port=redis_conf.port, password=redis_conf.password)

	def push(self, list_name:str, value:str) -> bool:
		if not self.redis.rpush(list_name, value):
			print(f"Error while pushing LPUSH {list_name} {value}")
			return False
		return True

	def rpush(self, list_name:str, value:str) -> bool:
		if self.redis.lpop(list_name):
			return self.push(list_name, value)
		return False

	def len(self, list_name:str) -> int:
		return self.redis.llen(list_name)

	def get(self, list_name:str, pos:int) -> float:
		return float(self.redis.lindex(list_name, pos))

	def delete(self, list_name:str) -> bool:
		return self.redis.delete(list_name)

	def global_check(self, list_name:str, value:str) -> bool:
		return self.redis.sismember(list_name, value)

	def global_add(self, list_name:str, value:str) -> bool:
		return self.redis.sadd(list_name, value)

	def global_rem(self, list_name:str, value:str) -> bool:
		return self.redis.srem(list_name, value)

