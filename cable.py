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

        self.inner_block_clip_offset = 1

        self.kerf = self.parameters.kerf * 2

        self.cable_holder_height = self.parameters.cable_hole_height - self.parameters.kerf



        self.logger.debug('Cable Hole Witdh: %f', self.parameters.cable_hole_width)
        self.logger.debug('Cable Hole Height: %f', self.parameters.cable_hole_height)
        self.logger.debug('Cable Diameter: %f', self.parameters.cable_diameter)



    def holder_full(self):

        cable_hole_plate_width = self.parameters.cable_hole_width + (self.stop_plate_overhang * 2)
        cable_hole_plate_height = self.parameters.cable_hole_height# + (self.stop_plate_overhang * 2)
        
        holder = cube([cable_hole_plate_width, cable_hole_plate_height, self.stop_plate_thickness], center = True)

        clip_part = self.clip()

        clip_part = right((self.parameters.cable_hole_width / 2) - self.clip_arm_thickness) (clip_part)

        clip_part += mirror([1, 0, 0]) ( clip_part )

        holder += clip_part

        inner_block_width = self.parameters.cable_hole_width - (self.inner_block_clip_offset * 2) - (self.clip_arm_thickness * 2) 

        holder += up((self.parameters.case_wall_thickness / 2) + (self.stop_plate_thickness / 2)) ( 
            cube([inner_block_width, self.cable_holder_height, self.parameters.case_wall_thickness], center = True)
        )

        hole = scale([.95, 1.05, 1.0]) ( 
            cylinder(
                r = self.parameters.cable_diameter / 2, 
                h = self.parameters.case_wall_thickness * 4, 
                center = True
            )
        )

        holder -= hole

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

        solid = linear_extrude(height = self.cable_holder_height, center = True) (shape)

        solid = rotate(90, [1, 0, 0]) (solid)

        return solid


    def holder_side(self, side):

        diff_block = cube(
            [
                self.parameters.cable_hole_width * 2, 
                self.cable_holder_height * 2, 
                (self.parameters.case_wall_thickness + self.clip_long_edge) * 2
            ], 
            center = True
        )

        key_block = left((self.parameters.cable_diameter / 4)) ( cube(
            [
                (self.parameters.cable_diameter / 2), 
                (self.parameters.cable_diameter * 2), 
                (self.parameters.case_wall_thickness + self.clip_long_edge) * 2
            ], 
            center = True
        ))

        if side == 'right':
            diff_block = left((self.parameters.cable_hole_width) - self.kerf + (self.parameters.cable_diameter / 4)) (diff_block)
            diff_block +=  resize([0, (self.parameters.cable_diameter * 2) + (self.kerf *2), 0], auto = [False, True, True]) ( right(self.kerf) ( key_block ) )
            # diff_block += right(self.kerf) ( key_block )
        elif side == 'left':
            diff_block = right((self.parameters.cable_hole_width) - self.kerf - (self.parameters.cable_diameter / 4)) (diff_block)
            diff_block -= key_block

        return self.holder_full() - diff_block

    def holder_all(self):

        return self.holder_side('right') + up(0) ( self.holder_side('left') )


    def get_cable_hole(self):

        if self.parameters.cable_hole == True:
            return up(self.parameters.case_height_base_removed - (self.parameters.cable_hole_height / 2) - self.parameters.plate_thickness - self.parameters.cable_hole_down_offset ) (
                right(self.parameters.left_margin + (self.parameters.real_max_x / 2)) ( 
                    forward(self.parameters.bottom_margin + self.parameters.top_margin + self.parameters.real_max_y) ( 
                        cube([self.parameters.cable_hole_width, self.parameters.case_wall_thickness * 2, self.parameters.cable_hole_height], center = True) 
                    ) 
                ) 
            )
        else:
            return union()