from point import Point

class LineSegment: 
    
    def __init__(self, fromPoint, toPoint): 
        self._pointA = fromPoint
        self._pointB = toPoint
        
    def endPointA(self): 
        return self._pointA
    
    def endPointB(self): 
        return self._pointB
    
    def length(self): 
        return self._pointA.distance(self._pointB)
    
    def isVertical(self): 
        return self._pointA.getX() == self._pointB.getX()
    
    def isHorizontal(self): 
        return self._pointA.getY() == self._pointB.getY()
    
    def slope(self): 
        if self.isVertical(): 
            return None
        else: 
            run = self._pointA.getX() - self._pointB.getX()
            rise = self._pointA.getY() - self._pointB.getY()
            return rise / run
        
    def isParallel(self, otherLine): 
        if self.slope() == otherLine.slope(): 
            return True
        else: 
            return False
        
    def isPerpendicular(self, otherLine): 
        selfSlope = self.slope()
        otherSlope = otherLine.slope()
        if selfSlope == ((1 / otherSlope) * -1): 
            return True
        else: 
            return False
        
    def midpoint(self): 
        xMid = (self._pointA.getX() + self._pointB.getX()) / 2 
        yMid = (self._pointA.getY() + self._pointA.getY()) / 2
        return Point(xMid, yMid)
    
    def __str__(self): 
        return str(self._pointA) + "#" + str(self._pointB)
