import math


from solid import *
from solid.utils import *

import logging

from cell import Cell
from support import Support


class Body():

    def __init__(self, top_margin = 8.0, bottom_margin = 8.0, left_margin = 8.0, right_margin = 8.0, case_height = 10, plate_wall_thickness = 2.0, plate_thickness = 1.511, plate_corner_radius = 4, plate_only = False, plate_supports = False, support_bar_height = 3.0, support_bar_width = 1.0):

        self.logger = logging.getLogger('Body')
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

        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.left_margin = left_margin
        self.right_margin = right_margin
        self.case_height = case_height
        self.plate_wall_thickness = plate_wall_thickness
        self.plate_thickness = plate_thickness
        self.plate_corner_radius = plate_corner_radius
        self.plate_only = plate_only
        self.plate_supports = plate_supports

        self.max_x = 0.0
        self.min_y = 0.0

        self.real_max_x = 0.0
        self.real_max_y = 0.0

        self.support_bar_height = support_bar_height
        self.support_bar_width = support_bar_width
    

    def set_dimensions(self, max_x, min_y):

        self.max_x = max_x
        self.min_y = min_y
        self.logger.info('max_x: %d, min_y: %s', self.max_x, self.min_y)

        # Get rhe calculated real max and y sizes of the board
        self.real_max_x = Cell.u(self.max_x)
        self.real_max_y = Cell.u(abs(self.min_y))

        self.logger.info('real_max_x: %d, real_max_y: %s', self.real_max_x, self.real_max_y)

    def plate(self, case_x, case_y, pre_minkowski_thickness, corner):
        h = 1.0
        w = 1.0
        max_y = abs(self.min_y)

        plate_object = cube([case_x, case_y, pre_minkowski_thickness], center = True)
        plate_object = minkowski() ( plate_object, corner )

        self.logger.info('self.plate_supports: %s', str(self.plate_supports))

        side_margin_diff = self.right_margin - self.left_margin
        top_margin_diff = self.bottom_margin - self.top_margin

        if self.plate_supports == True:
            max_x_ceil = math.ceil(self.max_x)
            max_y_ceil = math.ceil(abs(self.min_y))
            self.logger.debug('range(max_x_ceil): %s, range(max_y_ceil): %s', str(range(max_x_ceil)), str(range(max_y_ceil)))
            for x in range(max_x_ceil):
                w = 1.0
                max_x_diff = self.max_x - (x + w)
                if max_x_diff < 0:
                    # Reduce w to be remaining x value
                    w = self.max_x - x
                for y in range(max_y_ceil):
                    self.logger.debug('x: %f, y: %f', x, y)
                    h = 1.0
                    max_y_diff = max_y - (y + h)
                    if max_y_diff < 0:
                        # Reduce h to be remaining y value
                        h = max_y - y
                    x_offset = x - ((self.real_max_x / 2) + (side_margin_diff / 2)) / Cell.SWITCH_SPACING
                    y_offset = -(y - ((self.real_max_y / 2) + (top_margin_diff / 2)) / Cell.SWITCH_SPACING)
                    
                    plate_object += Support(x_offset, y_offset, w, h, self.plate_thickness, self.support_bar_height, self.support_bar_width).get_moved()

        return plate_object

    def case_border(self, case_x, case_y, corner):
        case_wall = cube([case_x, case_y, self.case_height], center = True)
        case_inner = cube([case_x - (self.plate_wall_thickness * 2), case_y - (self.plate_wall_thickness * 2), self.case_height * 2], center = True)

        case_wall = minkowski() (case_wall, corner)
        case_inner = minkowski() (case_inner, corner)

        case_wall -= case_inner

        case_wall = down(self.case_height / 2) ( case_wall )

        return case_wall

    def case(self):
        # Get the margins for the plate without the ammount that the minkowski will add
        pre_minkowski_x_margin = ((self.right_margin + self.left_margin) / 2 - self.plate_corner_radius)
        pre_minkowski_y_margin = ((self.top_margin + self.bottom_margin) / 2 - self.plate_corner_radius)

        # get the pre minkowski plate sizes
        case_x = self.real_max_x + (pre_minkowski_x_margin * 2)
        case_y = self.real_max_y + (pre_minkowski_y_margin * 2)

        # Get the plate thickness before the minkowski
        pre_minkowski_thickness = self.plate_thickness / 2

        corner = cylinder(r = self.plate_corner_radius, h = pre_minkowski_thickness, center = True)

        self.logger.info('self.plate_supports: %s', str(self.plate_supports))

        plate_object = self.plate(case_x, case_y, pre_minkowski_thickness, corner)
        case_wall = self.case_border(case_x, case_y, corner)


        case_object = plate_object + case_wall
        if self.plate_only == True:
            case_object = plate_object
        
        # move case_object to line up with board

        side_margin_diff = self.right_margin - self.left_margin
        top_margin_diff = self.bottom_margin - self.top_margin

        self.logger.info('side_margin_diff: %s, top_margin_diff: %s', side_margin_diff, top_margin_diff)

        case_object = right((self.real_max_x / 2) + (side_margin_diff / 2)) ( back((self.real_max_y / 2) + (top_margin_diff / 2)) ( case_object ) )

        return case_object