

class Profile extends React.Component {
	
	constructor(props) {
		super(props);
		this.state = {
			user_id: null,
			photo: null,
			bio: null
		};

	}



	componentWillMount() {
	console.log("mounting comp")
        fetch('/user_basics.json', {
        	credentials: "include"
        })
          .then((response)=> response.json())
          	.then((data) => {
	      	this.setState({
	          user_id: data.user_id, 
	          photo: data.photo, 
	          bio: data.bio, 
	          favorites: data.favorites
	        });
	    })
	}


	render() {
	console.log("testing render");
		let all_favorites = [];
		const favorites = this.state.favorites;
		console.log(this.state);
		favorites && favorites.forEach(function(favorite) {
			// TODO: change API to return an object instead of a tuple, so we can call things like favorite.id, or favorite.photo instead of relying on indexes
			all_favorites.push(
				<Favorite
					key={ favorite[0] }
					favorite_id={ favorite[0] }
					favorite_photo={ favorite[1] }
				/>
			);
		})
		console.log("test");
		console.log(all_favorites);
		return(
			<div className="profile" onClick={ this.edit }>
				Hi World! 
				<h1>
					{ this.state.user_id }
				</h1>
				<img src={ this.state.photo }/>
				<p>
					bio: { this.state.bio }
				</p>
				{ all_favorites }
			</div>
		);
		}
}

class Favorite extends React.Component {

	render() {
		return (
			<div>
				<a href="/listings/{ this.props.favorite_id }">
					<img src={ this.props.favorite_photo }/>
				</a>
			</div>
		);
	}
}

class Listings extends React.Component {
	
}

class Mailbox extends React.Component {
	

}

ReactDOM.render(
<Profile />, 
document.getElementById("root")
);

