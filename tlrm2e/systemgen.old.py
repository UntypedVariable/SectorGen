import random
from math import sqrt
#
SOLL    = 1
SOLK    = 5800
SOLd    = 1400000
#

def main():
    #print( planet() + '\n\n' )
    testStar = star()
    testStar.new()
    testStar.name( 'Test Star' )
    testStar.show()
#    i = 0
#    while i < 5:
#        print( testStar.Class )
#        testStar.new()
#        i += 1
#

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
#

def objectAngle():
    r   = roll(2)
    if   r ==  2: rc = 180
    elif r ==  3: rc = 160
    elif r ==  4: rc = 140
    elif r ==  5: rc = 120
    elif r ==  6: rc = 100
    elif r ==  7: rc =  90
    elif r ==  8: rc =  80
    elif r ==  9: rc =  70
    elif r == 10: rc =  50
    elif r == 11: rc =  30
    elif r == 12: rc =  10
    return rc

class star():
    Name        = ''
    Class       = ''
    Color       = ''
    Diameter    = 0     # Km
    Luminosity  = 0     # L
    Temperature = 0     # K
    HabOuter    = 0     # Km
    HabCenter   = 0     # Km
    HabInner    = 0     # Km
    DiamZone100 = 0     # Km
    DiamZone150 = 0     # Km
    Planetoids  = 0     # num
    Planets     = []
    #
    AU          = 149597870.7
    #
    Classes     = ( \
                    {'class':'O',           \
                     'color':'Blue',        \
                     'L':30000.0,           \
                     'K':5.0,               \
                     'K-base':30000,        \
                     'K-range':300000,      \
                     'd-mult':6.6,          \
                     'desc':"Very hot and very luminous, being bluish in color; in fact, most of their output is in the ultraviolet range. These are the rarest of all main sequence stars, constituting as few as 1 in 3,000,000 in the solar neighborhood O-stars shine with a power over a million times our Sun's output. Because they are so huge, class O stars burn through their hydrogen fuel very quickly, and are the first stars to leave the main sequence."}, \
                    {'class':'B',           \
                     'color':'Blue-White',  \
                     'L':25.0,              \
                     'K':3.0,               \
                     'K-base':10000,        \
                     'K-range':20000,       \
                     'd-mult':4.2,          \
                     'desc':"Extremely luminous and blue. As O and B stars are so powerful, they only live for a very short time, and thus they do not stray far from the area in which they were formed. These stars tend to cluster together in what are called OB associations, which are associated with giant molecular clouds. The Orion OB1 association occupies a large portion of a spiral arm of our galaxy and contains many of the brighter stars of the constellation Orion. They constitute about 1 in 800 main sequence stars in the solar neighborhood."}, \
                    {'class':'A',           \
                     'color':'White',       \
                     'L':5.0,               \
                     'K':1.5,               \
                     'K-base':7500,         \
                     'K-range':2500,        \
                     'd-mult':1.6,          \
                     'desc':"Amongst the more common naked eye stars, and are white or bluish-white. They comprise about 1 in 160 of the main sequence stars in the solar neighborhood."}, \
                    {'class':'F',           \
                     'color':'Yellow-White',\
                     'L':1.5,               \
                     'K':1.25,              \
                     'K-base':6000,         \
                     'K-range':1500,        \
                     'd-mult':1.3,          \
                     'desc':"These stars' color is white with a slight tinge of yellow. These represent about 1 in 32 of the main sequence stars in the solar neighborhood."}, \
                    {'class':'G',           \
                     'color':'Yellow',      \
                     'L':1.0,               \
                     'K':1.0,               \
                     'K-base':5200,         \
                     'K-range':800,         \
                     'd-mult':1.0,          \
                     'desc':"The best known, if only for the reason that Sol (Terra) is of this class. Supergiant stars often swing between O or B (blue) and K or M (red). While they do this, they do not stay for long in the G classification as this is an extremely unstable place for a supergiant to be. G stars represent about 1 in 13 of the main sequence stars in the solar neighborhood."}, \
                    {'class':'K',           \
                     'color':'Orange',      \
                     'L':0.6,               \
                     'K':0.75,              \
                     'K-base':2700,         \
                     'K-range':1500,        \
                     'd-mult':0.8,          \
                     'desc':"Orangish stars which are slightly cooler than our Sun. Some K stars are giants and supergiants, such as Arcturus, while others, like Alpha Centauri B, are main sequence stars. These make up 1 in 8 of the main sequence stars in the solar neighborhood."}, \
                    {'class':'M',           \
                     'color':'Red',         \
                     'L':0.08,              \
                     'K':0.5,               \
                     'K-base':2400,         \
                     'K-range':1300,        \
                     'd-mult':0.6,          \
                     'desc':"By far the most common class. At least 80% of the main sequence stars in the solar neighborhood are red dwarfs such as Proxima Centauri. M is also host to most giants and some supergiants such as Antares and Betelgeuse , as well as Mira variables. The late-M group holds hotter brown dwarfs that are above the L spectrum. This is usually in the range of M6.5 to M9.5."} \
                    )
    #
    
    def toPAU( self, km ):
        rc  = int( km / self.AU * 100 )
        return rc
    
    def new( self ):
        def getType():
            r   = roll(2)
            rc  = ''
            
            if   r  ==  2:
                rx  = roll(1)
                if rx   >=  5:
                    rc  += 'O'
                else:
                    rc  += 'B'
            elif r  ==  3:              rc += 'A'
            elif r  ==  5:              rc += 'F'
            elif r  >=  6 and r  <=  7: rc += 'G'
            elif r  >=  8 and r  <=  9: rc += 'K'
            elif r  >= 10 and r  <= 12: rc += 'M'
            
            for cl in self.Classes:
                if cl['class'] == rc:
                    return cl
            return getType()
        type    = getType()
        
        def getClass():
              rc = type['class'] + str( roll(1,10) - 1 ) + 'V'
              return rc
        self.Class          = getClass()
        self.Color          = type['color']
        
        def getLum():
            r   = roll(2)
            
            if   r  ==  2:              rv  = 2.0
            elif r  >=  3 and r  <=  5: rv  = 1.5
            elif r  >=  6 and r  <=  8: rv  = 1.0
            elif r  >=  9 and r  <= 11: rv  = 0.8
            elif r  == 12:              rv  = 0.6
            
            rc  = int( 100 * type['L'] * rv ) / 100
            return rc
        self.Luminosity     = getLum()
        
        def getTemp():
            rc = int( 100 * type['K-base'] + round( type['K-range'] / 9 * ( 10 - int( self.Class[1:2] ) ), -1 ) ) / 100
            return rc
        self.Temperature    = getTemp()
        
        def getDiam():
            rc = type['d-mult'] * SOLd
            return rc
        self.Diameter       = getDiam()
        self.DiamZone100    = self.Diameter * 100
        self.DiamZone150    = self.Diameter * 150
        
        def getHabZone():
            rc = round( self.AU * 1.34 * sqrt( self.Luminosity * self.Temperature / SOLK ), 5 )
            rOuter  = rc
            rCenter = rc * 0.745
            rInner  = rc * 0.38
            return rOuter, rCenter, rInner
        self.HabOuter, self.HabCenter, self.HabInner    = getHabZone()      
    
        def getPtoids():
            rc  = roll(3)-4
            if rc < 0: rc = 0
            return rc
        self.Planetoids     = getPtoids()
        
        i   = 0
        while i < self.Planetoids:
            
            def getPlanet():
                near = False
                mid  = False
                far  = False
                rc   = 0
                ty   = ''
                r    = roll(3)
                if   r  <=  5: near = True
                elif r  <=  9: far  = True
                elif r  <= 12: mid  = True
                
                r    = roll(1)
                if near:
                    rc  =  10 + roll(1, 55)
                    if   r  <=  6: ty   = 'Terrestrial'
                elif mid:
                    rc  =  65 + roll(1, 65)
                    if   r  <=  5: ty   = 'Terrestrial'
                    elif r  <=  6: ty   = 'Jovian'
                elif far:
                    rc  = 140 + roll(1,200)
                    if   r  <=  2: ty   = 'Terrestrial'
                    elif r  <=  6: ty   = 'Jovian'
                return int(rc * type['d-mult']), ty
            l,ty = getPlanet()
            self.Planets.append( [l,ty] )
            i  += 1
    
    def name( self, name ):
        self.Name = name
    
    def show( self ):
        star    = ''
        star += 'Name:'             .ljust(16) + self.Name                              + '\n'
        star += 'Class:'            .ljust(16) + self.Class                             + '\n'
        star += 'Color:'            .ljust(16) + self.Color                             + '\n'
        star += 'Temperature:'      .ljust(16) + str( self.Temperature )                .rjust(12) + ' K' + '\n'
        star += 'Luminosity:'       .ljust(16) + str( self.Luminosity  )                .rjust(12) + ' L' + '\n'
        star += 'Diameter:'         .ljust(16) + str( self.Diameter    )                .rjust(12) + ' Km'+ '\n'
        star += 'HabZone Inner:'    .ljust(16) + str( self.toPAU(self.HabInner ) )      .rjust(12) + ' %AU'+ '\n'
        star += 'HabZone Center:'   .ljust(16) + str( self.toPAU(self.HabCenter) )      .rjust(12) + ' %AU'+ '\n'
        star += 'HabZone Outer:'    .ljust(16) + str( self.toPAU(self.HabOuter ) )      .rjust(12) + ' %AU'+ '\n'
        star += '100 Diameters:'    .ljust(16) + str( self.toPAU(self.DiamZone100 ) )   .rjust(12) + ' %AU'+ '\n'
        star += '150 Diameters:'    .ljust(16) + str( self.toPAU(self.DiamZone150 ) )   .rjust(12) + ' %AU'+ '\n'
        star += 'Planetoids:'       .ljust(16) + str( self.Planetoids )                 .rjust( 2)         + '\n'
        for planet in sorted(self.Planets):
            star += '        ' + str(planet[0]).rjust(6) + '  ' + planet[1].rjust(12) + '\n'
        print( star )

def planet():
    planet  = ''
    
    def tag():
        r   = roll(1,100)
        rc  = ''
        
        tags    = [ 'Abandoned Colony', \
                    'Alien Ruins',      \
                    'Altered Humanity', \
                    'Anthromorphs',     \
                    'Battleground',     \
                    'Bubble Cities',    \
                    'Cheap Life',       \
                    'Civil War',        \
                    'Cold War',         \
                    'Colony',           \
                    'Cyclical Doom',    \
                    'Doomed World',     \
                    'Dying Race',       \
                    'Eugenics Cult',    \
                    'Feral World',      \
                    'Flying Cities',    \
                    'Forbidden Tech',   \
                    'Freak Geology',    \
                    'Freak Weather',    \
                    'Friendly Foe',     \
                    'Gold Rush',        \
                    'Great Work',       \
                    'Hatred',           \
                    'Hivemind',         \
                    'Holy War',         \
                    'Hostile Biosphere', \
                    'Hostile Space',    \
                    'Immortals',        \
                    'Local Specialty',  \
                    'Local Tech',       \
                    'Major Spaceyard',  \
                    'Megacorps',        \
                    'Mercenaries',      \
                    'Minimal Contact',  \
                    'Misandry/Misogyny', \
                    'Night World',      \
                    'Nomads',           \
                    'Out of Contact',   \
                    'Outpost World',    \
                    'Pilgrimage Site',  \
                    'Pleasure World',   \
                    'Police State',     \
                    'Post-Scarcity',    \
                    'Tech Cultists',    \
                    'Primitive Aliens', \
                    'Quarantined World', \
                    'Radioactive World', \
                    'Refugees',         \
                    'Regional Hegemon', \
                    'Restrictive Laws', \
                    'Revanchists',      \
                    'Revolutionaries',  \
                    'Rigid Culture',    \
                    'Rising Hegemon',   \
                    'Ritual Combat',    \
                    'Robots',           \
                    'Seagoing Cities',  \
                    'Sealed Menace',    \
                    'Secret Masters',   \
                    'Sectarians',       \
                    'Seismic Instability', \
                    'Shackled World',   \
                    'Societal Despair', \
                    'Sole Supplier',    \
                    'Taboo Treasure',   \
                    'Terraform Failure', \
                    'Tomb World',       \
                    'Unshackled AI',    \
                    'Urbanized Surface', \
                    'Utopia',           \
                    'Xenophiles',       \
                    'Xenophobes',       \
                    'Zombies'           ]
        rc      = random.choice( tags )
        return rc
    tag     = tag() + ', ' + tag()
    
    def atmosphere():
        r   = roll(2)
        rc  = ''
        
        if   r  ==  2: rc += 'Corrosive'
        elif r  ==  3: rc += 'Inert'
        elif r  ==  4: rc += 'Airless or Thin'
        elif r  >=  5 and r  <=  9: rc += 'Breathable'
        elif r  == 10: rc += 'Thick'
        elif r  == 11: rc += 'Invasive'
        elif r  == 12: rc += 'Corrosive and Invasive'
        
        return rc
    atmo    = atmosphere()
    
    def temperature():
        r   = roll(2)
        rc  = ''
        
        if   r  ==  2: rc += 'Frozen'
        elif r  ==  3: rc += 'Cold'
        elif r  >=  4 and r  <=  5: rc += 'Variable cold'
        elif r  >=  6 and r  <=  8: rc += 'Temperate'
        elif r  >=  9 and r  <= 10: rc += 'Variable warm'
        elif r  == 11: rc += 'Warm'
        elif r  == 12: rc += 'Burning'
        
        return rc
    temp    = temperature()
    
    def hydrosphere():
        r   = roll(2)
        rc  = ''
        
        if   r  ==  2: rc += 'Completely Barren'
        elif r  ==  3: rc += 'Only Groundwater'
        elif r  >=  4 and r  <=  5: rc += 'Lakes & Seas'
        elif r  >=  6 and r  <=  8: rc += 'Small Oceans'
        elif r  >=  9 and r  <= 10: rc += 'Large Oceans'
        elif r  == 11: rc += 'Archipelagos'
        elif r  == 12: rc += 'Ocean World'
        
        return rc
    hydro   = hydrosphere()
    
    def biosphere():
        r   = roll(2)
        rc  = ''
        
        if   r  ==  2: rc += 'Remnant'
        elif r  ==  3: rc += 'Microbial'
        elif r  >=  4 and r  <=  5: rc += 'None'
        elif r  >=  6 and r  <=  8: rc += 'Human-miscible'
        elif r  >=  9 and r  <= 10: rc += 'Immiscible'
        elif r  == 11: rc += 'Hybrid'
        elif r  == 12: rc += 'Engineered'
        
        return rc
    bio     = biosphere()
    
    def population():
        r   = roll(2)
        rc  = ''
        
        if   r  ==  2: rc += 'Failed colony'
        elif r  ==  3: rc += 'Outpost'
        elif r  >=  4 and r  <=  5: rc += 'Fewer than a million'
        elif r  >=  6 and r  <=  8: rc += 'Several million'
        elif r  >=  9 and r  <= 10: rc += 'Hundreds of millions'
        elif r  == 11: rc += 'Billions'
        elif r  == 12: rc += 'Aliens'
        
        return rc
    pop     = population()
    
    def techLevel():
        r   = roll(2)
        rc  = ''
        
        if   r  ==  2: rc += 'Neolithic Age'
        elif r  ==  3: rc += 'Medieval Age'
        elif r  >=  4 and r  <=  5: rc += 'Early Industrial Age'
        elif r  >=  6 and r  <=  8: rc += 'Interstellar Space Age'
        elif r  >=  9 and r  <= 10: rc += '21st Century Earth Tech'
        elif r  == 11: rc += 'Interstellar Space, Hi-Tech'
        elif r  == 12: rc += 'Superscience Tech'
        
        return rc
    tech    = techLevel()
    
    planet += 'Atmosphere:'.ljust(13)   + atmo  + '\n'
    planet += 'Temperature:'.ljust(13)  + temp  + '\n'
    planet += 'Hydrosphere:'.ljust(13)  + hydro + '\n'
    planet += 'Biosphere:'.ljust(13)    + bio   + '\n'
    planet += 'Population:'.ljust(13)   + pop   + '\n'
    planet += 'Tech Level:'.ljust(13)   + tech  + '\n'
    planet += 'Tags:'.ljust(13)         + tag   + ''
    
    return planet
#
#

if __name__ == '__main__':
    main()
#