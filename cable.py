from solid import *
from solid.utils import *

import logging

from parameters import Parameters


class Cable():

    def __init__(self, parameters: Parameters = None):


        self.logger = logging.getLogger('Cable')
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


        self.parameters = parameters

        self.stop_plate_thickness = 1

        self.stop_plate_overhang = 3

        self.clip_short_edge = 1

        self.clip_long_edge = 6

        self.clip_arm_thickness = 1

        self.clip_body_gap = 0.1

        self.inner_block_clip_offset = 0.2



    def holder_full(self):

        cable_hole_plate_width = self.parameters.cable_hole_width + (self.stop_plate_overhang * 2)
        cable_hole_plate_height = self.parameters.cable_hole_height + (self.stop_plate_overhang * 2)

        
        holder = cube([cable_hole_plate_width, cable_hole_plate_height, self.stop_plate_thickness], center = True)

        clip_part = self.clip()

        clip_part = right((self.parameters.cable_hole_width / 2) - self.clip_arm_thickness) (clip_part)

        clip_part += mirror([1, 0, 0]) ( clip_part )

        holder += clip_part

        inner_block_width = self.parameters.cable_hole_width - (self.inner_block_clip_offset * 2) - (self.clip_arm_thickness * 2) 

        holder += up((self.parameters.case_wall_thickness / 2) + (self.stop_plate_thickness / 2)) ( 
            cube([inner_block_width, self.parameters.cable_hole_height, self.parameters.case_wall_thickness], center = True)
        )

        return holder



    def clip(self):

        poly_points = [
            [0, 0],
            [0, self.parameters.case_wall_thickness + self.clip_long_edge],
            [self.clip_arm_thickness + self.clip_short_edge, self.parameters.case_wall_thickness + self.clip_body_gap],
            [self.clip_arm_thickness, self.parameters.case_wall_thickness + self.clip_body_gap],
            [self.clip_arm_thickness, 0]
        ]

        poly_path = [range(len(poly_points))]

        shape = polygon(poly_points, poly_path)

        solid = linear_extrude(height = self.parameters.cable_hole_height, center = True) (shape)

        solid = rotate(90, [1, 0, 0]) (solid)

        return solid