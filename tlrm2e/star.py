import random
from math import sqrt
#

#

def main():
    star = App()
    star.new()
    star.name("Testor")
    star.show()
    pass

class App:
    # xml handling
    XML_TOP_LAYER   = '#document'
    XML_ATTR_TAG    = '#attributes'
    XML_CDATA       = '#cdata'
    VN='vn'
    SO='so'
    HS='hs'
    BA='ba'
    def __init__(self,db_esp=None):
        self.db_esp=db_esp
        if db_esp==None and __name__=="__main__":
            from sys import argv
            from testing_tools.db_parse import App as XML_Parse
            path=argv[0][:argv[0].rfind("\\")]
            path=path[:path.rfind("\\")+1]
            self.db_esp=XML_Parse.load(path,"lib\\xml\\esp_information.xml")
        self.AU    = float( self.db_esp[self.XML_TOP_LAYER]['traveller']['reference']['astronomical_unit'][self.XML_CDATA] )
        self.SOL_L = float( self.db_esp[self.XML_TOP_LAYER]['traveller']['reference']['sol_luminosity'   ][self.XML_CDATA] )
        self.SOL_K =   int( self.db_esp[self.XML_TOP_LAYER]['traveller']['reference']['sol_temperature'  ][self.XML_CDATA] )
        self.SOL_d =   int( self.db_esp[self.XML_TOP_LAYER]['traveller']['reference']['sol_diameter'     ][self.XML_CDATA] )
        self.Name        = ''
        self.Class       = ''
        self.Color       = ''
        self.Diameter    = 0     # Km
        self.Luminosity  = 0     # L
        self.Temperature = 0     # K
        self.HabOuter    = 0     # Km
        self.HabCenter   = 0     # Km
        self.HabInner    = 0     # Km
        self.DiamZone70  = 0     # Km
        self.DiamZone100 = 0     # Km
        self.DiamZone150 = 0     # Km
        self.Planetoids  = 0     # num
        self.Planets     = []
        self.comment     = "---"
        pass
    def toPAU( self, km ):
        rc  = int( km / self.AU * 100 )
        return rc

    def new( self,mode=None, load=None ):
        def getType(type=None):
            if type==None:
                r   = roll(2)
                rc  = ''

                if   r  ==  2:
                    rx  = roll(1)
                    if rx   >=  5:          rc += 'O'
                    else:                   rc += 'B'
                elif r  ==  3:              rc += 'A'
                elif r  ==  5:              rc += 'F'
                elif r  >=  6 and r  <=  7: rc += 'G'
                elif r  >=  8 and r  <=  9: rc += 'K'
                elif r  >= 10 and r  <= 12: rc += 'M'
            else:
                rc = type

            for cl in self.db_esp[self.XML_TOP_LAYER]['traveller']['stars']['class']:
                if cl[self.XML_ATTR_TAG]['name'] == rc:
                    rd = {'class'   :        cl[self.XML_ATTR_TAG]['name']                  ,\
                          'color'   :        cl['color'                  ][self.XML_CDATA]  ,\
                          'L'       : float( cl['luminosity'             ][self.XML_CDATA] ),\
                          'K'       : float( cl['temperature_multiplier' ][self.XML_CDATA] ),\
                          'K-base'  :   int( cl['temperature_base'       ][self.XML_CDATA] ),\
                          'K-range' :   int( cl['temperature_range'      ][self.XML_CDATA] ),\
                          'd-mult'  : float( cl['diam_multiplier'        ][self.XML_CDATA] ),\
                          'desc'    :        cl['description'            ][self.XML_CDATA]   \
                          }
                    return rd
            return getType()
        if load!=None:
            usp=load
            # PARSE
            p1=8
            p2=usp.find("|n|")+3
            p3=p2+usp[p2:].find("|n|")
            p4=usp.find("|c|")+3
            p5=p4+usp[p4:].find("|c|")
            star_code   =usp[p1:p1+3].strip()
            star_name   =usp[p2:p3]
            star_comment=usp[p4:p5]
            # APPLY
            self.name(star_name)
            self.comment        = star_comment
            self.Class          = star_code
            type                = getType( self.Class[0:1] )
        else:
            type                = getType()
        def getClass():
              rc = type['class'] + str( roll(1,10) - 1 ) + 'V'
              return rc
        def getLum():
            r   = roll(2)

            if   r  ==  2:              rv  = 2.0
            elif r  >=  3 and r  <=  5: rv  = 1.5
            elif r  >=  6 and r  <=  8: rv  = 1.0
            elif r  >=  9 and r  <= 11: rv  = 0.8
            elif r  == 12:              rv  = 0.6

            rc  = int( 100 * type['L'] * rv ) / 100
            return rc
        def getTemp():
            rc = int( 100 * type['K-base'] + round( type['K-range'] / 9 * ( 10 - int( self.Class[1:2] ) ), -1 ) ) / 100
            return rc
        def getDiam():
            rc = type['d-mult'] * self.SOL_d
            return rc
        def getHabZone():
            rc = round( self.AU * 1.34 * sqrt( self.Luminosity * self.Temperature / self.SOL_K ), 5 )
            rOuter  = rc
            rCenter = rc * 0.745
            rInner  = rc * 0.38
            return rOuter, rCenter, rInner
        def getPtoids():
            rc  = roll(4)-3
            if rc < 0: rc = 0
            return rc

        # carry together
        if load==None: self.Class          = getClass()
        self.Color          = type['color']
        self.Luminosity     = getLum()
        self.Temperature    = getTemp()
        self.Diameter       = getDiam()
        self.DiamZone70     = self.Diameter *  70
        self.DiamZone100    = self.Diameter * 100
        self.DiamZone150    = self.Diameter * 150
        self.HabOuter, self.HabCenter, self.HabInner = getHabZone()
        if load==None: self.Planetoids     = getPtoids()

        i   = 0
        while i < self.Planetoids:
            def getPlanet(mode):
                near  = False
                mid   = False
                far   = False
                rogue = False
                rc    = 0
                ty    = ''
                rge   = ''
                r     = roll(3)
                
                if mode in (None,self.VN,self.SO,self.HS):
                    if    r  >= 15: rogue = True
                    elif  r  >= 10: mid   = True
                    elif  r  >=  6: far   = True
                    elif  r  >=  3: near  = True
                elif mode in (self.BA):
                    if    r  >= 13: rogue = True
                    elif  r  >= 12: mid   = True
                    elif  r  >=  7: far   = True
                    elif  r  >=  4: near  = True

                r    = roll(1)
                if near:
                    rge="Near"
                    rc  =  10 + roll(1, 55)
                    if r  <=  6: ty   = 'Terrestrial'
                elif mid:
                    rge="Mid"
                    rc  =  65 + roll(1, 65)
                    if   r  <=  5: ty   = 'Terrestrial'
                    elif r  <=  6: ty   = 'Jovian'
                elif far:
                    rge="Far"
                    rc  = 140 + roll(1,1640)
                    if   r  <=  2: ty   = 'Terrestrial'
                    elif r  <=  6: ty   = 'Jovian'
                elif rogue:
                    rge="Rogue"
                    rc  =2000 + roll(1,3000)
                    if   r  <=  6: ty   = 'Terrestrial'
                    #elif r  <=  6: ty   = 'Jovian'
                return int(rc * type['d-mult']), ty, rge
            l,ty,rge = getPlanet(mode)
            self.Planets.append( [l,ty,rge] )
            i  += 1
        pass

    def name( self, name ):
        self.Name = name
        pass

    #def load( self, usp ):
    #    # PARSE
    #    p1=8
    #    p2=usp.find("|n|")+3
    #    p3=usp[p2].find("|n|")
    #    p4=usp.find("|c|")+3
    #    p5=usp[p2].find("|c|")
    #    star_code   =usp[p1:p2-3].strip()
    #    star_name   =usp[p2:p3]
    #    star_comment=usp[p4:p5]
    #    # APPLY
    #    self.Name           =star_name
    #    self.comment        =star_comment
    #    self.Class          = star_code
    #    # RE-GENERATE
    #    type                = self.getType(self.Class[0:1])
    #    self.Color          = type['color']
    #    self.Luminosity     = self.getLum()
    #    self.Temperature    = self.getTemp()
    #    self.Diameter       = self.getDiam()
    #    self.DiamZone100    = self.Diameter * 100
    #    self.DiamZone150    = self.Diameter * 150
    #    self.HabOuter, self.HabCenter, self.HabInner = getHabZone()
    #    pass
    #
    def show( self, src=None ):
        justification_l=16
        justification_r=12
        star    = ''
        star += 'Name:'             .ljust(justification_l) + self.Name                              + '\n'
        star += 'Class:'            .ljust(justification_l) + self.Class                             + '\n'
        star += 'Color:'            .ljust(justification_l) + self.Color                             + '\n'
        star += 'Temperature:'      .ljust(justification_l) + str( self.Temperature )                .rjust(justification_r) + ' K' + '\n'
        star += 'Luminosity:'       .ljust(justification_l) + str( self.Luminosity  )                .rjust(justification_r) + ' L' + '\n'
        star += 'Diameter:'         .ljust(justification_l) + str( int(self.Diameter)    )                .rjust(justification_r) + ' Km'+ '\n'
        star += 'HabZone Inner:'    .ljust(justification_l) + str( self.toPAU(self.HabInner ) )      .rjust(justification_r) + ' %AU'+ '\n'
        star += 'HabZone Center:'   .ljust(justification_l) + str( self.toPAU(self.HabCenter) )      .rjust(justification_r) + ' %AU'+ '\n'
        star += 'HabZone Outer:'    .ljust(justification_l) + str( self.toPAU(self.HabOuter ) )      .rjust(justification_r) + ' %AU'+ '\n'
        star += ' 70 Diameters:'    .ljust(justification_l) + str( self.toPAU(self.DiamZone70  ) )   .rjust(justification_r) + ' %AU'+ '\n'
        star += '100 Diameters:'    .ljust(justification_l) + str( self.toPAU(self.DiamZone100 ) )   .rjust(justification_r) + ' %AU'+ '\n'
        star += '150 Diameters:'    .ljust(justification_l) + str( self.toPAU(self.DiamZone150 ) )   .rjust(justification_r) + ' %AU'+ '\n'
        if self.Planetoids>0:
            star += 'Planetoids:'       .ljust(justification_l) + str( self.Planetoids )                 .rjust( 2)         + '\n'
            for planet in sorted(self.Planets):
                star += '        ' + str(planet[0]).rjust(6) + ' ' + planet[1].rjust(justification_r) + '  ' + planet[2].ljust(6) + '\n'
        if src!=None:
            pass
        else:
            return star


def roll( dice, sides=6, mode='sum' ):
    start, steps, stop  = 1, 1, sides
    i   = 0
    rc  = []
    while i < dice:
        rc.append( random.randrange( start, stop, steps ) )
        i += 1
    if mode == 'list':
        return rc
    elif mode == 'sum':
        sum = 0
        for r in rc:
            sum += r
        #print( "rolling " + ( str(dice) + "d" + str(sides) ).ljust(5) + " ... " + str(sum) )
        return sum


if __name__=="__main__": main()