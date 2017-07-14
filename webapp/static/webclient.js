
$(document).ready(function(){
	var hentDataButton = $('#hentDataButton');

	hentDataButton.on('click', function(){
		$.get("http://websso-poc.herokuapp.com/kai-themes", function(data, status) {
		//$.get("http://www.google.com", function(data, status) {
			console.log(status)
			console.log(data)
		});
	});
});