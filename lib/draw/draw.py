import math

def main():
    hex1=HexDraw(P=Coordinates(50,50),r=50)
    pass

class InvalidParameter(Exception):
    def __str__(self):
        return "InvalidParameter passed to class/function."


class Coordinates:
    def __init__(self,x,y):
        if type(x) != int: raise InvalidParameter()
        if type(y) != int: raise InvalidParameter()
        self.x=x
        self.y=y
        pass
    def __add__(self,coord):
        if type(coord) != Coordinates: raise InvalidParameter()
        return Coordinates(self.x+coord.x,self.y+coord.y)


class HexDraw:
    def __init__(self,P,r):
        if type(P) != Coordinates: raise InvalidParameter()
        if type(r) != int:         raise InvalidParameter()
        self.P=P
        self.r=r                                    # inner radius
        self.R=int(self.r/math.cos(0.5235987756))   # outer radius
        self.t=self.R                               # side  length
        # CORNERS
        self.A=self.P+Coordinates( 0, self.R)
        #print( "A=({},{})+({},{})=({},{})".format(self.P.x,self.P.y,0,self.R,self.A.x,self.A.y) )
        self.B=self.P+Coordinates( self.r, self.t//2)
        self.C=self.P+Coordinates( self.r,-self.t//2)
        self.D=self.P+Coordinates( 0,-self.R)
        self.E=self.P+Coordinates(-self.r,-self.t//2)
        self.F=self.P+Coordinates(-self.r, self.t//2)
        pass
    def lines(self):
        rc=[]
        rc.append([self.A,self.B])
        rc.append([self.B,self.C])
        rc.append([self.C,self.D])
        rc.append([self.D,self.E])
        rc.append([self.E,self.F])
        rc.append([self.F,self.A])
        return rc
    def poly(self):
        rc=[]
        rc.append((self.A.x,self.A.y))
        rc.append((self.B.x,self.B.y))
        rc.append((self.C.x,self.C.y))
        rc.append((self.D.x,self.D.y))
        rc.append((self.E.x,self.E.y))
        rc.append((self.F.x,self.F.y))
        return rc


if __name__=="__main__": main()