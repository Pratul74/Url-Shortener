ALPHABETS="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

BASE = len(ALPHABETS)

_INDEX={c: i for i, c  in enumerate(ALPHABETS)}

def encode(n: int) -> str:
    if n==0:
        return ALPHABETS[0]
    out=[]
    while n:
        n, r = divmod(n, BASE)
        out.append(ALPHABETS[r])
    return ''.join(reversed(out))

def decode(s: str) -> int:
    n=0
    for c in s:
        n = n*BASE + _INDEX[c]
    return n
