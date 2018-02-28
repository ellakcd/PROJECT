function showProfile(results) {
	console.log(results["favorite"]);
	let listingId = results["listing_id"];
	if (results["favorite"] === true) {
		$("#favorite_or_not").html("<button id='unfavorite'> Unfavorite This Listing </button>");
		$("#unfavorite").on("click", unfavoriteListing);
		$("#unfavorite").data("listing-id", listingId);
	} else {
		$("#favorite_or_not").html("<button id='favorite'> Favorite This Listing </button>");
		$("#favorite").on("click", favoriteListing);
		$("#favorite").data("listing-id", listingId);
	}
}

function unfavoriteListing(evt) {

	let listingId = $(this).data("listingId");
	let formInputs = {
		"listing_id": listingId
	}

	$.post("/unfavorite_listing", formInputs, showProfile);
}

$("#unfavorite").on("click", unfavoriteListing);


function favoriteListing(evt) {

	let listingId = $(this).data("listingId");
	let formInputs = {
		"listing_id": listingId
	}

	$.post("/favorite_listing", formInputs, showProfile);
}

$("#favorite").on("click", favoriteListing);