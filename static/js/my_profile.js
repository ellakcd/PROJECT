function showProfile(results) {
	console.log(results["active"]);
	if (results["active"] === true) {
		$("#looking_or_not").html("LOOKING FOR APT: True<br><button id='deactivate' class='search_button btn'> Not Currently Looking For Apt? </button>");
		$("#deactivate").on("click", deactivateUser);
	} else {
		$("#looking_or_not").html("LOOKING FOR APT: False<br><button id='activate' class='search_button btn'> Looking Once More! </button>");
		$("#activate").on("click", activateUser);
	}
}

function deactivateUser(evt) {
	$.post("/deactivate_user", showProfile);
}

$("#deactivate").on("click", deactivateUser);


function activateUser(evt) {
	$.post("/reactivate_user", showProfile);
}

$("#activate").on("click", activateUser);