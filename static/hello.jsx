class Hello extends React.Component {
	render() {
	return <p> Hi World! </p>
	}
}

ReactDOM.render(
<Hello />, 
document.getElementById("root")
);


class Mailbox extends React.Component {
	
	getMessages() {
		fetch("/messages.json")
		.then((response)=> response.json())
		.then((data)=> alert(data.messages)
		);
	}

	render() {
		return <button onClick={this.getMessages}>
			Get Messages!
			</button>
	}
}

ReactDOM.render(
<Mailbox />, 
document.getElementById("root")
);
