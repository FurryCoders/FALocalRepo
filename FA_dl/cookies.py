import FA_var as favar

def cookies_error():
    print('Analyzing cookies file for errors:')
    cookies_name = ['__cfduid', 'b', '_adb', '__qca', '__asc', '__auc', '__gads', 'a']

    with open(favar.cookies_file, 'r') as f:
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
        if n not in [c['name'] for c in cookies if 'name' in list(c.keys())]:
            missing_names.append(n)
    if missing_names:
        print(' Following cookies are missing:')
        for n in missing_names:
            print('  {n}')
