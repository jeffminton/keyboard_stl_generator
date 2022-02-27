from solid import *
from solid.utils import *

import logging

from cell import Cell
from parameters import Parameters

class SupportCutout(Cell):

    def __init__(self, x, y, w, h, plate_thickness, support_bar_height, support_bar_width, rotation = 0.0,  r_x_offset = 0.0, r_y_offset = 0.0, set_to_origin = False, cell_value = '', parameters: Parameters = Parameters()):
        super().__init__(x, y, w, h, rotation,  r_x_offset, r_y_offset, cell_value = cell_value, parameters = parameters)

        self.logger = logging.getLogger().getChild(__name__)

        self.plate_thickness = plate_thickness
        self.set_to_origin = set_to_origin
        self.support_bar_height = support_bar_height
        self.support_bar_width = support_bar_width

        self.solid = self.support_cutout()

    # def u(self, u_value):
    #     return u_value * self.SWITCH_SPACING

    def __str__(self):
        return 'SupportCutout: ' + super().__str__()

    def support_cutout(self):    
        d = down(self.support_bar_height / 2) ( cube([self.w_mm, self.h_mm, self.support_bar_height + self.plate_thickness], center = True) )
    
        d = right(self.w_mm / 2) ( back(self.h_mm / 2) ( d ) )

        return d # right(u(w / 2)) ( back(u(h / 2)) ( d ) )
