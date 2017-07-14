
$(document).ready(function(){
	if (user_token) {
		var tnode = document.getElementById('harToken');
		tnode.innerText = "Vi er logget ind! Token er: "+user_token;	
	}

	var hentDataButton = $('#hentDataButton');

	hentDataButton.on('click', function(){
		$.get("http://websso-poc.herokuapp.com/kai-themes?token="+user_token, function(data, status) {
			var DOM_rep_window = document.getElementById('ResponseWindow');
			DOM_rep_window.appendChild(document.createElement("hr"));

			// If we are not logged in, we'll get a SAML AuthnRequest back.
			// Check if response is AuthnRequest.
			// (this an unsafe hacked way, don't do it. Could also be done by checking if user_token is set)
			if(data.indexOf("SAMLRequest") > -1) {
				var newnode = document.createElement("span");
				newnode.innerText = "Her vises det renderede respons fra Service Provider: (vi modificerer RelayState til at fortælle service provider hvor den skal redirect til, efter at have modtaget svar)";
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
			} else {
				// We got JSON back from the server
				newnode = document.createElement("span");
				newnode.innerText = "Her er data fra Service Provider (JSON med en liste KAI-temaer):";
				DOM_rep_window.appendChild(newnode);	
				newnode = document.createElement("div");
				console.log(data)
				newnode.innerHTML = data;
				DOM_rep_window.appendChild(newnode);
			}
		});
	});
});


