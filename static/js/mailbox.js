



// function showConvo(results) {
// 	let lines = results["lines"];
// 	for (let i=0; i<lines.length; i++) {
// 		let line = lines[i];
// 		$("#mailbox").append(`<div>${line}</div>`)
// 	}
// }


// function getConvo(evt) {
// 	let partner_id = $(this).data("convoPartner");
//   	let formInputs = {
//     "partner_id": partner_id
//   };
// 	$.get("/convo.json", formInputs, showConvo);
// }


// $("#see-full-convo").on("click", getConvo);


// function showConversations(results) {
// 	let convo_partners = results["convo_partners"];
// 	console.log(convo_partners);
// 	for (let i=0; i<convo_partners.length; i++) {
// 		let convo_partner = convo_partners[i];
// 		$("#mailbox").append(`<button id='see-full-convo' data-convo-partner="${convo_partner}">${convo_partner}</button>`)
// 	}
// }


// function getConversations(evt) {
// 	$.get("/conversations.json", showConversations);
// }


// $("#get-mail").on("click", getConversations);


function renderNewConvos(results) {
	console.log(results);
	let new_messages = results["new_messages"];
	let partner = results["partner"];
	let last = null;
	for (let i=0; i<new_messages.length; i++) {
		let new_message = new_messages[i];
		$(".senders").append("<br>" + new_message[1])
		last = new_message[0];
	}
	$(`#${partner}`).last = last;
}
//HOW DOES LAST MESSAGE UPDATE? - div.data = 

//wrap this in function and call setinterval on that function
function getNewMail() {
	$(".senders").each(function() {
		let last = $(this).data("last");
		let sender = $(this).data("sender");
		let formInputs = {
			"last": last, 
			"sender": sender
		}
		$.get("/new_messages.json", formInputs, renderNewConvos);
	});
}


setInterval(getNewMail, 10000);


console.log("in page");

