from typing import Union, Dict
import re

class ERROR:
	SUCCESS = {"err": 5000, "msg": "success"}
	INVALID_DATA = {"err": 5001, "msg": "invalid data"}
	RATE_LIMIT = {"err": 5002, "msg": "rate limit"}
	NOT_FOUND = {"err": 5003, "msg": "not found"}
	INVALID_URL = {"err": 5004, "msg": "invalid url"}
	BLOCKED_IP = {"err": 5007, "msg": "blocked IP"}
	INVALID_SHORT_CODE = {"err": 5008, "msg": "invalid short code"}
	AUTH_FAILED = {"err": 5009, "msg": "authorization failed"}
	ALREADY_BLOCKED = {"err": 5010, "msg": "IP already blocked"}
	ALREADY_UNBLOCKED = {"err": 5011, "msg": "IP already unblocked"}

def check_url(url:str) -> bool:
	url = str(url)
	regex = ("((http|https)://)(www.)?" +
			 "[a-zA-Z0-9@:%._\\+~#?&//=]" +
			 "{2,256}\\.[a-z]" +
			 "{2,6}\\b([-a-zA-Z0-9@:%" +
			 "._\\+~#?&//=]*)")

	p = re.compile(regex)

	if (url == None):
		return False

	if(re.search(p, url)):
		return True
	else:
		return False

def valid_ip(address) -> bool:
    try:
        host_bytes = address.split('.')
        valid = [int(b) for b in host_bytes]
        valid = [b for b in valid if b >= 0 and b<=255]
        return len(host_bytes) == 4 and len(valid) == 4
    except:
        return False

def check(data:dict(), lst:list()) -> Union[None, Dict[str, str]]:
	if not data:
		return None

	count = 0
	for name in lst:
		if name in data:
			if data[name]:
				count +=1

	if "url" in data:
		if not check_url(data["url"]):
			return ERROR.INVALID_URL

	if "time" in data:
		try:
			int(data["time"])
		except:
			return ERROR.INVALID_DATA

	if "times" in data:
		try:
			int(data["times"])
		except:
			return ERROR.INVALID_DATA

	if count == len(lst):
		return None
	return ERROR.INVALID_DATA



def check_admin_request():
	"""Print the runtime of the decorated function"""
	@functools.wraps(func)
	def wrapper_timer(*args, **kwargs):
		print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
		return value
	return wrapper_timer