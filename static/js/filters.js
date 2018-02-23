

// function renderNewConvos(results) {
// 	let new_messages = results["new_messages"];
// 	let partnerId = results["partner"];
// 	let last = $(`#${partnerId}`).data("last");
// 	for (let i=0; i<new_messages.length; i++) {
// 		let new_message = new_messages[i];
// 		$(`#${partnerId}`).append(new_message[1])
// 		last = new_message[0];
// 	}
// 	$(`#${partnerId}`).data("last", last);
// }


function showListings(results) {
	let listings = results["listings"]
	for (let i=0; i<listings.length; i++) {
		let listing = listings[i];
		let address = listing.address;
		let photo = listing.photo;

    	$("#results").append($('<img>',{id:'listing-pic', class: "tiny_photo", src:photo}))
    	$("#results").append("<br>" + address + "<br>");
    	// $("#restuls").append()
	}
	
	// show all the neighborhoods and have a form w a hidden input of listings and 
}


function filterByNeighborhood(evt) {
	evt.preventDefault();
	let neighborhoods = [];
	$(".hood:checked").each(function(){
		neighborhoods.push($(this).val);
	});
	console.log("TEST");
	console.log(neighborhoods);
	let formInputs = {
		"neighborhoods": neighborhoods
	}
	$.get("/listings_in_neighborhood", formInputs, showListings);
}




// $("#neighborhood").on("submit", filterByNeighborhood);


