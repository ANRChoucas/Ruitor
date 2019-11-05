class FuzzyficationFunction(list):

    ftypes = {1: "crisp", 2: "linear", 3: "triangular", 4: "trapezoidal"}

    def __init__(self, *args):
        super().__init__(*args)
        sorted(self, key=lambda x: x[0])

        self.ftype = self.ftypes[len(self)]

    def to_linear(self):
        pass

    def to_triangular(self):
        pass

    def to_trapezoidal(self):
        pass

    def to_crisp(self):
        pass
