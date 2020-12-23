#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys        import argv
from platform   import system
import tkinter  as tk
import __main__ as tlr
import sys

# in-file settings
if system().lower().startswith("win"):
    SLASH="\\"
else:
    SLASH="/"

path=argv[0][:argv[0].rfind(SLASH)+1]
path_up=path[ :path[:-1].rfind(SLASH)+1]
config_src  = "config"+SLASH+"inspect.ini"


def main():
    window = TlrGui()
    window.mainloop()
    window.destroy()
    sys.exit(0)
    pass


class TlrGui(tk.Tk):
    def __init__(self,config=config_src):
        ### config BEGIN
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
        #   [GEOMETRY]
        self.input_width  =int(self.config.get("GEOMETRY","width"         ).strip())
        self.input_height =int(self.config.get("GEOMETRY","height"        ).strip())
        self.padding_y     =int(self.config.get("GEOMETRY","padding x"     ).strip())
        self.padding_x     =int(self.config.get("GEOMETRY","padding y"     ).strip())
        self.line1_height  =int(self.config.get("GEOMETRY","line-1 height" ).strip())
        self.line1_padding =int(self.config.get("GEOMETRY","like-1 padding").strip())
        #   [TESTING]
        self.testing_hex   =    self.config.get("TESTING","testing hex"    ).strip()
        self.testing_mode  =    self.config.get("TESTING","testing mode"   ).strip()
        ### config END

        ### WINDOW
        tk.Tk.__init__(self)
        self.geometry("{}x{}".format(self.input_width,self.input_height))

        ### GUI ELEMENTS
        self.label_greeting = tk.Label(self,text="Greetings, Traveller!")

        self.label_instruction = tk.Label(self,text="Enter the hex location\nof the tile you wish to inspect.")

        self.label_hex_location = tk.Label(self,text="Hex Coordinates")

        self.entry_hex_location = tk.Entry(self,width=4)
        self.entry_hex_location.insert(0,self.testing_hex)

        self.mode=tk.IntVar()
        if self.testing_mode.startswith("v"): self.mode.set(True)
        self.checkbox_verbose = tk.Checkbutton(self,
            text="verbose",
            variable=self.mode,
            onvalue=True,
            offvalue=False)

        self.button_inspect_hex = tk.Button(self,
            text   ="Inspect",
            width  =9,
            height =1,
            command=self.button_inspect_hex_method)

        self.text_box_inspection = tk.Text(self)

        ### GUI ELEMENT GEOMETRY
        self.label_hex_location_padding_x=110

        ### ELEMENT PLACEMENT (COORDINATION)
        #  headline & subhead
        label_greeting_x      =  self.input_width/2
        label_greeting_y      =  self.padding_y
        label_instruction_x   =  self.input_width/2
        label_instruction_y   =  self.padding_y+self.line1_height*1+self.line1_padding*1
        #  inspector interface
        label_hex_location_y  =  self.padding_y+self.line1_height*4+self.line1_padding*2
        entry_hex_location_x  =  self.padding_x+self.label_hex_location_padding_x
        entry_hex_location_y  =  label_hex_location_y +1
        checkbox_verbose_x    =  entry_hex_location_x -5
        checkbox_verbose_y    =  self.padding_y+self.line1_height*5+self.line1_padding*3 +1
        button_inspect_hex_x  =  entry_hex_location_x -1
        button_inspect_hex_y  =  self.padding_y+self.line1_height*6+self.line1_padding*4 +1 +5
        text_box_inspection_x =  self.padding_x
        text_box_inspection_y =  self.padding_y+self.line1_height*6+self.line1_padding*5    +5 +35
        text_box_inspection_w =  self.input_width-text_box_inspection_x*2
        text_box_inspection_h =  self.input_height-(text_box_inspection_y)-self.padding_y

        ### ELEMENT PLACEMENT (PLACEMENT)
        # headline & subhead
        self.label_greeting     .place( anchor=tk.N,
                                        x=label_greeting_x,
                                        y=label_greeting_y)
        self.label_instruction  .place( anchor=tk.N,
                                        x=label_instruction_x,
                                        y=label_instruction_y)
        # inspector interface
        self.label_hex_location .place( anchor=tk.NW,
                                        x=self.padding_x,
                                        y=label_hex_location_y)
        self.entry_hex_location .place( anchor=tk.NW,
                                        x=entry_hex_location_x,
                                        y=entry_hex_location_y)
        self.checkbox_verbose   .place( anchor=tk.NW,
                                        x=checkbox_verbose_x,
                                        y=checkbox_verbose_y)
        self.button_inspect_hex .place( anchor=tk.NW,
                                        x=button_inspect_hex_x,
                                        y=button_inspect_hex_y)
        self.text_box_inspection.place( anchor=tk.NW,
                                        x=text_box_inspection_x,
                                        y=text_box_inspection_y,
                                        width =text_box_inspection_w,
                                        height=text_box_inspection_h)

        ### BIND
        self.bind("<Return>",self.button_inspect_hex_method)
        pass

    def button_inspect_hex_method(self,evt=None):
        hex_location = self.entry_hex_location.get()
        if not self.__is_hex_location(hex_location): return 1

        self.text_box_inspection.delete('1.0',tk.END)
        self.text_box_inspection.insert('1.0',"Looking up information on Hex {}...".format(hex_location))

        # inspection
        from tlrm2e.inspect     import App     as Inspector
        inspector = Inspector()

        mode    =   None
        if self.mode.get(): mode = inspector.VERBOSE
        else:               mode = inspector.TERSE

        depth   =   'mw'
        #MAINWORLD
        #SYSTEM
        #STAR

        if   depth in ('sy','system'):    depth = inspector.SYSTEM
        elif depth in ('s','star'):       depth = inspector.STAR
        elif depth in ('mw','mainworld'): depth = inspector.MAINWORLD
        inspected_hex = inspector.inspect(hex_location,mode=mode,depth=depth)

        self.text_box_inspection.delete('1.0',tk.END)
        info=""
        try:
            if inspected_hex.startswith("Nothing"):
                info = inspected_hex
        except:
            for info_block in inspected_hex:
                if not info_block==None:
                    info+=info_block+"\n"
        self.text_box_inspection.insert('1.0',info)
        return 0

    def __is_hex_location(self,hex_location):
        try:
            y = int(hex_location[:2])
            x = int(hex_location[2:])
            if x == 0 and y == 0: raise Exception()
        except:
            return False
        return True





if __name__=="__main__": main()