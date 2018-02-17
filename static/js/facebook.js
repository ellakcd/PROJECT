FB.init({
      appId      : '{554256274953457}',
      cookie     : true,
      xfbml      : true,
      version    : '{v2.8}'
    });





(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = 'https://connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.8&appId=554256274953457&autoLogAppEvents=1';
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));


 //  window.fbAsyncInit = function() {
 //    FB.init({
 //      appId      : '{554256274953457}',
 //      cookie     : true,
 //      xfbml      : true,
 //      version    : '{v2.8}'
 //    });
      
 // //    FB.AppEvents.logPageView();   
 // //    FB.api('/me', function(response) {
	// // console.log(JSON.stringify(response));
	// // });
 //  };


function loggin() {
    FB.getLoginStatus(function(response) {
  if (response.status === 'connected') {
    console.log('Logged in.');
  } else {
    console.log('Try again.');
  } 
} );
}


function logout() {
  FB.logout();
  FB.getLoginStatus(function(response) {
  if (response.status !== 'connected') {
    console.log('Logged out.');
}} );
}

function showMe() {
 FB.api('/me', function(response) {
   $.post("/login", JSON.stringify(response), function(){
     console.log("logged in")
   });
 });
}

   function findFriends(){
        url = "/" + FB.getUserID() + "/friends";
        console.log(url);
          FB.api(
            url,
            function (response) {
              if (response && !response.error) {
                console.log(response)
              }
            }
          );
      }
   findFriends()



// $("fb-login-button").on("click", testAPI);

 function testAPI() {
        console.log('Welcome!  Fetching your information.... ');
        FB.api('/me', function(response) {
          console.log('Successful login for: ' + response.name);
          document.getElementById('status').innerHTML =
            'Thanks for logging in, ' + response.name + '!';
        });
      }


// $("fb-logout-button").on("click", FB.logout);
  