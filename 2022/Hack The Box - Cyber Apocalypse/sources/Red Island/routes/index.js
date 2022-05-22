express = require('express'); 
const router = express.Router({caseSensitive: true}); 
const AuthMiddleware = require('../middleware/AuthMiddleware'); 
const createRed = require('../helpers/createRed') 
const ImageDownloader = require('../helpers/ImageDownloader'); 

let db; 

const response = data => ({ message: data }); 

router.get('/', (req, res) => { 
	return res.render('login.html'); 
}); 

router.post('/api/register', async (req, res) => { 
	const { username, password } = req.body; 
	if (username && password) { 
		return db.getUser(username) 
			.then(user => { 
				if (user) return res.status(401).send(response('This username is already registered!')); 
				return db.registerUser(username, password) 
					.then(() => res.send(
						response('Account registered successfully!'))) 
					}) 
					.catch(() => res.status(500).send(response('Something went wrong!'))); 
	} 
	return res.status(401).send(response('Please fill out all the required fields!')); 
}); 

router.post('/api/login', async (req, res) => { 
	const { username, password } = req.body; 
	if (username && password) { 
		return db.loginUser(username, password) 
			.then(user => { 
				req.session.username = user.username; 
				res.send(response('User authenticated successfully!')); 
			}) 
			.catch((e) => { 
				console.log(e); 
				res.status(403).send(response('Invalid username or password!')); 
			}); 
	} 
	
	return res.status(500).send(response('Missing parameters!')); 
}); 

router.get('/dashboard', AuthMiddleware, async (req, res, next) => { return res.render('dashboard.html'); }); 

router.post('/api/red/generate', AuthMiddleware, async (req, res, next) => { 
	const { url } = req.body; 
	return ImageDownloader.downloadImage(url) 
		.then(imgData => { 
			createRed.addRedFilter(imgData) 
				.then(imgURI => { 
					res.send(response(imgURI)); 
				}) 
				.catch(e => { 
					res.status(401).send(response(e)) 
				}) 
		}) 
		.catch(e => { 
			if (e.isCurlError) return res.status(401).send(response('The URL specified is unreachable!'));
			
			res.status(401).send(response('Unknown error occured while fetching the image file: ' + e.toString())) 
		});
}); 

router.get('/logout', (req, res) => { 
	res.clearCookie('session'); 
	return res.redirect('/'); 
}); 

module.exports = database => { 
	db = database; 
	return router; 
};


