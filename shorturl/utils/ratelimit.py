from shorturl.utils.db import RateLimitList
from flask import request, jsonify
from collections import deque
from functools import wraps
from time import time as timestamp
from re import compile, findall


class RateLimit(RateLimitList):
	'''
	Rate = [int] numbers of requests allowed
	default rate limit: 10 requests allowed in 2 min (60 seconds * 2)
	global rate condition: 10 requests in 4 seconds after rate limit
	'''
	second = 1
	minute = 60
	hour = 60 * 60
	day = 60 * 60 *60

	def __init__(self, global_rate:str="10 per 4second"):
		super().__init__()

		self.GLOBAL_NAME = "GLOBAL"
		self.GLOBAL_RATE = global_rate

	def ratelimit(self, rate:str="10 per 2minute"):
		def limit(func):
			@wraps(func)
			def inner(*args, **kwargs):

				requests, in_time = self._parse_time(rate)
				name = f"BEFORE:{self.addr}"

				if error:=self.is_global():
					return error

				length = self.len(name)

				if length >= requests:
					cTime = timestamp()
					diff = (cTime - self.get(name, length-requests))
					if diff > in_time:
						self.rpush(name, cTime)
						self.clear_global()
						return func(*args, **kwargs)
					else:
						return self.pass_global(in_time - diff)
				self.push(name, timestamp())
				return func(*args, **kwargs)

			return inner
		return limit

	def pass_global(self, retry_after:float):
		
		requests, in_time = self._parse_time(self.GLOBAL_RATE)
		
		name = f"AFTER:{self.addr}"

		if requests == self.len(name):
			cTime = timestamp()
			if cTime - self.get(name, 0) > in_time:
				self.rpush(name, cTime)
				return self.error(_global=False, retry_after=retry_after)
			else:
				self.set_global()
				return self.error(_global=True)
		self.push(name, timestamp())
		return self.error(_global=False, retry_after=retry_after)

	@property
	def addr(self):
		return request.remote_addr

	def _parse_time(self, rate:str):
		pattern = compile(r"([0-9]+) per ([0-9]+)?([a-z]+)")
		requests, times, type = findall(pattern, rate)[0]
		if times:
			return int(requests), int(times) * getattr(self, type)
		return int(requests), getattr(self, type)

	def error(self, _global:bool, retry_after:float=0.0):
		return jsonify({
			"message": "you are being rate limited.",
			"global": _global,
			"retry_after": retry_after
			}), 429, {
			"X-RateLimit-Global": _global, 
			"Retry-After": int(retry_after)
			}

	def is_global(self):
		if self.global_check(self.GLOBAL_NAME, self.addr):
			return self.error(_global=True)

	def set_global(self):
		self.global_add(self.GLOBAL_NAME, self.addr)
		for name in [f"AFTER:{self.addr}", f"BEFORE:{self.addr}"]:
			self.delete(name)

	def clear_global(self):
		self.delete(f"AFTER:{self.addr}")
