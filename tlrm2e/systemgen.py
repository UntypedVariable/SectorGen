#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys      import argv,exit
from platform import system
import random


#if __name__=="__main__":
#    #from inspect                import App as Inspector
#    from star                   import App as Star
#    from planet                 import Planet as Planet
#    #from system                 import App as StarSystem
#    from testing_tools.db_parse import App as XML_Parse
#else:
try:
    #from plugins.SectorGen.tlrm2e.inspect   import App as Inspector
    from plugins.SectorGen.tlrm2e.star      import App as Star
    from plugins.SectorGen.tlrm2e.planet    import Planet as Planet
    #from plugins.SectorGen.tlrm2e.system    import App as StarSystem
    from tools.db_parse                     import App as XML_Parse
except:
    try:
        #from tlrm2e.inspect     import App     as Inspector
        from tlrm2e.star        import App as Star
        from tlrm2e.planet      import Planet as Planet
        #from tlrm2e.system      import App as StarSystem
        from lib.tools.db_parse import App as XML_Parse
    except:
        #from inspect                import App as Inspector
        from star                   import App as Star
        from planet                 import Planet as Planet
        #from system                 import App as StarSystem
        from testing_tools.db_parse import App as XML_Parse


# in-file settings
if system().lower().startswith("win"):
    SLASH="\\"
else:
    SLASH="/"

# critical paths
path        = argv[0][:argv[0].rfind(SLASH)+1]
config_src  = "config"+SLASH+"systemgen.ini"

def main():
    path2=path[:-1]
    starsystem=App(new=True)
    filepath=path2[:path2.rfind(SLASH)+1]+"save"+SLASH+"sector"+SLASH+"0000_{name}.test.system"
    starsystem.show(file_out=path2[:path2.rfind(SLASH)+1]+"save"+SLASH+"sector"+SLASH+"0000_{name}.test.system")
    with open(filepath.format(name=starsystem.name),'r',encoding='utf8') as f:
        s=f.read()
        starsystem.load(s)
    starsystem.show()
    pass



class App:
    HEX_EXPANDED  =["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p"]
    VN='vn'
    SO='so'
    HS='hs'
    BA='ba'
    def __init__(self,new=False,name="noname",mode=None,db_uwp=None,db_esp=None):
        global path
        self.name          =None
        self.star          =None
        self.planetoids    =[]
        self.mainworld     =None
        self.population_mod=0
        self.asteroid_belts=0
        self.jovian_planets=0
        self.db_esp=db_esp
        if db_esp==None and __name__=="__main__":
            from sys import argv
            from testing_tools.db_parse import App as XML_Parse
            path=argv[0][:argv[0].rfind("\\")]
            path=path[:path.rfind("\\")+1]
            self.db_esp=XML_Parse.load(path,"lib\\xml\\esp_information.xml")
        self.db_uwp=db_uwp
        if db_uwp==None and __name__=="__main__":
            from sys import argv
            from testing_tools.db_parse import App as XML_Parse
            path=argv[0][:argv[0].rfind("\\")]
            path=path[:path.rfind("\\")+1]
            self.db_uwp=XML_Parse.load(path,"lib\\xml\\uwp_information.xml")
        self.name=name
        # config
        from configparser       import ConfigParser

        self.config = ConfigParser()
        try:
            with open(path+"plugins"+SLASH+"SectorGen"+SLASH+config_src) as f:
                self.config.read_file(f)
        except:
            try:
                with open(path+config_src) as f:
                    self.config.read_file(f)
            except:
                path=path[:path[:-1].rfind(SLASH)+1]
                with open(path+config_src) as f:
                    self.config.read_file(f)
        
        # retrieve config
        if mode==None: self.mode=self.config.get("DEFAULT","mode").strip()
        else:          self.mode=mode
        # set mode settings
        if   self.mode in (self.VN,self.SO,self.HS): self.populated=True
        elif self.mode == self.BA: self.populated=False
        if new: self.new()
        pass

    def get_gDist(self,PosInPAU,debug=False):
        ri=0
        gSize=( self.star.HabOuter-self.star.HabInner )/self.star.AU*100
        gRaw =  PosInPAU-(self.star.HabCenter/self.star.AU*100)
        ri   =int(gRaw/(gSize/2)*10)
        if debug: print( "Object at orbital band {} %AU is {} %AU distant from the GZ({}) of a {} %AU wide HZ, translating to {} mod.".format(PosInPAU,int(gRaw),int(self.star.HabCenter/self.star.AU*100),int(gSize),ri) )
        #raise Exception
        return ri
    def new(self):
        self.star=Star(db_esp=self.db_esp)
        self.star.new(mode=self.mode)
        self.star.name(self.name)

        for i in range(self.star.Planetoids):
            if self.star.Planets[i][1].startswith("Jov"):
                self.jovian_planets+=1
                AUtoStar=self.star.Planets[i][0]/100
                gDist   =self.get_gDist(self.star.Planets[i][0])
                self.planetoids.append( Planet(populated=False,mainworld=False,db=self.db_uwp,type='rgg',band=self.star.Planets[i][2].lower(),AUtoStar=AUtoStar,GoldieDist=gDist) )
            else:
                AUtoStar=self.star.Planets[i][0]/100
                gDist   =self.get_gDist(self.star.Planets[i][0])
                self.planetoids.append( Planet(populated=False,mainworld=False,db=self.db_uwp,band=self.star.Planets[i][2].lower(),AUtoStar=AUtoStar,GoldieDist=gDist) )
                if self.planetoids[i].size==0: self.asteroid_belts+=1
                #self.planetoids[i].AUtoStar=self.star.Diameter*166*self.planetoids[i].orbit
        self.purge()
        i=0
        for planet in sorted(self.planetoids,key=lambda x: x.AUtoStar):
            sequential_planet_name=self.star.Name+" "+int_to_roman(i+1)
            planet.name=sequential_planet_name
            planet.name_satellites()
            i+=1
        self.findMainworld()
        #get_gDist(self.mainworld.AUtoStar*100,debug=True)
        pass
    def purge(self):
        orbital_ring_mod=1.66/6.5
        for planetoid_one in self.planetoids:
            i=0
            while i < len(self.planetoids):
                if planetoid_one==self.planetoids[i]:
                    i+=1
                    continue
                if planetoid_one.AUtoStar//orbital_ring_mod==self.planetoids[i].AUtoStar//orbital_ring_mod:
                    if self.planetoids[i].type.lower() in ("lgg","sgg","rgg"): self.jovian_planets-=1
                    if self.planetoids[i].size == 0                          : self.asteroid_belts-=1
                    del(self.planetoids[i])
                    #print("Purged planet!")
                else:
                    i+=1
        pass
    def findMainworld(self):
        func_testing=False
        mainworld       =None
        populated_worlds=0
        mainworld_found =False
        # CRITERIA EVALUATION FUNCTION
        def evaluate_planetoid(planetoid,criteria):
            criteria=criteria.split(",")
            matches_criteria=True
            for criterium in criteria:
                if matches_criteria==False: break
                if criterium.find("or"): criterium=criterium.split("or")
                else: criterium=[criterium]
                sub_criterium_matches=False
                for sub_criterium in criterium:
                    sub_criterium=sub_criterium.strip()
                    if sub_criterium.startswith("tc("):
                        if planetoid.trade_codes.lower().find(sub_criterium[3:-1].lower()) != -1:
                            sub_criterium_matches=True
                            continue
                        else:
                            continue
                    else:
                        if   sub_criterium.find("{}")!=-1 and eval(sub_criterium.format("planetoid"))==True:
                            sub_criterium_matches=True
                            continue
                        elif sub_criterium.find("{}")==-1 and eval("planetoid."+sub_criterium)==True:
                            sub_criterium_matches=True
                            continue
                        else:
                            continue
                if sub_criterium_matches: continue
                else:
                    matches_criteria=False
                    break
            return matches_criteria
        def evaluate_for_criteria(criteria,bill="",mainworld_found=False,populated_worlds=0,functest=False):
            for planet in sorted(self.planetoids, key=lambda x: x.AUtoStar):
                if evaluate_planetoid(planet,criteria):
                    mainworld_found, populated_worlds = select_planetoid(planet,mainworld_found,populated_worlds)
                    if functest: print("selected planet '{}'. ({})".format(planet.name,bill))
                else:
                    for satellite in sorted(planet.satellites, key=lambda x: x.orbit):
                        if evaluate_planetoid(satellite,criteria):
                            mainworld_found, populated_worlds = select_planetoid(satellite,mainworld_found,populated_worlds)
                            if functest: print("selected satellite '{}' of planet '{}'. ({})".format(satellite.name,planet.name,bill))
                        else:
                            continue
            return mainworld_found, populated_worlds
        # SELECTION PROCESSING FUNCTION
        def select_planetoid(planetoid,mainworld_found,populated_worlds):
            if not mainworld_found:
                planetoid.isMainworld=True
                self.mainworld=planetoid
                mainworld_found=True
                if self.populated:
                    planetoid.populated=self.populated
                    planetoid.new(from_scratch=False)
                planetoid.pos=0
                if planetoid.type=="satellite": planetoid.parent.pos=0
                if  planetoid.tech_level_civilian_environment>=7\
                and planetoid.tech_level_transportation_space>=6:
                    roll_range=min(planetoid.tech_level_civilian_environment+planetoid.tech_level_transportation_space,planetoid.population)
                    populated_worlds+=max(random.randrange(roll_range),0)
                if self.populated:
                    self.population_mod=min(max((random.randrange(18)+3)//3+max((random.randrange(6)+1)-3,0),1,populated_worlds),9)
                else:
                    self.population_mod=0
            elif populated_worlds > 0:
                populated_worlds -= 1
                planetoid.populated=True
                planetoid.new(from_scratch=False,max_pop=self.mainworld.population-1,max_tl=self.mainworld.tech_level-1)
            return mainworld_found, populated_worlds
        #
        # MAINWORLD CRITERIA
        NOT_GG=",isGasGiant==False"

        mainworld_preferences=(\
            ("HZ & Ga or Wa, not Fl","tc(Ga) or tc(Wa),atmosphere <= 9,abs({}.GoldieDist)<=10"),\
            ("HZ & Nearly-Ag","atmosphere >= 4,atmosphere <= 9,hydrographics >= 4,hydrographics <= 8,abs({}.GoldieDist)<=10"),\
            ("HZ & Semi-Viable Atmosphere and any Water","atmosphere > 1,atmosphere <= 9,hydrographics > 0,abs({}.GoldieDist)<=10"),\
            ("Asteroid Belt","tc(As)"),\
            ("HZ & Semi-Viable Atmosphere","atmosphere > 1,atmosphere <= 9,abs({}.GoldieDist)<=10"),\
            ("HZ & Good-Sized and any Water","size >= 3,size <= 9,hydrographics > 0,abs({}.GoldieDist)<=10"),\
            ("HZ & any Water","hydrographics > 0,abs({}.GoldieDist)<=10"),\
            ("Good-Sized and any Water","size >= 3,size <= 9,hydrographics > 0"),\
            ("Any Water","hydrographics > 0"),\
            ("Good-Sized","size >= 3,size <= 9"),\
            ("Any","size >= 0"),\
            )
        for preference in mainworld_preferences:
            mainworld_found, populated_worlds = evaluate_for_criteria(preference[1]+NOT_GG,preference[0],mainworld_found,populated_worlds)
        pass
    def getPBJ(self):
        pbj="{}{}{}"
        result = pbj.format(self.HEX_EXPANDED[self.population_mod].upper() ,\
                            self.HEX_EXPANDED[self.asteroid_belts].upper() ,\
                            self.HEX_EXPANDED[self.jovian_planets].upper()  )
        return result
    def load(self,esp):
        esp=esp.split("\n")
        # load star
        #   parse
        usp=esp[0]      # universal star profile
        #   apply
        self.star=Star(db_esp=self.db_esp)
        self.star.new(load=usp)
        # load P(BJ)
        p1=usp.find("|p|")+3
        p2=p1+1
        self.population_mod=findPosInList(self.HEX_EXPANDED,usp[p1:p2])[0]
        # load name
        p1=usp.find("|sn|")+4
        p2=p1+usp[p1:].find("|sn|")
        self.name=usp[p1:p2]
        # load planets
        self.planetoids=[]
        planet_markers   =("•","M")
        satellite_markers=(">","m")
        uwppp=""        # universal world profile ++ (satellites)
        most_recent_planet=None
        for i in range(len(esp)):
            if i==0: continue
            line=esp[i].strip()
            if   line[0:1] in planet_markers:
                planet=Planet(new=False,populated=False,db=self.db_uwp)
                planet.load(line)
                if line[0:1]=="M":
                    planet.isMainworld=True
                    self.mainworld=planet
                if planet.size==0: self.asteroid_belts+=1
                elif planet.isGasGiant: self.jovian_planets+=1
                most_recent_planet=planet
                self.planetoids.append(planet)
            elif line[0:1] in satellite_markers\
            and most_recent_planet!=None:
                satellite=Planet(new=False,populated=False,db=self.db_uwp)
                satellite.load(line)
                if line[0:1]=="m":
                    satellite.isMainworld=True
                    self.mainworld=satellite
                most_recent_planet.satellites.append(satellite)
        ## ref: M  49 - X420000-0  KN3 00000 0-00000 0-0000 0-0000 00000     |n|noname I|n|  |a|     Ba De Po |o|143.18|1.00|0.00|o| |c|---|c|
        pass
    def show(self,file_out=None,indent=3):
        rs =''
        indent=indent*" "
        uwp_template="{uwp:<9.9} {cog:>4.4} {widttp:>6.6} {extl:>21.21} {trade:>5.5} {culture:>3.3} |n|{name}|n| {bases} |a|{allegiance:4.4} {tc} {orbit}"
        rs_line_template="{indentation}{marker:1}{orbit:>4} - {uwp} |c|{comment}|c|\n"
        layer=0
        rs+=rs_line_template.format(indentation=indent*layer,orbit=0,uwp=self.star.Class+" |p|{:1} |n|{}|n| |sn|{}|sn|".format(self.HEX_EXPANDED[self.population_mod].upper(),self.star.Name,self.name),marker="S",comment=self.star.comment)
        i=0
        for planet in sorted(self.planetoids,key=lambda x: x.AUtoStar,reverse=False):
            comment=planet.comment
            marker="•"
            if planet.isMainworld: marker="M"
            uwp=uwp_template.format(                 \
                uwp         = planet.getUWP()       ,\
                cog         = planet.getCOG()       ,\
                widttp      = planet.getWDITTP()    ,\
                extl        = planet.getExTL()      ,\
                trade       = planet.getTrade()     ,\
                culture     = planet.getC()         ,\
                name        = planet.name           ,\
                bases       = planet.bases          ,\
                allegiance  = planet.allegiance     ,\
                tc          = planet.trade_codes[1:],\
                orbit       = planet.getOrbitInfo()  )
            rs+=rs_line_template.format(indentation=indent*layer,orbit=planet.orbit,uwp=uwp,marker=marker,comment=comment)
            if len(planet.satellites) > 0:
                layer+=1
                for satellite in sorted(planet.satellites,key=lambda x: x.orbit,reverse=False):
                    comment=satellite.comment
                    marker=">"
                    if satellite.isMainworld: marker="m"
                    uwp=uwp_template.format(                    \
                        uwp         = satellite.getUWP()       ,\
                        cog         = satellite.getCOG()       ,\
                        widttp      = satellite.getWDITTP()    ,\
                        extl        = satellite.getExTL()      ,\
                        trade       = satellite.getTrade()     ,\
                        culture     = satellite.getC()         ,\
                        name        = satellite.name           ,\
                        bases       = satellite.bases          ,\
                        allegiance  = satellite.allegiance     ,\
                        tc          = satellite.trade_codes[1:],\
                        orbit       = satellite.getOrbitInfo()  )
                    rs+=rs_line_template.format(indentation=indent*layer,orbit=satellite.orbit,uwp=uwp,marker=marker,comment=comment)
                layer-=1
            i+=1
        if file_out!=None:
            with open(file_out.format(name=self.name),'w+',encoding='utf8') as f:
                f.write(rs)
        else:
            self.star.show()
            print(rs)




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


def findPosInList(list,item):
    try:
        rc = [i for i,x in enumerate(list) if x == item]
        if rc==[]: raise Exception
        return rc
    except: return [-1]


if __name__ == '__main__': main()