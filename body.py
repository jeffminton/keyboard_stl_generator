from ast import Param
import math

from solid import *
from solid.utils import *

import logging

from cell import Cell
from support import Support
from parameters import Parameters


class Body():

    def __init__(self, parameters: Parameters = Parameters()):

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

        self.parameters = parameters

        self.x_build_size = self.parameters.x_build_size
        self.y_build_size = self.parameters.y_build_size

        self.top_margin = self.parameters.top_margin
        self.bottom_margin = self.parameters.bottom_margin
        self.left_margin = self.parameters.left_margin
        self.right_margin = self.parameters.right_margin
        self.case_height = self.parameters.case_height
        self.case_wall_thickness = self.parameters.case_wall_thickness
        self.plate_thickness = self.parameters.plate_thickness
        self.plate_corner_radius = self.parameters.plate_corner_radius
        self.plate_supports = self.parameters.plate_supports
        self.support_bar_height = self.parameters.support_bar_height
        self.support_bar_width = self.parameters.support_bar_width

        # self.create_screw_holes = False
        self.screw_count = self.parameters.screw_count
        self.screw_diameter = self.parameters.screw_diameter
        self.screw_edge_inset = self.parameters.screw_edge_inset
        self.screw_hole_body_wall_width = 2
        self.screw_hole_body_support_x_factor = 4

        self.bottom_cover_thickness = self.parameters.bottom_cover_thickness

        self.case_height_extra = 30

        self.min_x = 0.0
        self.max_x = 0.0
        self.min_y = 0.0
        self.max_y = 0.0

        self.real_max_x = 0.0
        self.real_max_y = 0.0
        self.real_case_width = 0.0
        self.real_case_height = 0.0

        # self.parameter_dict = parameter_dict

        # if self.parameter_dict is not None:
        #     self.build_attr_from_dict(self.parameter_dict)

        self.screw_hole_coordinates = []

        self.screw_hole_info = {}

        # Calculated attributes
        self.update_calculated_attributes()

        # self.x_build_size = 200.0
        # self.y_build_size = 200.0

        # self.top_margin = 8.0
        # self.bottom_margin = 8.0
        # self.left_margin = 8.0
        # self.right_margin = 8.0
        # self.case_height = 10
        # self.case_wall_thickness = 2.0
        # self.plate_thickness = 1.511
        # self.plate_corner_radius = 4
        # self.plate_only = False
        # self.plate_supports = False
        # self.support_bar_height = 3.0
        # self.support_bar_width = 1.0

        # self.create_screw_holes = False
        # self.screw_count = 4
        # self.screw_diameter = 4
        # self.screw_edge_inset = 8
        # self.screw_hole_body_wall_width = 2
        # self.screw_hole_body_support_x_factor = 4

        # self.bottom_cover_thickness = 2.0

        # self.case_height_extra = 30

        # self.min_x = 0.0
        # self.max_x = 0.0
        # self.min_y = 0.0
        # self.max_y = 0.0

        # self.real_max_x = 0.0
        # self.real_max_y = 0.0
        # self.real_case_width = 0.0
        # self.real_case_height = 0.0

        # self.parameter_dict = parameter_dict

        # if self.parameter_dict is not None:
        #     self.build_attr_from_dict(self.parameter_dict)

        # self.screw_hole_coordinates = []

        # self.screw_hole_info = {}

        # # Calculated attributes
        # self.update_calculated_attributes()

    
    def update_calculated_attributes(self):
        # Calculated attributes
        self.case_height_base_removed = self.case_height - self.bottom_cover_thickness
        self.case_height_extra_fill = self.case_height + self.case_height_extra
        self.side_margin_diff = self.right_margin - self.left_margin
        self.top_margin_diff = self.bottom_margin - self.top_margin
        self.screw_tap_hole_diameter = self.screw_diameter - 0.35
        self.screw_hole_body_diameter = self.screw_diameter + (self.screw_hole_body_wall_width * 2)
        self.screw_hole_body_radius = self.screw_hole_body_diameter / 2
        self.x_screw_width = self.real_case_width - ((self.screw_edge_inset * 2))# + self.screw_diameter)
        self.y_screw_width = self.real_case_height - ((self.screw_edge_inset * 2))# + self.screw_diameter)
        self.bottom_section_count = math.ceil(self.real_case_width / self.x_build_size)
        # self.screw_hole_body_support_end_x = (self.case_height_extra_fill / self.screw_hole_body_support_x_factor) + x_offset


    def set_dimensions(self, max_x, min_y, min_x, max_y):

        self.max_x = max_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.logger.debug('min_x: %f, max_x: %f, max_y: %f, min_y: %f', self.min_x, self.max_x, self.max_y, self.min_y)

        # Get rhe calculated real max and y sizes of the board
        self.real_max_x = Cell.u(self.max_x)
        self.real_max_y = Cell.u(abs(self.min_y))

        self.real_case_width = self.real_max_x + self.left_margin + self.right_margin
        self.real_case_height = self.real_max_y + self.top_margin + self.bottom_margin

        self.logger.debug('real_max_x: %d, real_max_y: %s', self.real_max_x, self.real_max_y)

        self.update_calculated_attributes()


    def build_attr_from_dict(self, parameter_dict):
        for param in parameter_dict.keys():
            value = parameter_dict[param]
            
            setattr(self, param, value)

            if param == 'screw_count':
                self.logger.debug('%s: %s, self.screw_count: %s', str(param), str(value), str(self.screw_count))
    
    
    def set_parameter_dict(self, parameter_dict):
        self.parameter_dict = parameter_dict
        self.build_attr_from_dict(self.parameter_dict)
        self.update_calculated_attributes()

    def plate(self, case_x, case_y, pre_minkowski_thickness, corner):
        # Get absolute value of min_y to get real y value
        max_y = abs(self.min_y)

        # Create plate and round the corners using cylcinder that was passed in
        plate_object = cube([case_x, case_y, pre_minkowski_thickness], center = True)
        plate_object = minkowski() ( plate_object, corner )

        plate_object = right((self.real_max_x / 2) + (self.side_margin_diff / 2)) ( back((self.real_max_y / 2) + (self.top_margin_diff / 2)) ( plate_object ) )

        self.logger.debug('self.plate_supports: %s', str(self.plate_supports))

        # screw_holes = self.screw_hole_objects()
        # if screw_holes is not None:
        #     plate_object -= screw_holes

        # If palte supprts should be added
        if self.plate_supports == True:
            # Get the ceiling values for the max x and y so thet we loop ove all spaces
            max_x_ceil = math.ceil(self.max_x)
            max_y_ceil = math.ceil(max_y)
            self.logger.debug('range(max_x_ceil): %s, range(max_y_ceil): %s', str(range(max_x_ceil)), str(range(max_y_ceil)))
            
            # Build full border to ensure outside edges are full suppport width
            perimeter_x = Cell.u(self.max_x) + self.support_bar_width
            perimeter_y = Cell.u(max_y) + self.support_bar_width
            perimeter_height = self.support_bar_height + self.plate_thickness
            perimeter = left(self.support_bar_width / 2) ( back(self.support_bar_width / 2) ( cube([perimeter_x, perimeter_y, perimeter_height]) ) )

            perimeter_inner = cube([Cell.u(self.max_x), Cell.u(max_y), self.support_bar_height])

            perimeter -= perimeter_inner

            perimeter = down(self.support_bar_height + (self.plate_thickness / 2)) ( perimeter )

            perimeter = back(Cell.u(max_y)) ( perimeter )

            plate_object += perimeter

            # For each x in the ceiling of max_x
            for x in range(max_x_ceil):
                # Set support width
                w = 1.0
                # Find diff between farthest end of support and max x
                max_x_diff = self.max_x - (x + w)
                # If the support would go beyond the max x reduce the width to fit
                if max_x_diff < 0:
                    # Reduce w to be remaining x value
                    w = self.max_x - x
                # For each y in the ceiling of max_y
                for y in range(max_y_ceil):
                    self.logger.debug('x: %f, y: %f', x, y)
                    # Set support height
                    h = 1.0
                    # Find diff between top of support and max y
                    max_y_diff = max_y - (y + h)
                    # If the support would go beyond the max y reduce the heght to fit
                    if max_y_diff < 0:
                        # Reduce h to be remaining y value
                        h = max_y - y

                    # Get X and Y offset to move support to corect location
                    # x_offset = x - ((self.real_max_x / 2) + (self.side_margin_diff / 2)) / Cell.SWITCH_SPACING
                    # y_offset = -(y - ((self.real_max_y / 2) + (self.top_margin_diff / 2)) / Cell.SWITCH_SPACING)
                    x_offset = x
                    y_offset = -y
                    
                    # Add support object to plate
                    plate_object += Support(x_offset, y_offset, w, h, self.plate_thickness, self.support_bar_height, self.support_bar_width).get_moved()

        # eturn palte object
        return plate_object


    def case_body_block(self, case_x, case_y, corner):
        # Create case wall part
        case_block = cube([case_x, case_y, self.case_height_extra_fill], center = True)

        # Round the corners of the case wall and
        case_block = minkowski() (case_block, corner)

        return case_block


    def case_border(self, case_x, case_y, corner):
        # Create case wall part
        case_wall = self.case_body_block(case_x, case_y, corner)

        # Create inner area that will be removed from case wall 
        case_inner = cube([case_x - (self.case_wall_thickness * 2), case_y - (self.case_wall_thickness * 2), self.case_height_extra_fill * 2], center = True)

        # Round the corners of the case wall and case inner
        case_inner = minkowski() (case_inner, corner)

        # Remove the innser empty space from the case wall
        case_wall -= case_inner

        # Move case wall to match origin of rest of keyboard
        self.logger.debug('side_margin_diff: %s, top_margin_diff: %s', self.side_margin_diff, self.top_margin_diff)
        case_wall = right((self.real_max_x / 2) + (self.side_margin_diff / 2)) ( back((self.real_max_y / 2) + (self.top_margin_diff / 2)) ( case_wall ) )

        # Move case wall down to match with the top of the plate
        case_wall = down(self.case_height_extra_fill / 2) ( case_wall )

        # Return the case wall object
        return case_wall

    def case(self, body_block_only = False, plate_only = False):
        # Get the margins for the plate without the ammount that the minkowski will add
        pre_minkowski_x_margin = ((self.right_margin + self.left_margin) / 2 - self.plate_corner_radius)
        pre_minkowski_y_margin = ((self.top_margin + self.bottom_margin) / 2 - self.plate_corner_radius)

        # get the pre minkowski plate sizes
        case_x = self.real_max_x + (pre_minkowski_x_margin * 2)
        case_y = self.real_max_y + (pre_minkowski_y_margin * 2)

        # Get the plate thickness before the minkowski
        pre_minkowski_thickness = self.plate_thickness / 2

        # Create cylinder to be used for rounding case and palte border
        corner = cylinder(r = self.plate_corner_radius, h = pre_minkowski_thickness, center = True)

        # Create Plate object. Add it to function return case object
        case_object = self.plate(case_x, case_y, pre_minkowski_thickness, corner)

        # If not only making the plate add the case border to the case object
        if plate_only == False:
            case_object += self.case_border(case_x, case_y, corner)

        # move case_object to line up with board
        case_object = case_object

        if body_block_only == True:
            case_object = self.case_body_block(case_x, case_y, corner)
            case_object = right((self.real_max_x / 2) + (self.side_margin_diff / 2)) ( back((self.real_max_y / 2) + (self.top_margin_diff / 2)) ( case_object ) )

            # Move case wall down to match with the top of the plate
            case_object = down(self.case_height_extra_fill / 2) ( case_object )

        return case_object


    def screw_hole(self, tap = False):
        try:
            if tap == False:
                radius = self.screw_diameter / 2
            else:
                radius = self.screw_tap_hole_diameter / 2
        except:
            return None

        return cylinder(r = radius, h = self.case_height_extra_fill * 4, center = True)


    def screw_hole_body_support(self, direction = 'right', screw_name = ''):
        # self.logger.info('screw_hole_body_support: screw_name: %s, direction: %s', screw_name, direction)
        x_offset = self.screw_hole_body_radius
        screw_hole_body_support_end_x = (self.case_height_extra_fill / self.screw_hole_body_support_x_factor) + x_offset
        poly_points = [
            [0, 0],
            [0, self.case_height_extra_fill],
            [x_offset, self.case_height_extra_fill],
            # [(self.case_height_extra_fill / self.screw_hole_body_support_x_factor) + x_offset, 0]
            [screw_hole_body_support_end_x, 0]
        ]
        poly_path = [[0, 1, 2, 3]]

        # self.logger.info(poly_points)

        hole_support = polygon(poly_points, poly_path)
        hole_support = linear_extrude(height = 2, center = True) ( hole_support )
        hole_support = rotate(90, [1, 0, 0]) ( hole_support )

        self.screw_hole_info[screw_name]['support_directions'][direction] = screw_hole_body_support_end_x

        if direction == 'right':
            return hole_support
        elif direction == 'left':
            return rotate(180, [0, 0, 1]) ( hole_support )
        elif direction == 'forward':
            return rotate(90, [0, 0, 1]) ( hole_support )
        elif direction == 'back':
            return rotate(270, [0, 0, 1]) ( hole_support )

        return hole_support


    def screw_hole_body(self, left_support = False, right_support = False, forward_support = False, back_support = False, screw_name = ''):

        hole_body = cylinder(r = self.screw_hole_body_radius, h = self.case_height_extra_fill)


        if right_support == True:
            hole_body += self.screw_hole_body_support('right', screw_name)
        if left_support == True:
            hole_body += self.screw_hole_body_support('left', screw_name)
        if forward_support == True:
            hole_body += self.screw_hole_body_support('forward', screw_name)
        if back_support == True:
            hole_body += self.screw_hole_body_support('back', screw_name)
            

        return hole_body


    def generate_screw_holes_coordinates(self):

        screw_hole_collection = union()
        corner_count = 4
        remaining_screws = 0

        # screw_radius = self.screw_diameter / 2

        screw_set_min_x = 0
        screw_set_min_y = 0

        self.logger.debug('self.real_case_width: %f, self.screw_edge_inset: %f, self.screw_diameter: %f', self.real_case_width, self.screw_edge_inset, self.screw_diameter)
        self.logger.debug('self.real_case_width - ((self.screw_edge_inset * 2) + self.screw_diameter): %f', self.real_case_width - ((self.screw_edge_inset * 2) + self.screw_diameter))

        x_screw_count = 0
        y_screw_count = 0

        # Bottom Left
        self.screw_hole_coordinates.append([0, 0])
        # Top Left
        self.screw_hole_coordinates.append([0, self.y_screw_width])
        # Top Right
        self.screw_hole_coordinates.append([self.x_screw_width, self.y_screw_width])
        # Bottom Right
        self.screw_hole_coordinates.append([self.x_screw_width, 0])

        remaining_screw_count = int((self.screw_count - 4) / 2)

        # self.logger.info('remaining_screw_count: %f', type(remaining_screw_count))

        x_per_screw_spacing = 0
        y_per_screw_spacing = 0

        for i in range(remaining_screw_count):
            x_per_screw_spacing = self.x_screw_width / (x_screw_count + 1)
            y_per_screw_spacing = self.y_screw_width / (y_screw_count + 1)

            if x_per_screw_spacing >= y_per_screw_spacing:
                x_screw_count += 1
            else:
                y_screw_count += 1

            self.logger.debug('x_screw_count: %d, y_screw_count: %d', x_screw_count, y_screw_count)

        x_per_screw_spacing = self.x_screw_width / (x_screw_count + 1)
        y_per_screw_spacing = self.y_screw_width / (y_screw_count + 1)

        self.logger.debug('x_per_screw_spacing: %f, y_per_screw_spacing: %f', x_per_screw_spacing, y_per_screw_spacing)

        for i in range(x_screw_count):
            # Top Screws
            self.screw_hole_coordinates.append([(i + 1) * x_per_screw_spacing, self.y_screw_width])
            # Bottom Screws
            self.screw_hole_coordinates.append([(i + 1) * x_per_screw_spacing, 0])

        for i in range(y_screw_count):
            # Left Screws
            self.screw_hole_coordinates.append([0, (i + 1) * y_per_screw_spacing])
            # Right Screws
            self.screw_hole_coordinates.append([self.x_screw_width, (i + 1) * y_per_screw_spacing])

        # for coord in self.screw_hole_coordinates:
        #     self.logger.debug(coord)

        for coords in self.screw_hole_coordinates:
            coords_string = str(coords[0]) + ',' + str(coords[1])
            # coords_string = ','.join(coords)
            self.screw_hole_info[coords_string] = {
                'coordinates': coords,
                'x': coords[0] + self.screw_edge_inset,
                'y': coords[1] + self.screw_edge_inset,
                'support_directions': {
                    'right': 0.0,
                    'left': 0.0,
                    'forward': 0.0,
                    'back': 0.0
                }
            }
        

    def screw_hole_objects(self, tap = False):

        if len(self.screw_hole_info.keys()) == 0:
            self.generate_screw_holes_coordinates()

        screw_hole_collection = union()
        screw_hole_body_collection = union()
        screw_hole_body_scaled_collection = union()
        corner_count = 4
        remaining_screws = 0
        
        for coord_string in self.screw_hole_info.keys():
            coord = self.screw_hole_info[coord_string]['coordinates']
            x = coord[0]
            y = coord[1]

            # self.logger.info('coord: %s, self.x_screw_width: %f, self.y_screw_width: %f', str(coord), self.x_screw_width, self.y_screw_width)
            # Skip the center top screw hole if it is in the top center and the case has a cable hole
            if self.parameters.cable_hole == True and y == self.y_screw_width and x == self.x_screw_width / 2:
                # self.logger.info('coord: %s', str(coord))
                continue

            hole = right(x) ( forward(y) ( self.screw_hole(tap = tap) ) )
            screw_hole_collection += hole

            right_support = False
            left_support = False
            forward_support = False
            back_support = False

            if x == 0 and y == 0:
                forward_support = True
                right_support = True
            elif x == 0 and y == self.y_screw_width:
                back_support = True
                right_support = True
            elif x == self.x_screw_width and y == self.y_screw_width:
                back_support = True
                left_support = True
            elif x == self.x_screw_width and y == 0:
                forward_support = True
                left_support = True
            elif y != self.y_screw_width and y != 0:
                forward_support = True
                back_support = True
            elif x != self.x_screw_width and x != 0:
                right_support = True
                left_support = True

            hole_body = self.screw_hole_body(right_support = right_support, left_support = left_support, forward_support = forward_support, back_support = back_support, screw_name = coord_string)
            scaled_hole_body = scale([1.0, 1.0, 1.0]) (hole_body)

            hole_body = right(x) (
                forward(y) (
                    hole_body
                )
            )

            scaled_hole_body = right(x) (
                forward(y) (
                    scaled_hole_body
                )
            )


            screw_hole_body_collection += hole_body
            screw_hole_body_scaled_collection += scaled_hole_body

        x_offset = (-self.left_margin) + self.screw_edge_inset

        # x_offset = (-self.left_margin)
        y_offset = (self.real_max_y + self.bottom_margin) - self.screw_edge_inset

        # self.logger.info('-self.left_margin: %f, self.screw_edge_inset: %f, x_offset: %f', -self.left_margin, self.screw_edge_inset, x_offset)

        screw_hole_collection = right(x_offset) ( 
            back(y_offset) (
                screw_hole_collection
            )
        )

        screw_hole_body_collection = right(x_offset) (
            back(y_offset) (
                down(self.case_height_extra_fill + (self.plate_thickness / 2)) (
                    screw_hole_body_collection
                )
            )
        )

        screw_hole_body_scaled_collection = right(x_offset) (
            back(y_offset) (
                down(self.case_height_extra_fill + (self.plate_thickness / 2)) (
                    screw_hole_body_scaled_collection
                )
            )
        )

        return screw_hole_collection, screw_hole_body_collection, screw_hole_body_scaled_collection
        
    

    def bottom_cover(self):

        if self.bottom_cover_thickness > 0:
            plate = down(self.bottom_cover_thickness) ( left(self.real_case_width / 2) ( back(self.real_case_height / 2) ( cube([self.real_case_width * 2, self.real_case_height * 2, self.bottom_cover_thickness]) ) ) )
        else:
            plate = union()

        return plate
