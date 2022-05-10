

import math
import logging
import sys

from solid import *
from solid.utils import *

from switch import Switch
from support import Support
from support_cutout import SupportCutout
from cell import Cell
from item_collection import ItemCollection
from rotation_collection import RotationCollection
from body import Body
from pcb import PCB
from switch_config import SwitchConfig
from parameters import Parameters
from cable import Cable
from shape_cutout import ShapeCutout



class Keyboard():

    def __init__(self, parameters: Parameters = Parameters()):

        self.parameters = parameters

        self.logger = logging.getLogger().getChild(__name__)
        
        self.modifier_include_list = ['x', 'y', 'w', 'h', 'r', 'rx', 'ry', 'd']

        self.kerf = self.parameters.kerf

        self.body = None

        self.desired_section_number = -1

        self.cable_hole_up_offset = self.parameters.cable_hole_up_offset
        self.cable_hole_down_offset = self.parameters.cable_hole_down_offset

        self.cable_hole = self.parameters.cable_hole

        self.switch_type = self.parameters.switch_type
        self.stabilizer_type = self.parameters.stabilizer_type

        self.switch_config = self.parameters.switch_config

        self.build_x = math.floor(parameters.x_build_size / self.parameters.switch_spacing)
        self.build_y = math.floor(parameters.y_build_size / self.parameters.switch_spacing)

        self.switch_collection = ItemCollection()
        self.support_collection = ItemCollection()
        self.support_cutout_collection = ItemCollection()
        self.switch_rotation_collection = RotationCollection(self.parameters)
        self.support_rotation_collection = RotationCollection(self.parameters)
        self.support_cutout_rotation_collection = RotationCollection(self.parameters)

        self.custom_polygon_collection = ItemCollection()

        self.switch_cutouts = union()
        self.switch_supports = union()
        self.switch_support_cutouts = union()
        self.rotate_switch_cutout_collection = union()
        self.rotate_support_collection = union()
        self.rotate_support_cutout_collection = union()

        self.custom_polygon_cutout_collection = union()

        self.switch_section_list = [ItemCollection()]
        self.support_section_list = [ItemCollection()]
        self.support_cutout_section_list = [ItemCollection()]

        self.cable = Cable(parameters)



    def process_keyboard_layout(self, keyboard_layout_dict):
        y = 0.0
        rotation = 0.0
        rx = 0.0
        ry = 0.0
        # r_x_offset = 0.0
        # r_y_offset = 0.0
        
        for row in keyboard_layout_dict:
            x = 0.0
            w = 1.0
            h = 1.0

            if type(row) == type([]):
                # A flag to be used to ignore non key data from the layout file
                ignore_next = False
                for col in row:               
                    if type(col) == type({}):

                        for key in col.keys():
                            modifier_type = key
                            
                            if modifier_type in self.modifier_include_list:
                                size = float(col[key])
                                if modifier_type == 'w':
                                    w = size
                                if modifier_type == 'h':
                                    h = size
                                if modifier_type == 'x':
                                    x += size
                                    r_x_offset = size
                                if modifier_type == 'y':
                                    y += size
                                    r_y_offset = size
                                if modifier_type == 'r':
                                    rotation = size
                                    y = 0
                                    x = 0
                                if modifier_type == 'rx':
                                    rx = size
                                if modifier_type == 'ry':
                                    ry = size
                                if modifier_type == 'd':
                                    # self.logger.debug('Ignore next Item')
                                    ignore_next = True
                        
                    elif ignore_next == False:
                        col_escaped = col.encode("unicode_escape").decode("utf-8")
                        # split on newline character and get the lat element in the resulting list
                        col_escaped = col_escaped.split('\\n')[-1]
                        # self.logger.debug('column value: %s', col_escaped)
                        
                        x_offset = x
                        y_offset = -(y)

                        switch = Switch(x_offset, y_offset, w, h, rotation = rotation, cell_value = col_escaped, switch_config = self.switch_config, parameters = self.parameters)
                        support = Support(x_offset, y_offset, w, h, self.parameters.plate_thickness, self.parameters.support_bar_height, self.parameters.support_bar_width, rotation = rotation, parameters = self.parameters)
                        support_cutout = SupportCutout(x_offset, y_offset, w, h, self.parameters.plate_thickness, self.parameters.support_bar_height, self.parameters.support_bar_width, rotation = rotation, parameters = self.parameters)

                        # Create switch cutout and support object without rotation
                        if rotation == 0.0:
                            self.switch_collection.add_item(x_offset, y_offset, switch)    
                            self.support_collection.add_item(x_offset, y_offset, support)
                            self.support_cutout_collection.add_item(x_offset, y_offset, support_cutout)
                            
                            
                        # Create switch cutout and support object without rotation
                        elif rotation != 0.0:
                            self.switch_rotation_collection.add_item(rotation, x_offset, y_offset, switch, rx, ry)
                            self.support_rotation_collection.add_item(rotation, x_offset, y_offset, support, rx, ry)
                            self.support_cutout_rotation_collection.add_item(rotation, x_offset, y_offset, support_cutout, rx, ry)

                        x += w    
                        w = 1.0
                        h = 1.0

                    elif ignore_next == True:
                        ignore_next = False

                y += 1

        self.switch_collection.set_collection_neighbors('global')

        # create sections of the keyboard for usin in splitting for printing
        self.split_keyboard()

    def process_custom_shapes(self):
        

        if self.parameters.custom_polygons is not None:
            for shape in self.parameters.custom_polygons:
                custom_shape_type = shape['type']
                coordinates_list = shape['coordinates']

                for coordinates in coordinates_list:
                    x = coordinates[0]
                    y = coordinates[1]

                    custom_shape = ShapeCutout(x, y, custom_shape_type, shape, self.parameters)
                    self.custom_polygon_collection.add_item(x, y, custom_shape)


    def get_assembly(self, top = False, bottom = False, all = True, plate_only = False):
        
        
        # Init top_assembly and bottom_assembly objects
        top_assembly = union()
        bottom_assembly = union()

        # Get the x and y bounds of the switches
        (min_x, max_x, max_y, min_y) = self.switch_collection.get_collection_bounds()

        # Add all switch and support collection objects to switch and support attributes
        support_collection = self.support_collection
        switch_collection = self.switch_collection
        support_cutout_collection = self.support_cutout_collection

        if self.desired_section_number > -1:
            support_collection = self.support_section_list[self.desired_section_number]
            switch_collection = self.switch_section_list[self.desired_section_number]
            support_cutout_collection = self.support_cutout_section_list[self.desired_section_number]

        self.switch_supports += support_collection.get_moved_union()
        self.switch_cutouts += switch_collection.get_moved_union()
        self.switch_support_cutouts += support_cutout_collection.get_moved_union()

        if self.parameters.custom_polygons is not None:
            self.custom_polygon_cutout_collection = self.custom_polygon_collection.get_moved_union()

        (rotated_min_x, rotated_max_x, rotated_max_y, rotated_min_y) = self.switch_rotation_collection.get_real_collection_bounds()

        self.logger.debug('rotation_bounds: rotated_min_x: %f, rotated_max_x: %f, rotated_max_y: %f, rotated_min_y: %f', 
            rotated_min_x, rotated_max_x, rotated_max_y, rotated_min_y)

        if rotated_min_x < min_x:
            min_x = rotated_min_x
        if rotated_max_x > max_x:
            max_x = rotated_max_x
        if rotated_min_y < min_y:
            min_y = rotated_min_y
        if rotated_max_y > max_y:
            max_y = rotated_max_y

        # Union together all rotated switch cutouts 
        for rotation in self.switch_rotation_collection.get_rotation_list():
            self.switch_cutouts += self.switch_rotation_collection.get_rotated_moved_union(rotation)
            self.switch_supports += self.support_rotation_collection.get_rotated_moved_union(rotation)
            self.switch_support_cutouts += self.support_cutout_rotation_collection.get_rotated_moved_union(rotation)

        # Set body dimensions
        self.parameters.set_dimensions(max_x, min_y, min_x, max_y)

        # Init body object
        self.body = Body(self.parameters)

        # Init PCB object
        # if self.parameters.custom_pcb == True:
        self.pcb = PCB(self.parameters)
        pcb_model = self.pcb.get_model()

        # Add case to top_assembly
        top_assembly += self.body.case(plate_only = plate_only)

        if self.parameters.simple_test == False:
            # Remove switch suport cutouts
            top_assembly -= self.switch_support_cutouts

            # Add switch supports and remove switch cutouts
            top_assembly += self.switch_supports
            top_assembly -= self.switch_cutouts
        
        # Generate screw hole related objects
        screw_hole_collection = None
        screw_hole_body_collection = None
        screw_hole_body_scaled_collection = None
        if self.parameters.screw_count > 0:
            screw_hole_collection, screw_hole_body_collection, screw_hole_body_scaled_collection = self.body.screw_hole_objects(tap = bottom)

            # Remove screw holes from top top_assembly
            top_assembly -= screw_hole_collection

            bottom_assembly = screw_hole_body_collection
            bottom_assembly -= screw_hole_collection

        body_block = self.body.case(body_block_only = True)
        
        # Remove items marked as not part of desired section
        if self.desired_section_number > -1:
            top_assembly -= self.get_top_section_remove_block(self.desired_section_number)
            # TODO
            bottom_section_inclusion = self.get_bottom_section_remove_block(self.desired_section_number)
            # bottom_assembly -= self.get_bottom_section_remove_block(self.desired_section_number)
        

        self.custom_polygon_cutout_collection = up(self.parameters.case_height_base_removed - (self.parameters.plate_thickness / 2)) (
            self.custom_polygon_cutout_collection
        )
        # Move top_assembly so that the bottom left sits at 0, 0, 0
        top_assembly = up(self.parameters.case_height_base_removed - (self.parameters.plate_thickness / 2)) (
            forward(self.parameters.real_max_y + self.parameters.bottom_margin) (
                right(self.parameters.left_margin) (
                    top_assembly 
                )
            )
        )

        top_assembly += up(self.parameters.case_height_base_removed) ( #) - (self.parameters.plate_thickness / 2)) (
            right(0) (
                pcb_model 
            )
        )

        bottom_assembly = up(self.parameters.case_height_base_removed - (self.parameters.plate_thickness / 2)) (
            forward(self.parameters.real_max_y + self.parameters.bottom_margin) (
                right(self.parameters.left_margin) (
                    bottom_assembly
                )
            )
        )
        
        if screw_hole_collection is not None:
            screw_hole_collection = up(self.parameters.case_height_base_removed - (self.parameters.plate_thickness / 2)) (
                forward(self.parameters.real_max_y + self.parameters.bottom_margin) (
                    right(self.parameters.left_margin) (
                        screw_hole_collection
                    )
                )
            )
            screw_hole_body_collection = up(self.parameters.case_height_base_removed - (self.parameters.plate_thickness / 2)) (
                forward(self.parameters.real_max_y + self.parameters.bottom_margin) (
                    right(self.parameters.left_margin) (
                        screw_hole_body_collection
                    )
                )
            )
            screw_hole_body_scaled_collection = up(self.parameters.case_height_base_removed - (self.parameters.plate_thickness / 2)) (
                forward(self.parameters.real_max_y + self.parameters.bottom_margin) (
                    right(self.parameters.left_margin) (
                        screw_hole_body_scaled_collection
                    )
                )
            )
        
        body_block = up(self.parameters.case_height_base_removed - (self.parameters.plate_thickness / 2)) (
            forward(self.parameters.real_max_y + self.parameters.bottom_margin) (
                right(self.parameters.left_margin) (
                    body_block
                )
            )
        )

        if self.desired_section_number > -1:
            bottom_section_inclusion = up(self.parameters.case_height_base_removed - (self.parameters.plate_thickness / 2)) (
                forward(self.parameters.real_max_y + self.parameters.bottom_margin) (
                    right(self.parameters.left_margin) (
                        bottom_section_inclusion
                    )
                )
            )

        # Create block that will remove material to make case bottom flat
        bottom_diff_plate_width = (self.parameters.real_max_x + self.parameters.right_margin + self.parameters.left_margin) * 2
        bottom_diff_plate_height = (self.parameters.real_max_y + self.parameters.top_margin + self.parameters.bottom_margin) * 2
        bottom_diff_plate = down(self.parameters.case_height_extra * 2) (
            back(bottom_diff_plate_height / 4) (
                left(bottom_diff_plate_width / 4) (
                    cube([ bottom_diff_plate_width, bottom_diff_plate_height, self.parameters.case_height_extra * 2 ])
                )
            )
        )

        # Remove space for a cable to pass through the body
        top_assembly -= self.cable.get_cable_hole()

        # Interesect objects with a test block to handle testing specific parts of a model
        if self.parameters.test_block == True:
            test_block_x = self.parameters.test_block_x_end - self.parameters.test_block_x_start
            test_block_y = self.parameters.test_block_y_end - self.parameters.test_block_y_start
            test_block_z = self.parameters.test_block_z_end - self.parameters.test_block_z_start

            self.logger.info('test_block_x: %f, test_block_y: %f, test_block_z: %f', test_block_x, test_block_y, test_block_z)

            test_block = translate(
                [
                    self.parameters.test_block_x_start, 
                    self.parameters.test_block_y_start, 
                    self.parameters.test_block_z_start
                ]
            ) (
                cube([test_block_x, test_block_y, test_block_z])
            )

            top_assembly *= test_block
            bottom_assembly *= test_block
            screw_hole_collection *= test_block
            screw_hole_body_collection *= test_block
            screw_hole_body_scaled_collection *= test_block
            body_block *= test_block

        # Remove thw custom cutouts before tilting
        top_assembly -= self.custom_polygon_cutout_collection

        # Tile the body if desired
        if self.parameters.tilt > 0.0:
            top_assembly = rotate(self.parameters.tilt, [1, 0, 0]) ( top_assembly )
            bottom_assembly = rotate(self.parameters.tilt, [1, 0, 0]) ( bottom_assembly )
            if screw_hole_collection is not None:
                screw_hole_collection = rotate(self.parameters.tilt, [1, 0, 0]) ( screw_hole_collection )
                screw_hole_body_collection = rotate(self.parameters.tilt, [1, 0, 0]) ( screw_hole_body_collection )
                screw_hole_body_scaled_collection = rotate(self.parameters.tilt, [1, 0, 0]) ( screw_hole_body_scaled_collection )
            body_block = rotate(self.parameters.tilt, [1, 0, 0]) ( body_block )

        # Remove bottom block to make bottom of case flat
        top_assembly -= bottom_diff_plate
        bottom_assembly -= down(self.parameters.bottom_cover_thickness) ( bottom_diff_plate )



        # bottom_assembly += self.body.bottom_cover()
        # bottom_assembly += body_block
        bottom_assembly += self.body.bottom_cover() * body_block
        if self.desired_section_number > -1:
            bottom_assembly *= bottom_section_inclusion

        if screw_hole_collection is not None:
            bottom_assembly -= screw_hole_collection

        # # TEST ####
        # # Union together all rotated supports
        # rotation = list(self.support_rotation_collection.get_rotation_list())[0]
        # # top_assembly = self.support_rotation_collection.get_union(rotation)
        # # top_assembly -= self.switch_rotation_collection.get_union(rotation)
        # rx_list = list(self.support_rotation_collection.get_rx_list(rotation))
        # # self.logger.debug('rotation %f, rx_list: %s', rotation, str(rx_list))
        # ry_list = list(self.support_rotation_collection.get_ry_list_in_rx(rotation, rx_list[0]))
        # rx = rx_list[0]
        # ry = ry_list[0]
        # self.logger.debug('rotation %f, rx_list: %s, ry_list: %s', rotation, str(rx_list), str(ry_list))
        # top_assembly = self.support_rotation_collection.get_rotated_union(rotation)
        # top_assembly -= self.switch_rotation_collection.get_rotated_union(rotation)
        # rotation_max_x = self.switch_rotation_collection.get_max_x(rotation, rx, ry)
        # (rotation_min_x, rotation_max_x, rotation_max_y, rotation_min_y) = self.switch_rotation_collection.get_real_collection_bounds()
        # self.logger.debug('rotation %f, rotation_min_x: %f, rotation_max_x: %f, rotation_max_y: %f, rotation_min_y: %f', rotation, rotation_min_x, rotation_max_x, rotation_max_y, rotation_min_y)
        # # top_assembly = self.support_rotation_collection.get_rotated_moved_union(rotation)
        # # top_assembly -= self.switch_rotation_collection.get_rotated_moved_union(rotation)

        # top_assembly = self.switch_rotation_collection.draw_rotated_items(rotation)
        
        # return top_assembly
        # ############


        if top == True or plate_only == True:
            if screw_hole_body_scaled_collection is not None:
                return (top_assembly - screw_hole_body_scaled_collection)
            else:
                return top_assembly
        elif bottom == True:
            return bottom_assembly 
        else:
            top_assembly += bottom_assembly
            return top_assembly
        
    
    # def get_cable_hole(self):

    #     if self.cable_hole == True:
    #         return up(self.parameters.case_height_base_removed - (self.parameters.cable_hole_height / 2) - self.parameters.plate_thickness - self.cable_hole_down_offset ) (
    #             right(self.parameters.left_margin + (self.parameters.real_max_x / 2)) ( 
    #                 forward(self.parameters.bottom_margin + self.parameters.top_margin + self.parameters.real_max_y) ( 
    #                     cube([self.parameters.cable_hole_width, self.parameters.case_wall_thickness * 2, self.parameters.cable_hole_height], center = True) 
    #                 ) 
    #             ) 
    #         )
    #     else:
    #         return union()


    def split_keyboard(self):
        

        (min_x, max_x, max_y, min_y) = self.switch_collection.get_collection_bounds()
        self.logger.debug('max_x: %d, min_y: %d', max_x, min_y)
        self.logger.debug('build_x: %d, build_y: %d', self.build_x, self.build_y)

        x_parts = math.ceil(max_x / self.build_x)
        y_parts = math.ceil(abs(min_y) / self.build_y)
        self.logger.debug('x_parts: %d, y_parts: %d', x_parts, y_parts)

        x_per_part = math.ceil(max_x / x_parts)
        y_per_part = math.floor(min_y / y_parts)
        self.logger.debug('x_per_part: %d, y_per_part: %d', x_per_part, y_per_part)

        # Union all standard switch cutouts together
        current_x_start = 0.0
        # current_y_start = 0.0
        current_x_section = 0
        # current_y_section = 0
        next_x_section = 0
        # next_y_section = 0
        
        # build_area = left(self.parameters.left_margin) ( back(self.y_build_size - self.parameters.top_margin) ( down(10) ( cube([self.parameters.x_build_size, self.y_build_size, 10]) ) ) )

        switch_object_dict = self.switch_collection.get_collection_dict()
        for x in self.switch_collection.get_sorted_x_list():
            for y in self.switch_collection.get_sorted_y_list_in_x(x):
                # self.logger.debug('\tx: %d, y: %d', x, y)
                # switch_cutouts += x_row[y].get_moved()
                current_switch: Switch = self.switch_collection.get_item(x, y)
                current_support = self.support_collection.get_item(x, y)
                current_support_cutout = self.support_cutout_collection.get_item(x, y)
                w = current_switch.w
                h = current_switch.h
                cell_value = current_switch.cell_value

                switch_x_max = current_switch.x_end_mm + self.parameters.left_margin
                # switch_x_min = current_switch.x_start_mm + self.parameters.left_margin
                # switch_y_max = current_switch.y_end_mm + self.parameters.top_margin
                # switch_y_min = current_switch.y_start_mm + self.parameters.top_margin

                if switch_x_max - current_x_start < self.parameters.x_build_size:
                    # self.logger.debug('current_x_section:', current_x_section)
                    self.switch_section_list[current_x_section].add_item(x, y, current_switch)
                    self.support_section_list[current_x_section].add_item(x, y, current_support)
                    self.support_cutout_section_list[current_x_section].add_item(x, y, current_support_cutout)
                elif switch_x_max - current_x_start > self.parameters.x_build_size and next_x_section > current_x_section:
                    self.switch_section_list[next_x_section].add_item(x, y, current_switch)
                    self.support_section_list[next_x_section].add_item(x, y, current_support)
                    self.support_cutout_section_list[next_x_section].add_item(x, y, current_support_cutout)
                else:
                    # self.logger.debug('switch_x_max:', switch_x_max, 'current_x_start:', current_x_start, 'switch_x_max - current_x_start:', switch_x_max - current_x_start, 'x_build_size:', x_build_size)
                    next_x_section = current_x_section + 1
                    self.switch_section_list.append(ItemCollection())
                    self.switch_section_list[next_x_section].add_item(x, y, current_switch)

                    self.support_section_list.append(ItemCollection())
                    self.support_section_list[next_x_section].add_item(x, y, current_support)

                    self.support_cutout_section_list.append(ItemCollection())
                    self.support_cutout_section_list[next_x_section].add_item(x, y, current_support_cutout)

                
                # self.logger.debug('\tswitch_x: (', switch_x_min, ',', switch_x_max, '), switch_y: (', switch_y_min, switch_y_max, ')')
            
            if next_x_section > current_x_section:
                # current_x_start = self.switch_section_list[next_x_section][0]['switch_x_min']
                current_x_start = self.parameters.U(self.switch_section_list[next_x_section].get_min_x())
                # self.logger.debug('current_x_start: %f', current_x_start)
                current_x_section = next_x_section

        for idx, section in enumerate(self.switch_section_list):
            # self.logger.debug('Set Item neighbors for section %d', idx)
            section.set_collection_neighbors()

    def get_top_section_remove_block(self, section_number):
        this_function_name = sys._getframe(  ).f_code.co_name
        
        section = self.switch_section_list[section_number]

        self.logger.debug('Get Section %d', section_number)

        (min_x, max_x, max_y, min_y) = section.get_collection_bounds()

        min_x_mm = self.parameters.U(min_x)
        max_x_mm = self.parameters.U(max_x)
        max_y_mm = self.parameters.U(max_y)
        min_y_mm = self.parameters.U(min_y)
        
        # (case_min_x, case_max_x, case_max_y, case_min_y) = section.get_collection_bounds()

        self.logger.debug('Section Bounds: min_x: %f, max_x: %f, max_y: %f, min_y: %f', min_x, max_x, max_y, min_y)

        include_right_border = False
        include_left_border = False
        # include_top_border = False
        # include_bottom_border = False

        if max_x == self.parameters.max_x:
            include_right_border = True

        if min_x == self.parameters.min_x:
            include_left_border = True
        
        # if max_y == self.parameters.max_y:
        #     include_top_border = True
        
        # if min_y == self.parameters.min_y:
        #     include_bottom_border = True
        #     if abs(min_y) < self.build_y:
        #         include_top_border = True

        remove_block = union()

        remove_block_height = self.parameters.case_height_base_removed * 4
        remove_block_z_offset = remove_block_height / 2
        remove_block_length = self.parameters.real_max_x
        
        section_has_right_global_neighbor = section.has_global_right_neighbor_section()
        section_has_left_global_neighbor = section.has_global_left_neighbor_section()

        # Draw non border edges
        for rx in section.get_rx_list():
            for ry in section.get_ry_list_in_rx(rx):
                for x in section.get_x_list_in_rx_ry(rx, ry):
                    for y in section.get_y_list_in_rx_ry_x(x, rx, ry):
                        item: Switch
                        item = section.get_item(x, y)

                        # base separator bar height
                        bar_height = self.parameters.U(item.h) + (self.kerf * 2)
                        y_offset = self.parameters.U(item.y - item.h) - self.kerf
                        right_x_offset = 0.0
                        self.logger.debug('right_x_offset: %f', right_x_offset)
                        left_x_offset = 0.0

                        # if switch has a local top neighbor include any offset between this and that key in separator bar
                        if item.has_neighbor('top') == True:
                            offset = self.parameters.U(item.get_neighbor_offset('top'))
                            # self.logger.debug('%s, Local Top Bar True, offset: %f', str(item), offset)
                            bar_height += offset
                        
                        # If switch has no global top neighbor include the board edge in this separator bar
                        if item.has_neighbor('top', 'global') == False:
                            # self.logger.debug('%s, Global Top Bar False', str(item))
                            bar_height += self.parameters.U(abs(item.y)) + self.parameters.top_margin
                            # self.logger.debug('\t bar_height: %f', bar_height)

                        # If switch has no global bottom neighbor include the board edge in this separator bar
                        if item.has_neighbor('bottom', 'global') == False:
                            # self.logger.debug('%s, Global Bottom Bar False', str(item))
                            bar_height += self.parameters.U( abs(self.parameters.min_y) - (abs(item.y) + item.h) ) + self.parameters.bottom_margin
                            # self.logger.debug('\t bar_height: %f', bar_height)
                            y_offset -= (self.parameters.bottom_margin + self.parameters.U( abs(self.parameters.min_y) - (abs(item.y) + item.h) ) )

                            # if item.has_neighbor('right') == True:
                                # perp_offset = item.get_neighbor_perp_offset('right')
                                # if perp_offset > 0.0:
                                #     self.logger.debug('Switch: %s, perp_offset: %f', str(item), perp_offset)

                        
                        # If switch has no global right neighbor and 
                        if item.has_neighbor('right', 'global') == False and item.end_x == max_x:
                            self.logger.debug('Switch %s, No global right neighbor. item.end_x == max_x (%d == %d)', str(item), item.end_x, max_x)
                            neighbor = None
                            neighbor_offset = 0.0

                            # Switch has local top neighbor
                            if item.has_neighbor('top') == True:
                                neighbor = item.get_neighbor('top')
                                # self.logger.debug('Switch: %s, top neighbor: %s', str(item), str(neighbor))
                                offset = neighbor.get_neighbor_offset('right', 'global')
                                if offset > neighbor_offset:
                                    neighbor_offset = offset

                            # Switch has local bottom neighbor
                            if item.has_neighbor('bottom') == True:
                                neighbor = item.get_neighbor('bottom')
                                # self.logger.debug('Switch: %s, bottom neighbor: %s', str(item), str(neighbor))
                                offset = neighbor.get_neighbor_offset('right', 'global')
                                if offset > neighbor_offset:
                                    neighbor_offset = offset

                            # self.logger.debug('Switch: %s, neighbor_offset: %f', str(item), neighbor_offset)

                            if neighbor_offset > 0.0:
                                right_x_offset += self.parameters.U(neighbor_offset) / 2
                                self.logger.debug('right_x_offset: %f', right_x_offset)
                                # self.logger.debug('1: switch %s, right_x_offset %f', str(item), right_x_offset)

                        
                        # if include_right_border == False:
                        if item.has_neighbor('right') == False:
                            # self.logger.debug('switch %s, has right neighbor %s', str(item), str(item.has_neighbor('right')))
                            right_x_offset += self.parameters.U(item.x + item.w)
                            self.logger.debug('right_x_offset: %f', right_x_offset)
                            
                            # Switch has global right neighbor
                            if item.has_neighbor('right', 'global') == True:
                                # Get Global roght neightbor offset
                                # Set right_x_offset to minimum value of half neighbor offset or the maximum x for the setion
                                neighbor_offset = item.get_neighbor_offset('right', 'global')
                                right_x_offset += self.parameters.U(min([neighbor_offset / 2, max_x]))
                                self.logger.debug('right_x_offset: %f', right_x_offset)
                                # self.logger.debug('\t\tglobal right neighbor offset: %f, right_x_offset: %f', neighbor_offset, right_x_offset - self.parameters.U(item.x + item.w))
                            else:
                                # Set right_x_offset to maximum x for the setion minus the end x coordinate of the switch
                                right_x_offset += self.parameters.U(max_x - item.end_x)
                                self.logger.debug('right_x_offset: %f', right_x_offset)

                            
                            if include_right_border == False:
                                remove_block += down(remove_block_z_offset) ( right(right_x_offset) ( forward(y_offset) ( cube([remove_block_length, bar_height, remove_block_height]) ) ) )
                        
                        # If switch has no local left neighbor
                        if item.has_neighbor('left') == False:
                            # self.logger.debug('2: switch %s, left_x_offset %f', str(item), left_x_offset)
                            # self.logger.debug('switch %s, has left neighbor %s', str(item), str(item.has_neighbor('left')))
                            # self.logger.debug('remove_block_length: %f, item.x: %f, self.parameters.U(item.x): %f, -(remove_block_length) + self.parameters.U(item.x): %f', remove_block_length, item.x, self.parameters.U(item.x), -(remove_block_length) + self.parameters.U(item.x))
                            # if switch has no global left neighbor
                            if item.has_neighbor('left', 'global') == False:
                                if section_has_left_global_neighbor == True:
                                    left_x_offset += -(remove_block_length) + self.parameters.U(min_x)
                            
                            
                            
                            # self.logger.debug('3: switch %s, left_x_offset %f', str(item), left_x_offset)

                            if item.has_neighbor('left', 'global') == True:
                                left_x_offset += -(remove_block_length) + self.parameters.U(item.x)
                                neighbor_offset = item.get_neighbor_offset('left', 'global')
                                # self.logger.debug('\t\tglobal left neighbor offset: %f, left_x_offset: %f', neighbor_offset, left_x_offset)
                                if neighbor_offset > 0.0:
                                    left_x_offset -= self.parameters.U(neighbor_offset) / 2
                                    # self.logger.debug('\t\tglobal left neighbor offset: %f, left_x_offset: %f', neighbor_offset, left_x_offset)

                            if include_left_border == False:
                                # self.logger.debug('4: switch %s, left_x_offset %f', str(item), left_x_offset)
                                remove_block += down(remove_block_z_offset) ( right(left_x_offset) ( forward(y_offset) ( cube([remove_block_length, bar_height, remove_block_height]) ) ) )
                                # remove_block += down(self.support_bar_height * 3) ( right(left_x_offset) ( forward(self.parameters.U(item.y - item.h) ) ( cube([self.support_bar_width / 2, bar_height, self.support_bar_height * 10]) ) ) )
                        
                        # if include_top_border == False:
                        #     self.logger.debug('switch %s, has top neighbor %s', str(item), str(item.has_neighbor('top')))
                        #     if item.has_neighbor('top') == False:
                        #         self.logger.debug('\tno top neighbor')
                        #         top_switch_edge += down(self.support_bar_height * 3) ( right(self.parameters.U(item.x + item.w)) ( forward(self.parameters.U(item.y - item.h) ) ( cube([self.support_bar_width / 2, self.parameters.U(item.h), self.support_bar_height * 10]) ) ) )
                        
                        # if include_bottom_border == False:
                        #     self.logger.debug('switch %s, has bottom neighbor %s', str(item), str(item.has_neighbor('bottom')))
                        #     if item.has_neighbor('bottom') == False:
                        #         self.logger.debug('\tno bottom neighbor')
                        #         bottom_switch_edge += down(self.support_bar_height * 3) ( right(self.parameters.U(item.x + item.w)) ( forward(self.parameters.U(item.y - item.h) ) ( cube([self.support_bar_width / 2, self.parameters.U(item.h), self.support_bar_height * 10]) ) ) )

        return remove_block

    
    def get_bottom_section_remove_block(self, section_number):
        
        
        # section = self.switch_section_list[section_number]

        self.logger.debug('Get Section %d', section_number)

        self.logger.debug('real_case_width: %f', self.parameters.real_case_width)
        self.logger.debug('real_case_height: %f', self.parameters.real_case_height)

        section_size = self.parameters.real_case_width / self.parameters.bottom_section_count

        self.logger.debug('section_size: %f', section_size)

        start_x = section_size * section_number
        end_x = start_x + section_size

        (start_x, end_x) = self.get_screw_support_interference_offset(start_x, end_x)

        x_offset = start_x - self.parameters.right_margin
        y_offset = self.parameters.real_case_height / 2 + self.parameters.real_case_height
        z_offset = self.parameters.case_height_extra_fill / 2


        width = end_x - start_x
        height = self.parameters.real_case_height * 2
        thickness = self.parameters.case_height_extra_fill * 2

        self.logger.debug('section: %d, x_offset: %f, width: %f, y_offset: %f', section_number, x_offset, width, y_offset)

        return right(x_offset) ( back(y_offset) ( down(z_offset) ( cube([width, height, thickness]) ) ) )



    def get_screw_support_interference_offset(self, start_x, end_x):

        for coord_string in self.body.screw_hole_info.keys():
            screw_hole_info = self.body.screw_hole_info[coord_string]

            screw_x = screw_hole_info['x']
            # screw_y = screw_hole_info['y']

            # self.logger.debug('coord_string: %s, screw_x: %f, screw_y: %f', coord_string, screw_x, screw_y)

            screw_hole_min_x = screw_x - screw_hole_info['support_directions']['left']
            screw_hole_max_x = screw_x + screw_hole_info['support_directions']['right']

            # self.logger.debug('screw_hole_min_x: %f, screw_hole_max_x: %f', screw_hole_min_x, screw_hole_max_x)

            # Left side of section cutout is within a screw hole support
            if start_x > screw_hole_min_x and start_x < screw_hole_max_x:
                # self.logger.debug('Left side in support: old start_x: %f', start_x)
                # Left sie of section cutout is in the middle of a screw hole
                # move the start to the right
                if start_x >= screw_x:
                    start_x = screw_hole_max_x
                if start_x < screw_x:
                    start_x = screw_hole_min_x

                # self.logger.debug('Left side in support: new start_x: %f', start_x)

            # Right side of section cutout is within a screw hole support
            if end_x > screw_hole_min_x and end_x < screw_hole_max_x:
                # self.logger.debug('Right side in support: old end_x: %f', end_x)
                # Right side of section cutout is in the middle of a screw hole
                # move the end to the right
                if end_x >= screw_x:
                    end_x = screw_hole_max_x
                if end_x < screw_x:
                    end_x = screw_hole_min_x

                # self.logger.debug('Right side in support: new end_x: %f', end_x)

        return (start_x, end_x)




    
    def set_section(self, section_number):
        self.desired_section_number = section_number

    def get_top_section_count(self):
        return len(self.switch_section_list)


    def get_bottom_section_count(self):
        return self.parameters.bottom_section_count