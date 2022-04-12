# National Cyber Security Congress

[Securiday](https://www.facebook.com/Securiday-104756755537130/) qualifiation round, hosted by [Securinets](https://www.facebook.com/Securinets), a 24 hour CTF. Top #10 teams will be able to compete in Securiday CTF.<br/>
I've participated in the CTF as a member of Enthousiast team. We ranked 22 out of 295 teams.

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

