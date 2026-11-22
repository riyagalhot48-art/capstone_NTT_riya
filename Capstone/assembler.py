"""Hack assembler (two-pass).  K = 10  ->  extra feature: clear error
messages with line numbers instead of crashing.
Usage: python assembler.py Prog.asm   ->  writes Prog.hack
"""
import re
import sys

SYMBOLS = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
           "SCREEN": 16384, "KBD": 24576}
for i in range(16):
    SYMBOLS[f"R{i}"] = i

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
}
# same operations using M instead of A (a-bit = 1)
for k, v in list(COMP.items()):
    if "A" in k:
        COMP[k.replace("A", "M")] = "1" + v[1:]

DEST = {"": "000", "M": "001", "D": "010", "MD": "011",
        "A": "100", "AM": "101", "AD": "110", "AMD": "111"}
JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}

NAME = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")


def assemble(lines):
    errors = []          # list of (line_number, message)
    symbols = dict(SYMBOLS)
    code = []            # list of (line_number, text)

    # ---------- First pass: remove comments/blanks, record labels ----------
    for n, raw in enumerate(lines, 1):
        text = raw.split("//")[0].replace(" ", "").replace("\t", "").strip()
        if not text:
            continue
        if text.startswith("("):
            if not text.endswith(")") or not NAME.match(text[1:-1]):
                errors.append((n, f"invalid label '{text}'"))
            else:
                symbols[text[1:-1]] = len(code)   # address of next instruction
        else:
            code.append((n, text))

    # ---------- Second pass: translate to 16-bit binary ----------
    out = []
    next_var = 16
    for n, text in code:
        if text.startswith("@"):
            val = text[1:]
            if val.isdigit():
                num = int(val)
                if num > 32767:
                    errors.append((n, f"number too large '{text}' (max 32767)"))
                    continue
            elif NAME.match(val):
                if val not in symbols:
                    symbols[val] = next_var
                    next_var += 1
                num = symbols[val]
            else:
                errors.append((n, f"invalid A-instruction '{text}'"))
                continue
            out.append(format(num, "016b"))
        else:
            dest, jump, comp = "", "", text
            if "=" in comp:
                dest, comp = comp.split("=", 1)
            if ";" in comp:
                comp, jump = comp.split(";", 1)
            if dest not in DEST:
                errors.append((n, f"invalid destination '{dest}'"))
            elif comp not in COMP:
                errors.append((n, f"invalid instruction '{text}' (bad computation '{comp}')"))
            elif jump not in JUMP:
                errors.append((n, f"invalid jump '{jump}'"))
            else:
                out.append("111" + COMP[comp] + DEST[dest] + JUMP[jump])
    return out, errors


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".asm"):
        print("Usage: python assembler.py Prog.asm")
        sys.exit(1)
    path = sys.argv[1]
    try:
        with open(path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: file '{path}' not found")
        sys.exit(1)

    out, errors = assemble(lines)
    if errors:
        for n, msg in errors:
            print(f"Line {n}: {msg}")
        print(f"Assembly failed with {len(errors)} error(s). No .hack file written.")
        sys.exit(1)

    hack = path[:-4] + ".hack"
    with open(hack, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"OK: wrote {hack} ({len(out)} instructions)")


if __name__ == "__main__":
    main()