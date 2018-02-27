

function showListingInfo(results) {
  console.dir(results)
  $("#popup").append("<br>Price:<br>" + results["price"]);
  $("#popup").append("<br>Start date:<br>" + results["start date"]);
  $("#popup").append("<br> Friends:")
  let friends = results["friends"]
  for (let i=0; i < friends.length; i++){
    let friend = friends[i]
    $("#popup").append("<br>" + friend[0] + "<br>");
    $("#popup").append($('<img>',{id:'friend-pic', class: "tiny_photo", src:friend[1]}))
   }
}

function getListingInfo(evt) {
  console.log("mousover");
  let listing_id = $(this).data("listingId");
  let formInputs = {
    "listing_id": listing_id
  };

  $.get("/listing-info.json", formInputs, showListingInfo);
}

function clear(evt) {
  $("#popup").empty();
}

$(".listing").on("mouseover", getListingInfo);
$(".listing").on("mouseleave", clear);





function showUserInfo(results) {
  console.dir(results)
  $("#popup").append("<br>Common Answers:<br>")
  let answers = results["answers"]
  for (let i=0; i < answers.length; i++){
    let answer = answers[i]
    $("#popup").append(answer + "<br>");
  }
  $("#popup").append("Mutual Friends:")
  let friends = results["friends"]
  for (let i=0; i < friends.length; i++){
    let friend = friends[i]
    $("#popup").append("<br>" + friend[0] + "<br>");
    $("#popup").append($('<img>',{id:'friend-pic', class: "tiny_photo", src:friend[1]}))
  }
}

function getUserInfo(evt) {
  console.log("MOuSING");
  let user_id = $(this).data("userId");
  let formInputs = {
    "user_id": user_id
  };

  $.get("/user-info.json", formInputs, showUserInfo);
}

function clear(evt) {
  $("#popup").empty();
}

$(".user").on("mouseenter", getUserInfo);
$(".user").on("mouseleave", clear);


console.log("IN SCRIPT");
