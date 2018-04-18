def tiers(ID, t1=10000000, t2=1000000, t3=1000):
    ID = int(ID)
    tier1 = ID//t1
    tier2 = (ID-(t1*tier1))//t2
    tier3 = ((ID-(t1*tier1))-(t2*tier2))//t3

    return f'{tier1}/{tier2}/{tier3:03d}'

def cookies_error():
    print('Analyzing cookies file for errors:')
    cookies_name = ['__cfduid', 'b', '_adb', '__qca', '__asc', '__auc', '__gads', 'a']

    with open('FA.cookies.json', 'r') as f:
        cookies = json.load(f)

    missing_names = 0
    missing_values = 0
    for c in cookies:
        if 'name' not in list(c.keys()):
            missing_names += 1
        if 'value' not in list(c.keys()):
            missing_values += 1
    if missing_names:
        print(f" {missing_names} cookie{'s'*int(len(missing_names) != 1)} without the 'name' field")
    if missing_values:
        print(f" {missing_values} cookie{'s'*int(len(missing_values) != 1)} without the 'name' field")

    missing_names = []
    for n in cookies_name:
        if n not in [c['name'] for c in cookies]:
            missing_names.append(n)
    if missing_names:
        print(' Following cookies are missing:')
        for n in missing_names:
            print('  {n}')
