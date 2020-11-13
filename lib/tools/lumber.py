#!/usr/bin/env python3

class jack():
    """lumber.jack is the class that collects logs and prints them.
lumber.jack.log(*arg)           --> collects and immediately writes *args
lumber.jack.chop(*args)         --> collects *args and adds them for future writing
lumber.jack.burn()              --> empties out the data stored by lumber.jack.chop
lumber.jack.timber()            --> writes the information collected by lumber.jack.chop
lumber.jack.config(**kwargs)    --> modify keyword information stored in lumber.jack
                                >>> lumber.jack.config("help") for more info"""
    def __init__(self,file=None,path=None):
        from datetime import datetime
        from platform import system
        from sys import argv
        self.__now = datetime.now
        # configurables
        self.file,self.path=file,path
        self.slash   ="/"
        self.split   =" | "
        self.colwdt  =20
        # hidden
        self.__timber=[]
        # location info
        if system().lower().startswith("windows"): self.slash = "\\"
        if self.file in [None,""]:
            self.file    = argv[0][argv[0].rfind(self.slash)+1:argv[0].rfind(".")]
        if self.path in [None,""]:
            self.path    = argv[0][:argv[0].rfind(self.slash)+1]
        self.file+=".log"
    
    def config(self,*args,**kwargs):
        if "help" in args:
            keys = list(self.__dict__.keys())
            for key in keys:
                if key.startswith("_"): keys.remove(key)
            print( keys )
        else:
            for arg in kwargs.keys():
                if arg in self.__dict__.keys():
                    exec(  "self.{} = kwargs[arg]".format(arg) )
    
    def chop(self,*args):
        self.__timber+=args
    
    def burn(self):
        self.__timber=[]
    
    def timber(self):
        with open(self.path+self.file,"a+",encoding="UTF-8") as f: f.write(("[{:.22}]".format(str(self.__now()))+((self.split+"{:<"+str(self.colwdt)+"."+str(self.colwdt)+"}")*len(self.__timber)).format(*self.__timber)).strip()+"\n")
        self.burn()
    
    def log(self,*args):
        with open(self.path+self.file,"a+",encoding="UTF-8") as f: f.write(("[{:.22}]".format(str(self.__now()))+((self.split+"{:<"+str(self.colwdt)+"."+str(self.colwdt)+"}")*len(args)).format(*args)).strip()+"\n")


if __name__=="__main__":
    print( jack.__doc__ )
    Lumberjack = jack()
    Lumberjack.config( "help" )
    settings={ "colwdt":22,"split":"  -(|.|)-  ","file":"lumber.yard" }
    Lumberjack.config( **settings )
    from sys import argv
    from random import choice
    Lumberjack.log( argv[0][argv[0].rfind(Lumberjack.slash)+1:argv[0].rfind(".")], "dork", "OK!" )
    example_events=["ERROR!"]+["FAULT!"]*2+["OK!"]*4
    cycles=12
    for i in range(cycles):
        try:
            Lumberjack.chop("|"*(i+1))
            Lumberjack.chop("zork!")
            Lumberjack.chop(choice(example_events))
        finally:
            Lumberjack.timber()