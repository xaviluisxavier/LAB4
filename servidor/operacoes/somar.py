class Somar:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.res = 0


    def execute(self,x:int, y:int)->float:
        self.x = x
        self.y = y
        self.res = x + self.y
        return self.res