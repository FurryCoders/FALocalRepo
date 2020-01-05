def tiers(ID, t1=10000000, t2=1000000, t3=1000):
    ID = int(ID)
    tier1 = ID // t1
    tier2 = (ID - (t1 * tier1)) // t2
    tier3 = ((ID - (t1 * tier1)) - (t2 * tier2)) // t3

    return f"{tier1}/{tier2}/{tier3:03d}"


def header(s, brk="-", end="\n", l=20):
    print(brk * l)
    print(s)
    print(brk * l)
    print(end=end)
