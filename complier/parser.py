class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

        self.config = {
            "speed": 0,
            "speed_increase": {
                "amount": 0,
                "interval": 0
            }
        }

    def current(self):
        return self.tokens[self.pos]

    def advance(self):
        self.pos += 1

    def parse(self):

        while self.pos < len(self.tokens):

            token, value = self.current()

            # PLAYER SPEED 30
            if token == "PLAYER":
                self.advance()  # PLAYER
                self.advance()  # SPEED

                _, speed = self.current()
                self.config["speed"] = speed
                self.advance()

            # INCREASE SPEED 3 EVERY 15
            elif token == "INCREASE":
                self.advance()  # INCREASE
                self.advance()  # SPEED

                _, amount = self.current()
                self.config["speed_increase"]["amount"] = amount
                self.advance()

                self.advance()  # EVERY

                _, interval = self.current()
                self.config["speed_increase"]["interval"] = interval
                self.advance()

            else:
                self.advance()

        return self.config