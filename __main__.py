#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from   tkinter      import *
from   sys          import argv,exit
from   os           import getcwd
from   platform     import system
import getopt
# custom
#from tlrm2e.inspect     import App     as Inspector

# in-file settings
if system().lower().startswith("win"):
    SLASH="\\"
else:
    SLASH="/"

# critical paths
#path        = argv[0][:argv[0].rfind(SLASH)+1]
path        = getcwd()+SLASH
config_src  = "config"+SLASH+"sector.ini"

#temp
from tlrm2e.inspect     import App     as Inspector


def main():
    ## inspector
    inspector_use       = False
    inspector_hex       = "test"
    inspect_verbose     = False
    inspector_selection = False
    
    ## sectorgen
    sectorgen_use   = False
    generate_new    = False
    mode            = None
    draw_complete   = False
    draw_quadrants  = False
    draw_subsectors = False
    draw_all        = False
    
    ## settings
    justification   = 16
    settingsf       = "{:<"+str(justification)+"}: {}\n"
    
    ## helptext
    helptext        = "\n  --help --generate --draw --inspect=<hex_location>\n"
    helptext_g      = "\n-g, --generate\nGenerates a new full sector.\n\nModifiers: -m, --mode ;\n\nMODES:\n  hs = Hard Sci-Fi\n  so = Space Opera\n  vn = Vanilla/Default\n\nEXAMPLE: --generate --mode=hs\n"
    helptext_d      = "\n-d, --draw\nDraws a hexmap of the current full sector in \"save/sector\".\n\nEXAMPLE: --draw\n"
    helptext_i      = "\n-i, --inspect\nReturns a readout of the information contained in a specific 4-digit hex-location.\n\nModifiers: -v, --verbose ; -s, --system ;\n\nEXAMPLE: --inspect=1403 --verbose\n"
    try:
        opts, args = getopt.getopt(argv[1:],"h:gm:di:vs:",["help=","generate","mode=","draw","inspect=","verbose","selection="])
    except getopt.GetoptError:
        print(helptext)
        exit(2)
    
    ## SELECTION OF ARGUMENTS
    
    for opt, arg in opts:
        if opt == opt in ("-h", "--help"):
            try:
                topic = arg.strip()
                if   topic in ("g","generate","m","mode"):
                    print(helptext_g)
                elif topic in ("d","draw"):
                    print(helptext_d)
                elif topic in ("i","inspect","v","verbose","s","selection"):
                    print(helptext_i)
            except:
                print(helptext)
            exit(0)


        elif opt in ("-g", "--generate"):
            sectorgen_use   = True
            generate_new    = True
        elif opt in ("-m", "--mode"):
            mode = arg.strip()


        elif opt in ("-d", "--draw"):
            sectorgen_use   = True
            draw_all        = True


        elif opt in ("-i", "--inspect"):
            inspector_hex = arg.strip()
            inspector_use = True
        elif opt in ("-v", "--verbose"):
            inspect_verbose = True
        elif opt in ("-s", "--selection"):
            inspector_selection = arg.strip()
            
    ## settings output
    #s=""
    #s+=settingsf.format("Inspector",    inspector_use)
    #s+=settingsf.format("SectorGen",    sectorgen_use)
    #s+=settingsf.format("Draw Hexmaps", draw_all     )
    #print(s)
    
    # CONSTANTS
    VN='vn' # vanilla
    SO='so' # space opera
    HS='hs' # hard sci-fi
    # used functions:
    ## all
    selected_sector = "save"+SLASH+"sector_index.txt"
    
    try:
        APP=App(False)
        if sectorgen_use:
            if generate_new:
                # create sector
                APP.create_sector(mode=mode)
                # export sector
                APP.save_sector()

            # import sector
            if not generate_new: APP.load_sector()
            
            # draw Sector
            if draw_complete or draw_all:
                sc_name="save"+SLASH+"Sector-complete.png"
                draw_region=APP.sectorGenerator.show_sector(True)
                APP.draw(draw_region,sc_name,multiplier=4)
            
            # draw Subsectors (Quadrants)
            if draw_quadrants or draw_all:
                base_name="Quadrant-{:02}-{}.png"
                quadrants=["Alpha","Beta","Gamma","Delta"]
                for i in range(4):
                    name="save"+SLASH+base_name.format(i+1,quadrants[i])
                    #APP.sectorGenerator.show_subsector(i+1,False,True)
                    draw_region=APP.sectorGenerator.show_subsector(i+1,True,True)
                    #check_region(draw_region)
                    APP.draw(draw_region,name,multiplier=2)
            
            # draw Subsectors
            if draw_subsectors or draw_all:
                base_name="Subsector-{:02}-{:02}{}.png"
                subsectors=[["","","",""],["","","",""],["","","",""],["","","",""]]
                for j in range(4):
                    n = j
                    if   n == 2: n = 3
                    elif n == 3: n = 2
                    sect_x  = int(n%2)
                    sect_y  = int(n/2)
                    subsectors_list=[sect_y*8+  sect_x*2,sect_y*8+  sect_x*2+1,\
                                     sect_y*8+4+sect_x*2,sect_y*8+4+sect_x*2+1]
                    #print("subsectors_list",subsectors_list)
                    for i in range(4):
                        n2=subsectors[n][i]
                        if n2!="": n2 = "-"+n2
                        name="save"+SLASH+base_name.format(n+1,i+1,n2)
                        #APP.sectorGenerator.show_subsector(subsectors_list[i],False,False)
                        draw_region=APP.sectorGenerator.show_subsector(subsectors_list[i]+1,True,False)
                        #check_region(draw_region)
                        APP.draw(draw_region,name)

        if inspector_use:
            # inspection
            from tlrm2e.inspect     import App     as Inspector
            inspector = Inspector()
            mode=None    
            if inspect_verbose: mode = inspector.VERBOSE
            depth=None    
            if   inspector_selection in ('s','star'):       depth = inspector.SYSTEM
            elif inspector_selection in ('mw','mainworld'): depth = inspector.MAINWORLD
            else:                                           depth = None
            inspected_hex = inspector.inspect(inspector_hex,mode=mode,depth=depth)
            for info_block in inspected_hex:
                print(info_block)
    except Exception as e:
        import traceback
        exc = traceback.format_exc()
        print(exc)
    
    input("Done. Press any key to Exit.")
    exit(0)
    pass




# TESTING FUNCTIONS
def check_region(draw_region):
    sp=""
    for hex in draw_region:
        if hex.planet!=None: sp+=hex.planet.location_code+" - "+hex.planet.getUWP()+" "+hex.planet.trade_codes+"\n"
    print(sp)
    pass


# PRIMARY FUNCTIONS
class App:
    CONF_GEN='generation'
    CONF_HEX='hexdraw'
    INDENT  =37
    def __init__(self,new=True,config=config_src):
        # imports
        from configparser       import ConfigParser
        
        # console outputs
        self.LOADING ="{:<"+str(self.INDENT)+"} [ .... ]"
        self.LOADED  ="{:<"+str(self.INDENT)+"} [ OKAY ]"

        # config
        self.new    = new
        self.config = ConfigParser()
        try:
            with open(path+"plugins"+SLASH+"SectorGen"+SLASH+config) as f:
                self.config.read_file(f)
        except:
            with open(path+config) as f:
                self.config.read_file(f)
        self.configs_loaded=[]
        pass
    def create_sector(self,system_chance=None,populated_chance=None,mode='vn'):
        if not self.CONF_GEN in self.configs_loaded: self.config_load(self.CONF_GEN)
        if system_chance==None:    system_chance   =self.system_chance
        if populated_chance==None: populated_chance=self.populated_chance
        print("Generating sector...",end="\r")
        self.sectorGenerator.populate(system_chance=system_chance,populated_chance=populated_chance,mode=mode)
        pass
    def save_sector(self,src=None):
        if not self.CONF_GEN in self.configs_loaded: self.config_load(self.CONF_GEN)
        if src==None: src=self.sector_systems_save
        print(self.LOADING.format("Saving sector..."),end="\r")
        self.sectorGenerator.export_sector(path+src,systems=True)
        print(self.LOADED.format("Sector saved!"),end="\r\n")
        pass
    def load_sector(self,src=None):
        if not self.CONF_GEN in self.configs_loaded: self.config_load(self.CONF_GEN)
        if src==None: src=self.sector_systems_load
        print(self.LOADING.format("Retrieving sector information."),end="\r")
        # import sector
        self.sectorGenerator.import_sector(path+src,systems=True)
        print(self.LOADED.format("Retrieved sector information."),end="\r\n")
        pass
    def config_load(self,config=None):
        ## Valid configs: generation, hexdraw
        print(self.LOADING.format("Retrieving {} configurations.".format(config)),end="\r")
        ## CONFIG SELECTOR
        if config==self.CONF_GEN:
            from tlrm2e.sectorgen   import Hexgrid as SectorGen
            from lib.tools.db_parse import App as XML_Parse
            # DEFAULT
            self.system_chance      =int( self.config.get("DEFAULT","system chance"      )  )
            self.populated_chance   =int( self.config.get("DEFAULT","populated chance"   )  )
            self.sector_index_save  =     self.config.get("DEFAULT","sector_index_save"  ).replace("/",SLASH)
            self.sector_index_load  =     self.config.get("DEFAULT","sector_index_load"  ).replace("/",SLASH)
            self.sector_systems_save=     self.config.get("DEFAULT","sector_systems_save").replace("/",SLASH)
            self.sector_systems_load=     self.config.get("DEFAULT","sector_systems_load").replace("/",SLASH)
            # DATABASES
            self.xml_path_uwp_information   =self.config.get("DATABASES","uwp_information").replace("/",SLASH)
            self.xml_path_esp_information   =self.config.get("DATABASES","esp_information").replace("/",SLASH)
            self.xml_path_db_names          =self.config.get("DATABASES","names"          ).replace("/",SLASH)
            
            # uwp database
            self.dict_uwp_information=XML_Parse.load(path,self.xml_path_uwp_information)
            self.dict_esp_information=XML_Parse.load(path,self.xml_path_esp_information)
            self.dict_db_names       =XML_Parse.load(path,self.xml_path_db_names       )
            
            # create sector generator
            self.sectorGenerator=SectorGen(populated=self.new,db_uwp=self.dict_uwp_information,db_esp=self.dict_esp_information,db_names=self.dict_db_names)
        elif config==self.CONF_HEX:
            from PIL                import Image
            from math               import cos
            # GEOMETRY
            self.grid_w             = int( self.config.get("GEOMETRY","grid width"      ) )
            self.grid_h             = int( self.config.get("GEOMETRY","grid height"     ) )
            self.hex_r              = int( self.config.get("GEOMETRY","hex_r"           ) )
            hex_r_R                 = self.config.get("GEOMETRY","image_r_ratio").split(":")
            self.hex_r_multiplier   = 2
            self.hex_R_multiplier   = int(hex_r_R[1])/int(hex_r_R[0])*2
            # IMAGES
            # ----  icons
            self.img_path_gas_giant_present     =self.config.get("IMAGES","gas_giant_present"    ).replace("/",SLASH)
            self.img_path_amber_zone            =self.config.get("IMAGES","amber_zone"           ).replace("/",SLASH)
            self.img_path_asteroid_belt         =self.config.get("IMAGES","asteroid_belt"        ).replace("/",SLASH)
            self.img_path_fuel_dump             =self.config.get("IMAGES","fuel_dump"            ).replace("/",SLASH)
            self.img_path_fuel_station          =self.config.get("IMAGES","gas_station"          ).replace("/",SLASH)
            self.img_path_fuel_station_plus     =self.config.get("IMAGES","gas_station_plus"     ).replace("/",SLASH)
            # ----  big icons    
            self.img_path_mw_planet_generic     =self.config.get("IMAGES","mw_planet_generic"    ).replace("/",SLASH)
            self.img_path_mw_asteroid_belt      =self.config.get("IMAGES","mw_asteroid_belt"     ).replace("/",SLASH)
            self.img_path_mw_fuel_dump          =self.config.get("IMAGES","void_fuel_dump"       ).replace("/",SLASH)
            self.img_path_mw_fuel_station       =self.config.get("IMAGES","void_gas_station"     ).replace("/",SLASH)
            self.img_path_mw_fuel_station_plus  =self.config.get("IMAGES","void_gas_station_plus").replace("/",SLASH)
            # COLORS
            self.white          = eval( self.config.get("COLORS","white" ) )
            self.green          = eval( self.config.get("COLORS","green" ) )
            self.green_shady    = eval( self.config.get("COLORS","green shady" ) )
            self.red            = eval( self.config.get("COLORS","red"   ) )
            self.blue           = eval( self.config.get("COLORS","blue"  ) )
            self.yellow         = eval( self.config.get("COLORS","yellow") )
            self.orange         = eval( self.config.get("COLORS","orange") )
            self.brown          = eval( self.config.get("COLORS","brown" ) )
            self.gbrown         = eval( self.config.get("COLORS","green brown" ) )
            self.black          = eval( self.config.get("COLORS","black" ) )

            # derived
            self.hex_R  = int(self.hex_r/cos(0.5235987756))
            self.width  = self.hex_r*2*(self.grid_w+1)
            self.height = self.hex_R*2*(self.grid_h+1)

            # info icons
            self.jovian_i_img = Image.open(path+self.img_path_gas_giant_present,   'r').convert("RGBA")
            self.hazard_i_img = Image.open(path+self.img_path_amber_zone,          'r').convert("RGBA")
            self.aster_i_img  = Image.open(path+self.img_path_asteroid_belt,       'r').convert("RGBA")
            self.fueld_i_img  = Image.open(path+self.img_path_fuel_dump,           'r').convert("RGBA")
            self.fuels_i_img  = Image.open(path+self.img_path_fuel_station,        'r').convert("RGBA")
            self.fuels_p_i_img= Image.open(path+self.img_path_fuel_station_plus,   'r').convert("RGBA")
            # system icons
            self.globe_img    = Image.open(path+self.img_path_mw_planet_generic,   'r').convert("RGBA")
            self.aster_img    = Image.open(path+self.img_path_mw_asteroid_belt,    'r').convert("RGBA")
            self.fueld_img    = Image.open(path+self.img_path_mw_fuel_dump,        'r').convert("RGBA")
            self.fuels_img    = Image.open(path+self.img_path_mw_fuel_station,     'r').convert("RGBA")
            self.fuels_p_img  = Image.open(path+self.img_path_mw_fuel_station_plus,'r').convert("RGBA")
        print(self.LOADED.format("Retrieved {} configurations.".format(config)),end="\r\n")
        # indicate config is loaded
        self.configs_loaded.append(config)
        pass
    def draw(self,region,name,multiplier=1):
        if not self.CONF_HEX in self.configs_loaded: self.config_load(self.CONF_HEX)
        print(self.LOADING.format("{} drawing".format(name)),end="\r")
        # setup imaging library tools
        from PIL import Image, ImageDraw
        image1 = Image.new("RGBA",(int(self.hex_r*self.hex_r_multiplier)*(self.grid_w*multiplier+1),int(self.hex_R*self.hex_R_multiplier)*(self.grid_h*multiplier+1)))
        draw   = ImageDraw.Draw(image1)
        # setup hexmap tools
        from lib.draw.draw  import HexDraw, Coordinates
        pointer  = Coordinates(self.hex_r,2*self.hex_R)
        whitegrid= []
        blackgrid= []
        i=0
        for row in range(self.grid_h*multiplier):
            if row!=0: pointer+=Coordinates(0,int(1.5*self.hex_R+1))
            if (row+1)%2==0: pointer.x =int(2.5*self.hex_r-1)
            else:            pointer.x =int(1.5*self.hex_r+0)
            for col in range(self.grid_w*multiplier):
                if col!=0: pointer+=Coordinates(2*self.hex_r-1,0)
                hex=HexDraw(P=pointer,r=self.hex_r)
                # system information
                system_present=False
                try:
                    system_obj=region[i].system
                except IndexError:
                    print("Index out of range at 'region' ",i,"/",len(region))
                if system_obj!=None and system_obj.mainworld!=None:
                    system_present=True
                    fill=self.green
                    service_oriented=True
                    if  system_obj.mainworld.travel_code             =="a": fill=self.green_shady # Hazardous
                    if  service_oriented \
                    and system_obj.mainworld.starport.lower() in ('x','e'): fill=self.gbrown      # Bad Starport
                    if  system_obj.mainworld.population              == 0 : fill=self.brown       # Barren
                    if  system_obj.mainworld.tech_level              >=12 : fill=self.blue        # Hi Tech
                    if  service_oriented \
                    and system_obj.jovian_planets                    <= 0 \
                    and system_obj.mainworld.hydrographics           <= 0 \
                    and system_obj.mainworld.starport.lower()        =="x": fill=self.red         # No Fuel
                else:
                    fill=self.black
                # prep the hexes for drawing
                self.drawpoly(draw,hex.poly(),fill=fill,outline=None)
                if system_present: blackgrid.append(hex.poly())
                else: whitegrid.append(hex.poly())
                # add hex number
                loc_code=region[i].location_code
                if fill==self.black: draw.text((pointer.x-4*3+1,pointer.y-self.hex_R+15),loc_code,self.white)
                else:                draw.text((pointer.x-4*3+1,pointer.y-self.hex_R+15),loc_code,self.black)
                # add planet symbol
                if system_obj!=None and system_obj.mainworld!=None:
                    if system_obj.mainworld.size==0:
                        image1.paste(self.aster_img,(pointer.x-20,pointer.y-20),self.aster_img)
                    else:
                        image1.paste(self.globe_img,(pointer.x-20,pointer.y-20),self.globe_img)
                # add planet codes
                if system_present: # UWP
                    draw.text((pointer.x-9*3+1,pointer.y+25),system_obj.mainworld.getUWP(),self.black)
                    tc=""
                    for trade_code in system_obj.mainworld.trade_codes:
                        tc+=trade_code
                    s_UWP="{:^18}".format(tc.strip())
                    del(tc)
                    draw.text((pointer.x-18*3+1,pointer.y+40),s_UWP,self.black)
                    #s_UWP="{:^24}".format(system_obj.mainworld.quirk)
                    #draw.text((pointer.x-24*3+1,pointer.y+55),s_QRK,self.black)
                    del(s_UWP)
                if system_present: # name
                    draw.text((pointer.x-(len(system_obj.name))*3+1,pointer.y-40),system_obj.name,self.black)

                if system_present: # COG
                    draw.text((pointer.x-4*3+1+self.hex_r//3*2-10,pointer.y-self.hex_R//3*2),system_obj.mainworld.getCOG()+"\n COG",self.black)
                if system_present: # PBJ
                    draw.text((pointer.x-4*3+1-self.hex_r//3*2+10,pointer.y-self.hex_R//3*2),system_obj.getPBJ()+"\nPBJ",self.black)
                if system_present: # WDITTP
                    draw.text((pointer.x-6*3+1,pointer.y+self.hex_R//3*2-5),system_obj.mainworld.getWDITTP()+"\nWDITTP",self.black)
                # add symbols
                offset=5
                symbols=0
                if system_present and system_obj.mainworld.travel_code=="a" and system_obj.mainworld.populated:
                    image1.paste(self.hazard_i_img,(pointer.x+self.hex_r-35,pointer.y-self.hex_R//2+offset+30*symbols),self.hazard_i_img)
                    symbols+=1
                if system_present and system_obj.mainworld.starport.lower() in ('b','a'):
                    image1.paste(self.fuels_p_i_img,(pointer.x+self.hex_r-35,pointer.y-self.hex_R//2+offset+30*symbols),self.fuels_p_i_img)
                    symbols+=1
                elif system_present and system_obj.mainworld.starport.lower() in ('d','c'):
                    image1.paste(self.fuels_i_img,(pointer.x+self.hex_r-35,pointer.y-self.hex_R//2+offset+30*symbols),self.fuels_i_img)
                    symbols+=1
                elif system_present and system_obj.jovian_planets>0:
                    image1.paste(self.jovian_i_img,(pointer.x+self.hex_r-35,pointer.y-self.hex_R//2+offset+30*symbols),self.jovian_i_img)
                    symbols+=1
                if system_present and system_obj.asteroid_belts>0 and system_obj.mainworld.size!=0:
                    image1.paste(self.aster_i_img,(pointer.x+self.hex_r-35,pointer.y-self.hex_R//2+offset+30*symbols),self.aster_i_img)
                    symbols+=1
                # draw grid
                for dotmap in whitegrid: self.drawpoly(draw,dotmap,    fill=None,outline=self.white)
                for dotmap in blackgrid: self.drawpoly(draw,hex.poly(),fill=None,outline=self.white)
                i+=1
        filename = name
        image1.save(path+filename,format="png")
        print(self.LOADED.format("{} drawn".format(name)),end="\r\n")
        pass
    def drawline(self,draw,line,fill=0,width=1):
        if fill==0: fill=self.black
        #print( "Drawing line from ({},{}) to ({},{})".format(line[0].x,line[0].y,line[1].x,line[1].y))
        draw.line([(line[0].x,line[0].y), (line[1].x,line[1].y)], fill=fill, width=width)
        pass
    def drawpoly(self,draw,poly,outline=None,fill=None):
        draw.polygon(poly,fill=fill,outline=outline)
        pass






if __name__=="__main__": main()