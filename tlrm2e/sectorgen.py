#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from   sys          import argv,exit
from   platform     import system
# custom

        
# in-file settings
if system().lower().startswith("win"):
    SLASH="\\"
else:
    SLASH="/"

# critical paths
path        = argv[0][:argv[0].rfind(SLASH)+1]
config_src  = "config"+SLASH+"sectorgen.ini"


try:
    #from plugins.SectorGen.tlrm2e.inspect       import App as Inspector
    from plugins.SectorGen.tlrm2e.planet        import Planet
    from plugins.SectorGen.tlrm2e.systemgen     import App as SystemGen
    #from plugins.SectorGen.tlrm2e.system        import App as StarSystem
    path        = argv[0][:argv[0].rfind(SLASH)+1]+"plugins"+SLASH+"SectorGen"+SLASH
except:
    try:
        #from tlrm2e.inspect     import App     as Inspector
        from tlrm2e.planet      import Planet
        from tlrm2e.systemgen   import App as SystemGen
        #from tlrm2e.system      import App as StarSystem
    except:
        #from inspect    import App as Inspector
        from planet     import Planet
        from systemgen  import App as SystemGen
        #from system     import App as StarSystem



"""Notes:
Density: Typically 350 to 650 worlds per sector.
Nomenclature:
 - march (or marches)
 - region
 - reach (or reaches)
 - quadrant
 - matrix
"""

# CONSTANTS
VN='vn' # vanilla
SO='so' # space opera
HS='hs' # hard sci-fi


def main():
    sector=Hexgrid(populated=True)
    sector.export_sector()
    sector.import_sector()
    sector.show_subsector(6)
    input("Done.")
    exit()
    pass

class Hexgrid:
    VN='vn'
    BA='ba'
    TOP_LAYER="#document"
    ATTR_TAG ="#attributes"
    CDATA    ="#cdata"
    def __init__(self,populated=False,config=config_src,db_uwp=None,db_esp=None,db_names=None):
        global path
        from configparser       import ConfigParser

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
                path=path[:path[:-1].rfind(SLASH)+1]
                with open(path+config) as f:
                    self.config.read_file(f)

        # DEFAULT
        self.subsectors_per_quadrant_w=int( self.config.get("DEFAULT","quadrant width in subsectors")  )
        self.subsectors_per_quadrant_h=int( self.config.get("DEFAULT","quadrant height in subsectors")  )
        self.QUADRANTS_PER_SECTOR     =int( self.config.get("DEFAULT","quadrants per sector")  )
        # PATHS
        self.sector_index_save  =     self.config.get("PATHS","sector_index_save"  ).replace("/",SLASH).strip()
        self.sector_index_load  =     self.config.get("PATHS","sector_index_load"  ).replace("/",SLASH).strip()
        self.sector_systems_save=     self.config.get("PATHS","sector_systems_save").replace("/",SLASH).strip()
        self.sector_systems_load=     self.config.get("PATHS","sector_systems_load").replace("/",SLASH).strip()
        # GEOMETRY
        self.subsector_w      = int( self.config.get("GEOMETRY","subsector width")  )
        self.subsector_h      = int( self.config.get("GEOMETRY","subsector height") )
        # MISC
        self.mode             =      self.config.get("MISC","mode").strip()
        self.system_chance    = int( self.config.get("MISC","system chance"    )  )
        self.populated_chance = int( self.config.get("MISC","populated chance" )  )
        self.named_ba_chance  = int( self.config.get("MISC","named ba system").strip() )
        # DERIVED
        self.sector_hexes_num=self.subsector_w*self.subsector_h*(self.subsectors_per_quadrant_w+self.subsectors_per_quadrant_h)*self.QUADRANTS_PER_SECTOR
        self.grid_w=self.subsector_w*self.subsectors_per_quadrant_w*self.QUADRANTS_PER_SECTOR/2
        self.grid_h=self.subsector_h*self.subsectors_per_quadrant_h*self.QUADRANTS_PER_SECTOR/2

        # CONSTANTS
        self.log_template="{hex:>4} - {uwp:<9} {cog:>4} {pbj:>3} {widtt:>5} {extl:>21} {culture:>3}"

        # databases
        self.db_uwp  =db_uwp
        self.db_esp  =db_esp
        self.db_names=db_names

        # System GeneratorExit
        self.systemGen = SystemGen

        # INDEX
        self.main_index=[]
        if populated: self.populate()
        pass
    def populate(self,system_chance=None,populated_chance=None):
        if system_chance==None: system_chance=self.system_chance
        if populated_chance==None: populated_chance=self.populated_chance
        list_star_names=None
        #self.db_names=None #TEST
        if self.db_names!=None: list_star_names=self.db_names[self.TOP_LAYER]['traveller']['stars']['name']
        star_prefixes=("IAS {:04}","PED {:04}")
        used_star_names=[]
        _systems=0
        for i in range(self.sector_hexes_num):
            mode=self.mode
            starsystem=None
            r_sys=random.randrange(100)
            r_pop=random.randrange(100)
            if r_sys<system_chance:
                if r_pop>=populated_chance:
                    mode=self.BA
                if ((not mode==self.BA and self.db_names!=None)  \
                or (self.named_ba_chance>random.randrange(100))) \
                and (len(list_star_names)>0):
                    r=random.randrange(len(list_star_names))
                    name=list_star_names[r][self.CDATA]
                    del(list_star_names[r])
                else:
                    r=random.randrange(10)
                    if r<1: prefix=star_prefixes[1]
                    else:   prefix=star_prefixes[0]
                    while True:
                        name=prefix.format(random.randrange(9999))
                        if not name in used_star_names:
                            used_star_names.append(name)
                            break
                starsystem=self.systemGen(name=name,mode=mode,db_uwp=self.db_uwp,db_esp=self.db_esp)
                starsystem.new()
                #print( "{:<24} - sys: {:03}/{:03} pop: {:03}/{:03}".format(starsystem.name,r_sys,system_chance,r_pop,populated_chance))
                _systems+=1
            hex=Hex(i,system=starsystem)
            hex.update_adjacency(self.grid_w,self.grid_h)
            ssct_c=int(hex.col/self.subsector_w)
            ssct_r=int(hex.row/self.subsector_h)*self.subsectors_per_quadrant_w*self.QUADRANTS_PER_SECTOR/2
            hex.subsector=ssct_c+ssct_r
            self.main_index.append(hex)
        print("Generated {} systems on a hex map of a sector {} hexes in size.".format(_systems,self.sector_hexes_num))
        pass
    def show_subsector(self,num,listed=False,quadrant=False):
        if quadrant:
            width  = self.subsector_w*self.subsectors_per_quadrant_w
            height = self.subsector_h*self.subsectors_per_quadrant_h
            if   num == 3: num = 4
            elif num == 4: num = 3
            num_x  = int((num-1)%2)
            num_y  = int((num-1)/2)
            #print("Quadrant {}: w{:02} h{:02} | nx{} ny{}".format(num,width,height,num_x,num_y))
        else:
            width   = self.subsector_w
            height  = self.subsector_h
            num_x   = int((num-1)%(self.subsectors_per_quadrant_w*self.QUADRANTS_PER_SECTOR/2))
            num_y   = int((num-1)/(self.subsectors_per_quadrant_h*self.QUADRANTS_PER_SECTOR/2))
            #print("Sector {}: w{:02} h{:02} | nx{} ny{}".format(num,width,height,num_x,num_y))
        min_x = width *(num_x)-1
        max_x = width *(num_x+1)
        min_y = height*(num_y)-1
        max_y = height*(num_y+1)
        #print("Range of selection: {:02}{:02} to {:02}{:02}".format(min_y+2,min_x+2,max_y,max_x))
        
        if listed:
            rc=[]
            for hex in self.main_index:
                hex.update_adjacency(self.grid_w,self.grid_h)
                if  hex.col > min_x and hex.col < max_x \
                and hex.row > min_y and hex.row < max_y :
                    #hex.subsector=num-1
                    rc.append(hex)
                else:
                    continue
            return rc
        else:
            rs="Showing Subsector {}\n".format(num)
            for hex in self.main_index:
                hex.update_adjacency(self.grid_w,self.grid_h)
                if  hex.col > min_x and hex.col < max_x \
                and hex.row > min_y and hex.row < max_y :
                    hex.subsector=num-1
                else:
                    continue
                if hex.system==None:
                    rs+=self.log_template.format(                               \
                                                 hex  =hex.location_code       ,\
                                                 uwp  ="Void"                  ,\
                                                 cog  =""                      ,\
                                                 pbj  =""                      ,\
                                                 widtt=""                      ,\
                                                 extl =""                      ,\
                                                 culture =""                   ,\
                                                 star =""                       \
                                                                                )
                else:
                    rs+=self.log_template.format(                               \
                                                 hex  =hex.system.mainworld.location_code,\
                                                 uwp  =hex.system.mainworld.getUWP()     ,\
                                                 cog  =hex.system.mainworld.getCOG()     ,\
                                                 pbj  =hex.system.mainworld.getPBJ()     ,\
                                                 widtt=hex.system.mainworld.getWDITTP()  ,\
                                                 extl =hex.system.mainworld.getExTL()    ,\
                                                 culture =hex.system.mainworld.getC()    ,\
                                                 star    =hex.system.star.Class           \
                                                                                )
                if hex != self.main_index[-1]: rs+="\n"
            print(rs)
        pass
    def show_sector(self,listed=True):
        if listed:
            rc=[]
            for hex in self.main_index:
                rc.append(hex)
            return rc
        else:
            rs=""
            for hex in self.main_index:
                if hex.system==None:
                    rs+=self.log_template.format(                               \
                                                 hex  =hex.location_code       ,\
                                                 uwp  ="Void"                  ,\
                                                 cog  =""                      ,\
                                                 pbj  =""                      ,\
                                                 widtt=""                      ,\
                                                 extl =""                      ,\
                                                 culture =""                   ,\
                                                 star    =""                    \
                                                                                )
                else:
                    rs+=self.log_template.format(                               \
                                                 hex  =hex.system.mainworld.location_code,\
                                                 uwp  =hex.system.mainworld.getUWP()     ,\
                                                 cog  =hex.system.mainworld.getCOG()     ,\
                                                 pbj  =hex.system.mainworld.getPBJ()     ,\
                                                 widtt=hex.system.mainworld.getWDITTP()  ,\
                                                 extl =hex.system.mainworld.getExTL()    ,\
                                                 culture =hex.system.mainworld.getC()    ,\
                                                 star    =hex.system.star.Class           \
                                                                                )
                if hex != self.main_index[-1]: rs+="\n"
            return rs
    def clear_directory(self,src=None):
            if not src==None:
                import os
                for f in os.listdir(src):
                    if f.endswith(".test.system") or not f.endswith(".system"):
                        continue
                    os.remove(os.path.join(src, f))
            else:
                print("No directory specified for clear_directory(src).")    
    def export_sector(self,src=None,systems=True):
        if systems:
            if src==None:
                src=path+self.sector_systems_save
            self.clear_directory(src)
            for hex in self.main_index:
                if hex.system!=None:
                    with open(src+hex.location_code+".system",'w+') as f:
                        hex.system.show(file_out=src+hex.location_code+".system")
        else:
            if src==None:
                src=path+self.sector_index_save
            with open(src,'w+') as f:
                s=self.show_sector(False)
                f.write(s)
    def import_sector(self,src=None,systems=True):
        # INDEX
        self.main_index=[]
        ## SYSTEMS import
        if systems:
            i=0
            for iy in range(int(self.grid_h)):
                for ix in range(int(self.grid_w)):
                    if src==None:
                        src=path+self.sector_systems_load
                    file = "{:02}{:02}.system".format(iy+1,ix+1)
                    starsystem = None
                    try:
                        with open(src+file,'r',encoding='utf8') as f:
                            esp=f.read()
                            if esp.startswith("S"):
                                starsystem=self.systemGen(new=False,db_uwp=self.db_uwp,db_esp=self.db_esp)
                                starsystem.load(esp) #import system
                    except:
                        pass #print("Bad encoding in '{}'".format(file))
                    hex=Hex(i,system=starsystem)
                    hex.location_code=file[:4]
                    self.main_index.append(hex)
                    i+=1
        for hex in self.main_index:
            #print(hex.system,hex.location_code)
            hex.update_adjacency()
        ## RESET SECTOR INFO
        # INDEX
        #self.main_index=[]
        ## BEGIN IMPORT PROCESS
        #s,i=[],0
        #with open(src,'r') as f: s=f.read().split("\n")
        #for planetcode in s:
        #    FIND SYSTEM FILE
        #    READ SYSTEM FILE
        #---------------------------
        #    #print(planetcode)
        #    if not planetcode.find("Void")==-1:
        #        planet=None
        #    else:
        #        planet=Planet(new=False,db=self.db_uwp)
        #        planet.import_planet(planetcode)
        #    self.main_index.append(Hex(i,planet))
        #    i+=1
        #for hex in self.main_index:
        #    hex.update_adjacency(self.grid_w,self.grid_h)


class Hex:
    # Grid layout: "odd-r" = odd rows are shifted right
    def __init__(self,num,system=None):
        self.adjacent_to=[] # hex numbers
        self.location_code=None
        self.row=None
        self.col=None
        self.subsector=None
        self.position=num
        self.system=system
        self.allegiance=None
        if self.system!=None and system.mainworld!=None:
            self.allegiance=self.system.mainworld.allegiance
            self.system.mainworld.parent=self.system
        pass
    def update_adjacency(self,grid_w=None,grid_h=None):
        loc_template="{:>02d}{:>02d}"
        rc=[]
        if grid_w!=None and grid_h!=None:
            row=int(self.position/grid_w)
            col=int(self.position-row*grid_w)
        elif self.location_code!=None:
            row=int(self.location_code[:2])
            col=int(self.location_code[2:])
        self.row=row
        self.col=col
        if self.location_code==None:
            self.location_code=loc_template.format(self.row+1,self.col+1)

        if self.row%2==1:
            if not (self.col+1<1 and self.row-1<1): rc.append(loc_template.format(self.row-1,self.col+1)) # NE
            if not (self.col+1<1 and self.row+1<1): rc.append(loc_template.format(self.row+1,self.col+1)) # SE
        else:
            if not (self.col-1<1 and self.row-1<1): rc.append(loc_template.format(self.row-1,self.col-1)) # NW
            if not (self.col-1<1 and self.row+1<1): rc.append(loc_template.format(self.row+1,self.col-1)) # SW

        if not self.row-1<1:                      rc.append(loc_template.format(self.row-1,self.col  )) # NE/NW
        if not self.col-1<1:                      rc.append(loc_template.format(self.row  ,self.col-1)) #  W
        
        if grid_w!=None:
            if not self.row+1>grid_w:                 rc.append(loc_template.format(self.row+1,self.col  )) # SE/SW
            if not self.col+1>grid_w:                 rc.append(loc_template.format(self.row  ,self.col+1)) #  E

        self.adjacent_to=rc


if __name__=="__main__": main()