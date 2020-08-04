from typing import List

from PythonRead import getkey


def menu(options: List[str]) -> int:
    options = list(map(lambda o: f"{o[0]}) {o[1]}", enumerate(options, 1)))

    print("\n".join(options))
    print("\nChoose option: ", end="", flush=True)

    choice: int = 0
    while choice < 1 or choice > len(options):
        choice_str = getkey()
        if choice_str.isdigit():
            choice = int(choice_str)
        elif choice_str in ("\x03", "\x04", "\x1B"):
            choice = len(options)

    print(choice)

    return choice
