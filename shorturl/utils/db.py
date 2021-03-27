import redis
from string import ascii_lowercase, ascii_uppercase, digits
from random import choice
from time import time as timestamp
from typing import Union, Dict, Any
from shorturl.utils.helper import ERROR
from uuid import uuid4
from shorturl.utils.config import redis_conf


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

	def status(self, scode:str, auth:str) -> Dict[str, str]:
		scode = f"URL:{scode}"
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

	def remove(self, scode:str, auth:str) -> Dict[str, str]:
		scode = f"URL:{scode}"
		if data:=self._auth(scode, auth):
			if isinstance(data, tuple):
				return data	
		else:
			return ERROR.AUTH_FAILED, 403

		if self.redis.delete(scode):
			return ERROR.SUCCESS, 204

		return ERROR.INVALID_SHORT_CODE, 404

	def _auth(self, scode:str, auth:str) -> bool:
		if self.redis.exists(scode):
			if self.redis.hget(scode, "auth").decode() == auth:
				return True
			return False
		return ERROR.INVALID_SHORT_CODE, 404

	def _check_short_url(self, scode:str) -> Union[None, str]:
		if not self.redis.keys(f"URL:{scode}"):
			return scode

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

