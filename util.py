
def avg(l):
    return sum(l) / len(l)

def isRed(a):
    return a[2] > 625 and a[2] < 655

def isGreen(a):
    return a[2] > 900

def isGround(a):
    return not isRed(a) and not isYellow(a)
