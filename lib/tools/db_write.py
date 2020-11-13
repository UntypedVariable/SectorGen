#!/usr/bin/env python

# GENERAL  IMPORTS
import traceback    as tb
import db_parse
# SPECIFIC IMPORTS
from xml.dom.minidom    import parse
from xml.dom.minidom    import Document



if __name__ == "__main__":
    from sys import argv
    # CONSTANTS
    __file__    = "db_write.py"
    __path__    = argv[0][:-len(__file__)]
    __db_in__   = "writing.xml"
    __db_out__  = "writing2.xml"


# VARIABLES
###

# SPECIAL
DEBUG       = False
INDENT      = " "


class App():
    TOP_LAYER   = "#document"
    ATTR_TAG    = "#attributes"
    CDATA       = "#cdata"
    pass
    
    def dict_to_xml( self={} ):
        dict = self
        return dict_to_xml( dict )
    
    def write_xml_to_file( self, file_path, pretty=False ):
        dom = self
        tgt_doc = open( file_path+".xml", 'w')
        if pretty:  tgt_doc.write(  dom.toprettyxml().replace( "?>","encoding=\"utf-8\" ?>",1 ) )
        else:       tgt_doc.write(  dom.toxml()      .replace( "?>","encoding=\"utf-8\" ?>",1 ) )
        tgt_doc.close()
    
    def write( dict, file_path, pretty=Fales):
        dom = dict_to_xml( dict )
        App.write_xml_to_file( dom, file_path, pretty)


# MAIN FUNCTION
def main():
    #dom = db_parse.App.load(__path__,__db_in__)
    #dom     = parse(__path__+__db_in__)
    
    d   = db_parse.App.load(__path__,__db_in__)
    db_parse.printDict(d)
    dom = dict_to_xml( d )
    
    tgt_doc = open( __path__+__db_out__, 'w')
    tgt_doc.write( dom.toprettyxml().replace( "?>","encoding=\"utf-8\" ?>\n",1 ) )
    tgt_doc.close()
    pass


def dict_to_xml( dict ):
    dom = createDocument()
    for item in dict['#document']:
        parseDictItem( dom, item, dict['#document'][item] )
    return dom


def parseDictItem( parent, dict_pointer, dict_item ):
    node    = createNode(parent,dict_pointer)
    
    def parsingLoop( parent, dict_pointer, dict_item ):
        for item in dict_item:
            if dict_item[item] == None \
            or dict_item[item] =='None':continue
            if item.endswith("__info"): continue
            #print( " >",item )
            if item == App.CDATA   :
                createCDATA(     node, dict_item[item] )
                continue
            if item == App.ATTR_TAG:
                createATTRIBUTE( node, dict_item[item] )
                continue
            if type(dict_item[item]) == type({})\
            or type(dict_item[item]) == type([]):
                parseDictItem( node, item, dict_item[item] )
                continue
            #try:    parent.appendChild( Document.createTextNode( None, "\n" ) )
            #except: pass
    
    if dict_item != None:
        if   type(dict_item) == type([]):
            for sub_item in dict_item:      parsingLoop( parent, dict_pointer,  sub_item )
        elif type(dict_item) == type({}):   parsingLoop( parent, dict_pointer, dict_item )
    return node


def createDocument():
    document    = Document()
    #document.childNodes.append( Document.createTextNode( "", "\n" ) )
    return document


def createCDATA(parent,data):
    textNode    = Document.createTextNode( None, data )
    parent.appendChild( textNode )


def createATTRIBUTE(parent,attr):
    for attribute in attr:
        attributeNode       = Document.createAttribute( None, attribute )
        attributeNode.value = attr[attribute]
        #print( attributeNode.name, "=", attributeNode.value )
        parent.setAttributeNode( attributeNode )
    
    #for i in range(parent.attributes.length):
    #    print(parent.attributes.item(i).name,"=",parent.attributes.item(i).value)
    

def createNode(parent,tagName,**kwargs):
    #try:    parent.appendChild( Document.createTextNode( None, "\n" ) )
    #except: pass
    node    = Document.createElement( None, tagName )
    
    # insert data
    if 'data' in kwargs:    createCDATA(     node, kwargs['data'] )
    else:                   pass
    
    # insert attributes
    if 'attr' in kwargs:    createATTRIBUTE( node, kwargs['data'] )
    else:                   pass
    
    #if 'tagName' in kwargs:
    #    node.nodeType = kwargs['tagName']
    
    parent.childNodes.append( node )
    #try:    parent.appendChild( Document.createTextNode( None, "\n" ) )
    #except: pass
    return node


# TESTING EXECUTION
if __name__ == "__main__":
    try:    main()
    except: tb.print_exc()