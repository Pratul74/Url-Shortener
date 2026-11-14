ALPHABETS="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

BASE = len(ALPHABETS)

def encode(n: int) -> str:
    if n==0:
        return ALPHABETS[0]
    out=[]
    while n:
        n, r = divmod(n, BASE)
        out.append(ALPHABETS[r])
    return ''.join(reversed(out))
