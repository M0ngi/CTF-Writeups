from opcode import opmap as OPCODE_MAPPING

G = globals()

for name, number in OPCODE_MAPPING.items():
    G[name] = number
