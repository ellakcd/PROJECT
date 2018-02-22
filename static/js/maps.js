// MAP STUFF


function addPointerByAddress(address) {
  let pointerLocation = new google.maps.Geocoder();
  let houseAddress = `${address}`;
  console.log(houseAddress)

  pointerLocation.geocode({'address': houseAddress},
    function(results, status) {
      if (status === google.maps.GeocoderStatus.OK) {
        let map = new google.maps.Map(document.querySelector('#map'), {
        center: results[0].geometry.location,
        zoom: 14,
        });
        let marker = new google.maps.Marker({
          map: map,
          position: results[0].geometry.location
        });
        let infoWindow = new google.maps.InfoWindow({
          map: map,
          content: `<a href="https://maps.google.com/?q=${houseAddress}">View on Google Maps</a>`,
          maxWidth: 200
        });
        marker.addListener('click', function() {
          infoWindow.open(map, marker);
        });
      } 
  });
}

function getListingAddress() {
  let listingAddress = $("#map").data("address");
  console.log(listingAddress)
  addPointerByAddress(listingAddress);
}

getListingAddress()