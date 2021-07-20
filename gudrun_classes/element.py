class Element:
    def __init__(self, atomicSymbol, massNo, abundance):
        self.atomicSymbol = atomicSymbol
        self.massNo = massNo
        self.abundance = abundance
    
    def __str__(self):
        return self.atomicSymbol + '  ' + str(self.massNo) + '  ' + str(self.abundance)

    def __repr__(self):
        return str(self)
