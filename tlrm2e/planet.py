#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys      import argv,exit
from platform import system
import random
try:
    from tools.db_parse         import App as XML_Parse
except:
    try:
        from lib.tools.db_parse import App as XML_Parse
    except ModuleNotFoundError:
        from testing_tools.db_parse import App as XML_Parse



# in-file settings
if system().lower().startswith("win"):
    SLASH="\\"
else:
    SLASH="/"

# critical paths
path        = argv[0][:argv[0].rfind(SLASH)+1]
config_src  = "config"+SLASH+"planet.ini"


def main():
    planet=Planet()
    out_template="{hex:>4} - {uwp:<9} {cog:>4} {pbj:>3} {widtt:>5} {extl:>21} {culture:>3}"
    s = out_template.format(                               \
                            hex     = planet.location_code,\
                            uwp     = planet.getUWP()     ,\
                            cog     = planet.getCOG()     ,\
                            pbj     = planet.getPBJ()     ,\
                            widtt   = planet.getWDITTP()  ,\
                            extl    = planet.getExTL()    ,\
                            culture = planet.getC()       ,\
                            star    = ""                   \
                                                           )
    print(s)
    pass


class Planet:
    HEX_EXPANDED  =["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p"]
    STARPORT_CHART=["x","e","e","d","d","c","c","b","b","a","a"]
    VN='vn'
    SO='so'
    HS='hs'
    def __init__(self,location="0000",parent=None,type='planet',config=config_src,mode=None,band=None,mainworld=True,populated=True,new=True,db=None,AUtoStar=None,GoldieDist=None,name="unnamed"):
        from configparser       import ConfigParser

        self.mode=mode
        self.band=band
        self.name=name

        self.isGasGiant=False
        self.isGasGiantSmall=False
        self.isGasGiantLarge=False

        # config
        self.config = ConfigParser()
        try:
            with open(path+"plugins"+SLASH+"SectorGen"+SLASH+config) as f:
                self.config.read_file(f)
        except:
            try:
                with open(path+config) as f:
                    self.config.read_file(f)
            except:
                with open(path[:path[:-1].rfind(SLASH)+1]+config) as f:
                    self.config.read_file(f)

        # DEFAULT
        if   type=="planet"     :
            if mode==None: self.mode=self.config.get("DEFAULT","mode"        ).strip()
            if band==None: self.band=self.config.get("DEFAULT","orbital band").strip()
        elif type=="satellite"  :
            if mode==None: self.config.get("DEFAULT","mode (satellites)").strip()

        # parenting
        self.parent = parent

        # tables
        self.list_table_size_R_S = ["R","D","S"]

        # determine mode
        self.SOpera=False
        self.HScifi=False
        if   self.mode==self.SO:
            self.SOpera=True
        elif self.mode==self.HS:
            self.SOpera=True
            self.HScifi=True

        # db imports
        self.TRADECODES =db[XML_Parse.TOP_LAYER]['traveller']['tradecodes']
        self.CULTURE    =db[XML_Parse.TOP_LAYER]['traveller']['culture'   ]
        self.db=db

        # save metainfo
        self.populated    = populated
        self.adjacent_to  =[]
        self.location_code=location
        self.row          =int(self.location_code[:2])
        self.col          =int(self.location_code[2:])
        self.isMainworld  = mainworld
        if type!=None and type.lower() in ["sgg","lgg","rgg"]:
            self.isGasGiant=True
            if   type.lower()=='sgg': self.isGasGiantSmall=True
            elif type.lower()=='lgg': self.isGasGiantLarge=True
            elif type.lower()=='rgg':
                if roll(1,6)==1: self.isGasGiantLarge=True
                else:            self.isGasGiantSmall=True

        self.type=type
        self.clear()
        if AUtoStar  !=None: self.AUtoStar  =AUtoStar
        if GoldieDist!=None: self.GoldieDist=GoldieDist
        if self.GoldieDist==None and self.parent!=None:
            self.GoldieDist=self.parent.GoldieDist
        if new: self.new()
    def clear(self):
        # undefined starport
        self.starport                            = "X"
        # empty SAH-sequence
        self.size                                = 0
        self.size_str                            = ""
        self.atmosphere                          = 0
        self.hydrographics                       = 0
        # empty PGL-sequence
        self.population                          = 0
        self.government                          = 0
        self.law_level                           = 0
        # undefined tech_level
        self.tech_level                          = 0
        # empty COG-sequence
        self.climate                             = 0
        self.orbit                               = 0
        self.gravity                             = 0
        # empty PBJ-sequence
        self.population_mod                      = 0
        self.asteroid_belts                      = 0
        self.jovian_planets                      = 0
        # empty WDITTP-sequence
        self.law_level_weapons                   = 0
        self.law_level_drugs                     = 0
        self.law_level_information               = 0
        self.law_level_technology                = 0
        self.law_level_travellers                = 0
        self.law_level_powers                    = 0
        # empty CTM-sequence
        # tECCME
        self.tech_level_civilian                 = 0
        self.tech_level_civilian_energy          = 0
        self.tech_level_civilian_computing       = 0
        self.tech_level_civilian_communication   = 0
        self.tech_level_civilian_medicine        = 0
        self.tech_level_civilian_environment     = 0
        # tLWAS
        self.tech_level_transportation           = 0
        self.tech_level_transportation_land      = 0
        self.tech_level_transportation_water     = 0
        self.tech_level_transportation_air       = 0
        self.tech_level_transportation_space     = 0
        # tPPHH
        self.tech_level_military                 = 0
        self.tech_level_military_personalweapons = 0
        self.tech_level_military_personalarmour  = 0
        self.tech_level_military_heavyweapons    = 0
        self.tech_level_military_heavyarmour     = 0
        # undefined Peripheral Information
        self.trade_codes                         = ""
        self.travel_code                         = ""
        self.quirk                               = ""
        self.bases                               = "" ## GENERATION NOT IMPLEMENTED
        self.allegiance                          = "" ## GENERATION NOT IMPLEMENTED
        # trade information
        self.trade_number                        = 0  ## GENERATION NOT IMPLEMENTED
        self.imports                             = 0  ## GENERATION NOT IMPLEMENTED
        self.exports                             = 0  ## GENERATION NOT IMPLEMENTED
        self.transient_trade                     = 0  ## GENERATION NOT IMPLEMENTED
        self.port_size                           = 0  ## GENERATION NOT IMPLEMENTED
        # orbit info
        self.pos                                 = 0.0
        self.orbital_period                      = 0.0
        self.rotations_per_orbit                 = 0.0
        self.weekly_traversal                    = 0.0
        self.isTideLocked                        = False
        # intra-system info
        self.AUtoStar                            = 0.0      # star_diam * self.orbit * 166
        self.GoldieDist                          = None
        # satelites/moons
        self.satellites                          = []
        # comment
        self.comment                             = "---"
    def new(self,from_scratch=True,distFromGZ=None,max_pop=20,max_tl=20,quirk_chance=0):
        if self.isGasGiant:
            self.newCOG(distFromGZ)
            if   self.isGasGiantLarge: self.size=int( self.config.get("GAS GIANTS","size (lgg)") )
            elif self.isGasGiantSmall: self.size=int( self.config.get("GAS GIANTS","size (sgg)") )
            self.gravity=self.size
            self.atmosphere    =int( self.config.get("GAS GIANTS","atmosphere")    )
            self.hydrographics =int( self.config.get("GAS GIANTS","hydrographics") )
            self.newSat()
            self.newOrbitInfo()
        else:
            if from_scratch:
                self.newCOG(distFromGZ)
                self.newSAH()       # # # Will get weird results if newCOG() is not run first
                if self.type!="satellite": self.newSat() # #
                self.newOrbitInfo() #
            if self.populated:
                self.newPGL(max_pop=max_pop)    # # # # self.populated dependent
                self.newSPort()                 # # #
                self.newExTL(max_tl=max_tl)     # #
                self.newWDITTP()                #
            self.newInfo(quirk_chance)
        pass
    def newCOG(self,distFromGZ=None):
        if self.type=="planet":
            # Defaults
            if distFromGZ==None:
                if   self.GoldieDist!=None        : distFromGZ=self.GoldieDist
                elif self.band.startswith("near" ): distFromGZ=- 100
                elif self.band.startswith("mid"  ): distFromGZ=    0
                elif self.band.startswith("far"  ): distFromGZ=  100
                elif self.band.startswith("rogue"): distFromGZ= 1000
            # C(O)G-sequence (habitability)
            self.climate      =        roll(4,6)//2-2
            self.gravity      =min(max(roll(6,6)//3-7,-3),3)
            if   int( distFromGZ ) >  12 : self.climate = 0
            elif int( distFromGZ ) >   8 : self.climate-= 8  # Outer HZ Edge
            elif int( distFromGZ ) >   6 : self.climate-= 4
            elif int( distFromGZ ) >   4 : self.climate-= 2
            elif int( distFromGZ ) >   2 : self.climate-= 1
            elif int( distFromGZ ) >  -1 : self.climate+= 0
            elif int( distFromGZ ) >  -3 : self.climate+= 1
            elif int( distFromGZ ) >  -5 : self.climate+= 2
            elif int( distFromGZ ) >  -7 : self.climate+= 4
            elif int( distFromGZ ) > -11 : self.climate+= 8  # Inner HZ Edge
            else:                          self.climate =20
            self.climate      =min(max(self.climate,0),25)
            self.orbit        =int(self.AUtoStar*100)
        elif self.type=="satellite":
            # (C)OG-sequence
            self.climate      = self.parent.climate
            if   self.band.startswith("n"): self.orbit =  0+roll(1,  6)
            elif self.band.startswith("m"): self.orbit =  6+roll(1, 29)
            elif self.band.startswith("f"): self.orbit = 35+roll(1, 35)
            elif self.band.startswith("r"): self.orbit = 70+roll(1,140)
            self.gravity      =min(max(roll(6,6)//3-7,-2),2)
        pass
    def newSAH(self):
        if self.type=="planet":
            # SAH-sequence
            if self.band!=None:
                if   self.band.startswith("near" ): self.size =     roll(1,6)
                elif self.band.startswith("mid"  ): self.size =     roll(2,6)-2
                elif self.band.startswith("far"  ): self.size = max(roll(3,6)-5,0)
                elif self.band.startswith("rogue"): self.size =     roll(1,6)
            self.size_str=self.HEX_EXPANDED[max(self.size,0)]
        elif self.type=="satellite":
            # SAH-sequence
            if self.band!=None:
                if   self.band.startswith("near" ): self.size =              -2
                elif self.band.startswith("mid"  ): self.size = roll(2,6)-5
                elif self.band.startswith("far"  ): self.size = roll(3,6)-6
                elif self.band.startswith("rogue"): self.size = roll(1,6)-3
            self.size         =    min(self.size,self.parent.size//2)
            if self.orbit < 7:   self.size = -1
            if   self.size <=-1:
                if   self.orbit <=7: self.size_str=self.list_table_size_R_S[0]
                elif self.orbit >=8: self.size_str=self.list_table_size_R_S[1]
            elif self.size <= 0: self.size_str=self.list_table_size_R_S[2]
            else:
                self.size_str=self.HEX_EXPANDED[max(self.size,0)]
        self.size         = max(self.size,0)
        self.gravity     +=    self.size
        self.gravity      =min(max(self.gravity,0),12)
        self.atmosphere   =max(roll(2,6)-7+self.gravity+max(self.size-8,-4),0)  # using gravity instead of size
        if self.type=="satellite" and self.size_str.upper() in ["R","D"]: self.atmosphere=0
        # SOpera change
        if self.SOpera and self.size <= 4:
            if self.size <= 2:
                self.atmosphere=0
            if self.size >  2:
                if self.atmosphere <= 2:
                    self.atmosphere=0
                elif self.atmosphere > 2 and self.atmosphere <= 5:
                    self.atmosphere=1
                elif self.atmosphere > 5:
                    self.atmosphere=10
        # HScifi change (custom)
        if self.HScifi:
            if self.atmosphere > 1 and self.atmosphere < 10 and roll(1,6)<5:
                possibilities=[10,10,10,11,11,12,12,15]
                self.atmosphere=possibilities[random.randrange(len(possibilities))]
            if self.hydrographics>7 and self.atmosphere==15 and roll(1,6)<4:
                self.atmosphere   =15
                self.hydrographics=10
        self.hydrographics=max(roll(2,6)-7+self.size,0)
        if self.size <= 1: self.hydrographics=0
        elif self.atmosphere <= 1 or ( self.atmosphere >= 10 and self.atmosphere <= 12 ):
            self.hydrographics-=4
        if self.atmosphere != 13:
            if self.climate > 7: self.hydrographics-=2
            if self.climate > 9: self.hydrographics-=6
        self.atmosphere =min(max(self.atmosphere,0),15)
        # SOpera change
        if self.SOpera:
            if self.size >= 3 and self.size <= 4 and self.atmosphere==10:
                self.hydrographics-=6
            if self.atmosphere <= 1:
                self.hydrographics-=6
            elif self.atmosphere in (2,3,11,12):
                self.hydrographics-=4
        self.hydrographics =min(max(self.hydrographics,0),10)
    def newSat(self):
        # SATELLITES
        satellites=0
        if self.size != 0:
            if   self.gravity<= 4: satellites=max(roll(1,6)-4,0)
            elif self.gravity<= 6: satellites=max(roll(1,6)-3,0)
            elif self.gravity<= 8: satellites=max(roll(1,6)-2,0)
            elif self.gravity<=12: satellites=max(roll(1,6)-1,0)
            elif self.gravity<=16: satellites=max(roll(2,6)-2,0)
            elif self.gravity<=20: satellites=max(roll(2,6)+roll(1,6)//2-2,0)
            if self.band=="near" : satellites=max(satellites-2,0)
        for i in range(satellites):
            r     = roll(3,6)
            if    r  >= 15: band="rogue"
            elif  r  >= 10: band="mid"
            elif  r  >=  6: band="far"
            elif  r  >=  3: band="near"
            self.satellites.append(Planet(parent=self,type="satellite",band=band,populated=False,mainworld=False,db=self.db))
        #for satellite in self.satellites:
        #    print("   ",satellite.name,satellite.orbit,satellite.band)
        self.purge()
        self.name_satellites()
        pass
    def name_satellites(self):
        i=0
        for satellite in sorted(self.satellites,key=lambda x: x.orbit):
            sequential_satellite_name=self.name+" - "+int_to_roman(i+1)
            satellite.name=sequential_satellite_name
            i+=1
        pass
    def purge(self):
        for planetoid_one in self.satellites:
            i=0
            while i < len(self.satellites):
                if planetoid_one==self.satellites[i]:
                    i+=1
                    continue
                if planetoid_one.orbit==self.satellites[i].orbit:
                    r=random.randrange(2)
                    del(self.satellites[i])
                    #print("Purged satellite!")
                else:
                    i+=1
        pass
    def newPGL(self,max_pop=20):
        # PGL-sequence
        if self.populated:
            self.population   =    roll(2,6)-2
            # HScifi change
            if self.HScifi:
                if self.size <= 2:
                    self.population-=1
                elif self.size == 10:
                    self.population-=1
                if self.atmosphere in (5,6,8):
                    self.population+=1
                else:
                    self.population-=1
            self.population =min(max(self.population,0),max_pop)
            if self.population != 0:
                self.government   =max(roll(2,6)-7+self.population,0)
                if self.government != 0:
                    self.law_level    =max(roll(2,6)-7+self.government,0)
                else:
                    self.law_level    =0
            else:
                self.government   =0
                self.law_level    =0
        else:
            self.population   =0
            self.government   =0
            self.law_level    =0
    def newSPort(self):
        # starport
        if self.populated and self.population > 0:
            self.starport     =self.STARPORT_CHART[roll(2,6)-2]
        else:
            self.starport     ="X"
    def newExTL(self,max_tl=20):
        # TL calculation
        if self.population > 0:
            self.tech_level   =    roll(2,6)//2
            if   self.starport      == "x": self.tech_level-=4
            elif self.starport      == "c": self.tech_level+=2
            elif self.starport      == "b": self.tech_level+=4
            elif self.starport      == "a": self.tech_level+=6

            if   self.size          <=  1 : self.tech_level+=2
            elif self.size          <=  4 : self.tech_level+=1

            if   self.atmosphere    <=  3 : self.tech_level+=1
            elif self.atmosphere    >= 10 : self.tech_level+=1

            if   self.hydrographics in (0,9) : self.tech_level+=1
            elif self.hydrographics == 10 : self.tech_level+=2

            if   self.population    >=  1 \
            and  self.population    <=  5 : self.tech_level+=1
            if   self.population    >= 10 : self.tech_level+=1
            if   self.population    >= 11 : self.tech_level+=1
            if   self.population    >= 12 : self.tech_level+=1
            if   self.population    >= 13 : self.tech_level+=1

            if   self.government    in (0,5) : self.tech_level+1
            elif self.government    ==  7 : self.tech_level+=2
            elif self.government    == 13 : self.tech_level-=2
            elif self.government    == 14 : self.tech_level-=2
        else:
            self.tech_level   =0
        self.tech_level=min(self.tech_level,max_tl)
        # CTM-sequence (specialized technology levels)
        if self.population > 0:
            # tECCME
            self.tech_level_civilian       = min(max(self.tech_level-7+roll(6,6)//3,0),max_tl)
            self.tech_level_civilian_energy          = min(max(self.tech_level_civilian-3+roll(4,6)//2//2,0),max_tl)
            self.tech_level_civilian_computing       = min(max(self.tech_level_civilian-3+roll(6,6)//3//2,0),max_tl)
            self.tech_level_civilian_communication   = min(max(self.tech_level_civilian-3+roll(6,6)//3//2,0),max_tl)
            self.tech_level_civilian_medicine        = min(max(self.tech_level_civilian-3+roll(2,6)//1//2,0),max_tl)
            self.tech_level_civilian_environment     = min(max(self.tech_level_civilian-3+roll(4,6)//2//2,0),max_tl)
            # tLWAS
            self.tech_level_transportation = min(max(self.tech_level-7+roll(6,6)//3,0),max_tl)
            self.tech_level_transportation_land      = min(max(self.tech_level_transportation-3+roll(6,6)//3//2,0),max_tl)
            self.tech_level_transportation_water     = min(max(self.tech_level_transportation-3+roll(6,6)//3//2,0),max_tl)
            self.tech_level_transportation_air       = min(max(self.tech_level_transportation-3+roll(4,6)//2//2,0),max_tl)
            self.tech_level_transportation_space     = min(max(self.tech_level_transportation-3+roll(4,6)//2//2,0),max_tl)
            # tPPHH
            self.tech_level_military       = min(max(self.tech_level-7+roll(6,6)//3,0),max_tl)
            self.tech_level_military_personalweapons = min(max(self.tech_level_military-3+roll(6,6)//3//2,0),max_tl)
            self.tech_level_military_personalarmour  = min(max(self.tech_level_military-3+roll(6,6)//3//2,0),max_tl)
            self.tech_level_military_heavyweapons    = min(max(self.tech_level_military-3+roll(6,6)//3//2,0),max_tl)
            self.tech_level_military_heavyarmour     = min(max(self.tech_level_military-3+roll(6,6)//3//2,0),max_tl)
        else:
            # tECCME
            self.tech_level_civilian       = 0
            self.tech_level_civilian_energy          = 0
            self.tech_level_civilian_computing       = 0
            self.tech_level_civilian_communication   = 0
            self.tech_level_civilian_medicine        = 0
            self.tech_level_civilian_environment     = 0
            # tLWAS
            self.tech_level_transportation = 0
            self.tech_level_transportation_land      = 0
            self.tech_level_transportation_water     = 0
            self.tech_level_transportation_air       = 0
            self.tech_level_transportation_space     = 0
            # tPPHH
            self.tech_level_military       = 0
            self.tech_level_military_personalweapons = 0
            self.tech_level_military_personalarmour  = 0
            self.tech_level_military_heavyweapons    = 0
            self.tech_level_military_heavyarmour     = 0
    def newPBJ(self):
        # PBJ-sequence (resources)
        if self.population==0: self.population_mod=0
        self.asteroid_belts =max(roll(2,6)//2-3,0)
        if self.size==0:
            self.asteroid_belts+=1
        self.jovian_planets =max(roll(2,6)-5,0)
    def newWDITTP(self):
        # WDITTP-sequence (specialized law levels)
        if self.population > 0:
            self.law_level_weapons     = self.law_level-2+roll(1,6)//2
            self.law_level_drugs       = self.law_level-2+roll(1,6)//2
            self.law_level_information = self.law_level-2+roll(1,6)//2
            self.law_level_technology  = self.law_level-2+roll(1,6)//2
            self.law_level_travellers  = self.law_level
            self.law_level_powers      = self.law_level-2+roll(1,6)//2
            # Government-ammended WDITTP-sequence
            if self.government in [0,10]:
                self.law_level -= 1
            if self.government in [1,3,4,5,6,8,9,11,12]:
                self.law_level_weapons    += roll(1,6)
            if self.government in [1,2,4,8,9]:
                self.law_level_drugs      += roll(1,6)
            if self.government in [5,9,11]:
                self.law_level_information+= roll(1,6)
            if self.government in [1,3,5,6,9,11]:
                self.law_level_technology += roll(1,6)
            if self.government in [1,3,6,9]:
                self.law_level_travellers += roll(1,6)
            if self.government in [1,3,4,9]:
                self.law_level_powers     += roll(1,6)
            if self.government>=13 or self.government==7:
                for i in range(roll(1,6)-1):
                    es=random.choice(("self.law_level_weapons    ",\
                                      "self.law_level_drugs      ",\
                                      "self.law_level_information",\
                                      "self.law_level_technology ",\
                                      "self.law_level_travellers ",\
                                      "self.law_level_powers     "))
                    exec(es+"+=(roll(2,6)+1)//2")
            self.law_level = self.law_level_travellers
        else:
            self.law_level_weapons                   = 0
            self.law_level_drugs                     = 0
            self.law_level_information               = 0
            self.law_level_technology                = 0
            self.law_level_travellers                = 0
            self.law_level_powers                    = 0
        # reset law levels
        self.law_level_weapons    = max(self.law_level_weapons    ,0)
        self.law_level_drugs      = max(self.law_level_drugs      ,0)
        self.law_level_information= max(self.law_level_information,0)
        self.law_level_technology = max(self.law_level_technology ,0)
        self.law_level_travellers = max(self.law_level_travellers ,0)
        self.law_level_powers     = max(self.law_level_powers     ,0)
        pass
    def newInfo(self,quirk_chance):
        # travel code
        self.travel_code=" "
        if   self.population              >   0 \
        and  self.populated                     \
        and (self.government              ==  0 \
        or   self.government              ==  7 \
        or   self.government              == 10 \
        or   self.law_level               ==  0 \
        or   self.law_level_weapons       ==  0 \
        or   self.law_level_information   >=  9 \
        or   self.law_level_technology    >=  9 \
        or   self.law_level_travellers    >=  9 \
        or   self.government              ==  0 \
        or   self.atmosphere              >= 10 ):
            self.travel_code="a"
        self.trade_codes = self.getTradeCodes()
        if   self.population>0 \
        and  quirk_chance<random.randrange(100):
            self.quirk = self.getQuirk()
        else:
            self.quirk = ""
        pass
    def getTradeCodes(self):
        rc  = ''
        from traceback import print_exc
        from sys import argv
        path          = argv[0][:argv[0].rfind("\\")+1]
        NAME          = 'name'
        TAG           = 'tag'
        SIZE          = 'size'
        ATMOSPHERE    = 'atmosphere'
        HYDROGRAPHICS = 'hydrographics'
        POPULATION    = 'population'
        GOVERNMENT    = 'government'
        LAWLEVEL      = 'lawlevel'
        TECHLEVEL     = 'techlevel'


        for tradecode in self.TRADECODES['tradecode']:
            try:
                tcode = True
                for requirement in tradecode['requirements'].keys():
                    if requirement.endswith('__info')   \
                    or requirement == XML_Parse.CDATA   \
                    or requirement == XML_Parse.ATTR_TAG\
                    or tradecode['requirements'][requirement][XML_Parse.CDATA]         == None \
                    or tradecode['requirements'][requirement][XML_Parse.CDATA].strip() == ''   :
                        continue
                    else:
                        req_info = tradecode['requirements'][requirement][XML_Parse.CDATA]
                    if requirement == SIZE:
                        req = splitup( req_info )
                        if self.size  in req: pass
                        else: tcode = False
                    elif requirement == ATMOSPHERE:
                        req = splitup( req_info )
                        if self.atmosphere in req: pass
                        else: tcode = False
                    elif requirement == HYDROGRAPHICS:
                        req = splitup( req_info )
                        if self.hydrographics in req: pass
                        else: tcode = False
                    elif requirement == POPULATION:
                        req = splitup( req_info )
                        if self.population in req: pass
                        else: tcode = False
                    elif requirement == GOVERNMENT:
                        req = splitup( req_info )
                        if self.government in req: pass
                        else: tcode = False
                    elif requirement == LAWLEVEL:
                        req = splitup( req_info )
                        if self.law_level in req: pass
                        else: tcode = False
                    elif requirement == TECHLEVEL:
                        req = splitup( req_info )
                        if self.tech_level in req: pass
                        else: tcode = False
#                    print( '  ' + tradecode['name'] + ' is ' + str(tcode) )
                if tradecode[XML_Parse.ATTR_TAG][TAG]=="As" and self.type=="satellite": tcode=False
                if tradecode[XML_Parse.ATTR_TAG][TAG]=="Ga" and abs(self.GoldieDist)>10: tcode=False
                if tradecode[XML_Parse.ATTR_TAG][TAG]=="Ic" and self.GoldieDist>12 and self.hydrographics>0: tcode=True
                if tcode:
                    rc += " " + tradecode[XML_Parse.ATTR_TAG][TAG]
            except Exception as e:
                print(tradecode[XML_Parse.ATTR_TAG][TAG])
                print_exc()#print(e)
        return rc
    def getTag(self):
        r   = roll(1,100)
        rc  = ''
        tags    = [ 'Abandoned Colony',    \
                    'Alien Ruins',         \
                    'Altered Humanity',    \
                    'Anthromorphs',        \
                    'Battleground',        \
                    'Bubble Cities',       \
                    'Cheap Life',          \
                    'Civil War',           \
                    'Cold War',            \
                    'Colony',              \
                    'Cyclical Doom',       \
                    'Doomed World',        \
                    'Dying Race',          \
                    'Eugenics Cult',       \
                    'Feral World',         \
                    'Flying Cities',       \
                    'Forbidden Tech',      \
                    'Freak Geology',       \
                    'Freak Weather',       \
                    'Friendly Foe',        \
                    'Gold Rush',           \
                    'Great Work',          \
                    'Hatred',              \
                    'Hivemind',            \
                    'Holy War',            \
                    'Hostile Biosphere',   \
                    'Hostile Space',       \
                    'Immortals',           \
                    'Local Specialty',     \
                    'Local Tech',          \
                    'Major Spaceyard',     \
                    'Megacorps',           \
                    'Mercenaries',         \
                    'Minimal Contact',     \
                    'Misandry/Misogyny',   \
                    'Night World',         \
                    'Nomads',              \
                    'Out of Contact',      \
                    'Outpost World',       \
                    'Pilgrimage Site',     \
                    'Pleasure World',      \
                    'Police State',        \
                    'Post-Scarcity',       \
                    'Tech Cultists',       \
                    'Primitive Aliens',    \
                    'Quarantined World',   \
                    'Radioactive World',   \
                    'Refugees',            \
                    'Regional Hegemon',    \
                    'Restrictive Laws',    \
                    'Revanchists',         \
                    'Revolutionaries',     \
                    'Rigid Culture',       \
                    'Rising Hegemon',      \
                    'Ritual Combat',       \
                    'Robots',              \
                    'Seagoing Cities',     \
                    'Sealed Menace',       \
                    'Secret Masters',      \
                    'Sectarians',          \
                    'Seismic Instability', \
                    'Shackled World',      \
                    'Societal Despair',    \
                    'Sole Supplier',       \
                    'Taboo Treasure',      \
                    'Terraform Failure',   \
                    'Tomb World',          \
                    'Unshackled AI',       \
                    'Urbanized Surface',   \
                    'Utopia',              \
                    'Xenophiles',          \
                    'Xenophobes',          \
                    'Zombies'              ]
        rc      = random.choice( tags )
        return rc
    def getQuirk(self):
        rc  = ''
        from traceback import print_exc
        from sys import argv
        dom_quirk=random.choice(self.CULTURE['quirk'])
        rc+=dom_quirk[XML_Parse.ATTR_TAG]['index']
        return rc
    def newOrbitInfo(self):
        year=365.25
        week=7
        day =1
        self.isTideLocked=False
        if self.type=="satellite":
            # position in orbit
            if self.isMainworld:
                self.parent.pos=0
                self.pos=0
            else:
                self.pos=random.randrange(73)*5
            # orbital period
            if   self.band.startswith("near" ):
                self.orbital_period=1.0
            elif self.band.startswith("mid"  ):
                if roll(1,6)<=1: retrograde= 1.00
                else:            retrograde=-1.25
                self.orbital_period=year*max(self.parent.gravity,1)/10*(3+roll(2,6))/10*retrograde
            elif self.band.startswith("far"  ):
                if roll(1,6)<=3: retrograde= 1.00
                else:            retrograde=-1.25
                self.orbital_period=year*max(self.parent.gravity*1.1,1)/10*(roll(1,2)*0.5+0.15)*retrograde
            elif self.band.startswith("rogue"):
                if roll(1,6)<=5: retrograde= 1.00
                else:            retrograde=-1.25
                self.orbital_period=year*max(self.parent.gravity*1.5,1)/10*(roll(1,2)*0.15+0.15)*retrograde
            else:
                self.orbital_period=1.0
            # length of day
            if   self.band.startswith("near" ):
                self.isTideLocked =True
                self.rotations_per_orbit=1.0
            elif self.band.startswith("mid"  ):
                if self.parent.gravity+roll(2,6) > 12:
                    self.isTideLocked=True
                    self.rotations_per_orbit=1.0
                else:
                    self.rotations_per_orbit=day*32*(3+roll(2,6))/10
            elif self.band.startswith("far"  ):
                if self.parent.gravity+roll(2,6) > 16:
                    self.isTideLocked=True
                    self.rotations_per_orbit=1.0
                else:
                    self.rotations_per_orbit=day*32*(3+roll(2,6))/7
            elif self.band.startswith("rogue"):
                if self.parent.gravity+roll(2,6) > 20:
                    self.isTideLocked=True
                    self.rotations_per_orbit=1.0
                else:
                    self.rotations_per_orbit=day*32*(3+roll(2,6))/5
            # traversal
            self.weekly_traversal=360*(7/self.orbital_period)
        else:
            # re-get orbit
            self.orbit=int(self.AUtoStar*100)
            # position in orbit
            if self.isMainworld:
                self.pos=0
            else:
                self.pos=random.randrange(73)*5
            # orbital period
            if   self.band.startswith("near" ): self.orbital_period=year*self.AUtoStar*(2+roll(2,4))/10
            elif self.band.startswith("mid"  ): self.orbital_period=year*self.AUtoStar*(7+roll(1,6))/10
            elif self.band.startswith("far"  ):
                if roll(1,6)<=1: retrograde= 1.00
                else:            retrograde=-1.25
                self.orbital_period=year*self.AUtoStar*(2+roll(2,6))*retrograde
            elif self.band.startswith("rogue"):
                if roll(1,6)<=2: retrograde= 1.00
                else:            retrograde=-1.25
                self.orbital_period=year*self.AUtoStar*(4+4*roll(4,6))*retrograde
            else:
                self.orbital_period=1.0
            # length of day
            if   self.band.startswith("near" ):
                if roll(2,6) > 5:
                    self.isTideLocked=True
                    self.rotations_per_orbit=1.0
                else:
                    self.rotations_per_orbit=day*self.AUtoStar*roll( 1,6)
            elif self.band.startswith("mid"  ):
                if not self.isGasGiant and roll(2,6) > 9:
                    self.isTideLocked=True
                    self.rotations_per_orbit=1.0
                else:
                    self.rotations_per_orbit=day*self.AUtoStar*roll(10,6)*10
            elif self.band.startswith("far"  ):
                if not self.isGasGiant and roll(2,6) > 11:
                    self.isTideLocked=True
                    self.rotations_per_orbit=1.0
                else:
                    self.rotations_per_orbit=day*self.AUtoStar*roll( 3,6)*100
            elif self.band.startswith("rogue"):
                self.rotations_per_orbit=day*self.AUtoStar*roll( 3,6)*100
            # traversal
            self.weekly_traversal=360*(7/self.orbital_period)
        
        if self.atmosphere==15:
            if self.hydrographics==10:
                self.comment  +="Atmo:\"Panthalassic world (>85% water by volume)\","
            elif not self.isTideLocked and roll(1,6)==2:
                self.comment  +="Atmo:\"Constant Storms (pressure changes wildly)\","
            elif not self.isTideLocked and self.size>2 and self.size<7:
                self.comment  +="Atmo:\"Ellipsoidal Atmosphere (viable density only at equator)\","
        pass
    def load(self,uwppp):
        #               #
        ## ref: M  49 - X420000-0  KN3 00000 0-00000 0-0000 0-0000 00000     |n|noname I|n|  |a|     Ba De Po |o|143.18|1.00|0.00|o| |c|---|c|
        # create pointer
        p=0
        # Mainworld Status
        self.isMainworld=False
        p+=0
        length=1
        marker=uwppp[p:p+length]
        if marker in ("M","m"): self.isMainworld=True
        if marker in ("•","M"): self.type="planet"
        else:                   self.type="satellite"
        # AUtoStar
        p+=length
        length=4
        if self.type!="satellite":        
            self.AUtoStar = float( uwppp[p:p+length] ) / 100
            self.orbit    = int( float( uwppp[p:p+length] ) )
        else:
            self.AUtoStar = -1
            self.orbit    = int( float( uwppp[p:p+length] ) )
        # UWP
        p+=length+3
        length=9
        uwp=uwppp[p:p+length]
        if   uwp.lower().startswith("sgg"):
            self.isGasGiant=True
            self.isGasGiantSmall=True
            self.size           =int( self.config.get("GAS GIANTS","size (sgg)") )
            self.gravity        =     self.size
            self.atmosphere     =int( self.config.get("GAS GIANTS","atmosphere")    )
            self.hydrographics  =int( self.config.get("GAS GIANTS","hydrographics") )
            self.population     =0
            self.government     =0
            self.law_level      =0
            self.tech_level     =0
        elif uwp.lower().startswith("lgg"):
            self.size           =int( self.config.get("GAS GIANTS","size (lgg)") )
            self.gravity        =self.size
            self.atmosphere     =int( self.config.get("GAS GIANTS","atmosphere")    )
            self.hydrographics  =int( self.config.get("GAS GIANTS","hydrographics") )
            self.population     =0
            self.government     =0
            self.law_level      =0
            self.tech_level     =0
        else:
            self.starport      =                                uwp[ 0: 1].lower()
            self.size          =                                uwp[ 1: 2].lower()
            self.atmosphere    =findPosInList(self.HEX_EXPANDED,uwp[ 2: 3].lower())[0]
            self.hydrographics =findPosInList(self.HEX_EXPANDED,uwp[ 3: 4].lower())[0]
            self.population    =findPosInList(self.HEX_EXPANDED,uwp[ 4: 5].lower())[0]
            self.government    =findPosInList(self.HEX_EXPANDED,uwp[ 5: 6].lower())[0]
            self.law_level     =findPosInList(self.HEX_EXPANDED,uwp[ 6: 7].lower())[0]
            # -
            self.tech_level    =findPosInList(self.HEX_EXPANDED,uwp[ 8: 9].lower())[0]
            try:
                if self.size.upper() in self.list_table_size_R_S: raise Exception("non-standard size")
                self.size=findPosInList(self.HEX_EXPANDED,self.size)[0]
                self.size_str=self.HEX_EXPANDED[max(self.size,0)]
            except:
                for i in range(3):
                    if self.size == self.list_table_size_R_S[i].lower():
                        self.size_str=self.size
                        self.size    =i-3
                        break
        if  self.population==0: self.populated=False
        else:                   self.populated=True
        # TC(O)G
        p+=length+1
        length=4
        tcog=uwppp[p:p+length]
        self.travel_code   =                                tcog[ 0: 1].lower()
        self.climate       =findPosInList(self.HEX_EXPANDED,tcog[ 1: 2].lower())[0]
        band               =                                tcog[ 2: 3].lower()
        if   band.startswith("n"): self.band="near" 
        elif band.startswith("m"): self.band="mid"  
        elif band.startswith("f"): self.band="far"  
        elif band.startswith("r"): self.band="rogue"
        #self.orbit         =                                tcog[ 2: 3].lower()
        self.gravity       =findPosInList(self.HEX_EXPANDED,tcog[ 3: 4].lower())[0]
        # WDITTP
        p+=length+1
        length=6
        wdittp=uwppp[p:p+length]
        self.law_level_weapons    =findPosInList(self.HEX_EXPANDED,wdittp[ 0: 1].lower())[0]
        self.law_level_drugs      =findPosInList(self.HEX_EXPANDED,wdittp[ 1: 2].lower())[0]
        self.law_level_information=findPosInList(self.HEX_EXPANDED,wdittp[ 2: 3].lower())[0]
        self.law_level_technology =findPosInList(self.HEX_EXPANDED,wdittp[ 3: 4].lower())[0]
        self.law_level_travellers =findPosInList(self.HEX_EXPANDED,wdittp[ 4: 5].lower())[0]
        self.law_level_powers     =findPosInList(self.HEX_EXPANDED,wdittp[ 5: 6].lower())[0]
        # ExTL - Civilian
        p+=length+1
        length=7
        ctm_c=uwppp[p:p+length]
        self.tech_level_civilian                =findPosInList(self.HEX_EXPANDED,ctm_c[ 0: 1].lower())[0]
        self.tech_level_civilian_energy         =findPosInList(self.HEX_EXPANDED,ctm_c[ 2: 3].lower())[0]
        self.tech_level_civilian_computing      =findPosInList(self.HEX_EXPANDED,ctm_c[ 3: 4].lower())[0]
        self.tech_level_civilian_communication  =findPosInList(self.HEX_EXPANDED,ctm_c[ 4: 5].lower())[0]
        self.tech_level_civilian_medicine       =findPosInList(self.HEX_EXPANDED,ctm_c[ 5: 6].lower())[0]
        self.tech_level_civilian_environment    =findPosInList(self.HEX_EXPANDED,ctm_c[ 6: 7].lower())[0]
        # ExTL - Transportation
        p+=length+1
        length=6
        ctm_t=uwppp[p:p+length]
        self.tech_level_transportation          =findPosInList(self.HEX_EXPANDED,ctm_t[ 0: 1].lower())[0]
        self.tech_level_transportation_land     =findPosInList(self.HEX_EXPANDED,ctm_t[ 2: 3].lower())[0]
        self.tech_level_transportation_water    =findPosInList(self.HEX_EXPANDED,ctm_t[ 3: 4].lower())[0]
        self.tech_level_transportation_air      =findPosInList(self.HEX_EXPANDED,ctm_t[ 4: 5].lower())[0]
        self.tech_level_transportation_space    =findPosInList(self.HEX_EXPANDED,ctm_t[ 5: 6].lower())[0]
        # ExTL - Military
        p+=length+1
        length=6
        ctm_m=uwppp[p:p+length]
        self.tech_level_military                =findPosInList(self.HEX_EXPANDED,ctm_m[ 0: 1].lower())[0]
        self.tech_level_military_personalweapons=findPosInList(self.HEX_EXPANDED,ctm_m[ 2: 3].lower())[0]
        self.tech_level_military_personalarmour =findPosInList(self.HEX_EXPANDED,ctm_m[ 3: 4].lower())[0]
        self.tech_level_military_heavyweapons   =findPosInList(self.HEX_EXPANDED,ctm_m[ 4: 5].lower())[0]
        self.tech_level_military_heavyarmour    =findPosInList(self.HEX_EXPANDED,ctm_m[ 5: 6].lower())[0]
        # Trade Info
        p+=length+1
        length=5
        t_info=uwppp[p:p+length]
        self.trade_number                       =findPosInList(self.HEX_EXPANDED,t_info[0:1].lower())[0]
        self.imports                            =findPosInList(self.HEX_EXPANDED,t_info[1:2].lower())[0]
        self.exports                            =findPosInList(self.HEX_EXPANDED,t_info[2:3].lower())[0]
        self.transient_trade                    =findPosInList(self.HEX_EXPANDED,t_info[3:4].lower())[0]
        self.port_size                          =findPosInList(self.HEX_EXPANDED,t_info[4:5].lower())[0]
        # Cultural Quirk
        p+=length+1
        length=3
        quirk=uwppp[p:p+length]
        self.quirk                              =quirk
        # Name
        p=uwppp.find("|n|")+3
        length=uwppp[p:].find("|n|")
        name=uwppp[p:p+length]
        self.name                               =name
        # bases [WIP]
        self.bases                              = "" ## LOADING NOT IMPLEMENTED
        # allegiance
        p=uwppp.find("|a|")+3
        length=4
        allegiance=uwppp[p:p+length]
        self.allegiance                         = allegiance
        # Orbit Information
        p=uwppp.find("|o|")+3
        length=uwppp[p:].find("|")
        orbital_period=uwppp[p:p+length]
        self.orbital_period                     = float( orbital_period )
        p+=length+1
        length=uwppp[p:].find("|")
        rotations_per_orbit=uwppp[p:p+length]
        self.rotations_per_orbit                = float( rotations_per_orbit )
        p+=length+1
        length=uwppp[p:].find("|o|")
        pos=uwppp[p:p+length]
        self.pos                                = float( pos )
        self.weekly_traversal                   = 360*(7/self.orbital_period)
        self.isTideLocked                       = False
        if self.rotations_per_orbit==1.0: self.isTideLocked=True
        # Comment
        p=uwppp.find("|c|")+3
        length=uwppp[p:].find("|c|")
        comment=uwppp[p:p+length]
        self.comment                            = comment
        # Trade Codes
        p=uwppp.find("|a|")+3+4
        length=uwppp[p:].find("|o|")
        trade_codes=uwppp[p:p+length]
        if self.isGasGiant: self.trade_codes=""
        else:               self.trade_codes=trade_codes
        pass
    def import_planet(self,planetcode):
        self.clear()
        s_HID=planetcode[0: 4]
        self.row=int(s_HID[:2])
        self.col=int(s_HID[2:])
        self.location_code=s_HID
        # Get UWP
        s_UWP=planetcode[7:16]
        self.starport      =                                s_UWP[ 0: 1].lower()
        self.size          =findPosInList(self.HEX_EXPANDED,s_UWP[ 1: 2].lower())[0]
        self.atmosphere    =findPosInList(self.HEX_EXPANDED,s_UWP[ 2: 3].lower())[0]
        self.hydrographics =findPosInList(self.HEX_EXPANDED,s_UWP[ 3: 4].lower())[0]
        self.population    =findPosInList(self.HEX_EXPANDED,s_UWP[ 4: 5].lower())[0]
        self.government    =findPosInList(self.HEX_EXPANDED,s_UWP[ 5: 6].lower())[0]
        self.law_level     =findPosInList(self.HEX_EXPANDED,s_UWP[ 6: 7].lower())[0]
        # -
        self.tech_level    =findPosInList(self.HEX_EXPANDED,s_UWP[ 8: 9].lower())[0]

        try:
            self.size=int(self.size)
        except:
            for i in range(2):
                if self.size == self.list_table_size_R_S[i]:
                    self.size_str=self.size
                    self.size    =i-2
                    break

        # Get COG-sequence
        s_COG=planetcode[17:21]
        self.travel_code   =                                s_COG[ 0: 1].lower()
        self.climate       =findPosInList(self.HEX_EXPANDED,s_COG[ 1: 2].lower())[0]
        self.orbit         =findPosInList(self.HEX_EXPANDED,s_COG[ 2: 3].lower())[0]
        self.gravity       =findPosInList(self.HEX_EXPANDED,s_COG[ 3: 4].lower())[0]
        # Get PBJ-sequence
        s_PBJ=planetcode[22:25]
        self.population_mod=findPosInList(self.HEX_EXPANDED,s_PBJ[ 0: 1].lower())[0]
        self.asteroid_belts=findPosInList(self.HEX_EXPANDED,s_PBJ[ 1: 2].lower())[0]
        self.jovian_planets=findPosInList(self.HEX_EXPANDED,s_PBJ[ 2: 3].lower())[0]
        # Get WDITTP-sequence
        s_WDITTP=planetcode[26:32]
        self.law_level_weapons    =findPosInList(self.HEX_EXPANDED,s_WDITTP[ 0: 1].lower())[0]
        self.law_level_drugs      =findPosInList(self.HEX_EXPANDED,s_WDITTP[ 1: 2].lower())[0]
        self.law_level_information=findPosInList(self.HEX_EXPANDED,s_WDITTP[ 2: 3].lower())[0]
        self.law_level_technology =findPosInList(self.HEX_EXPANDED,s_WDITTP[ 3: 4].lower())[0]
        self.law_level_travellers =findPosInList(self.HEX_EXPANDED,s_WDITTP[ 4: 5].lower())[0]
        self.law_level_powers     =findPosInList(self.HEX_EXPANDED,s_WDITTP[ 5: 6].lower())[0]
        # Get CTM-sequence
        s_CTM=planetcode[33:54].split(" ")
        # tECCME
        self.tech_level_civilian                =findPosInList(self.HEX_EXPANDED,s_CTM[0][ 0: 1].lower())[0]
        self.tech_level_civilian_energy         =findPosInList(self.HEX_EXPANDED,s_CTM[0][ 2: 3].lower())[0]
        self.tech_level_civilian_computing      =findPosInList(self.HEX_EXPANDED,s_CTM[0][ 3: 4].lower())[0]
        self.tech_level_civilian_communication  =findPosInList(self.HEX_EXPANDED,s_CTM[0][ 4: 5].lower())[0]
        self.tech_level_civilian_medicine       =findPosInList(self.HEX_EXPANDED,s_CTM[0][ 5: 6].lower())[0]
        self.tech_level_civilian_environment    =findPosInList(self.HEX_EXPANDED,s_CTM[0][ 6: 7].lower())[0]
        # tLWAS
        self.tech_level_transportation          =findPosInList(self.HEX_EXPANDED,s_CTM[1][ 0: 1].lower())[0]
        self.tech_level_transportation_land     =findPosInList(self.HEX_EXPANDED,s_CTM[1][ 2: 3].lower())[0]
        self.tech_level_transportation_water    =findPosInList(self.HEX_EXPANDED,s_CTM[1][ 3: 4].lower())[0]
        self.tech_level_transportation_air      =findPosInList(self.HEX_EXPANDED,s_CTM[1][ 4: 5].lower())[0]
        self.tech_level_transportation_space    =findPosInList(self.HEX_EXPANDED,s_CTM[1][ 5: 6].lower())[0]
        # tPPHH
        self.tech_level_military                =findPosInList(self.HEX_EXPANDED,s_CTM[2][ 0: 1].lower())[0]
        self.tech_level_military_personalweapons=findPosInList(self.HEX_EXPANDED,s_CTM[2][ 2: 3].lower())[0]
        self.tech_level_military_personalarmour =findPosInList(self.HEX_EXPANDED,s_CTM[2][ 3: 4].lower())[0]
        self.tech_level_military_heavyweapons   =findPosInList(self.HEX_EXPANDED,s_CTM[2][ 4: 5].lower())[0]
        self.tech_level_military_heavyarmour    =findPosInList(self.HEX_EXPANDED,s_CTM[2][ 5: 6].lower())[0]
        # derived
        if  self.population==0 \
        and self.government==0 \
        and self.law_level ==0 \
        and self.tech_level==0 :
            self.populated=False
        else:
            self.populated=True
        # Trade Codes
        self.trade_codes=self.getTradeCodes()
        self.quirk=planetcode[55:58]
        pass
    def getUWP(self):
        if self.isGasGiant:
            if   self.isGasGiantLarge: return "LGG      "
            elif self.isGasGiantSmall: return "SGG      "
        else:
            uwp="{}{}{}{}{}{}{}-{}"
            result = uwp.format(                      self.starport         .upper() ,\
                                                      self.size_str         .upper() ,\
                                self.HEX_EXPANDED[max(self.atmosphere   ,0)].upper() ,\
                                self.HEX_EXPANDED[max(self.hydrographics,0)].upper() ,\
                                self.HEX_EXPANDED[max(self.population   ,0)].upper() ,\
                                self.HEX_EXPANDED[max(self.government   ,0)].upper() ,\
                                self.HEX_EXPANDED[max(self.law_level    ,0)].upper() ,\
                                self.HEX_EXPANDED[max(self.tech_level   ,0)].upper()  )
            return result
    def getCOG(self):
        cog="{}{}{}{}"
        if   self.band.startswith("near" ): orbit="n"
        elif self.band.startswith("mid"  ): orbit="m"
        elif self.band.startswith("far"  ): orbit="f"
        elif self.band.startswith("rogue"): orbit="r"
        else:                               orbit="e"
        result = cog.format(self.travel_code                              .upper() ,\
                            self.HEX_EXPANDED[max(min(self.climate,25),0)].upper() ,\
                                                       orbit              .upper() ,\
                            self.HEX_EXPANDED[max(min(self.gravity,25),0)].upper()  )
        return result
    def getPBJ(self):
        pbj="{}{}{}"
        result = pbj.format(self.HEX_EXPANDED[self.population_mod].upper() ,\
                            self.HEX_EXPANDED[self.asteroid_belts].upper() ,\
                            self.HEX_EXPANDED[self.jovian_planets].upper()  )
        return result
    def getWDITTP(self):
        wdittp="{}{}{}{}{}{}"
        result = wdittp.format(self.HEX_EXPANDED[max(min(self.law_level_weapons    ,25),0)].upper() ,\
                               self.HEX_EXPANDED[max(min(self.law_level_drugs      ,25),0)].upper() ,\
                               self.HEX_EXPANDED[max(min(self.law_level_information,25),0)].upper() ,\
                               self.HEX_EXPANDED[max(min(self.law_level_technology ,25),0)].upper() ,\
                               self.HEX_EXPANDED[max(min(self.law_level_travellers ,25),0)].upper() ,\
                               self.HEX_EXPANDED[max(min(self.law_level_powers     ,25),0)].upper()  )
        return result
    def getExTL(self):
        extl="{}-{}{}{}{}{} {}-{}{}{}{} {}-{}{}{}{}"
        result = extl.format(self.HEX_EXPANDED[max(min(self.tech_level_civilian                 ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_civilian_energy          ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_civilian_computing       ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_civilian_communication   ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_civilian_medicine        ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_civilian_environment     ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_transportation           ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_transportation_land      ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_transportation_water     ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_transportation_air       ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_transportation_space     ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_military                 ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_military_personalweapons ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_military_personalarmour  ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_military_heavyweapons    ,25),0)].upper() ,\
                             self.HEX_EXPANDED[max(min(self.tech_level_military_heavyarmour     ,25),0)].upper()  )
        return result
    def getTrade(self):
        trade_template="{}{}{}{}{}"
        trade=trade_template.format(\
            self.trade_number      ,\
            self.imports           ,\
            self.exports           ,\
            self.transient_trade   ,\
            self.port_size          )
        return trade
    def getC(self):
        culture="{}"
        result =culture.format(self.quirk)
        return result
    def getOrbitInfo(self):
        rObitInfo_template="|o|{:.2f}|{:.2f}|{:.2f}|o|"

        rObitInfo=rObitInfo_template.format(\
            self.orbital_period,            \
            self.rotations_per_orbit,       \
            self.pos                        )
        return rObitInfo


def roll(dice,sides):
    result=0
    for die in range(dice):
        result+=random.randrange(sides)+1
    return result


def findPosInList(list,item):
    try:
        rc = [i for i,x in enumerate(list) if x == item]
        if rc==[]: raise Exception
        return rc
    except: return [-1]


def splitup( string ):
    if string == None: return []
    if ',' in string:
        sl = string.split(',')
    else:
        sl = [string]
    for s in sl:
        try:
            if '-' in s:
                sl.remove(s)
                s = s.split('-')
                s = range( int(s[0]), int(s[1])+1 )
                sl += s
        except:
            pass
    for s in sl:
        try:
            sl.remove(s)
            sl.append( int(s) )
        except:
            pass
    return sl




def int_to_roman(input):
   """
   Convert an integer to Roman numerals.

   Examples:
   >>> int_to_roman(0)
   Traceback (most recent call last):
   ValueError: Argument must be between 1 and 3999

   >>> int_to_roman(-1)
   Traceback (most recent call last):
   ValueError: Argument must be between 1 and 3999

   >>> int_to_roman(1.5)
   Traceback (most recent call last):
   TypeError: expected integer, got <type 'float'>

   >>> for i in range(1, 21): print int_to_roman(i)
   ...
   I
   II
   III
   IV
   V
   VI
   VII
   VIII
   IX
   X
   XI
   XII
   XIII
   XIV
   XV
   XVI
   XVII
   XVIII
   XIX
   XX
   >>> print int_to_roman(2000)
   MM
   >>> print int_to_roman(1999)
   MCMXCIX
   """
   if type(input) != type(1):
      raise TypeError
   if not 0 < input < 4000:
      raise ValueError
   ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
   nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
   result = ""
   for i in range(len(ints)):
      count = int(input / ints[i])
      result += nums[i] * count
      input -= ints[i] * count
   return result


if __name__=="__main__": main()