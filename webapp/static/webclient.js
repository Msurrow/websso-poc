
$(document).ready(function(){
	var hentDataButton = $('#hentDataButton');

	hentDataButton.on('click', function(){
		$.get("http://websso-poc.herokuapp.com/kai-themes", function(data, status) {
			var DOM_rep_window = document.getElementById('ResponseWindow');
			DOM_rep_window.appendChild(document.createElement("hr"));
			var newnode = document.createElement("span");
			newnode.innerText = "Her vises det renderede respons fra service provider: (vi modificerer RelayState til at fortælle service provider hvor den skal redirect til, efter at have modtaget svar)";
			DOM_rep_window.appendChild(newnode);
			newnode = document.createElement("div");
			newnode.style.border = "solid #0000FF";
			newnode.innerHTML = data;
			DOM_rep_window.appendChild(newnode);
			// This is where we modify the RelayState to tell the server where to redirect upon getting
			// SAML Response from IdP
			rsnode = document.getElementsByName("RelayState")[0];
			rsnode.value = "http://localhost:8000/login_complete"
			DOM_rep_window.appendChild(document.createElement("hr"));
			var newnode = document.createElement("span");
			newnode.innerText = "Her vises det få respons fra service provider:";
			DOM_rep_window.appendChild(newnode);
			newnode = document.createElement("span");
			newnode.innerText = data;
			DOM_rep_window.appendChild(newnode);
		});
	});
});


