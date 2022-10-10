# GDG Algiers

This was an unofficial participation for my team & despite being a day behind, we ranked 14th out of more than 700 teams.

For this one, I focused on *Jail* & *PWN*. I solved 3 jails & 4 pwn challenges, 1 was after the end of the CTF.

I did enjoy 3 challenges in this CTF, which encouraged me to work on a detailed writeup for the solves. These challenges are:

* [Kevin Higgs: The Revenge (PyJail)](#jail3)
* [Notes keeper (Pwn)](#pwn2)
* [Faster python (Pwn)](#pwn4)

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
    Binary Security:

    <p align="center">
    <img src="/2022/GDG%20Algiers/img/Notes%20Keeper/checksec.png"><br/>
    </p>

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

    * **Exploiting**:

    WIP

<br />

3. <p name="pwn3"><b>Mind games</b></p>

<br />

4. <p name="pwn4"><b>Faster Python</b></p>

<br />

### Jail
1. <p name="jail1"><b>Red Diamond</b></p>

<br />

2. <p name="jail2"><b>Type it</b></p>

<br />

3. <p name="jail3"><b>Kevin Higgs: The Revenge</b></p>

------------

WIP