const express = require('express');
const app=express();
const { MongoClient, ObjectID } = require('mongodb');
const MONGO_URL=process.env.MONGO_URL;
const SECRET=process.env.SECRET;
const bodyParser = require('body-parser');
const got=require('got') ;
const session=require("express-session");
const ejs=require("ejs");
app.use(bodyParser.urlencoded({extended:false}));
app.use(bodyParser.json());
app.use(session({secret:SECRET,resave:false,saveUninitialized:false}))
app.use(express.static('static'));
app.set('views', './views');
app.set('view engine', 'ejs');
const client = new MongoClient(MONGO_URL);

//Insert important infos in the DB
var services=[
{"Service":"web","username":"shisui","password":"Random","IP":"0000"},
{"Service":"web","username":"itachi","password":"Secure","IP":"127.0.0.1"},
{"Service":"ssh","username":process.env.USERNAME,"password":process.env.PASSWORD,"IP":process.env.IP},
{"Service":"net","username":"sasuke","password":"Random","IP":"0000"}
];
client.connect(function (err){
        if (err) return res.render("register",{error:"An unknown error has occured"});
        const db=client.db("uchiha");
        const collection=db.collection("services");
        collection.insertMany(services,function(err, res) {
                if (err) console.log(err);
                console.log("Number of documents inserted: " + res.insertedCount);
        });

});


//generate jutsus
//credits Harekaze Mini CTF
let articles = [];
articles[0]={jutsu:"I heard that there is something interesting in jutsu number 1337, it's the most secret one!!"};
articles[1]={jutsu:`I'm using the following to avoid access to jutsus higher than 9; is it safe? :
let id = parseInt(request.params.id, 10);
  // baka saijin can't read the jutsus with id >9
        if (id > 9) {
                return res.render("jutsu",{jutsu:"Access Denied sorry"})
        }
`};
for (let i = 2; i < 10000; i++) {
  articles.push({
    jutsu: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'.trim()
  });
}
articles[1337] = {
  jutsu: `Wow,Awesome Jutsu! It's called Dockeru. I stored the jutsu code there: id=shisuiyogo pass=YogoShisuiIsStrong image=forum  `
};


app.get("/",(req,res)=>{
        return res.render("index");
});
app.get("/jutsu/:id",(req,res)=>{
        if (/^[\b\t\n\v\f\r \xa0]*-/.test(req.params.id)) {
                return res.render("jutsu",{"jutsu":"Hacking Attempted"});
        }
          let id = parseInt(req.params.id, 10);

  // baka saijin can't read the jutsus with id >9
        if (id > 9) {
                return res.render("jutsu",{jutsu:"Access Denied sorry"})
        }
        const jutsu = articles.at(id) ?? {
                jutsu: 'Not found'
        };
        return res.render("jutsu",jutsu);
});

app.get("/login",(req,res)=>{
        if(req.session.username){
                res.redirect(302,"/home");
        }
        else{
                return res.render("login",{error:""});
        }
})


app.post("/login",(req,res)=>{
        var username=req.body.username;
        if(username){
                got.get(`http://3.141.109.49/auth/${encodeURI(username)}/users`).then((resp)=>{
                if (resp.statusCode==200){
                        req.session.username=username;
                        return res.redirect(302,"/home");
                }
                else{
                        return res.render("login",{error:"Your username is wrong"});
                }
                }).catch((err)=>{return res.render("login",{error:"Your username is wrong"});});
        }
        else{
                return res.redirect(302,"/login");
        }

});

app.get("/home",(req,res)=>{
        if(req.session.username){
                return res.render("home",{"username":req.session.username});
        }
        else{
                res.redirect(302,"/login");
        }

});

app.get("/services",(req,res)=>{
        if(req.session.username){
                return res.render("service",{error:""});
        }
        else{
                return res.redirect(302,"/login");
        }
});

app.post("/services",(req,res)=>{
        if(req.session.username){
                if (req.body.service){
					// gggg\",\"x\": process.env.USERNAME,\"xx\": \"hi
					//gggg","Service":{"$gt":""},"xx": "hi
                        var query=JSON.parse(`{"Service":"${req.body.service}"}`);
                        client.connect(function(err){
                                if (err) return res.render("service",{error:"An unknown error has occured"});
                        const db=client.db("uchiha");
                        const collection=db.collection("services");
                        collection.findOne(query,(err,result)=>{
                                if (err) return res.render("service",{error:"An unknown error has occured"});
                                if (result) {
                                        return res.render("service",{error:"Service is UP"});
                                }
                                else{ return res.render("service",{error:"Service is Down"})};
                        });
                        });
                }
                else{
                        return res.render("service",{error:"An unknown error has occured"});

                }
        }

else { return res.redirect(302,"/login");}

});

//authentication
app.get("/auth/:username/users",(req,res)=>{
        if (req.params.username==process.env.REDACTED){
                return res.send("OK");
        }
        else{
                return res.sendStatus(202);
        }
}
)

app.listen(8000,"0.0.0.0");
console.log("Listening 8000 ..");