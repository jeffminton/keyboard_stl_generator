from solid import *
from solid.utils import *

import logging

from parameters import Parameters


class Cable():

    def __init__(self, parameters: Parameters = None):


        self.logger = logging.getLogger().getChild(__name__)

        self.parameters = parameters

        # length and thickness of the pabck pannel that exends beyond the cable hole 
        # to prevent the holder from falling into the case
        self.stop_plate_thickness = 1
        self.stop_plate_overhang = 3

        # Clip parameters
        # Clip triangle parameters
        self.clip_short_edge = 1.2
        self.clip_long_edge = 6
        self.clip_arm_thickness = 1
        # spacing between the clip and the cable hole wall
        self.clip_body_gap = 0.75

        # holder support block parameters
        # The spacing between the clips and the suport block
        self.inner_block_clip_offset = 1
        # Width ofthe support block
        self.inner_block_width = self.parameters.cable_hole_width - (self.inner_block_clip_offset * 2) - (self.clip_arm_thickness * 2) 


        # Gap to allow between the cable hole size and the clip size
        # Needed to accounts for the impoerfections in the printing that can cause holes to be smaller than defined
        self.cable_hole_holder_offset = 0.5

        self.cable_holder_height = self.parameters.cable_hole_height - self.cable_hole_holder_offset # (self.parameters.kerf * 4)

        # Parameters to shape the cable holder hole into an elipse that is either horizontal or vertical
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

        # Clamp parameters
        # The width of the clapm is a percentage of the width of the suport block
        # This defines the clamp percentage
        self.clamp_percentage = .9
        self.clamp_holder_gap = .1 # self.parameters.kerf * 2
        self.clamp_block_height = self.cable_holder_height / 4
        self.clamp_block_width = (self.inner_block_width * self.clamp_percentage)# - (self.clamp_holder_gap * 2)
        # Set a value that will reduce the height of the cable hole when the clamp is inserted
        self.clamp_hole_offset = .1
        self.clamp_height_percent_of_holder_height = .75


        self.logger.debug('Cable Hole Witdh: %f', self.parameters.cable_hole_width)
        self.logger.debug('Cable Hole Height: %f', self.parameters.cable_hole_height)
        self.logger.debug('Cable Diameter: %f', self.parameters.cable_diameter)



    def holder_full(self):

        # Calculate the total stop plate width
        cable_hole_plate_width = self.parameters.cable_hole_width + (self.stop_plate_overhang * 2)
        # cable_hole_plate_height = self.parameters.cable_hole_height# + (self.stop_plate_overhang * 2)
        
        # Create stop plate. The stop clock only extends to the sides of the cable holder
        holder = cube([cable_hole_plate_width, self.cable_holder_height, self.stop_plate_thickness], center = True)

        # Get clip object
        clip_part = self.clip()

        # Move clip to the right and mirror it for the left side clip
        clip_part = right((self.parameters.cable_hole_width / 2) - self.clip_arm_thickness - (self.cable_hole_holder_offset / 2)) (clip_part)
        clip_part += mirror([1, 0, 0]) ( clip_part )

        # Add clips to the holder
        holder += clip_part

        # Add block that fills the width of the wall for more support
        holder += up((self.parameters.case_wall_thickness / 2) + (self.stop_plate_thickness / 2)) ( 
            cube([self.inner_block_width, self.cable_holder_height, self.parameters.case_wall_thickness], center = True)
        )

        # Remvoe the 
        holder -= self.holder_hole(include_slot = True)

        return holder



    def holder_hole(self, include_slot = False):
        
        # Main cable hole
        hole = cylinder(
            r = self.parameters.cable_diameter / 2, 
            h = self.parameters.case_wall_thickness * 4, 
            center = True
        )

        # Transform cable hole into elipse in direction defined above
        hole = scale([self.x_scale, self.y_scale, 1.0]) ( hole )


        if include_slot == True:
            # Include a slot above the hole that will accept the cable and clamp
            # Slot object
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

            # Scale slot to match the x size of the hole elipse
            slot = scale([self.x_scale, 1, 1]) ( slot )
            
            hole += slot
        
        return hole


    def clip(self):

        # Clip polygon
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
        
        # Get full holder
        holder_main_body = self.holder_full()

        # Create block that will be removed from the main holde rto make space for the clamp
        clamp_remove_block = self.holder_clamp(clamp_remove_block = True)

        # Remove clamp remove block from main holder
        holder_main_body -= clamp_remove_block

        return holder_main_body



    def holder_clamp(self, clamp_remove_block = False):
        # Declare parameters used to provide spacing for the clamp in the main cable holder
        clamp_holder_gap = self.clamp_holder_gap
        clamp_holder_extra = 0.0

        if clamp_remove_block == True:
            clamp_holder_gap = 0.0
            clamp_holder_extra = self.clamp_holder_gap
        
        # Set the depth of the clapm and include the stop plate tickness and space for the sorrinuding clamp blocks
        clamp_depth = self.parameters.case_wall_thickness + (self.stop_plate_thickness * 3)

        # Create clamp block
        clamp_block = forward((self.cable_holder_height / 2) - (self.clamp_block_height / 2) + (clamp_holder_gap)) ( 
            cube([self.clamp_block_width + (clamp_holder_extra * 2), self.clamp_block_height - (clamp_holder_gap * 2), clamp_depth], center = True) 
        )

        # Create strip that will fit into the cable hole slot
        strip = forward(self.clamp_block_height) ( 
            cube(
                [
                    self.parameters.cable_diameter - (clamp_holder_gap * 2), 
                    self.cable_holder_height / 2, 
                    clamp_depth
                ], 
                center = True
            )
        )

        # Scale strip to match x sacale of cable hole
        clamp_block += scale([self.x_scale, 1, 1]) ( strip )

        # Move block up to allign with holder body
        clamp_block = up((self.parameters.case_wall_thickness / 2)) ( clamp_block )

        # Get the clamp height as a percentage of the whole holder height
        clamp_height = self.cable_holder_height * self.clamp_height_percent_of_holder_height

        # Set offset for surround block height
        surround_block_height_offset = (self.cable_holder_height - clamp_height) #(clamp_holder_gap * 24)

        # Create surround block
        surround_block = forward((surround_block_height_offset / 2)) ( # forward(self.clamp_block_height - self.clamp_hole_offset) ( 
            cube(
                [
                    self.clamp_block_width + (clamp_holder_extra * 2), 
                    clamp_height,
                    self.stop_plate_thickness - (clamp_holder_gap * 2)
                ], 
                center = True
            )
        )

        # Add a instance of the curround block to one end and another end of the clamp block
        clamp_block += up( ( clamp_depth / 2 ) + self.stop_plate_thickness + clamp_holder_gap) ( surround_block )
        clamp_block += down(self.stop_plate_thickness + clamp_holder_gap) ( surround_block )

        # Remove a 180 degree rotated version of the cable hole with a slot from the clamp block
        clamp_block -= back(self.clamp_hole_offset) ( rotate(180, [0, 0, 1]) ( self.holder_hole(include_slot = True) ) )

        return clamp_block



    def holder_all(self):

        # Get a version of the cable holder with the main holder and clamp in an assembled view
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