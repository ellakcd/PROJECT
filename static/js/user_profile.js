function showProfile(results) {
	console.log(results["friends"]);
	let userId = results["user_id"];
	if (results["friends"] === true) {
		$("#friends_or_not").empty();
	} else {
		$("#friends_or_not").html("<button id='friend'> Add "+userId+" as a Friend</button>");
		$("#friend").on("click", friendUser);
		$("#friend").data("user-id", userId);

	}
}


function friendUser(evt) {

	let userId = $(this).data("userId");
	let formInputs = {
		"user_id": userId
	}

	$.post("/friend_user", formInputs, showProfile);
}

$("#friend").on("click", friendUser);