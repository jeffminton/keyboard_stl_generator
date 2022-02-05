

import math
import logging

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
        self.logger = logging.getLogger('Keyboard')
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

        self.modifier_include_list = ['x', 'y', 'w', 'h', 'r', 'rx', 'ry']

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
            'support_bar_width' : 1.0,
            'tilt': 0.0
        }

        self.build_attr_from_dict(self.default_parameter_dict)
        
        if self.parameter_dict is not None:
            self.build_attr_from_dict(self.parameter_dict)


        self.build_x = math.floor(self.x_build_size / Cell.SWITCH_SPACING)
        self.build_y = math.floor(self.y_build_size / Cell.SWITCH_SPACING)

        self.switch_collection = ItemCollection()
        self.support_collection = ItemCollection()
        self.support_cutout_collection = ItemCollection()
        self.switch_rotation_collection = RotationCollection()
        self.support_rotation_collection = RotationCollection()
        self.support_cutout_rotation_collection = RotationCollection()

        self.switch_cutouts = union()
        self.switch_supports = union()
        self.switch_support_cutouts = union()
        self.rotate_switch_cutout_collection = union()
        self.rotate_support_collection = union()
        self.rotate_support_cutout_collection = union()

        self.section_list = [ItemCollection()]

        self.body = None

        self.desired_section_number = -1

        self.cable_hole_up_offset = 1




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


    def process_keyboard_layout(self, keyboard_layout_dict):
        y = 0.0
        rotation = 0.0
        rx = 0.0
        ry = 0.0
        r_x_offset = 0.0
        r_y_offset = 0.0
        
        for row in keyboard_layout_dict:
            x = 0.0
            w = 1.0
            h = 1.0

            if type(row) == type([]):
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
                        
                    else:
                        col_escaped = col.encode("unicode_escape").decode("utf-8")
                        # split on newline character and get the lat element in the resulting list
                        col_escaped = col_escaped.split('\\n')[-1]
                        # self.logger.debug('column value: %s', col_escaped)
                        
                        x_offset = x
                        y_offset = -(y)

                        # Create switch cutout and support object without rotation
                        if rotation == 0.0:
                            self.switch_collection.add_item(x_offset, y_offset, Switch(x_offset, y_offset, w, h, kerf = self.kerf, cell_value = col_escaped))
                            self.support_collection.add_item(x_offset, y_offset, Support(x_offset, y_offset, w, h, self.plate_thickness, self.support_bar_height, self.support_bar_width))
                            self.support_cutout_collection.add_item(x_offset, y_offset, SupportCutout(x_offset, y_offset, w, h, self.plate_thickness, self.support_bar_height, self.support_bar_width))
                            
                            
                        # Create switch cutout and support object without rotation
                        elif rotation != 0.0:
                            self.switch_rotation_collection.add_item(rotation, x_offset, y_offset, Switch(x_offset, y_offset, w, h, kerf = self.kerf, rotation = rotation, cell_value = col_escaped), rx, ry)
                            self.support_rotation_collection.add_item(rotation, x_offset, y_offset, Support(x_offset, y_offset,w, h, self.plate_thickness, self.support_bar_height, self.support_bar_width, rotation = rotation), rx, ry)

                        # Create normal switch support outline
                        # if rotation == 0.0:
                            
                            
                        # Create rotated switch support outline
                        # elif rotation != 0.0:
                            

                        x += w    
                        w = 1.0
                        h = 1.0

                y += 1

        self.switch_collection.set_item_neighbors('global')

        # create sections of the keyboard for usin in splitting for printing
        self.split_keyboard()
        self.logger.info('Sectons In Board: %d', self.get_section_count())

    def get_assembly(self, top = False, bottom = False, all = True):
        # Init top_assembly and bottom_assembly objects
        top_assembly = union()
        bottom_assembly = union()

        # Get the x and y bounds of the switches
        (min_x, max_x, max_y, min_y) = self.switch_collection.get_collection_bounds()

        # Add all switch and support collection objects to switch and support attributes
        self.switch_supports += self.support_collection.get_moved_union()
        self.switch_cutouts += self.switch_collection.get_moved_union()
        self.switch_support_cutouts += self.support_cutout_collection.get_moved_union()

        (rotated_min_x, rotated_max_x, rotated_max_y, rotated_min_y) = self.switch_rotation_collection.get_real_collection_bounds()
        self.logger.info('rotation_bounds: rotated_min_x: %f, rotated_max_x: %f, rotated_max_y: %f, rotated_min_y: %f', rotated_min_x, rotated_max_x, rotated_max_y, rotated_min_y)

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

        # Union together all rotated supports
        for rotation in self.support_rotation_collection.get_rotation_list():
            self.switch_supports += self.support_rotation_collection.get_rotated_moved_union(rotation)

        # Add rotated 
        # self.switch_supports += self.rotate_support_collection
        # self.switch_cutouts += self.rotate_switch_cutout_collection
        # self.switch_cutouts = switch_cutout(2.5)

        # Init body object
        self.body = Body(self.parameter_dict)

        # Set body dimensions
        self.body.set_dimensions(max_x, min_y, min_x, max_y)
        
        # Add case to top_assembly
        top_assembly += self.body.case()

        # Remove switch suport cutouts
        top_assembly -= self.switch_support_cutouts

        # Add switch supports and remove switch cutouts
        top_assembly += self.switch_supports
        top_assembly -= self.switch_cutouts
        
        # Generate screw hole related objects
        screw_hole_collection, screw_hole_body_collection = self.body.screw_hole_objects()

        # Remove screw holes from top top_assembly
        top_assembly -= screw_hole_collection


        bottom_assembly = screw_hole_body_collection
        bottom_assembly -= screw_hole_collection

        body_block = self.body.case(body_block_only = True)
        
        # Remove items marked as not part of desired section
        if self.desired_section_number > -1:
            top_assembly -= self.get_section_remove_block(self.desired_section_number)
            # TODO
            # bottom_assembly -= self.get_section_remove_block(self.desired_section_number)
        
        # Move top_assembly so that the bottom left sits at 0, 0, 0
        top_assembly = up(self.body.case_height_base_removed + (self.plate_thickness / 2)) ( forward(Cell.u(abs(min_y)) + self.bottom_margin) ( right(self.left_margin) ( top_assembly ) ) )
        bottom_assembly = up(self.body.case_height_base_removed + (self.plate_thickness / 2)) ( forward(Cell.u(abs(min_y)) + self.bottom_margin) ( right(self.left_margin) ( bottom_assembly ) ) )
        body_block = up(self.body.case_height_base_removed + (self.plate_thickness / 2)) ( forward(Cell.u(abs(min_y)) + self.bottom_margin) ( right(self.left_margin) ( body_block ) ) )
        

        # Create block that will remove material to make case bottom flat
        bottom_diff_plate = down(self.body.case_height_extra * 2) ( back(self.body.real_max_y / 2) ( left(self.body.real_max_x / 2) ( cube([self.body.real_max_x * 2, self.body.real_max_y * 2, self.body.case_height_extra * 2 ]) ) ) )

        # Remove space for a cable to pass through the body
        top_assembly -= self.get_cable_hole()

        # Tile the body if desired
        if self.tilt > 0.0:
            top_assembly = rotate(self.tilt, [1, 0, 0]) ( top_assembly )
            bottom_assembly = rotate(self.tilt, [1, 0, 0]) ( bottom_assembly )
            body_block = rotate(self.tilt, [1, 0, 0]) ( body_block )

        # Remove bottom block to make bottom of case flat
        top_assembly -= bottom_diff_plate
        bottom_assembly -= down(self.body.bottom_cover_thickness) ( bottom_diff_plate )



        # bottom_assembly += self.body.bottom_cover()
        # bottom_assembly += body_block
        bottom_assembly += self.body.bottom_cover() * body_block

        # # TEST ####
        # # Union together all rotated supports
        # rotation = list(self.support_rotation_collection.get_rotation_list())[0]
        # # top_assembly = self.support_rotation_collection.get_union(rotation)
        # # top_assembly -= self.switch_rotation_collection.get_union(rotation)
        # rx_list = list(self.support_rotation_collection.get_rx_list(rotation))
        # # self.logger.info('rotation %f, rx_list: %s', rotation, str(rx_list))
        # ry_list = list(self.support_rotation_collection.get_ry_list_in_rx(rotation, rx_list[0]))
        # rx = rx_list[0]
        # ry = ry_list[0]
        # self.logger.info('rotation %f, rx_list: %s, ry_list: %s', rotation, str(rx_list), str(ry_list))
        # top_assembly = self.support_rotation_collection.get_rotated_union(rotation)
        # top_assembly -= self.switch_rotation_collection.get_rotated_union(rotation)
        # rotation_max_x = self.switch_rotation_collection.get_max_x(rotation, rx, ry)
        # (rotation_min_x, rotation_max_x, rotation_max_y, rotation_min_y) = self.switch_rotation_collection.get_real_collection_bounds()
        # self.logger.info('rotation %f, rotation_min_x: %f, rotation_max_x: %f, rotation_max_y: %f, rotation_min_y: %f', rotation, rotation_min_x, rotation_max_x, rotation_max_y, rotation_min_y)
        # # top_assembly = self.support_rotation_collection.get_rotated_moved_union(rotation)
        # # top_assembly -= self.switch_rotation_collection.get_rotated_moved_union(rotation)

        # top_assembly = self.switch_rotation_collection.draw_rotated_items(rotation)
        
        # return top_assembly
        # ############


        if top == True:
            return top_assembly
        elif bottom == True:
            return bottom_assembly 
        else:
            top_assembly += bottom_assembly
            return top_assembly
        
    
    def get_cable_hole(self):

        if self.cable_hole == True:
            return up(self.cable_hole_up_offset + (self.hole_height / 2)) ( right(self.left_margin + (self.body.real_max_x / 2)) ( forward(self.bottom_margin + self.top_margin + self.body.real_max_y) ( cube([self.hole_width, self.plate_wall_thickness * 2, self.hole_height], center = True) ) ) )
        else:
            return union()


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
        current_y_start = 0.0
        current_x_section = 0
        current_y_section = 0
        next_x_section = 0
        next_y_section = 0
        
        # build_area = left(self.left_margin) ( back(self.y_build_size - self.top_margin) ( down(10) ( cube([self.x_build_size, self.y_build_size, 10]) ) ) )

        switch_object_dict = self.switch_collection.get_collection_dict()
        for x in sorted(switch_object_dict.keys()):
            x_row = switch_object_dict[x]
            for y in x_row.keys():
                self.logger.debug('\tx: %d, y: %d', x, y)
                self.logger.debug('x_row.keys(): %s', str(x_row.keys()))
                # switch_cutouts += x_row[y].get_moved()
                current_switch = x_row[y]
                w = current_switch.w
                h = current_switch.h
                cell_value = current_switch.cell_value
                
                switch_x_max = Cell.u(x + w) + self.left_margin
                switch_x_min = Cell.u(x) + self.left_margin
                switch_y_max = Cell.u(abs(y) + h) + self.top_margin
                switch_y_min = Cell.u(abs(y)) + self.top_margin

                new_switch = Switch(x, y, w, h, cell_value = cell_value)

                if switch_x_max - current_x_start < self.x_build_size:
                    # self.logger.debug('current_x_section:', current_x_section)
                    self.section_list[current_x_section].add_item(x, y, current_switch)
                elif switch_x_max - current_x_start > self.x_build_size and next_x_section > current_x_section:
                    self.section_list[next_x_section].add_item(x, y, current_switch)
                else:
                    # self.logger.debug('switch_x_max:', switch_x_max, 'current_x_start:', current_x_start, 'switch_x_max - current_x_start:', switch_x_max - current_x_start, 'x_build_size:', x_build_size)
                    next_x_section = current_x_section + 1
                    self.section_list.append(ItemCollection())
                    self.section_list[next_x_section].add_item(x, y, current_switch)

                
                # self.logger.debug('\tswitch_x: (', switch_x_min, ',', switch_x_max, '), switch_y: (', switch_y_min, switch_y_max, ')')
            
            if next_x_section > current_x_section:
                # current_x_start = self.section_list[next_x_section][0]['switch_x_min']
                current_x_start = Cell.u(self.section_list[next_x_section].get_min_x())
                # self.logger.debug('current_x_start: %f', current_x_start)
                current_x_section = next_x_section

        for idx, section in enumerate(self.section_list):
            self.logger.debug('Set Item neighbors for section %d', idx)
            section.set_item_neighbors()


    def get_section_count(self):
        return len(self.section_list)

    def get_section_remove_block(self, section_number):
        section = self.section_list[section_number]

        self.logger.debug('Get Section %d', section_number)

        (min_x, max_x, max_y, min_y) = section.get_collection_bounds()

        self.logger.debug('Section Bounds: min_x: %f, max_x: %f, max_y: %f, min_y: %f', min_x, max_x, max_y, min_y)

        include_right_border = False
        include_left_border = False
        include_top_border = False
        include_bottom_border = False

        if max_x == self.body.max_x:
            include_right_border = True

        if min_x == self.body.min_x:
            include_left_border = True
        
        if max_y == self.body.max_y:
            include_top_border = True
        
        if min_y == self.body.min_y:
            include_bottom_border = True
            if abs(min_y) < self.build_y:
                include_top_border = True

        remove_block = union()

        remove_block_height = self.body.case_height_base_removed * 4
        remove_block_z_offset = remove_block_height / 2
        remove_block_length = self.body.real_max_x
        
        # Draw non border edges
        for rx in section.get_rx_list():
            for ry in section.get_ry_list_in_rx(rx):
                for x in section.get_x_list_in_rx_ry(rx, ry):
                    for y in section.get_y_list_in_rx_ry_x(x, rx, ry):
                        item = section.get_item(x, y)

                        # base separator bar height
                        bar_height = Cell.u(item.h)
                        y_offset = Cell.u(item.y - item.h)

                        # if switch has a local top neighbor include any offset between this and that key in separator bar
                        if item.has_neighbor('top') == True:
                            offset = Cell.u(item.get_neighbor_offset('top'))
                            # self.logger.debug('%s, Local Top Bar True, offset: %f', str(item), offset)
                            bar_height += offset
                        
                        # If switch has no global top neighbor include the board edge in this separator bar
                        if item.has_neighbor('top', 'global') == False:
                            self.logger.debug('%s, Global Top Bar False', str(item))
                            bar_height += Cell.u(abs(item.y)) + self.top_margin
                            self.logger.debug('\t bar_height: %f', bar_height)

                        # If switch has no global bottom neighbor include the board edge in this separator bar
                        if item.has_neighbor('bottom', 'global') == False:
                            self.logger.debug('%s, Global Bottom Bar False', str(item))
                            bar_height += Cell.u( abs(min_y) - (abs(item.y) + item.h) ) + self.bottom_margin
                            self.logger.debug('\t bar_height: %f', bar_height)
                            y_offset -= self.bottom_margin 
                        
                        # if include_right_border == False:
                        if item.has_neighbor('right') == False:
                            self.logger.info('switch %s, has right neighbor %s', str(item), str(item.has_neighbor('right')))
                            x_offset = Cell.u(item.x + item.w)

                            if item.has_neighbor('right', 'global') == True:
                                neighbor_offset = item.get_neighbor_offset('right', 'global')
                                x_offset += Cell.u(min([neighbor_offset / 2, max_x]))
                                self.logger.info('\t\tglobal right neighbor offset: %f, x_offset: %f', neighbor_offset, x_offset - Cell.u(item.x + item.w))
                            remove_block += down(remove_block_z_offset) ( right(x_offset) ( forward(y_offset) ( cube([remove_block_length, bar_height, remove_block_height]) ) ) )
                        
                        # if include_left_border == False:
                        if item.has_neighbor('left') == False:
                            self.logger.info('switch %s, has left neighbor %s', str(item), str(item.has_neighbor('left')))
                            x_offset = -(remove_block_length) + Cell.u(item.x)

                            if item.has_neighbor('left', 'global') == True:
                                neighbor_offset = item.get_neighbor_offset('left', 'global')
                                if neighbor_offset > 0.0:
                                    x_offset -= Cell.u(neighbor_offset) / 2
                                    self.logger.info('\t\tglobal left neighbor offset: %f, x_offset: %f', neighbor_offset, x_offset)

                                remove_block += down(remove_block_z_offset) ( right(x_offset) ( forward(y_offset) ( cube([remove_block_length, bar_height, remove_block_height]) ) ) )
                                # remove_block += down(self.support_bar_height * 3) ( right(x_offset) ( forward(Cell.u(item.y - item.h) ) ( cube([self.support_bar_width / 2, bar_height, self.support_bar_height * 10]) ) ) )
                        
                        # if include_top_border == False:
                        #     self.logger.debug('switch %s, has top neighbor %s', str(item), str(item.has_neighbor('top')))
                        #     if item.has_neighbor('top') == False:
                        #         self.logger.debug('\tno top neighbor')
                        #         top_switch_edge += down(self.support_bar_height * 3) ( right(Cell.u(item.x + item.w)) ( forward(Cell.u(item.y - item.h) ) ( cube([self.support_bar_width / 2, Cell.u(item.h), self.support_bar_height * 10]) ) ) )
                        
                        # if include_bottom_border == False:
                        #     self.logger.debug('switch %s, has bottom neighbor %s', str(item), str(item.has_neighbor('bottom')))
                        #     if item.has_neighbor('bottom') == False:
                        #         self.logger.debug('\tno bottom neighbor')
                        #         bottom_switch_edge += down(self.support_bar_height * 3) ( right(Cell.u(item.x + item.w)) ( forward(Cell.u(item.y - item.h) ) ( cube([self.support_bar_width / 2, Cell.u(item.h), self.support_bar_height * 10]) ) ) )

        return remove_block

    def set_section(self, section_number):
        self.desired_section_number = section_number