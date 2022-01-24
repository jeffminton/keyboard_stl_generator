

import argparse
import json
import math
import re
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

logger = logging.getLogger('keyboard_layout_generator')
logger.setLevel(logging.INFO)

# create console handler and set level to info
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

logger.addHandler(ch)

# #[Model Features]#
plate_only = 0


# #[Printer Info]#
x_build_size = 200
y_build_size = 200
part_number = 1


# #[Switch Adjustment Dimensions]#
kerf = 0.00


# #[Holder Dimensions]# 
top_margin = 8
bottom_margin = 8
left_margin = 8
right_margin = 8
case_height = 10
plate_wall_thickness = 2.0
plate_thickness = 1.511
plate_corner_radius = 4


# #[Support Bars]#  
support_bar_height = 3.0
support_bar_width = 1.0
support_bar_tile_width = support_bar_width / 2


build_x = math.floor(x_build_size / Cell.SWITCH_SPACING)
build_y = math.floor(y_build_size / Cell.SWITCH_SPACING)


def main():

    parser = argparse.ArgumentParser(description='Build custom keyboard SCAD file using keyboard layout editor format')
    parser.add_argument('-i', '--input-file', metavar = 'layout_json_file_name.json', help = 'a path to a keyboard layout editor json file', required = True)
    parser.add_argument('-o', '--output-file', metavar = 'object_name.scad', help = 'a path to a file to store the generated open scad file')
    parser.add_argument('-r', '--resolution', metavar = 'num_segments', help = 'The resolution to be used when creating curves', default = 8)
    # parser.add_argument('-f', '--fill-edges', help = 'Fill empty edges to ensure keyboard is a complete rectangle', default = False, action = 'store_true')
    parser.add_argument('-x', '--x-fill', help = 'Pad empty spaces to the left of keys', default = False, action = 'store_true')
    parser.add_argument('-b', '--blank-fill', help = 'Pad empty spaces to the left of keys', default = False, action = 'store_true')
    # parser.add_argument('-b', '--build-area-break', metavar = 'sub_part_number', help = 'Pad empty spaces to the left of keys', default = -1 )
    parser.add_argument('-t', '--plate-thickness', type = float, metavar = 'plate_thickness', help = 'Plate thickness in milimeters', default = 1.51 ) 
    parser.add_argument('-p', '--plate-only', help = 'Only create the plate do not create case walls', default = False, action = 'store_true')
    parser.add_argument('-s', '--plate-supports', help = 'Create support grid on entire plate', default = False, action = 'store_true')


    args = parser.parse_args()
    # logger.info(vars(args))

    layout_json_file_name = args.input_file

    if args.output_file is None:
        scad_output_file_name = layout_json_file_name.replace('.json', '_out.scad')
    else:
        scad_output_file_name = args.output_file

    RESOLUTION = args.resolution

    plate_thickness = args.plate_thickness

    logger.info('plate_thickness: %d', plate_thickness)

    logger.info('Read layout from file %s write generated scad to %s', layout_json_file_name, scad_output_file_name)
    
    json_key_pattern = '([{,])([xywha1]+):'
    json_key_replace = '\\1"\\2":'

    col_split_regex = '","|",{|},"'

    modifier_ignore_list = ['a']
    modifier_include_list = ['x', 'y', 'w', 'h', 'r', 'rx', 'ry']

    f = open(layout_json_file_name)

    keyboard_layout = f.read()

    keyboard_layout_dict = None

    try:
        keyboard_layout_dict = json.loads(keyboard_layout)
        logger.info('Valid Json Parsed')
    except:
        keyboard_layout = '[%s]' % (keyboard_layout)
        json_replace_match = re.search(json_key_pattern, keyboard_layout)
        keyboard_layout = re.sub(json_key_pattern, json_key_replace, keyboard_layout)
        keyboard_layout_dict = json.loads(keyboard_layout)
        logger.info('Initial Json Invalid. Json modified and parsed')

    # logger.info('keyboard_layout_dict:', keyboard_layout_dict)

    # scad_keyboard_layout = []

    assembly = union()
    switch_cutouts = union()
    switch_supports = union()
    switch_support_cutouts = union()
    rotate_switch_cutout_collection = union()
    rotate_support_collection = union()
    rotate_support_cutout_collection = union()


    y = 0.0
    rotation = 0.0
    rx = 0.0
    ry = 0.0
    r_x_offset = 0.0
    r_y_offset = 0.0

    switch_collection = ItemCollection()
    support_collection = ItemCollection()
    support_cutout_collection = ItemCollection()

    switch_rotation_collection = RotationCollection()
    support_rotation_collection = RotationCollection()
    cupport_cutout_rotation_collection = RotationCollection()

    body = Body(top_margin, bottom_margin, left_margin, right_margin, case_height, plate_wall_thickness, plate_thickness, plate_corner_radius, args.plate_only, args.plate_supports)

    # Test Solids
    # switch_collection.add_item(3, 4, Switch(0, 0, 1, 1, kerf = kerf).get_moved() )

    # assembly = union()
    
    # assembly += Support(0, 0, 1, 1, plate_thickness, support_bar_height, support_bar_width).get_moved()
    # # assembly += right(25) ( SupportCutout(0, 0, 1, 1, plate_thickness, support_bar_height, support_bar_width).support_cutout() )
    # # assembly -= Switch(0, 0, 1, 1, kerf = kerf).get_moved()

    # scad_render_to_file(assembly, scad_output_file_name, file_header=f'$fn = {RESOLUTION};')

    # return
    # End Test Solids

    for idx, row in enumerate(keyboard_layout_dict):

        x = 0.0
        w = 1.0
        h = 1.0

        if type(row) == type([]):
            for col in row:               
                if type(col) == type({}):

                    for key in col.keys():
                        modifier_type = key
                        
                        if modifier_type in modifier_include_list:
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
                    x_offset = x
                    y_offset = -(y)

                    # Create switch cutout object without rotation
                    if rotation == 0.0:
                        switch_collection.add_item(x_offset, y_offset, Switch(x_offset, y_offset, w, h, kerf = kerf))
                        
                    # Create switch cutout object without rotation
                    elif rotation != 0.0:
                        switch_rotation_collection.add_item(rotation, x_offset, y_offset, Switch(x_offset, y_offset, w, h, kerf = kerf), rx, ry)

                    # Create normal switch support outline
                    if rotation == 0.0:
                        support_collection.add_item(x_offset, y_offset, Support(x_offset, y_offset, w, h, plate_thickness, support_bar_height, support_bar_width))
                        
                    # Create rotated switch support outline
                    elif rotation != 0.0:
                        support_rotation_collection.add_item(rotation, x_offset, y_offset, Support(x_offset, y_offset,w, h, plate_thickness, support_bar_height, support_bar_width), rx, ry)

                    x += w    
                    w = 1.0
                    h = 1.0

            y += 1

    max_x = support_collection.get_max_x()

    min_y = support_collection.get_min_y()

    logger.info('max_x: %d, min_y: %d', max_x, min_y)

    logger.info('build_x: %d, build_y: %d', build_x, build_y)

    x_parts = math.ceil(max_x / build_x)
    y_parts = math.ceil(abs(min_y) / build_y)
    logger.info('x_parts: %d, y_parts: %d', x_parts, y_parts)

    x_per_part = math.ceil(max_x / x_parts)
    y_per_part = math.floor(min_y / y_parts)
    logger.info('x_per_part: %d, y_per_part: %d', x_per_part, y_per_part)

    # Union all standard support blocks together
    for x in support_collection.get_x_list():
        for y in support_collection.get_y_list_in_x(x):
            switch_supports += support_collection.get_item(x, y).get_moved()
    
    # Union all standard switch cutouts together
    current_x_start = 0.0
    current_y_start = 0.0
    current_x_section = 0
    current_y_section = 0
    next_x_section = 0
    next_y_section = 0
    section_list = [[]]

    max_x, min_y = switch_collection.get_collection_bounds()

    switch_object_dict = switch_collection.get_collection_dict()
    for x in sorted(switch_object_dict.keys()):
        # if len(section_list) < current_x_section:
            
        #     section_list.append([])
        x_row = switch_object_dict[x]
        for y in x_row.keys():
            logger.debug('\tx: %d, y: %d', x, y)
            logger.debug('x_row.keys(): %s', str(x_row.keys()))
            switch_cutouts += x_row[y].get_moved()
            w = x_row[y].w
            h = x_row[y].h
            switch_support_cutouts += right(Cell.u(x)) ( forward(Cell.u(y)) ( 
                SupportCutout(x, y, w, h, plate_thickness, support_bar_height, support_bar_width).support_cutout()
                # switch_support_cutout( w = w, h = h, plate_thickness = 1.51 ) 
            ) )

            switch_x_max = Cell.u(x + w) + left_margin
            switch_x_min = Cell.u(x) + left_margin
            switch_y_max = Cell.u(abs(y) + h) + top_margin
            switch_y_min = Cell.u(abs(y)) + top_margin

            temp_object = {
                'x': x,
                'y': y,
                'w': w,
                'h': h,
                'switch_x_max': switch_x_max,
                'switch_x_min': switch_x_min,
                'switch_y_max': switch_y_max,
                'switch_y_min': switch_y_min,
                'object': x_row[y].get_moved()
            }

            if switch_x_max - current_x_start < x_build_size:
                # logger.info('current_x_section:', current_x_section)
                section_list[current_x_section].append(temp_object)
            elif switch_x_max - current_x_start > x_build_size and next_x_section > current_x_section:
                section_list[next_x_section].append(temp_object)
            else:
                # logger.info('switch_x_max:', switch_x_max, 'current_x_start:', current_x_start, 'switch_x_max - current_x_start:', switch_x_max - current_x_start, 'x_build_size:', x_build_size)
                section_list.append([temp_object])
                next_x_section = current_x_section + 1

            
            # logger.info('\tswitch_x: (', switch_x_min, ',', switch_x_max, '), switch_y: (', switch_y_min, switch_y_max, ')')
        
        if next_x_section > current_x_section:
            current_x_start = section_list[next_x_section][0]['switch_x_min']
            current_x_section = next_x_section

    section_objects = union()
    for idx, section in enumerate(section_list):
        # logger.info('new section: len', len(section))
        # logger.info('\tsection:', section)
        min_section_x = min(section, key=lambda switch:switch['x'])['switch_x_min']
        max_section_x = max(section, key=lambda switch:switch['x'])['switch_x_max']
        min_section_y = min(section, key=lambda switch:abs(switch['y']))['switch_y_min']
        max_section_y = max(section, key=lambda switch:abs(switch['y']))['switch_y_max']
        logger.info('min_section_x: %d', min_section_x)
        logger.info('max_section_x: %d', max_section_x)
        logger.info('min_section_y: %d', min_section_y)
        logger.info('max_section_y: %d', max_section_y)
        for section_item in section:
            section_objects += up(idx * 4) ( section_item['object'] )


    # Union together all switch cutouts 
    rotate_switch_cutout_collection = union()
    for rotation in switch_rotation_collection.get_rotation_list():
        rotate_switch_cutout_collection += switch_rotation_collection.get_rotated_moved_union(rotation)

    # Union together all support
    rotate_support_collection = union()
    for rotation in support_rotation_collection.get_rotation_list():
        rotate_support_collection += support_rotation_collection.get_rotated_moved_union(rotation)

    switch_supports += rotate_support_collection
    switch_cutouts += rotate_switch_cutout_collection
    # switch_cutouts = switch_cutout(2.5)

    body.set_dimensions(max_x, min_y)
    assembly += body.case()

    # assembly += switch_support_outline(set_to_origin = True)
    # assembly += right(20) ( get_moved() )

    assembly -= switch_support_cutouts
    # assembly -= rotate_support_cutout_collection
    assembly += switch_supports
    assembly -= switch_cutouts
    # assembly += section_objects
    # assembly = switch_cutouts

    scad_render_to_file(assembly, scad_output_file_name, file_header=f'$fn = {RESOLUTION};')


if __name__ == "__main__":
    main()
