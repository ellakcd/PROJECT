

function renderNewConvos(results) {
	let new_messages = results["new_messages"];
	let partnerId = results["partner"];
	let last = $(`#${partnerId}`).data("last");
	for (let i=0; i<new_messages.length; i++) {
		let new_message = new_messages[i];
		$(`#${partnerId}`).append(new_message[1] + "<br>")
		last = new_message[0];
	}
	$(`#${partnerId}`).data("last", last);
}

function getNewMail() {
	$(".conversation").each(function() {
		let last = $(this).data("last");
		let sender = $(this).data("sender");
		let formInputs = {
			"last": last, 
			"sender": sender
		}
		$.get("/new_messages.json", formInputs, renderNewConvos);
	});
}


setInterval(getNewMail, 2000);


function sendNewMessage(evt) {
	evt.preventDefault();
	console.log("it works");
	let receiverId = $(this).data("receiver");
	let message_space = $("textarea#"+receiverId+"message");
	let message = message_space.val();
	message_space.val("");

	let formInputs = {
			"user_id": receiverId, 
			"message": message
		}
	$.post("/add_message", formInputs, getNewMail);
}


$(".add_message").on("submit", sendNewMessage);