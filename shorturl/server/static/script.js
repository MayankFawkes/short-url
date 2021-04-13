String.prototype.toProperCase = function () {
	return this.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
};
const host = `${location.protocol}//${location.host}`

var ADMIN_TOKEN = window.localStorage.getItem("token") || "NA";

const updateTag = (key, value) => {
	document.getElementById(key).innerText = value;
}

const ValidateIPaddress = (ipaddress) => {
	if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ipaddress)) {	
		return (true)
	}
	Swal.fire('Error', 'Invalid IP', 'error')
	return (false)
}

const setHtags = async () => {
	var aa = await SEND("POST","/admin/stats", {});
	aa = await aa.json()
	for (const [key, value] of Object.entries(aa)){
		updateTag(key, value);
	}
}

const FormBoxApply = (type) => {
	let data = {
		delete:{
			formTitle: "Delete Short Link",
			formLabel: "Enter Short Code/URL Code",
			formAction: "Delete"
		},
		stats:{
			formTitle: "Stats of Short Link",
			formLabel: "Enter Short Code/URL Code",
			formAction: "Show"
		},
		unblock:{
			formTitle: "Unblock IP Address",
			formLabel: "Enter IP Address",
			formAction: "Unblock"
		},
		block:{
			formTitle: "Block IP Address",
			formLabel: "Enter IP Address",
			formAction: "Block"
		}
	};
	try {
		for (const [key, value] of Object.entries(data[type])){
			updateTag(key, value);
		}
		document.getElementById("formAction").setAttribute("onclick", `submit('${type}')`)
	}
	catch(err){
		console.log(err);
	}

}

const Toast = Swal.mixin({
	toast: true,
	position: 'top-end',
	showConfirmButton: false,
	timer: 3000,
	timerProgressBar: true,
	didOpen: (toast) => {
		toast.addEventListener('mouseenter', Swal.stopTimer)
		toast.addEventListener('mouseleave', Swal.resumeTimer)
	}
});

const makeBlur = async (num) => {
	for (ele of document.getElementsByClassName("can-blur")){ele.style.filter = `blur(${num}px)`;}
};

const SEND = async (type, url, data, login) => {
	const settings = {
		method: type,
		headers: {
			'Accept': 'application/json',
			'Content-Type': 'application/json',
			'X-ADMIN-TOKEN': ADMIN_TOKEN
		},
		body: JSON.stringify(data)
	};
	const fetchResponse = await fetch(host+url, settings);
	return fetchResponse;
	
	// try {
	// 	const fetchResponse = await fetch(host+url, settings)
	// 	if (fetchResponse.status == 204){
	// 		if (login){
	// 			window.localStorage.setItem("token", data["admin-token"]);
	// 			ADMIN_TOKEN = data["admin-token"];
	// 			return;
	// 		}
	// 		else {
	// 			return true;
	// 		}
	// 	}
	// 	if (fetchResponse.status == 403){
	// 		if (login){
	// 			return "Invalid / Permissions Denied";
	// 		}
	// 		else{
	// 			return false;
	// 		}
	// 	}
	// 	const gdata = await fetchResponse.json();
	// 	return gdata;
	// } catch (e) {
	// 	return e;
	// }
};


const logout = () => {
	window.localStorage.removeItem("token");
	ADMIN_TOKEN = "NA";
	loginProcess();
};

const login = async () => {
	await makeBlur(3);
	const { value: oauth } = await Swal.fire({
		title: 'Admin Login',
		input: 'text',
		inputLabel: 'Your OAuth Token',
		inputPlaceholder: 'Enter your OAuth Token',
		focusConfirm: false,
		allowOutsideClick: false,
		inputValidator: (value) => {
			if (!value) {
				return 'Please enter OAuth token!!'
			}
			else {
				let check = SEND("POST", "/admin/login", {"admin-token": value});
				return check.then(res => {
					if (res.status == 204){
						window.localStorage.setItem("token", value);
						ADMIN_TOKEN = value;
						return;
					}
					else if (res.status == 403){
						return "Invalid / Permissions Denied";
					}
					else if (res.status == 429) {
						return res.json();

					}

				}).then(data =>{
					console.log(data);
					if (data instanceof Object) {
						if (data.global) {
							return "Your IP is Permanently ban";
						}
						else {
							return `${data.message} retry_after ${data.retry_after}`;
						}
					}
					else {
						if (!data){
							return;
						}
						return data;;
					}
		

				})
				.catch(error => {
					return error;
				})

			}
		}
	})

	await setHtags();

	if (oauth) {
		await makeBlur(0);
		Toast.fire({
			icon: 'success',
			title: 'Signed in successfully'
		});
		return true;
	}
};

const handleerror = async (p) => {
	let num = p.status;
	if (num == 404){
		let j = await p.json();
		Swal.fire('Error', j.msg.toProperCase(), 'error')
	}
	else if (num == 403){
		let j = await p.json();
		Swal.fire('Error', j.msg.toProperCase(), 'error')
	}
	else if (num == 429){
		let j = await p.json();
		if (j.global) {
			Swal.fire('Error', 'Your IP is Permanently ban', 'error')
		}
		else {
			Swal.fire('Error', `${j.message} retry_after ${j.retry_after}`, 'error')
		}

		Swal.fire('Error', j.msg.toProperCase(), 'error')
	}
	else{
		Swal.fire('Error', p.statusText, 'error')
	}

}

const submitRequests = {
	delete: async () => {
		let value = document.getElementById("data").value;
		if (!value){return;}
		let p = await SEND("DELETE", "/admin/delete", {"code": value});
		if (p.status == 204){
			Swal.fire('Success','URL Deleted Successfully','success')
		}
		else{
			await handleerror(p);
		}
		console.log(p);

	},
	stats: async () => {
		let value = document.getElementById("data").value;
		if (!value){return;}
		let p = await SEND("POST", "/admin/urlstats", {"code": value});
		if (p.ok){
			let html = '<div class="box" style="width: auto"><table class="table"><tbody>';
			for (const [key, value] of Object.entries(await p.json())){
				html += `<tr><th>${key}</th><td>${value}</td></tr>`;
			}

			html += '</tbody></table></div>';
			console.log(html);
			await Swal.fire({title: 'Link Stats', html: html, focusConfirm: false});
		}
		else {
			await handleerror(p);
		}
	},
	unblock: async () => {
		let value = document.getElementById("data").value;
		if (!value){return;}
		if (!ValidateIPaddress(value)){return;}
		let p = await SEND("POST", "/admin/unblock", {"ip": value});
		if (p.ok){
			Swal.fire('Success',`IP: ${value} unblocked`,'success')
		}
		else{
			await handleerror(p);
		}
	},
	block: async () => {
		let value = document.getElementById("data").value;
		if (!value){return;}
		if (!ValidateIPaddress(value)){return;}
		let p = await SEND("POST", "/admin/block", {"ip": value});
		if (p.ok){
			Swal.fire('Success',`IP: ${value} blocked`,'success')
		}
		else{
			await handleerror(p);
		}
	},
}

const submit = (request_type) => {
	submitRequests[request_type]()
}


document.getElementById("data").onkeyup = function(e) {
	if (e.which == 13){
		document.getElementById("formAction").click()
	}

};


let loginProcess;

(loginProcess = async () => {
	if (ADMIN_TOKEN != "NA"){
		let o = await SEND("POST", "/admin/login", {"admin-token": ADMIN_TOKEN});
		if (o.status == 204){
			await setHtags();return;
		}
		else{
			logout()
		}

	}

	while (1) {
		var ok = await login();
		console.log(ok);
		if (ok) {
			break;
		}
	}
})()