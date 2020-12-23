#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys      import argv
from platform import system

# in-file settings
if system().lower().startswith("win"):
    SLASH="\\"
else:
    SLASH="/"

path=argv[0][:argv[0].rfind(SLASH)+1]
path_up=path[ :path[:-1].rfind(SLASH)+1]
config_src  = "config"+SLASH+"inspect.ini"

try:
    from tools.db_parse                         import App as XML_Parse
    from plugins.SectorGen.tlrm2e.sectorgen     import Hexgrid as SectorGen
    path = argv[0][:argv[0].rfind(SLASH)+1]+"plugins"+SLASH+"SectorGen"+SLASH
except:
    try:
        from testing_tools.db_parse             import App as XML_Parse
        from sectorgen                              import Hexgrid as SectorGen
    except:
        from lib.tools.db_parse                 import App as XML_Parse
        from tlrm2e.sectorgen                   import Hexgrid as SectorGen




def main():
    # load app
    print("{:<32} [ .... ]".format("Loading inspector"),end="\r")
    inspector=App()
    print("{:<32} [ OKAY ]".format("Inspector loaded")          )
    # run app test
    print("{:<32} [ .... ]".format("Fetching data on hex "+inspector.testing_hex),end="\r")
    data=inspector.inspect()
    print("{:<32} [ OKAY ]".format("Fetch completed for hex "+inspector.testing_hex)      )
    print("Commencing dump:")
    print(data)
    input("Done.")
    exit(0)
    pass




class App:
    HEX_EXPANDED  =["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p"]
    TERSE    ='t'
    VERBOSE  ='v'
    MAINWORLD='mw'
    SYSTEM   ='sy'
    STAR     ='s'
    def __init__(self,src=None,mode=None,depth=None,config=config_src):
        # config BEGIN
        #   prep config
        from configparser import ConfigParser
        self.config = ConfigParser()
        #   find config
        try:
            with open(path+config) as f:
                self.config.read_file(f)
        except:
            with open(path_up+config) as f:
                self.config.read_file(f)
        #   load config
        #   [DEFAULT]
        if src  ==None: self.sector_src=self.config.get("DEFAULT","src"   ).strip().replace("/",SLASH)
        else:           self.sector_src=src
        if mode ==None: self.mode      =self.config.get("DEFAULT","mode"  ).strip()
        else:           self.mode      =mode
        if depth==None: self.depth     =self.config.get("DEFAULT","depth" ).strip()
        else:           self.depth     =depth
        uwp_path                       =self.config.get("DEFAULT","db_uwp").strip().replace("/",SLASH)
        esp_path                       =self.config.get("DEFAULT","db_esp").strip().replace("/",SLASH)
        #   [FORMATING]
        self.indent                    =int( self.config.get("FORMATING","indentation"  ).strip() )
        self.just_width                =int( self.config.get("FORMATING","maximum width").strip() )
        #   [TESTING]
        self.testing_hex               =self.config.get("TESTING","testing hex").strip()
        # config END

        # resources BEGIN
        #   load xml databases
        try:
            self.db_uwp=XML_Parse.load( path,uwp_path )
            self.db_esp=XML_Parse.load( path,esp_path )
        except:
            self.db_uwp=XML_Parse.load( path_up,uwp_path )
            self.db_esp=XML_Parse.load( path_up,esp_path )
        self.TRAVELLER=self.db_uwp[XML_Parse.TOP_LAYER]['traveller']
        #   load sector
        self.sectorGen=SectorGen(populated=False,db_uwp=self.db_uwp,db_esp=self.db_esp)
        
        try:
            self.sectorGen.import_sector(src=path   +self.sector_src)
        except:
            self.sectorGen.import_sector(src=path_up+self.sector_src)
        # resources END
        pass
    def inspect(self,hex="test",mode=None,depth=None):
        if hex =="test": hex  =self.testing_hex
        if mode ==None : mode =self.mode
        if depth==None : depth=self.depth
        # find target
        inspected_hex=None
        for grid_hex in self.sectorGen.main_index:
            if grid_hex.location_code==hex:
                inspected_hex=grid_hex
        if inspected_hex==None: raise Exception("could not find grid position '{}'".format(hex))
        if inspected_hex.system==None: return "Nothing but cold, unfeeling void."
        # begin inspection
        rs=None
        if   depth==self.MAINWORLD:
            rs=self.__inspect_world(inspected_hex.system.mainworld,mode)
        elif depth==self.SYSTEM   :
            rs=self.__inspect_system(inspected_hex.system,mode)
        return rs
    def __inspect_world(self,world,mode):
        rs=""
        if   mode==self.VERBOSE: para=2
        elif mode==self.TERSE:   para=1
        
        fj_Tvl=self.__get_fj_Tvl(world,mode)
        fj_SAH=self.__get_fj_SAH(world,mode)
        fj_COG=self.__get_fj_COG(world,mode)
        fj_PGL=self.__get_fj_PGL(world,mode)
        fj_ExL=self.__get_fj_ExL(world,mode)
        fj_ExT=self.__get_fj_ExT(world,mode)
        fj_Qrk=self.__get_fj_Qrk(world,mode)
        fj_TrC=self.__get_fj_TrC(world,mode)
        
        if mode==self.VERBOSE:
            pt1=fj_Tvl+"\n"*para+fj_SAH+"\n"*para+fj_COG
            pt2=fj_PGL+"\n"*para+fj_ExL+"\n"*para+fj_ExT
            pt3=fj_Qrk+"\n"*para+fj_TrC
            pt4=None
            pt5=None
            return (pt1,pt2,pt3,pt4,pt5)
        elif mode==self.TERSE:
            return (fj_Tvl+"\n"*para+fj_SAH+"\n"*para+fj_COG+"\n"*para+fj_PGL+"\n"*para+fj_ExL+"\n"*para+fj_ExT+"\n"*para+fj_Qrk+"\n"*para+fj_TrC,None)
    def __get_fj_Tvl(self,world,mode,indent=None,just_width=None):
        if indent    ==None: indent_n  =self.indent
        else:                indent_n  =     indent
        indent       = indent_n*" "
        if just_width==None: just_width=self.just_width

        starport     =  world.starport
        travel_code  =  world.travel_code
        
        block_indent=0
        line_up=0
        dSPT_push=0
        dTRC_push=0
        dSPT_formatted=("None")
        dTRC_formatted=("None")
        
        if mode==self.VERBOSE:
            block_indent=0
            line_up=14
            dTRC_push=16
            dSPT_push=16
            dTRC=(  indent+"Travel Code".ljust(line_up)+"  ({}) - {tcode_info}\n", "" )
            dSPT=(1*indent+"Starport".ljust(line_up-indent_n)+"    ({})\n"           ,\
                  2*indent+"Quality           - {quality}\n"                         ,\
                  2*indent+"Berthing Cost     - {berthing}\n"                        ,\
                  2*indent+"Fuel              - {fuel}\n"                            ,\
                  2*indent+"Facilities        - {facilities}"                         )
        elif mode==self.TERSE:
            block_indent=1
            line_up=14
            dSPT_push=line_up+6
            dTRC_push=line_up+6
            dTRC=(indent+"Travel Code".ljust(line_up)+"({}) - {tcode_info}\n", "" )
            dSPT=(indent+"Starport".ljust(line_up)+"({}) - {quality}", "" )

        # retrieve Starport Info
        quality,berthing,fuel,facilities="","","",""
        for dom_starport in self.TRAVELLER['starport']['starport']:
            if dom_starport[XML_Parse.ATTR_TAG]['level'].lower()==starport.lower():
                quality   =dom_starport['quality'   ][XML_Parse.CDATA]
                berthing  =dom_starport['berthing'  ][XML_Parse.CDATA]
                fuel      =dom_starport['fuel'      ][XML_Parse.CDATA]
                facilities=dom_starport['facilities'][XML_Parse.CDATA]
                break

        # retrieve Travel Code Info
        for dom_travel_code in self.TRAVELLER['travel_code']['travel_code']:
            if dom_travel_code[XML_Parse.ATTR_TAG]['code'].lower()==travel_code.lower():
                travel_code_s=dom_travel_code[XML_Parse.CDATA]
                break
        
        if mode==self.VERBOSE:
            dSPT_formatted=(dSPT[0].format(starport.upper())     ,\
                            dSPT[1].format(quality=quality)      ,\
                            dSPT[2].format(berthing=berthing)    ,\
                            dSPT[3].format(fuel=fuel)            ,\
                            dSPT[4].format(facilities=facilities) )
            dTRC_formatted=(dTRC[0].format(travel_code.upper(),tcode_info=travel_code_s),"" )
        elif mode==self.TERSE:
            dSPT_formatted=(dSPT[0].format(starport.upper(),quality=quality),"" )
            dTRC_formatted=(dTRC[0].format(travel_code.upper(),tcode_info=travel_code_s),"" )

        dSPT_formatted_justified=""
        for line in dSPT_formatted: dSPT_formatted_justified+=justificate(line,dSPT_push+indent_n*(block_indent+1),just_width)
        dTRC_formatted_justified=""
        for line in dTRC_formatted: dTRC_formatted_justified+=justificate(line,dTRC_push+indent_n*(block_indent+1),just_width)
        
        WN_bump=0
        if   mode==self.VERBOSE: WN_bump=5
        elif mode==self.TERSE  : WN_bump=3
        
        rs ="World Name".ljust(line_up)+indent+WN_bump*" "+" - "+world.name+"\n"
        rs+=dTRC_formatted_justified+dSPT_formatted_justified
        return rs
    def __get_fj_SAH(self,world,mode,indent=None,just_width=None):
        if indent    ==None: indent_n  =self.indent
        else:                indent_n  =     indent
        indent    =     indent_n*" "
        if just_width==None: just_width=self.just_width

        # get SAH Info
        size         =                   world.size_str
        atmosphere   = self.HEX_EXPANDED[world.atmosphere   ]
        hydrographics= self.HEX_EXPANDED[world.hydrographics]
        
        # establish Templates
        if mode==self.VERBOSE:
            block_indent=3
            dWPs_push=14+indent_n
            dWPa_push=14+indent_n
            dWPh_push=14+indent_n
            dWPs=(     1*indent+"Size            ({size})"          ,\
                  "\n"+2*indent+"Type              - {type}"        ,\
                  "\n"+2*indent+"Diameter          - {diameter}"     )    
            dWPa=("\n"+1*indent+"Atmosphere      ({atmosphere})"    ,\
                  "\n"+2*indent+"Type              - {type}"        ,\
                  "\n"+2*indent+"Pressure          - {pressure}"    ,\
                  "\n"+2*indent+"Description       - {desc}"         )
            dWPh=("\n"+1*indent+"Hydrographics   ({hydrographics})" ,\
                  "\n"+2*indent+"Type              - {type}"        ,\
                  "\n"+2*indent+"Surface Water     - {surfacewater}" )
        elif mode==self.TERSE:
            block_indent=1
            line_up=14
            dWPs_push=line_up+6
            dWPa_push=line_up+6
            dWPh_push=line_up+6
            dWPs=(     indent+"Size         ".ljust(line_up)+"({size}) - {diameter}","" )
            dWPa=("\n"+indent+"Atmosphere   ".ljust(line_up)+"({atmosphere}) - {type}","" )
            dWPh=("\n"+indent+"Hydrographics".ljust(line_up)+"({hydrographics}) - {surfacewater}","" )

        # retrieve verbose Info
        size_info=("","")
        for dom_size in self.TRAVELLER['size']['size']:
            if dom_size[XML_Parse.ATTR_TAG]['level'].lower()==size:
                size_info=(dom_size['type'][XML_Parse.CDATA],dom_size['diameter'][XML_Parse.CDATA])
                break
        atmosphere_info=("","","")
        for dom_atmosphere in self.TRAVELLER['atmosphere']['atmosphere']:
            if dom_atmosphere[XML_Parse.ATTR_TAG]['level'].lower()==atmosphere:
                atmosphere_info=(dom_atmosphere['type'][XML_Parse.CDATA],dom_atmosphere['pressure'][XML_Parse.CDATA],dom_atmosphere['desc'][XML_Parse.CDATA])
                break
        p1=world.comment.find("Atmo:\"")
        if world.atmosphere==15 and p1!=-1:
            p1+=6
            p2=p1+world.comment[p1:].find("\",")
            atmosphere_info[2]=world.comment[p1:p2]

        hydrographics_info=("","")
        for dom_hydrographics in self.TRAVELLER['hydrographics']['hydrographics']:
            if dom_hydrographics[XML_Parse.ATTR_TAG]['level'].lower()==hydrographics:
                hydrographics_info=(dom_hydrographics['type'][XML_Parse.CDATA],dom_hydrographics['surfacewater'][XML_Parse.CDATA])
                break
        
        dWPs_formatted=(None,None,None)
        dWPa_formatted=(None,None,None)
        dWPh_formatted=(None,None,None)
        # allocate Info to Templates
        if mode==self.VERBOSE:
            dWPs_formatted=(dWPs[0].format(size=size.upper()),dWPs[1].format(type=size_info[0]),dWPs[2].format(diameter=size_info[1]))
            dWPa_formatted=(dWPa[0].format(atmosphere=atmosphere.upper()),dWPa[1].format(type=atmosphere_info[0]),dWPa[2].format(pressure=atmosphere_info[1]),dWPa[3].format(desc=atmosphere_info[2]))
            dWPh_formatted=(dWPh[0].format(hydrographics=hydrographics.upper()),dWPh[1].format(type=hydrographics_info[0]),dWPh[2].format(surfacewater=hydrographics_info[1]))
        elif mode==self.TERSE:
            dWPs_formatted=(dWPs[0].format(size=size.upper(),diameter=size_info[1]))
            dWPa_formatted=(dWPa[0].format(atmosphere=atmosphere.upper(),type=atmosphere_info[0]))
            dWPh_formatted=(dWPh[0].format(hydrographics=hydrographics.upper(),surfacewater=hydrographics_info[1]))

        # justificate Info
        dWPs_formatted_justified=""
        for line in dWPs_formatted: dWPs_formatted_justified+=justificate(line,dWPs_push+indent_n*(block_indent+1),just_width)
        dWPa_formatted_justified=""
        for line in dWPa_formatted: dWPa_formatted_justified+=justificate(line,dWPa_push+indent_n*(block_indent+1),just_width)
        dWPh_formatted_justified=""
        for line in dWPh_formatted: dWPh_formatted_justified+=justificate(line,dWPh_push+indent_n*(block_indent+1),just_width)

        rs=dWPs_formatted_justified+dWPa_formatted_justified+dWPh_formatted_justified
        return rs
    def __get_fj_COG(self,world,mode,indent=None,just_width=None):
        if indent    ==None: indent_n  =self.indent
        else:                indent_n  =     indent
        indent    =     indent_n*" "
        if just_width==None: just_width=self.just_width

        climate      =  world.climate
        orbit        =  world.orbit
        band         =  world.band
        gravity      =  world.gravity
        
        climate_type=""
        climate_temp=""
        climate_desc=""
        # retrieve Climate Info
        for dom_climate in self.TRAVELLER['climate']['climate']:
            digit_check,check_list_gt_lt=splitup(dom_climate[XML_Parse.ATTR_TAG]['level'],giveTup=True)
            go=False
            #print(climate,digit_check,check_list_gt_lt)
            if str(climate) in digit_check: go=True
            for check_tup in check_list_gt_lt:
                if climate >= int(check_tup[0]) and climate <= int(check_tup[1]): go=True
            if go:
                climate_type=dom_climate['type'       ][XML_Parse.CDATA]
                climate_temp=dom_climate['temperature'][XML_Parse.CDATA]
                climate_desc=dom_climate['desc'       ][XML_Parse.CDATA]
                break
        # retrieve Orbit Info
        #for dom_orbit in self.TRAVELLER['orbit']['orbit']:
        #    digit_check,check_list_gt_lt=splitup(dom_orbit[XML_Parse.ATTR_TAG]['level'],giveTup=True)
        #    go=False
        #    if str(orbit) in digit_check: go=True
        #    for check_tup in check_list_gt_lt:
        #        if int(orbit)>= int(check_tup[0]) and int(orbit)<= int(check_tup[1]): go=True
        #    if go:
        #        orbit_s=dom_orbit[XML_Parse.CDATA]
        #        break
        if   band.startswith("near" ): orbit_s="Inner World"
        elif band.startswith("mid"  ): orbit_s="Median World"
        elif band.startswith("far"  ): orbit_s="Far World"
        elif band.startswith("rogue"): orbit_s="Rogue World"
        else:                          orbit_s=""
        if orbit >= world.parent.star.HabInner/world.parent.star.AU*100 and orbit <= world.parent.star.HabOuter/world.parent.star.AU*100:
            orbit_s+= " \\ Habitable Zone"
        # retrieve Gravity Info
        for dom_gravity in self.TRAVELLER['gravity']['gravity']:
            digit_check,check_list_gt_lt=splitup(dom_gravity[XML_Parse.ATTR_TAG]['level'],giveTup=True)
            go=False
            if str(gravity) in digit_check: go=True
            for check_tup in check_list_gt_lt:
                if int(gravity)>= int(check_tup[0]) and int(gravity)<= int(check_tup[1]): go=True
            if go:
                gravity_s=dom_gravity[XML_Parse.CDATA]
                break

        # format InfoHydrographics
        if mode==self.VERBOSE:
            block_indent=3
            s_COGc_push=14+indent_n
            s_COGo_push=14+indent_n
            s_COGg_push=14+indent_n
            s_COGc=(1*indent+"Climate      "+indent+" ({})\n",\
                    2*indent+"Type         "+indent+"   - {type}\n",\
                    2*indent+"Temperature  "+indent+"   - {temp}\n",\
                    2*indent+"Description  "+indent+"   - {desc}\n" )
            t_COGo=indent+indent+"Orbit    "+indent+"   ({}) - ~{} %AU to Star, {}\n"
            t_COGg=indent+indent+"Gravity  "+indent+"   ({}) - {}\n"
        elif mode==self.TERSE:
            block_indent=1
            line_up=14
            s_COGc_push=line_up+6
            s_COGo_push=line_up+6
            s_COGg_push=line_up+6
            s_COGc=(indent+"Climate".ljust(line_up)+"({}) - {temp}\n", "" )
            t_COGo= indent+"Orbit  ".ljust(line_up)+"({}) - ~{} %AU to Star\n"
            t_COGg= indent+"Gravity".ljust(line_up)+"({}) - {}"

        if mode==self.VERBOSE:
            s_COGc_formatted=(s_COGc[0].format(climate),s_COGc[1].format(type=climate_type),s_COGc[2].format(temp=climate_temp),s_COGc[3].format(desc=climate_desc))
        elif mode==self.TERSE:
            s_COGc_formatted=(s_COGc[0].format(climate,temp=climate_temp),"")

        s_COGc_formatted_justified=""
        for line in s_COGc_formatted: s_COGc_formatted_justified+=justificate(line,s_COGc_push+indent_n*(block_indent+1),just_width)

        s_COGo_formatted          =t_COGo.format(world.band[:1].upper(),orbit,orbit_s)
        s_COGo_formatted_justified=justificate(s_COGo_formatted,s_COGo_push+indent_n*(block_indent+1),just_width)

        s_COGg_formatted          =t_COGg.format(self.HEX_EXPANDED[gravity].upper(),gravity_s)
        s_COGg_formatted_justified=justificate(s_COGg_formatted,s_COGg_push+indent_n*(block_indent+1),just_width)

        # return result
        rs=s_COGc_formatted_justified+s_COGo_formatted_justified+s_COGg_formatted_justified
        return rs
    def __get_fj_PGL(self,world,mode,indent=None,just_width=None):
        if indent    ==None: indent_n  =self.indent
        else:                indent_n  =     indent
        indent    =     indent_n*" "
        if just_width==None: just_width=self.just_width

        # get PG(L) Info
        population   = self.HEX_EXPANDED[world.population   ]
        government   = self.HEX_EXPANDED[world.government   ]

        # establish Templates
        if mode==self.VERBOSE:
            block_indent=4
            dWPg_push=14
            dWPp= indent+"Population "+indent+"   ({}) - ~{mod} {type}\n"
            dWPg=(indent+"Government "+indent+"   ({})\n",\
                  indent+indent+"Type              - {type}\n",\
                  indent+indent+"Description       - {desc}\n",\
                  indent+indent+"Example           - {example}")
        elif mode==self.TERSE:
            block_indent=1
            line_up=14
            dWPg_push=line_up+6
            dWPp= indent+"Population".ljust(line_up)+"({}) - ~{mod} {type}\n"
            dWPg=(indent+"Government".ljust(line_up)+"({}) - {type}","")


        # retrieve verbose data
        population_info=("","","")
        for dom_population in self.TRAVELLER['population']['population']:
            if dom_population[XML_Parse.ATTR_TAG]['level'].lower()==population.lower():
                population_info=(dom_population['type'][XML_Parse.CDATA],dom_population['desc'][XML_Parse.CDATA],dom_population['magnitude'][XML_Parse.CDATA])
                break
        government_info=("","","")
        for dom_government in self.TRAVELLER['government']['government']:
            if dom_government[XML_Parse.ATTR_TAG]['level'].lower()==government.lower():
                government_info=(dom_government['type'][XML_Parse.CDATA],dom_government['desc'][XML_Parse.CDATA],dom_government['examples'][XML_Parse.CDATA])
                break

        # format Templates
        population_mod=world.parent.population_mod
        ##adjust for pop=1
        if population=='1': population_mod=population_mod*10
        dWPp_formatted_justified=dWPp.format(population.upper(), mod=population_mod,type=population_info[0])

        if mode==self.VERBOSE:
            dWPg_formatted=(dWPg[0].format(government.upper()),dWPg[1].format(type=government_info[0]),dWPg[2].format(desc=government_info[1]),dWPg[3].format(example=government_info[2]))
        elif mode==self.TERSE:
            dWPg_formatted=(dWPg[0].format(government.upper(),type=government_info[0]),"")


        dWPg_formatted_justified=""
        for line in dWPg_formatted: dWPg_formatted_justified+=justificate(line,dWPg_push+indent_n*(block_indent+1),just_width)

        # return result
        rs=dWPp_formatted_justified+dWPg_formatted_justified
        return rs
    def __get_fj_ExL(self,world,mode,indent=None,just_width=None):
        if indent    ==None: indent_n  =self.indent
        else:                indent_n  =     indent
        indent    =     indent_n*" "
        if just_width==None: just_width=self.just_width

        if mode==self.VERBOSE:
            block_indent=4
            dWDITTP_push=14
            dWDITTP=(1*indent+"Law Levels      ({})\n",\
                     2*indent+"Weapons       ({}) - {weapons}\n",\
                     2*indent+"Drugs         ({}) - {drugs}\n",\
                     2*indent+"Information   ({}) - {information}\n",\
                     2*indent+"Technology    ({}) - {technology}\n",\
                     2*indent+"Travellers    ({}) - {travellers}\n",\
                     2*indent+"Powers        ({}) - {powers}")

            weapons,drugs,information,technology,travellers,powers=None,None,None,None,None,None
            weapons_i    =world.law_level_weapons
            drugs_i      =world.law_level_drugs
            information_i=world.law_level_information
            technology_i =world.law_level_technology
            travellers_i =world.law_level_travellers
            powers_i     =world.law_level_powers

            for dom_law_level in self.TRAVELLER['lawlevels']['level']:
                digit_check,check_list_gt_lt=splitup(dom_law_level[XML_Parse.ATTR_TAG]['level'],giveTup=True)
                go=[]
                if str(weapons_i) in digit_check: go+=['weapons']
                for check_tup in check_list_gt_lt:
                    if int(weapons_i)>= int(check_tup[0]) and int(weapons_i)<= int(check_tup[1]): go+=['weapons']
                if str(drugs_i) in digit_check: go+=['drugs']
                for check_tup in check_list_gt_lt:
                    if int(drugs_i)>= int(check_tup[0]) and int(drugs_i)<= int(check_tup[1]): go+=['drugs']
                if str(information_i) in digit_check: go+=['information']
                for check_tup in check_list_gt_lt:
                    if int(information_i)>= int(check_tup[0]) and int(information_i)<= int(check_tup[1]): go+=['information']
                if str(technology_i) in digit_check: go+=['technology']
                for check_tup in check_list_gt_lt:
                    if int(technology_i)>= int(check_tup[0]) and int(technology_i)<= int(check_tup[1]): go+=['technology']
                if str(travellers_i) in digit_check: go+=['travellers']
                for check_tup in check_list_gt_lt:
                    if int(travellers_i)>= int(check_tup[0]) and int(travellers_i)<= int(check_tup[1]): go+=['travellers']
                if str(powers_i) in digit_check: go+=['powers']
                for check_tup in check_list_gt_lt:
                    if powers_i>= int(check_tup[0]) and powers_i<= int(check_tup[1]): go+=['powers']

                if "weapons"     in go :
                    weapons      =dom_law_level['weapons'    ][XML_Parse.CDATA]
                if "drugs"       in go :
                    drugs        =dom_law_level['drugs'      ][XML_Parse.CDATA]
                if "information" in go :
                    information  =dom_law_level['information'][XML_Parse.CDATA]
                if "technology"  in go :
                    technology   =dom_law_level['technology' ][XML_Parse.CDATA]
                if "travellers"  in go :
                    travellers   =dom_law_level['travellers' ][XML_Parse.CDATA]
                if "powers"      in go :
                    powers       =dom_law_level['powers'     ][XML_Parse.CDATA]

            dWDITTP_formatted=(dWDITTP[0].format(self.HEX_EXPANDED[world.law_level].upper()),
                               dWDITTP[1].format(self.HEX_EXPANDED[weapons_i    ].upper(),weapons=weapons),
                               dWDITTP[2].format(self.HEX_EXPANDED[drugs_i      ].upper(),drugs=drugs),
                               dWDITTP[3].format(self.HEX_EXPANDED[information_i].upper(),information=information),
                               dWDITTP[4].format(self.HEX_EXPANDED[technology_i ].upper(),technology=technology),
                               dWDITTP[5].format(self.HEX_EXPANDED[travellers_i ].upper(),travellers=travellers),
                               dWDITTP[6].format(self.HEX_EXPANDED[powers_i     ].upper(),powers=powers))
            dWDITTP_formatted_justified=""
            for line in dWDITTP_formatted: dWDITTP_formatted_justified+=justificate(line,dWDITTP_push+indent_n*(block_indent+1),just_width)

            rs=dWDITTP_formatted_justified
        elif mode==self.TERSE:
            law_level    = world.law_level
            block_indent=1
            line_up=14
            dLLg_push=line_up+6
            dLLg=indent+"Law Level".ljust(line_up)+"({}) - {general}"
            
            general=""
            for dom_law_level in self.TRAVELLER['lawlevels']['level']:
                digit_check,check_list_gt_lt=splitup(dom_law_level[XML_Parse.ATTR_TAG]['level'],giveTup=True)
                go=[]
                if str(law_level) in digit_check: go+=['general']
                for check_tup in check_list_gt_lt:
                    if int(law_level)>= int(check_tup[0]) and int(law_level)<= int(check_tup[1]): go+=['general']
                if "general" in go    :
                  general     =dom_law_level['general'][XML_Parse.CDATA]
            
            dLLg_formatted=( dLLg.format(self.HEX_EXPANDED[law_level].upper(),general=general), "" )

            dLLg_formatted_justified=""
            for line in dLLg_formatted: dLLg_formatted_justified+=justificate(line,dLLg_push+indent_n*block_indent,just_width)
            rs=dLLg_formatted_justified
        return rs
    def __get_fj_ExT(self,world,mode,indent=None,just_width=None):
        if indent    ==None: indent_n  =self.indent
        else:                indent_n  =     indent
        indent    =     indent_n*" "
        if just_width==None: just_width=self.just_width

        if mode==self.VERBOSE:
            block_indent=2
            dTLc_push=16
            dTLt_push=8
            dTLm_push=19
            dTLc=(     2*indent+"Civilian\n",\
                       3*indent+"Energy        - {energy}\n",\
                       3*indent+"Computing     - {computing}\n",\
                       3*indent+"Communication - {communication}\n",\
                       3*indent+"Medicine      - {medicine}\n",\
                       3*indent+"Environment   - {environment}")
            dTLt=("\n"+2*indent+"Transportation\n",\
                       3*indent+"Land  - {land}\n",\
                       3*indent+"Water - {water}\n",\
                       3*indent+"Air   - {air}\n",\
                       3*indent+"Space - {space}")
            dTLm=("\n"+2*indent+"Military\n",\
                       3*indent+"Personal Weapons - {personalweapons}\n",\
                       3*indent+"Personal Armour  - {personalarmour}\n",\
                       3*indent+"Heavy Weapons    - {heavyweapons}\n",\
                       3*indent+"Heavy Armour     - {heavyarmour}")
                       
            energy,computing,communication,medicine,environment="","","","",""
            land,water,air,space="","","",""
            personalweapons,personalarmour,heavyweapons,heavyarmour="","","",""
            for tl in self.TRAVELLER['techlevels']['level']:
                # civilian
                if int(tl[XML_Parse.ATTR_TAG]['level'])==world.tech_level_civilian_energy: energy =tl['general']['energy' ][XML_Parse.CDATA]
                if int(tl[XML_Parse.ATTR_TAG]['level'])==world.tech_level_civilian_computing: computing =tl['general']['computing' ][XML_Parse.CDATA]
                if int(tl[XML_Parse.ATTR_TAG]['level'])==world.tech_level_civilian_communication: communication=tl['general']['communication'][XML_Parse.CDATA]
                if int(tl[XML_Parse.ATTR_TAG]['level'])==world.tech_level_civilian_medicine: medicine =tl['general']['medicine' ][XML_Parse.CDATA]
                if int(tl[XML_Parse.ATTR_TAG]['level'])==world.tech_level_civilian_environment: environment =tl['general']['environment' ][XML_Parse.CDATA]
                # transport
                if int(tl[XML_Parse.ATTR_TAG]['level'])==world.tech_level_transportation_land: land =tl['transport']['land' ][XML_Parse.CDATA]
                if int(tl[XML_Parse.ATTR_TAG]['level'])==world.tech_level_transportation_water: water=tl['transport']['water'][XML_Parse.CDATA]
                if int(tl[XML_Parse.ATTR_TAG]['level'])==world.tech_level_transportation_air: air =tl['transport']['air' ][XML_Parse.CDATA]
                if int(tl[XML_Parse.ATTR_TAG]['level'])== world.tech_level_transportation_space: space=tl['transport']['space'][XML_Parse.CDATA]
                # military
                if int(tl[XML_Parse.ATTR_TAG]['level'])==world.tech_level_military_personalweapons: personalweapons=tl['military']['personalweapons'][XML_Parse.CDATA]
                if int(tl[XML_Parse.ATTR_TAG]['level'])==world.tech_level_military_personalarmour: personalarmour =tl['military']['personalarmour' ][XML_Parse.CDATA]
                if int(tl[XML_Parse.ATTR_TAG]['level'])==world.tech_level_military_heavyweapons: heavyweapons =tl['military']['heavyweapons' ][XML_Parse.CDATA]
                if int(tl[XML_Parse.ATTR_TAG]['level'])==world.tech_level_military_heavyarmour: heavyarmour =tl['military']['heavyarmour' ][XML_Parse.CDATA]

            dTLc_formatted=(dTLc[0],dTLc[1].format(energy=energy),dTLc[2].format(computing=computing),dTLc[3].format(communication=communication),dTLc[4].format(medicine=medicine),dTLc[5].format(environment=environment))
            dTLc_formatted_justified=""
            for line in dTLc_formatted: dTLc_formatted_justified+=justificate(line,dTLc_push+indent_n*(block_indent+1),just_width)

            dTLt_formatted=(dTLt[0],dTLt[1].format(land=land),dTLt[2].format(water=water),dTLt[3].format(air=air),dTLt[4].format(space=space))
            dTLt_formatted_justified=""
            for line in dTLt_formatted: dTLt_formatted_justified+=justificate(line,dTLt_push+indent_n*(block_indent+1),just_width)

            dTLm_formatted=(dTLm[0],dTLm[1].format(personalweapons=personalweapons),dTLm[2].format(personalarmour=personalarmour),dTLm[3].format(heavyweapons=heavyweapons),dTLm[4].format(heavyarmour=heavyarmour))
            dTLm_formatted_justified=""
            for line in dTLm_formatted: dTLm_formatted_justified+=justificate(line,dTLm_push+indent_n*(block_indent+1),just_width)
            
            rs=indent+"Tech Levels\n"+dTLc_formatted_justified+dTLt_formatted_justified+dTLm_formatted_justified
        elif mode==self.TERSE:
            tech_level   = world.tech_level
            block_indent=1
            line_up=14
            dTLg_push=line_up+6
            dTLg=indent+"Tech Level".ljust(line_up)+"({}) - {general}"
            
            for tl in self.TRAVELLER['techlevels']['level']:
                # civilian
                if int(tl[XML_Parse.ATTR_TAG]['level'])==tech_level: general=tl['general']['general'][XML_Parse.CDATA]
            
            dTLg_formatted=( dTLg.format(self.HEX_EXPANDED[tech_level].upper(),general=general), "" )

            dTLg_formatted_justified=""
            for line in dTLg_formatted: dTLg_formatted_justified+=justificate(line,dTLg_push+indent_n*block_indent,just_width)
            rs=dTLg_formatted_justified
        return rs
    def __get_fj_Qrk(self,world,mode,indent=None,just_width=None):
        if indent    ==None: indent_n  =self.indent
        else:                indent_n  =     indent
        indent    =     indent_n*" "
        if just_width==None: just_width=self.just_width
        
        quirk=world.quirk
        quirk_name,quirk_desc="",""
        for dom_quirk in self.TRAVELLER['culture']['quirk']:
            if quirk=="   ": break
            if dom_quirk[XML_Parse.ATTR_TAG]['index'].lower()==quirk.lower():
                quirk_name=dom_quirk[XML_Parse.ATTR_TAG]['name']
                quirk_desc=dom_quirk[XML_Parse.CDATA]
                break
        
        if mode==self.VERBOSE:
            block_indent=2
            dQRK_push=0
            if quirk != "   ":
                dQRK=(indent+indent+"{name}\n"     ,\
                      indent+indent+indent+"{desc}" )
                dQRK_formatted=(dQRK[0].format(name=quirk_name),\
                                dQRK[1].format(desc=quirk_desc) )
            else:
                dQRK_formatted=(" "*indent_n*block_indent+"None")
            dQRK_formatted_justified=""
            for line in dQRK_formatted: dQRK_formatted_justified+=justificate(line,dQRK_push+indent_n*(block_indent+1),just_width)
            rs=indent+"Quirks\n"+dQRK_formatted_justified
        elif mode==self.TERSE:
            block_indent=1
            line_up=14
            dQRK_push=0
            if quirk != "   ":
                dQRK=(indent*block_indent+"Quirk".ljust(line_up)+"    - {name}", "" )
                dQRK_formatted=(dQRK[0].format(name=quirk_name), "" )
            else:
                dQRK_formatted=(indent*block_indent+"Quirk".ljust(line_up)+"    - None")
            dQRK_formatted_justified=""
            for line in dQRK_formatted: dQRK_formatted_justified+=justificate(line,dQRK_push+indent_n*(block_indent+1),just_width)
            rs=dQRK_formatted_justified
        return rs
    def __get_fj_TrC(self,world,mode,indent=None,just_width=None):
        if indent    ==None: indent_n  =self.indent
        else:                indent_n  =     indent
        indent    =     indent_n*" "
        if just_width==None: just_width=self.just_width
        
        
        
        if mode==self.VERBOSE:
            block_indent=2
            dTCD_push=1
            l_TCD=world.trade_codes.strip().split(" ")
            class TradeCode:
                def __init__(this,tag,name,desc):
                    this.tag=tag
                    this.name=name
                    this.desc=desc
            dTCD=[]
            for dom_tradecode in self.TRAVELLER['tradecodes']['tradecode']:
                for t_code in l_TCD:
                    if t_code.lower()==dom_tradecode[XML_Parse.ATTR_TAG]['tag'].lower():
                        t_code_obj=TradeCode(dom_tradecode[XML_Parse.ATTR_TAG]['tag'] ,\
                                             dom_tradecode[XML_Parse.ATTR_TAG]['name'],\
                                             dom_tradecode['desc'][XML_Parse.CDATA]    )
                        dTCD.append(t_code_obj)
            if len(dTCD)==0: dTCD=["None"]
            
            dTCD_template=indent+indent+"{name} ({tag})\n"+indent+indent+indent+"{desc}"
            dTCD_formatted=[]
            for t_code_obj in dTCD:
                dTCD_formatted.append(dTCD_template.format(name=t_code_obj.name,tag=t_code_obj.tag,desc=t_code_obj.desc)+"\n")
            dTCD_formatted_justified=""
            for line in dTCD_formatted: dTCD_formatted_justified+=justificate(line,dTCD_push+indent_n*(block_indent+1),just_width)
            rs=indent+"Trade Codes\n"+dTCD_formatted_justified[:-1]
        elif mode==self.TERSE:
            block_indent=1
            line_up=14
            rs=indent*block_indent+"Trade Codes".ljust(line_up)+"    - "+world.trade_codes.strip()
        return rs
    def __inspect_system(self,system,mode):
        rs = ""
        rs+= system.star.show()
        return (rs,None)


def findPosInList(list,item):
    try:
        rc = [i for i,x in enumerate(list) if x == item]
        if rc==[]: raise Exception
        return rc
    except: return [-1]


def justificate(line,indent,border):
    rs=""
    if len(line) < border: return line
    else:
        p1=line[:border].rfind(" ")+1
        rs+=line[:p1]
        rs+="\n"+justificate(indent*" "+line[p1:].strip(" "),indent,border)
        return rs


def splitup( string, giveTup=False ): # check with "0"
    if string == None: return []
    if giveTup: sx=[]
    if ',' in string:
        sl = string.split(',')
    else:
        sl = [string]
    for s in sl:
        try:
            if '-' in s:
                sl.remove(s)
                s = s.split('-')
                if not giveTup:
                    s = range( int(s[0]), int(s[1])+1 )
                    sl += s
                sx.append((int(s[0]),int(s[1])))
        except:
            pass
    if not giveTup:
        for s in sl:
            try:
                sl.remove(s)
                sl.append( int(s) )
            except:
                pass
    if not giveTup: return  sl
    else:           return (sl,sx)


if __name__=="__main__": main()