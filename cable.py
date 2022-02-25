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
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # create formatter
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

            # add formatter to console_handler
            console_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)


        self.parameters = parameters

        self.stop_plate_thickness = 1

        self.stop_plate_overhang = 3

        self.clip_short_edge = 1.2

        self.clip_long_edge = 6

        self.clip_arm_thickness = 1

        self.clip_body_gap = 0.75

        self.inner_block_clip_offset = 1

        self.kerf = self.parameters.kerf * 2

        self.cable_hole_holder_offset = 0.5

        self.cable_holder_height = self.parameters.cable_hole_height - self.cable_hole_holder_offset # (self.parameters.kerf * 4)

        self.inner_block_width = self.parameters.cable_hole_width - (self.inner_block_clip_offset * 2) - (self.clip_arm_thickness * 2) 

        self.elipse_vertical = False
        self.elipse_horizontal = True
        self.elipse_ratio = .1
        self.x_scale = 1.0
        self.y_scale = 1.0

        if self.elipse_horizontal == True:
            self.x_scale = self.x_scale + self.elipse_ratio
            self.y_scale = self.y_scale - self.elipse_ratio
        if self.elipse_vertical == True:
            self.x_scale = self.x_scale - self.elipse_ratio
            self.y_scale = self.y_scale + self.elipse_ratio

        self.clamp_percentage = .9


        self.logger.debug('Cable Hole Witdh: %f', self.parameters.cable_hole_width)
        self.logger.debug('Cable Hole Height: %f', self.parameters.cable_hole_height)
        self.logger.debug('Cable Diameter: %f', self.parameters.cable_diameter)



    def holder_full(self):

        cable_hole_plate_width = self.parameters.cable_hole_width + (self.stop_plate_overhang * 2)
        # cable_hole_plate_height = self.parameters.cable_hole_height# + (self.stop_plate_overhang * 2)
        
        holder = cube([cable_hole_plate_width, self.cable_holder_height, self.stop_plate_thickness], center = True)

        clip_part = self.clip()
        clip_part = right((self.parameters.cable_hole_width / 2) - self.clip_arm_thickness - (self.cable_hole_holder_offset / 2)) (clip_part)
        clip_part += mirror([1, 0, 0]) ( clip_part )

        holder += clip_part

        # Add block that fills the width of the wall for more support
        holder += up((self.parameters.case_wall_thickness / 2) + (self.stop_plate_thickness / 2)) ( 
            cube([self.inner_block_width, self.cable_holder_height, self.parameters.case_wall_thickness], center = True)
        )


        holder -= self.holder_hole(include_slot = True)

        return holder



    def holder_hole(self, include_slot = False):
        hole = cylinder(
            r = self.parameters.cable_diameter / 2, 
            h = self.parameters.case_wall_thickness * 4, 
            center = True
        )

        
        hole = scale([self.x_scale, self.y_scale, 1.0]) ( hole )

        if include_slot == True:
            slot = forward(self.parameters.cable_diameter * 2, ) ( 
                cube(
                    [
                        self.parameters.cable_diameter, 
                        self.parameters.cable_diameter * 4, 
                        self.parameters.case_wall_thickness * 4
                    ], 
                    center = True
                )
            )

            slot = scale([self.x_scale, 1, 1]) ( slot )
            
            hole += slot
        
        return hole


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


    
    def holder_main(self):

        holder_main_body = self.holder_full()

        clamp_remove_block_height = self.cable_holder_height / 4

        clamp_remove_block = forward((self.cable_holder_height / 2) - (clamp_remove_block_height / 2)) ( 
            cube([self.inner_block_width * self.clamp_percentage, clamp_remove_block_height, self.parameters.case_wall_thickness * 4], center = True) 
        )

        holder_main_body -= clamp_remove_block

        return holder_main_body



    def holder_clamp(self):

        clamp_block_height = self.cable_holder_height / 4
        clamp_block_width = (self.inner_block_width * self.clamp_percentage) - (self.kerf * 2)

        clamp_depth = self.parameters.case_wall_thickness + (self.stop_plate_thickness * 3)

        clamp_block = forward((self.cable_holder_height / 2) - (clamp_block_height / 2)) ( 
            cube([clamp_block_width - .1, clamp_block_height, clamp_depth], center = True) 
        )

        slot = forward(self.cable_holder_height / 4) ( 
            cube(
                [
                    self.parameters.cable_diameter - .1, 
                    self.cable_holder_height / 2, 
                    clamp_depth
                ], 
                center = True
            )
        )

        clamp_block += scale([self.x_scale, 1, 1]) ( slot )

        clamp_block = up((self.parameters.case_wall_thickness / 2)) ( clamp_block )

        surround_block = forward(self.cable_holder_height / 4) ( 
            cube(
                [
                    clamp_block_width - .1, 
                    self.cable_holder_height / 2, 
                    self.stop_plate_thickness - self.kerf * 2
                ], 
                center = True
            )
        )

        clamp_block += up((clamp_depth / 2) + self.stop_plate_thickness + self.kerf) ( surround_block )

        clamp_block += down(self.stop_plate_thickness + self.kerf) ( surround_block )

        clamp_block -= back(self.kerf ) ( self.holder_hole() )

        return clamp_block



    def holder_all(self):

        return self.holder_main() + up(0) ( self.holder_clamp() )


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