class Point : 
    
    def __init__(self, x, y): 
        self.xCoord = x 
        self.yCoord = y
        
    def getX(self): 
        return self.xCoord
    
    def getY(self): 
        return self.yCoord
    
    def distance (self, otherPoint): 
        xDiff = self.xCoord - otherPoint.xCoord
        yDiff = self.yCoord - otherPoint.yCoord
        return ((xDiff ** 2 + yDiff ** 2) ** 0.5)
    
    def __eq__(self, rhsPoint): 
        return self.xCoord == rhsPoint.xCoord and self.yCoord == rhsPoint.yCoord
    
    def __str__(self): 
        return "(" + str(self.xCoord) + ", " + str(self.yCoord) + ")"
