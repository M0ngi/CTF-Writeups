# YogoshaChristmas 

The Christmas Challenge, started the 25th of December at 19:00 UTC and ended the 31st of December at 19:00 UTC, is a CTF hosted by Yogosha Team.
The CTF consists of 5 consecutive challenges, based on a Naruto story.
I've joined the CTF the 26th of December & played till the 30th. At the end of the CTF I've ranked 20.


* ### Welcome Christmas (OSINT):

As a start & since it's an OSINT challenge, I googled the only thing I had: "ShisuiYogo".
I like Naruto but I haven't really watched it so I thought at first I'll probably need some knowledge about it
when I first landed on the Twitter profile & seen the picture of it.

I started digging around the profile, looking at the picture of it & the 4 posts in it but I had nothing in mind.
I even ended up checking the followers & the following of the account, I was so desperate to find a lead.

After a while, a pretty long one, I decided to actually focus on the content of the posts & get a meaning out of it.
The last post made me sure that I'll have to find what I'm looking for in an other website, not Twitter, but where?

```
I shared the important image I got in a popular website. I like this website since I'm the master of that Jutsu
```

<br/>
As a first thought, I ended up looking in Github, thanks to the "master" of that. After a couple of searches I decided to move on.<br/>
So since I've spent a while looking everywhere, I decided to study a little about this character since I have no clue what's he talking about in the posts.
Not to mention that this'll probably be an other goal for the OSINT challenge, gathering information, right?

I started reading about Uchiha Shisui & Uchiha Clan. Also I've searched for the teleportation jutsu since it was mentioned in the Twitter post.
Now, I have a little bit of knowledge & I suppose I'm ready to refresh my mind & re-check what I currently have.

Again, I quickly rechecked the pictures, even checked the link in the profile picture but decided to move on quickly. I tried few words that I found in the story but no results.
I went again to the last post in the account to recheck it. What could the website be? 

<p align="center">
  <img src="/2021/YogoshaChristmas/img/post.jpg"><br/>
</p>

"I'm a master of that jutsu", thanks to my little knowledge, I now know that Uchiha Shisui is known as a master of "Body Flicker" technique
and not the teleportation as the GIF shows, so I googled "Body Flicker", as simple as that BUT I didn't get anything specific so...
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


- WIP -

