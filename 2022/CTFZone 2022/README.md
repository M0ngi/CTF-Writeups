# CTFZone 2022

A 48h CTF Organized by BIZone which took place on August 24–26.

I played as a member of Soteria Team & together, we ranked 22th out of more than 1000 teams.

For this CTF, I've played pwn challenges & they were pretty tough. I've searched & learnt new stuff when dealing with these challenges therefore I really enjoyed this one. I've managed to solve 3 challeges & made progress in the fourth challenge (`stringi`) but I didn't manage to solve it. My favorite challenge for this CTF was [microp](#pwn3 "Writeup"), feel free to check the writeup for more details!

------------

- [Pwn](#pwn)
    -  [Python Bytecode Challenge - Welcome & Part 1](#pwn1 "Writeup")
	-  [OneChat](#pwn2 "Writeup")
    -  [microp](#pwn3 "Writeup")

------------

### Pwn
1. <p name="pwn1"><b>Python Bytecode Challenge - Welcome & Part 1</b> - Medium</p>

For this one, we were given a cli that took care of testing & submitting the solutions. This challenge consist of a set of challenges:

```
Tasks list without names:
- t0-series - 2 tasks - Welcome & guide
- t1-series - 6 tasks - 1 flag - easy-medium
- t2-series - 4 tasks - 1 flag - easy-medium
- t3-series - 3 tasks - 1 flag - medium-hard
- t4-series - 3 tasks - 1 flag - medium
- t5-series - 2 tasks - 1 flag - medium-hard
```

You may check out the cli [here](/2022/CTFZone%202022/source/bc_challenge/) & make sure to check the [guide](/2022/CTFZone%202022/source/bc_challenge/guide). I solved only the `t1-series` challenges therefore the rest of the tasks will be missing from there. The next task was automatically downloaded after solving a task.

The `t0-series` are a tutorial to how to use the cli & get friendly with the environment.

This challenge required a knowledge of Python OpCodes. We were asked to write a function with certain limits, such as opcodes used, the number of opcodes & constantss... And we had to retrieve a secret which could be found in a module or in a variable...

Tasks: [Link](/2022/CTFZone%202022/source/bc_challenge/bc_challenge/tasks/)<br>
Solutions: [Link](/2022/CTFZone%202022/source/bc_challenge/bc_challenge/solutions/)

For this challenge, [Python Documentation](https://docs.python.org/3.9/library/dis.html#python-bytecode-instructions) was good enough to figure out what opcodes to use/remove.

<br>

2. <p name="pwn2"><b>OneChat</b> - Easy</p>

<br>

2. <p name="pwn3"><b>microp</b> - Medium</p>