
import argparse
import json
import math
import re
import logging
import os
import os.path

from solid import *
from solid.utils import *

from switch import Switch
from support import Support
from support_cutout import SupportCutout
from cell import Cell
from item_collection import ItemCollection
from rotation_collection import RotationCollection
from body import Body



class Keyboard():

    def __init__(self, parameter_dict = {}):

        self.parameter_dict = parameter_dict

        self.default_parameter_dict = {
            'plate_only': True,
            'plate_supports': True,
            
            'x_build_size' : 200,
            'y_build_size' : 200,

            'kerf' : 0.00,

            'top_margin' : 8,
            'bottom_margin' : 8,
            'left_margin' : 8,
            'right_margin' : 8,
            'case_height' : 10,
            'plate_wall_thickness' : 2.0,
            'plate_thickness' : 1.511,
            'plate_corner_radius' : 4,

            'support_bar_height' : 3.0,
            'support_bar_width' : 1.0
        }

        self.build_attr_from_dict(self.default_parameter_dict)
        self.build_attr_from_dict(self.parameter_dict)


        self.build_x = math.floor(self.x_build_size / Cell.SWITCH_SPACING)
        self.build_y = math.floor(self.y_build_size / Cell.SWITCH_SPACING)


    def build_attr_from_dict(self, parameter_dict):
        for param in parameter_dict.keys():
             value = parameter_dict[param]

             setattr(self, param, value)
    
    
    def set_parameter_dict(self, parameter_dict):
        self.parameter_dict = parameter_dict
        self.build_attr_from_dict(self.parameter_dict)
    
    
    def get_param(self, paramaeter_name):

        if paramaeter_name in self.parameter_dict.keys():
            return self.parameter_dict[paramaeter_name]
        elif paramaeter_name in self.default_parameter_dict.keys():
            return self.default_parameter_dict[paramaeter_name]
        else:
            raise ValueError('No paramter exists with name %s' % (paramaeter_name))