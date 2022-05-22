const express = require('express'); 
const app = express(); 
const session = require('express-session'); 
const RedisStore = require("connect-redis")(session) 
const path = require('path'); 
const cookieParser = require('cookie-parser'); 
const nunjucks = require('nunjucks'); 
const routes = require('./routes'); 
const Database = require('./database'); 
const { createClient } = require("redis") 
const redisClient = createClient({ legacyMode: true }) 
const db = new Database('redisland.db'); 

app.use(express.json()); 
app.use(cookieParser()); 

redisClient.connect().catch(console.error)

app.use( session({ 
	store: new RedisStore({ client: redisClient }), 
	saveUninitialized: false, secret: "r4yh4nb34t5B1gM4c", resave: false, 
}));

nunjucks.configure('views', { autoescape: true, express: app }); 
app.set('views', './views'); 
app.use('/static', express.static(path.resolve('static')));

app.use(routes(db)); 

app.all('*', (req, res) => { 
	return res.status(404).send({ message: '404 page not found' }); 
}); 

(async () => { 
	await db.connect(); 
	await db.migrate(); 
	app.listen(1337, '0.0.0.0', () => console.log('Listening on port 1337')); 
})();
