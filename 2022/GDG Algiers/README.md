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