import base64

# Code translated from turbofilm base64 implementation
def enc_replace(g, f):
    c = ""
    b = ""
    a = 0
    e = ["2","I","0","=","3","Q","8","V","7","X","G","M","R","U","H","4","1","Z","5","D","N","6","L","9","B","W"]
    d = ["x","u","Y","o","k","n","g","r","m","T","w","f","d","c","e","s","i","l","y","t","p","b","z","a","J","v"]
    c = d
    b = e
    while a < len(c):
        g = enc_replace_ab(c[a], b[a], g)
        a += 1
    return g

def enc_replace_ab(e, d, c):
    c = c.replace(e, "___")
    c = c.replace(d, e)
    c = c.replace("___", d)
    return c

def decode(a):
    a = enc_replace(a, "d")
    return base64.b64decode(a)