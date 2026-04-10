import json
from lexer import tokenize
from parser import Parser


def compile_dsl(file):

    with open(file) as f:
        code = f.read()

    tokens = tokenize(code)

    parser = Parser(tokens)
    result = parser.parse()

    with open("../subway-final/game_config.json", "w") as f:
        json.dump(result, f, indent=4)

    print("Compilation successful!")
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    compile_dsl("game.dsl")