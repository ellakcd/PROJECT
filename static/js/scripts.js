

function showListingInfo(results) {

  console.dir(results)
  $(".popup").append("Price: " + results["price"]);
  $(".popup").append("<br>Start date: " + results["start date"]);

  let friends = results["friends"];
  let mutuals = results["mutuals"];

  if (friends.length > 0) {
      $(".popup").append("<br><br> Friends:");
      for (let i=0; i < friends.length; i++){
          let friend = friends[i]
          $(".popup").append("<br>" + friend[0] + "<br>");
          $(".popup").append($('<img>',{id:'friend-pic', class: "tiny_photo", src:friend[1]}));
  }} else {
          if (mutuals.length > 0) {
              $(".popup").append("<br><br> Mutual Friends:");
              for (let i=0; i < mutuals.length; i++){
                      let mutual = mutuals[i]
                      $(".popup").append("<br>" + mutual[0] + "<br>");
                      $(".popup").append($('<img>',{id:'friend-pic', class: "tiny_photo", src:mutual[1]}));
  }}}
    $(".popup").attr("id", "popup");
  }

function getListingInfo(evt) {
  let listing_id = $(this).data("listingId");
  let formInputs = {
    "listing_id": listing_id
  };
  // debugger;
  $(this).append($(".popup"));

  $.get("/listing-info.json", formInputs, showListingInfo);
}

function clear(evt) {
  $(".popup").empty();
  $(".popup").removeAttr("id");
}



function showUserInfo(results) {

  $(".popup").append("<br>Common Answers:<br>")
  let answers = results["answers"]

  if (answers.length > 0) {
      for (let i=0; i < answers.length; i++){
          let answer = answers[i]
          $(".popup").append(answer + "<br>");
      }
  } else {
      $(".popup").append("None, alas...<br>");
  }
  $(".popup").append("<br>Mutual Friends:")
  let friends = results["friends"]
  if (friends.length > 0) {
    for (let i=0; i < friends.length; i++){
        let friend = friends[i]
        $(".popup").append("<br>" + friend[0] + "<br>");
        $(".popup").append($('<img>',{id:'friend-pic', class: "tiny_photo", src:friend[1]}))
      }
  } else {
    $(".popup").append("None, alas...<br>");
  }
    $(".popup").attr("id", "popup");
}


function getUserInfo(evt) {
  let user_id = $(this).data("userId");
  let formInputs = {
    "user_id": user_id
  };

   $(this).append($(".popup"));

  $.get("/user-info.json", formInputs, showUserInfo);
}

function clear(evt) {
  $(".popup").empty();
  $(".popup").removeAttr("id");
}



$(".listing").on("mouseenter", getListingInfo);
$(".listing").on("mouseleave", clear);

$(".user").on("mouseenter", getUserInfo);
$(".user").on("mouseleave", clear);


