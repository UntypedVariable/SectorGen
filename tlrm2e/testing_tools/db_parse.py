#!/usr/bin/env python

# GENERAL  IMPORTS
import traceback    as tb
import copy         as copy
# SPECIFIC IMPORTS
from xml.dom.minidom    import parse



if __name__ == "__main__":
    from sys import argv
    # CONSTANTS
    __file__    = "db_parse.py"
    __path__    = argv[0][:-len(__file__)]
    __db__      = "merits.xml"
# VARIABLES
###
# SPECIAL
DEBUG       = False
INDENT      = " "


class App():
    TOP_LAYER   = "#document"
    ATTR_TAG    = "#attributes"
    CDATA       = "#cdata"

    def __str__(self):
        return __path__
    
    def load(self,__db__):
        return loadData(str(self),__db__)

# MAIN FUNCTION
def main():
    d   = loadData(__path__,__db__)
    print()
    printDict(d)
    pass

def loadData(__path__,__db__):
    dom     = parse(__path__+__db__)
    return processDOM( dom )


def processDOM( dom ):
    rdict   = { App.TOP_LAYER : {} }
    for primeNode in dom.childNodes:
        if not primeNode.nodeType == primeNode.TEXT_NODE: rdict[App.TOP_LAYER] = processNode(primeNode,ret="whole")
    return rdict


def processNode(node,dict=None,ret="whole"):
    if dict == None:                dict =       {                   }
    if type(dict) == list:          dict =       { node.tagName : {} }
    elif not node.tagName in dict:  dict.update( { node.tagName : {} } )
    if DEBUG: print( "Processing Node:",node.tagName )
    try:
        # process attributes
        dict[node.tagName].update( { App.ATTR_TAG : {} } )
        for attribute in node.attributes.values():
            dict[node.tagName][App.ATTR_TAG].update( { str(attribute.name) : str(attribute.value) } )
            #if DEBUG: print( attribute.value )
        if dict[node.tagName][App.ATTR_TAG] == {}:
            dict[node.tagName][App.ATTR_TAG] = None
        
        if node.hasChildNodes:
            if DEBUG: print( " ",node.tagName,"has Child Nodes!" )
            ## handle children
            # get a list of tag names, for finding duplicates
            tagNameList = []
            for child in node.childNodes:
                if child.nodeType == child.ELEMENT_NODE:
                    tagNameList.append( child.tagName )
                    #if DEBUG: print( child.tagName )
            
            # if a tag name is a list, then keep it in the list
            dict[node.tagName].update( { App.CDATA : None } )
            for child in node.childNodes:
                if child.nodeType == child.ELEMENT_NODE:
                    #if DEBUG: print( "Count of", child.tagName, " is:", tagNameList.count(child.tagName) )
                    if tagNameList.count(child.tagName) > 1:
                        dict[node.tagName].update( { child.tagName : [] } )
                        dict[node.tagName].update( { (str(child.tagName)+"__info") : "list" } )
                    elif tagNameList.count(child.tagName) == 1:
                        dict[node.tagName].update( { child.tagName : {} } )
                        dict[node.tagName].update( { (str(child.tagName)+"__info") : "dict" } )
                        tagNameList.remove(child.tagName)
                elif child.nodeType == child.TEXT_NODE:
                    dict[node.tagName].update( { App.CDATA : child.wholeText } )
            
            # assemble dict of children that are lists
            childListsDict = {}
            for tagName in tagNameList:
                childListsDict.update( {tagName:[]} )
                for child in node.childNodes:
                    if child.nodeType == child.ELEMENT_NODE:
                        if child.tagName == tagName: childListsDict[tagName].append(child)
            
            # handle unique child nodes        
            for child in node.childNodes:
                if child.nodeType == child.ELEMENT_NODE:
                    if type(dict[node.tagName][child.tagName]) != list: dict[node.tagName].update( processNode(child,ret="whole") )
                    
            # handle non-unique child nodes
            for childListName in childListsDict:
                for item in childListsDict[childListName]:
                    dict[node.tagName][childListName].append( processNode(item,ret="contents_only") )
                    
        if   ret == "whole":            return dict
        elif ret == "contents_only":    return dict[node.tagName] 
    except:
        tb.print_exc()
        printDict( { App.TOP_LAYER : dict } )
        
def nodeToDict(node):
    rdict = {}
    if node.nodeType == node.ELEMENT_NODE:
        rdict.update( { node.tagName : {} } )
        rdict[node.tagName].update( { App.ATTR_TAG : {} } )
        for attribute in node.attributes.values():
            print( attribute )
            rdict[node.tagName][App.ATTR_TAG].update( { str(attribute.name) : str(attribute.value.join("")) } )
    return rdict
    
def printDict(dict,layer=0):
    for child in dict:
        try:
            if not child.startswith("__"):
                if      type(dict[child]) == str:   print( layer*INDENT+str(child)+" : "+str(dict[child]) )
                elif    type(dict[child]) == list:
                    for item in dict[child]:
                        print( layer*INDENT+str(child) )
                        printDict(item,layer+1)
                else:
                    print( layer*INDENT+str(child) )
                    printDict(dict[child],layer+1)
        except: pass

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

if __name__ == "__main__":
    try: main()
    except: tb.print_exc()