
function showListingsThatMatch(results) {

	$("#results").html("<h1>POTENTIAL HOMES:</h1>")

	let filters = results["filters"];
	if (filters) {
		filters = filters.split("|");
		let htmlToAdd = "";

		for (let i=0; i<filters.length; i++) {
			let filter = filters[i];
			htmlToAdd += "<button class='remove_specific' id='remove_"+filter+"'> Remove "+filter+" filter</button>";
		}
		htmlToAdd += "<button id='remove_all_filters'> Remove All Filters </button>";

		$("#remove_filters").html(htmlToAdd);
		$("#remove_all_filters").on("click", removeFilters);
		$(".remove_specific").on("click", removeSpecific);

	} else {
		$("#remove_filters").empty();
	}


	let listings = results["listings"];
	let listing_ids = Object.keys(listings);
	if (listing_ids) {
		let listing_names = listing_ids.join("|");

		$("#results").append("<div id='main_map' data-listing-names="+listing_names+"></div>");
	}

	for(let i=0; i<listing_ids.length; i++) {
		let listing_id = listing_ids[i];
		$("#results").append("<br><a href='listings/"+listing_id+"' class='listing' data-listing-id="+listing_id+">"+listings[listing_id].address+"<br><img src="+listings[listing_id].photo+"><br></a>")
	}
	$(".listing").on("mouseenter", getListingInfo);
  	$(".listing").on("mouseleave", clear);

	getAllListingInfoForMap();
}


function filterByPrice(evt) {
	evt.preventDefault();
	console.log("price")
	let priceCap = $("#price_cap").val();
	
	console.log(priceCap);
	let formInputs = {
		"price_cap": priceCap
	}

  $.get("/filter_by_price.json", formInputs, showListingsThatMatch);
}


$("#price_filter").on("submit", filterByPrice)



function filterByLaundry(evt) {

	$.get("/filter_by_laundry.json", showListingsThatMatch);
}


$("#laundry_filter").on("click", filterByLaundry);


function filterByFriends(evt) {

	$.get("/filter_by_friends.json", showListingsThatMatch);
}


$("#friends_filter").on("click", filterByFriends);


function filterByPets(evt) {
	evt.preventDefault();
	console.log("pets");
	let pets = $('input[name=pets]:checked').val();
	let formInputs = {
		"pets": pets
	}
	$.get("/filter_by_pets.json", formInputs, showListingsThatMatch);
}


$("#pets_filter").on("submit", filterByPets);


function filterByRoommates(evt) {
	evt.preventDefault();
	console.log("roommate");
	let roommates = $('input[name=roommates]:checked').val();
	console.log(roommates);
	let formInputs = {
		"roommates": roommates
	}
	$.get("/filter_by_roommates.json", formInputs, showListingsThatMatch);

}

$("#roommates_filter").on("submit", filterByRoommates);


function filterByStartDate(evt) {
	evt.preventDefault();
	console.log("start date");

	let start_dates = [];

	$(".months:checked").each(function(){
		start_dates.push($(this).val());
	});

	console.log(start_dates);
	start_dates = start_dates.join("|");

	let formInputs = {
		"start_dates": start_dates
	}

	$.get("/filter_by_start_date.json", formInputs, showListingsThatMatch);
}


$("#start_date_filter").on("submit", filterByStartDate);


function filterByDuration(evt) {
	evt.preventDefault();
	console.log("duration");
	let duration = $('input[name=duration]:checked').val();
	let formInputs = {
		"duration": duration
	}
	$.get("/filter_by_duration.json", formInputs, showListingsThatMatch);
}

$("#duration_filter").on("submit", filterByDuration);


function filterByNeighborhood(evt) {
	evt.preventDefault();
	console.log("neighborhoods");
	let neighborhoods = [];

	$(".hood:checked").each(function(){
		neighborhoods.push($(this).val());
	});

	neighborhoods = neighborhoods.join("|");

	let formInputs = {
		"neighborhoods": neighborhoods
	}
	console.log(formInputs);
	$.get("/filter_by_neighborhoods.json", formInputs, showListingsThatMatch);
}


$("#neighborhood_filter").on("submit", filterByNeighborhood);


function showAllListingsPreFilter() {
	$.get("/get_all_listings.json", showListingsThatMatch);
}


function removeSpecific(evt) {
	let filterId = $(this).attr("id");
	console.log(filterId);
	formInputs = {
		"filter": filterId
	}

	$.get("/remove_specific", formInputs, showListingsThatMatch);
}


function removeFilters(evt) {
	console.log("in remove all");
	$.get("/remove_all_filters.json", showListingsThatMatch);
}


showAllListingsPreFilter();


function showNewState(results) {
	let new_state = results["state"];
	console.log(new_state);
	$("#listings_by_state").html("<a href='/listings_by_friends_in_state'> View All Active Listings By Friends and Friends of Friends in "+new_state+"</a><br>");
	$("#listings_by_state").append("<a href='/user_friends_in_state'> View All Friends and Friends of Friends Looking for Apts in "+new_state+"</a><br><br><br>");
	if (results["neighborhoods"].length === 0) {
		$("#neighborhoods_in_state").empty();
	} else {
		let htmlToAdd = "<form id='neighborhood_filter'> What neighborhoods are you interested in?:<br>"

		for (let i=0; i<results["neighborhoods"].length; i++) {
			let neighborhood = results["neighborhoods"][i];
			htmlToAdd += "<input type='checkbox' name='neighborhoods' class='hood' value='"+neighborhood+"'>"+neighborhood;
		}
		htmlToAdd += " <input type='submit' value='Filter By Neighborhood'></form>"
		$("#neighborhoods_in_state").html(htmlToAdd);
		$("#neighborhood_filter").on("submit", filterByNeighborhood);
	}
	removeFilters();
}


function updateState(evt) {
	evt.preventDefault();
	let new_state = $("#state").find(":selected").text();
	console.log(new_state);
	let formInputs = {
		"state": new_state
	}

	$.post("/update_state.json", formInputs, showNewState)
}


$("#update_state").on("submit", updateState);












