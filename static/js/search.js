


function showListingsThatMatch(results) {
	$("results").html("results: ")
}


function filterByPrice {
	evt.preventDefault();
	let priceCap = $(this).val();
	let formInputs = {
		"priceCap": priceCap
	}

  $.post("/filter_by_price.json", formInputs, showListingsThatMatch);
}


$("price_filter").on("submit", filterByPrice)