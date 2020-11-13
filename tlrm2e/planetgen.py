#!/usr/bin/env python
import random
from lib.tools.db_parse import App as XML_Parse
from sys import argv, platform
from traceback import print_exc
#
VN  = 'vn'
SO  = 'so'
HS  = 'hs'
BA  = 'ba'
#
NAME        = 'name'
TAG         = 'tag'
#
SIZE        = 'size'
ATMOSPHERE  = 'atmosphere'
HYDROSPHERE = 'hydrosphere'
POPULATION  = 'population'
GOVERNMENT  = 'government'
LAWLEVEL    = 'lawlevel'
TECHLEVEL   = 'techlevel'
#

if platform == 'win32':
    HOME    = argv[0][:argv[0].rfind('\\')+1]
#

def fetch( filepath ):
    global HOME
    return XML_Parse.load( HOME, filepath )
#
#print( fetch( 'lib\\xml\\tradecodes.xml' )[XML_Parse.TOP_LAYER]['traveller']['tradecodes'].keys() )
#TRADECODES = []
TRADECODES  = fetch( 'lib\\xml\\tradecodes.xml' )[XML_Parse.TOP_LAYER]['traveller']['tradecodes']
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
        return sum
#

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
#

def planet( mode='vn' ):
    '''
    modes:
        vn  = vanilla
        so  = space opera
        hs  = hard sci-fi
    '''
    code = ''
    SOpera = False
    HardSf = False
    if mode == 'so':
        SOpera = True
    elif mode == 'hs':
        SOpera = False
        HardSf = True
    
    
    def size():
        return roll(2)-2
    size = size()
    
    def atmo():
        rc = roll(2)-7+size
        if SOpera and size <= 4:
            if   size <= 2: rc = 0
            else:
                if   rc <= 2: rc =  0
                elif rc <= 5: rc =  1
                elif rc >= 6: rc = 10
        if rc < 0:
            return 0
        else:
            return rc
    atmo = atmo()
    
    def hydro():
        if size < 2:
            rc = 0
        else:
            rc = roll(2)-7+size
        
        if SOpera:
            if (size == 3 or size == 4) and atmo == 10: rc += -6
            if atmo >= 1: rc += -6
            if atmo == 2 or atmo == 3 or atmo == 11 or atmo == 12: rc += -4
            
        if atmo < 2 or ( atmo >= 10 and atmo <= 12 ):
            rc -= 4
        if rc < 0:
            return 0
        else:
            return rc
    hydro = hydro()
    
    def pop():
        rc = roll(2)-2
        
        adj = roll(3)
        if adj > 14: rc+=1
        if adj > 16: rc+=1
        if adj <  8: rc-=1
        
        if HardSf:
            if size <= 2 or size == 10: rc += -1
            if atmo == 5 or atmo == 6 or atmo == 8: rc += 1
            else: rc += -1
            
        return max(rc,0)
    pop = pop()
    
    def port():
        r  = roll(2)
        
        if HardSf:
            r += -7+pop
            
        rc = ''
        if   r <=  2: rc += 'X'
        elif r <=  4: rc += 'E'
        elif r <=  6: rc += 'D'
        elif r <=  8: rc += 'C'
        elif r <= 10: rc += 'B'
        elif r >= 11: rc += 'A'
        return rc
    port = port()
    
    govt, law, tech = 0, 0, 0
    
    if pop > 0:
        def govt():
            rc = roll(2)-7+pop
            if rc < 0:
                return 0
            else:
                return rc
        govt = govt()
        
        def law():
            rc = roll(2)-7+govt
            if rc < 0:
                return 0
            else:
                return rc
        law = law()
        
        def tech():
            rc = roll(1)
            if   port == 'A': rc +=  6
            elif port == 'B': rc +=  4
            elif port == 'C': rc +=  2
            elif port == 'X': rc += -4
            if   size <=   1: rc +=  2
            elif size <=   4: rc +=  1
            if   atmo <=   3: rc +=  1
            elif atmo >=  10: rc +=  1
            if   hydro ==  0: rc +=  1
            elif hydro ==  9: rc +=  1
            elif hydro == 10: rc +=  2
            if   pop  >=   0 and pop <=   5: rc +=  1
            elif pop  ==   9: rc +=  1
            elif pop  ==  10: rc +=  2
            elif pop  ==  11: rc +=  3
            elif pop  ==  12: rc +=  4
            if   govt ==   0: rc +=  1
            elif govt ==   5: rc +=  1
            elif govt ==   7: rc +=  2
            elif govt ==  13: rc += -2
            elif govt ==  14: rc += -2
            return rc
        tech = tech()
    
    tasc = 'G'
    if atmo >= 10 \
    or govt == 0 or govt == 7 or govt == 10 \
    or law  == 0 or law  >= 9:
        tasc = 'A'
    
    code +=     port
    code += hex(size )[-1:].upper()
    code += hex(atmo )[-1:].upper()
    code += hex(hydro)[-1:].upper()
    code += hex(pop  )[-1:].upper()
    code += hex(govt )[-1:].upper()
    code += hex(law  )[-1:].upper()
    code += "-"        
    code += hex(tech )[-1:].upper()
    if tasc != 'G':
        code += " " + tasc
    else:
        code += "  "
    
    def tradecodes():
        rc  = ''
                
        for tradecode in TRADECODES['tradecode']:
            try:
                tcode = True
                for requirement in tradecode['requirements'].keys():
                    if requirement.endswith('__info')\
                    or requirement == XML_Parse.CDATA\
                    or requirement == XML_Parse.ATTR_TAG:
                        continue
                    if tradecode['requirements'][requirement][XML_Parse.CDATA] == ''\
                    or tradecode['requirements'][requirement][XML_Parse.CDATA] == None:
                        continue
                    else:
                        req_info = tradecode['requirements'][requirement][XML_Parse.CDATA]
                    if requirement == SIZE:
                        req = splitup( req_info )
                        if size  in req: pass
                        else: tcode = False
                    elif requirement == ATMOSPHERE:
                        req = splitup( req_info )
                        if atmo  in req: pass
                        else: tcode = False
                    elif requirement == HYDROSPHERE:
                        req = splitup( req_info )
                        if hydro in req: pass
                        else: tcode = False
                    elif requirement == POPULATION:
                        req = splitup( req_info )
                        if pop   in req: pass
                        else: tcode = False
                    elif requirement == GOVERNMENT:
                        req = splitup( req_info )
                        if govt  in req: pass
                        else: tcode = False
                    elif requirement == LAWLEVEL:
                        req = splitup( req_info )
                        if law   in req: pass
                        else: tcode = False
                    elif requirement == TECHLEVEL:
                        req = splitup( req_info )
                        if tech  in req: pass
                        else: tcode = False
#                print( '  ' + tradecode['name'] + ' is ' + str(tcode) )
                if tcode:
                    rc += " " + tradecode[XML_Parse.ATTR_TAG][TAG]
            except Exception as e:
                print(tradecode[XML_Parse.ATTR_TAG][TAG])
                print_exc()#print(e)
        return rc
    code += tradecodes()
    
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
    
    if HardSf: special_tag_tn=0
    elif SOpera: special_tag_tn=35
    else: special_tag_tn=15
    if random.randrange(100) < special_tag_tn: code += " | " + tag()
    
    return code
#
#

def main():
    print( planet( mode=SO ) )
    print( planet( mode=SO ) )
    print( planet( mode=SO ) )
#

if __name__ == '__main__':
    main()
#