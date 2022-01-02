var express=require("express");
var bodyParser=require("body-parser");
var fs = require('fs');
var path=require("path");
var querystring=require("querystring");
const { MongoClient, ObjectID } = require('mongodb');
const MONGO_URL=process.env.MONGO_URL;
const SECRET=process.env.SECRET;
var app=express();
const session=require("express-session");
const ejs=require("ejs");
const sanitize=require("mongo-sanitize");
app.use(session({secret:SECRET,resave:false,saveUninitialized:false}))
app.use(express.static('static'));
app.set('views', './views');
app.set('view engine', 'ejs');
app.use(bodyParser.urlencoded({extended:true}));
const client = new MongoClient(MONGO_URL,{useUnifiedTopology: true});

const UNSAFE_KEYS = ["__proto__", "constructor", "prototype"];

const merge = (obj1, obj2) => {
  for (let key of Object.keys(obj2)) {
    if (UNSAFE_KEYS.includes(key)) continue; 
    const val = obj2[key];
    key = key.trim();                        
    if (typeof obj1[key] !== "undefined" && typeof val === "object") {
      obj1[key] = merge(obj1[key], val);     
    } else {
      obj1[key] = val;                     
    }
  }

  return obj1;
};


app.get("/",(req,res)=>{
	return res.render("index");
});

app.get("/home",(req,res)=>{
	if(req.session.username){
		return res.send("Not implemented yet! Left to little sasuke to do it");
	}
	else{
		res.redirect(302,"/login");
	}

});
app.get("/logout",(req,res)=>{
	try{
	if (req.session.username){
		req.session.destroy();
		res.redirect(302,"/");
	}
	else{
		res.redirect(302,"/");
	}
}
catch(err)
{
	console.log(err);
}})

app.get("/register",(req,res)=>{
	var sess=req.session;
	if(sess.username){
		res.redirect(302,"/home");
	}
	else{
		return res.render("register",{error:""});	
	}
});

app.post("/register",(req,res)=>{
	try{
	var username=sanitize(req.body.username);
	var password=sanitize(req.body.password);
	if(username && password){
		client.connect(function (err){
			if (err) return res.render("register",{error:"An unknown error has occured"});
			const db=client.db("kimetsu");
			const collection=db.collection("users");
			collection.findOne({"username":username},(err,result)=>{
				if (err) {return res.render("register",{error:"An unknown error has occured"});console.log(err);}
				if (result) return res.render("register",{error:"This username already exists, Please use another one"});
				else{
					collection.insertOne({"username":username,"password":password},(err,result)=>{
						if (err) {return res.render("register",{error:"An unknown error has occured"});console.log(err);}
						req.session.username=username;
						res.redirect(302,"/home");
						});
				}
		});
	});
}

	else return res.render("register",{error:"An unknown error has occured"});
}
catch(err){
	console.log(err);
}
});

app.get("/login",(req,res)=>{
	if(req.session.username){
		res.redirect(302,"/home");
	}
	else{
		return res.render("login",{error:""});
	}
});
app.post("/login",(req,res)=>{
	try{
	var username=sanitize(req.body.username);
	var password=sanitize(req.body.password);
	if (username && password){
		client.connect(function(err){
			if (err) return res.render("login",{error:"An unknown error has occured"});
			const db=client.db("kimetsu");
			const collection=db.collection("users");
			collection.findOne({"username":username,"password":password},(err,result)=>{
				if (err) return res.render("login",{error:"An unknown error has occured"});
				if (result) {
					req.session.username=username;
					res.redirect(302,"/home");
				}
				else{
					return res.render("login",{error:"Your username or password is wrong"});
				}
	});
	});
	}
	else return res.render("login",{error:"An unknown error has occured"});
}
catch(err){
	console.log(err);
}
});



app.post("/guinjutsu",function(req,res){
	//implement a filter for usernames starting only with uchiha! We are racist in Uchiha clan
	const filter={};
	merge(filter,req.body);
	console.log(req.session.isAdmin,req.session.username);
	if(req.session.isAdmin && req.session.username){
	var filename=req.body.filename;
	if (filename.includes("../")){
		return res.send("No No Sorry");
	}
	else{
		filename=querystring.unescape(filename);
		const data = fs.readFileSync(path.normalize("./"+filename), 'utf8');
		return res.send(data);
	}
	}
	else{
		res.send("Not Authorized");
	}

});

app.listen(5555);
console.log("Listening on 5555")

