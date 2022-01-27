from solid import *
from solid.utils import *

import logging

from cell import Cell

class SupportCutout(Cell):

    def __init__(self, x, y, w, h, plate_thickness, support_bar_height, support_bar_width, rotation = 0.0,  r_x_offset = 0.0, r_y_offset = 0.0, set_to_origin = False, cell_value = ''):
        super().__init__(x, y, w, h, rotation,  r_x_offset, r_y_offset, cell_value = cell_value)

        self.logger = logging.getLogger('SupportCutout')
        self.logger.setLevel(logging.INFO)

        if not self.logger.hasHandlers():
        # create console handler and set level to debug
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)

            # create formatter
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

            # add formatter to ch
            ch.setFormatter(formatter)

            self.logger.addHandler(ch)

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
        d = down(self.support_bar_height / 2) ( cube([self.u(self.w), self.u(self.h), self.support_bar_height + self.plate_thickness], center = True) )
    
        d = right(self.u(self.w / 2)) ( back(self.u(self.h / 2)) ( d ) )

        return d # right(u(w / 2)) ( back(u(h / 2)) ( d ) )
