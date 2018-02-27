// function addPointerByAddress(address) {
//   let pointerLocation = new google.maps.Geocoder();
//   let houseInfo = address;
//   console.log(houseInfo);
//   let houseAddress = houseInfo[0];
//   let houseId = houseInfo[1];
//   console.log(houseAddress);
//   console.log(houseId);

// // <a href="/listings/`${houseId}`">houseId</a>
//   pointerLocation.geocode({'address': houseAddress},
//     function(results, status) {
//       console.log(results);
//       if (status === google.maps.GeocoderStatus.OK) {
//         let marker = new google.maps.Marker({
//           map: main_map,
//           position: results[0].geometry.location
//         });
//         let contentString = `<a href="/listings/${houseId}">${houseAddress}</a>`;
//         let infoWindow = new google.maps.InfoWindow({
//           map: main_map,
//           content: contentString,
//           maxWidth: 200
//         });
//         marker.addListener('click', function() {
//           infoWindow.open(main_map, marker);
//         });
//       } 
//   });
// }




// function addMapByAddress(address) {
//   let pointerLocation = new google.maps.Geocoder();
//   let houseAddress = `${address}`;

//   pointerLocation.geocode({'address': houseAddress},
//     function(results, status) {
//       if (status === google.maps.GeocoderStatus.OK) {
//         window.main_map = new google.maps.Map(document.querySelector('#main_map'), {
//         center: results[0].geometry.location,
//         zoom: 10,
//         });
//       } else {
//         alert('Geocode was not successful for the following reason: ' + status);
//       }
//   });
// }


// function showListingInfoOnMap(map_data) {
//   let centerPoint = map_data[0][0];

//   addMapByAddress(centerPoint);

//   for (let i=0; i<map_data.length; i++) {
//     let address = map_data[i];
//     console.log(address);
//     addPointerByAddress(address);
//   }
// }

// showListingInfoOnMap(map_data);
// console.log(map_data);
