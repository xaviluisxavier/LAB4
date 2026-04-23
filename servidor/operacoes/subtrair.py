class Subtrair:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.res = 0


    def execute(self,x:float, y:float)->float:
        self.x = x  
        self.y = y  
        self.res = self.x - self.y
        return self.res