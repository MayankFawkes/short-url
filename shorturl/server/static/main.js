function _makeshort(url){
	fetch('/create/time', {
		method: 'post',
		headers: {
			'Accept': 'application/json, text/plain, */*',
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({'url': url, 'time': '900'})
	}).then(res => res.json())
		.then(res => auth_short(res));
}

function validURL(str) {
	var pattern = new RegExp('^(https:\\/\\/|http:\\/\\/)'+ // protocol
		'((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
		'((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
		'(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
		'(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
		'(\\#[-a-z\\d_]*)?$','i'); // fragment locator
	return !!pattern.test(str);
}

function makeshort(){
	var url = window.document.getElementById("url").value;
	if (url){
		if (validURL(url)){
			_makeshort(url);
		}
	}
}

function auth_short(data){
	if (data.err){
		Swal.fire({
			icon: 'error',
			title: 'Oops...',
			text: data.msg
		}); return;
	}
	if (data.message){
		Swal.fire({
			icon: 'error',
			title: `Global: ${data.global}`,
			text: `${data.message} Try after ${Math.floor(data.retry_after)} Seconds`
		}); return;
	}
	window.document.getElementById("shorturl").value = `${location.protocol}//${location.host}/${data.code}`;
	window.document.getElementById("authkey").value = data.auth;
}

function clip(what){
	window.navigator.clipboard.writeText(window.document.getElementById(what).value)
}

document.getElementById("url").onkeyup = function(e) {
	if (e.which == 13){
		makeshort();
	}
	else if (e.ctrlKey && e.which == 86) {
		setTimeout(makeshort, 10);
	}
	else {
		return;
	}

};