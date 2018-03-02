function showProfile(results) {
	console.log(results["favorite"]);
	let listingId = results["listing_id"];
	if (results["favorite"] === true) {
		$("#favorite_or_not").html("<button id='unfavorite'> Unfavorite This Listing </button>");
		$("#unfavorite").on("click", unfavoriteListing);
		$("#unfavorite").data("listing-id", listingId);
	} else {
		$("#favorite_or_not").html("<button id='favorite'> &#9825; Favorite This Listing &#9825; </button>");
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










function showActive(results) {
	console.log(results["listed"]);
	console.log(results["avail_date"]);
	let listingId = results["listing_id"];
	if (results["listed"] === true) {
		let availDate = results["avail_date"];
		$("#listed_or_not").html("<button id='unlist'> Take This Listing off The Market </button>");
		$("#unlist").on("click", unlistListing);
		$("#unlist").data("listing-id", listingId);
		$("#show_avail_dates").html("Avail as Of: " + availDate);
	} else {
		$("#listed_or_not").html("<form id='relist' data-listing-id='"+listingId+"'>When is it avail?:<br><input type='date' id='avail'><br><input type='submit' value='Put This Listing Back on the Market'><br></form>");
		$("#relist").on("submit", relistListing);
		$("#relist").data("listing-id", listingId);
		$("#show_avail_dates").html("Listing not Currently Available");
	}
}

function unlistListing(evt) {

	let listingId = $(this).data("listingId");
	let formInputs = {
		"listing_id": listingId
	}

	$.post("/unlist_listing", formInputs, showActive);
}



function relistListing(evt) {
	let listingId = $("#listed_or_not").data("listingId");
	console.log(listingId);
	let availDate = $("#avail").val();
	console.log(availDate);
	let formInputs = {
		"listing_id": listingId,
		"avail": availDate
	}

	$.post("/relist_listing", formInputs, showActive);


}


function findOutIfListingActive() {
	let listingId = $("#listed_or_not").data("listingId");
	console.log(listingId);
	let formInputs = {
		"listing_id": listingId
	}

	$.get("/listing_active", formInputs, showActive);
}

findOutIfListingActive();