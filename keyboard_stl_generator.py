

import argparse
import json
import math
import re
import logging
import os
import os.path

from solid import *
from solid.utils import *

from switch import Switch
from support import Support
from support_cutout import SupportCutout
from cell import Cell
from item_collection import ItemCollection
from rotation_collection import RotationCollection
from body import Body
from keyboard import Keyboard

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

# # #[Model Features]#
# plate_only = 0


# # #[Printer Info]#
# x_build_size = 200
# y_build_size = 200
# part_number = 1

# # #[Switch Adjustment Dimensions]#
# kerf = 0.00

# # #[Holder Dimensions]# 
# top_margin = 8
# bottom_margin = 8
# left_margin = 8
# right_margin = 8
# case_height = 10
# plate_wall_thickness = 2.0
# plate_thickness = 1.511
# plate_corner_radius = 4

# # #[Support Bars]#  
# support_bar_height = 3.0
# support_bar_width = 1.0


# support_bar_tile_width = support_bar_width / 2


# build_x = math.floor(x_build_size / Cell.SWITCH_SPACING)
# build_y = math.floor(y_build_size / Cell.SWITCH_SPACING)



def CheckExt(choices):
    class Act(argparse.Action):
        def __call__(self,parser,namespace,fname,option_string=None):
            ext = os.path.splitext(fname)[1][1:]
            if ext not in choices:
                option_string = '({})'.format(option_string) if option_string else ''
                parser.error("file doesn't end with one of {}{}".format(choices,option_string))
            else:
                setattr(namespace,self.dest,fname)

    return Act



def main():

    parser = argparse.ArgumentParser(description='Build custom keyboard SCAD file using keyboard layout editor format')
    parser.add_argument('-i', '--input-file', metavar = 'layout_json_file_name.json', help = 'A path to a keyboard layout editor json file', required = True, action=CheckExt({'json'}))
    parser.add_argument('-o', '--output-file', metavar = 'object_name.scad', help = 'A path to a file to store the generated open scad file', action=CheckExt({'scad'}))
    parser.add_argument('-p', '--parameter-file', metavar = 'parameters.json', help = 'A JSON file containing paramters for the object buing made', default = None, action=CheckExt({'json'}))
    parser.add_argument('-r', '--render', help = 'Render an STL from the generated scad file', default = False, action = 'store_true')
    parser.add_argument('-f', '--fragments', metavar = 'num_fragments', help = 'The number of fragments to be used when creating curves', default = 8)
    # parser.add_argument('-f', '--fill-edges', help = 'Fill empty edges to ensure keyboard is a complete rectangle', default = False, action = 'store_true')
    parser.add_argument('-x', '--x-fill', help = 'Pad empty spaces to the left of keys', default = False, action = 'store_true')
    parser.add_argument('-b', '--blank-fill', help = 'Pad empty spaces to the left of keys', default = False, action = 'store_true')
    # parser.add_argument('-b', '--build-area-break', metavar = 'sub_part_number', help = 'Pad empty spaces to the left of keys', default = -1 )
    # parser.add_argument('-t', '--plate-thickness', type = float, metavar = 'plate_thickness', help = 'Plate thickness in milimeters', default = 1.51 ) 
    # parser.add_argument('-p', '--plate-only', help = 'Only create the plate do not create case walls', default = False, action = 'store_true')
    # parser.add_argument('-s', '--plate-supports', help = 'Create support grid on entire plate', default = False, action = 'store_true')


    args = parser.parse_args()
    # logger.info(vars(args))

    layout_json_file_name = args.input_file

    if args.output_file is None:
        scad_output_file_name = layout_json_file_name.replace('.json', '_out.scad')
        stl_output_file_name = layout_json_file_name.replace('.json', '_out.stl')
    else:
        scad_output_file_name = args.output_file
        stl_output_file_name = scad_output_file_name.replace('.scad', '.stl')

    logger.info('Read layout from file %s write generated scad to %s. ', layout_json_file_name, scad_output_file_name)

    FRAGMENTS = args.fragments
    logger.info('\tFragments: %d', FRAGMENTS)

    json_key_pattern = '([{,])([xywha1]+):'
    json_key_replace = '\\1"\\2":'

    # modifier_include_list = ['x', 'y', 'w', 'h', 'r', 'rx', 'ry']

    f = open(layout_json_file_name)

    keyboard_layout = f.read()

    keyboard_layout_dict = None

    try:
        keyboard_layout_dict = json.loads(keyboard_layout)
        logger.warning('Valid Json Parsed')
    except:
        keyboard_layout = '[%s]' % (keyboard_layout)
        json_replace_match = re.search(json_key_pattern, keyboard_layout)
        keyboard_layout = re.sub(json_key_pattern, json_key_replace, keyboard_layout)
        try:
            keyboard_layout_dict = json.loads(keyboard_layout)
            logger.warning('Initial Json Invalid. Json modified and parsed')
        except:
            logger.error('Failed to parse json after attempt at correction.')
            raise

    logger.debug('keyboard_layout_dict:', keyboard_layout_dict)

    keyboard = Keyboard()

    parameter_dict = None
    # Read parameter file
    if args.parameter_file is not None:
        f = open(args.parameter_file)

        parameter_file_text = f.read()

        try:
            parameter_dict = json.loads(parameter_file_text)
            logger.warning('Valid Json Parsed')
        except:
            logger.error('Failed to parse json after attempt at correction.')
            raise

        keyboard.set_parameter_dict(parameter_dict)

    keyboard.process_keyboard_layout(keyboard_layout_dict)




    # max_x, min_y = keyboard.switch_collection.get_collection_bounds()
    # logger.info('max_x: %d, min_y: %d', max_x, min_y)
    # logger.info('build_x: %d, build_y: %d', keyboard.build_x, keyboard.build_y)

    # x_parts = math.ceil(max_x / keyboard.build_x)
    # y_parts = math.ceil(abs(min_y) / keyboard.build_y)
    # logger.info('x_parts: %d, y_parts: %d', x_parts, y_parts)

    # x_per_part = math.ceil(max_x / x_parts)
    # y_per_part = math.floor(min_y / y_parts)
    # logger.info('x_per_part: %d, y_per_part: %d', x_per_part, y_per_part)

    # # Union all standard switch cutouts together
    # current_x_start = 0.0
    # current_y_start = 0.0
    # current_x_section = 0
    # current_y_section = 0
    # next_x_section = 0
    # next_y_section = 0
    # section_list = [[]]

    # build_area = left(keyboard.left_margin) ( back(keyboard.y_build_size - keyboard.top_margin) ( down(10) ( cube([keyboard.x_build_size, keyboard.y_build_size, 10]) ) ) )

    # switch_object_dict = keyboard.switch_collection.get_collection_dict()
    # for x in sorted(switch_object_dict.keys()):
    #     # if len(section_list) < current_x_section:
            
    #     #     section_list.append([])
    #     x_row = switch_object_dict[x]
    #     for y in x_row.keys():
    #         logger.debug('\tx: %d, y: %d', x, y)
    #         logger.debug('x_row.keys(): %s', str(x_row.keys()))
    #         # switch_cutouts += x_row[y].get_moved()
    #         w = x_row[y].w
    #         h = x_row[y].h
            
    #         switch_x_max = Cell.u(x + w) + keyboard.left_margin
    #         switch_x_min = Cell.u(x) + keyboard.left_margin
    #         switch_y_max = Cell.u(abs(y) + h) + keyboard.top_margin
    #         switch_y_min = Cell.u(abs(y)) + keyboard.top_margin

    #         temp_object = {
    #             'x': x,
    #             'y': y,
    #             'w': w,
    #             'h': h,
    #             'switch_x_max': switch_x_max,
    #             'switch_x_min': switch_x_min,
    #             'switch_y_max': switch_y_max,
    #             'switch_y_min': switch_y_min,
    #             'object': x_row[y].get_moved()
    #         }

    #         if switch_x_max - current_x_start < keyboard.x_build_size:
    #             # logger.info('current_x_section:', current_x_section)
    #             section_list[current_x_section].append(temp_object)
    #         elif switch_x_max - current_x_start > keyboard.x_build_size and next_x_section > current_x_section:
    #             section_list[next_x_section].append(temp_object)
    #         else:
    #             # logger.info('switch_x_max:', switch_x_max, 'current_x_start:', current_x_start, 'switch_x_max - current_x_start:', switch_x_max - current_x_start, 'x_build_size:', x_build_size)
    #             section_list.append([temp_object])
    #             next_x_section = current_x_section + 1

            
    #         # logger.info('\tswitch_x: (', switch_x_min, ',', switch_x_max, '), switch_y: (', switch_y_min, switch_y_max, ')')
        
    #     if next_x_section > current_x_section:
    #         current_x_start = section_list[next_x_section][0]['switch_x_min']
    #         current_x_section = next_x_section


    assembly = keyboard.get_assembly()

    keyboard.split_keybaord()


    for idx, section in enumerate(keyboard.section_list):
        section_built = False
        for i in range(len(section)):
            max_x = 0.0
            max_x_y = 0.0
            max_x_min_y = 0.0
            min_y = 0.0
            min_y_x = 0.0
            min_y_max_x = 0.0
            for key in section:
                if key['accounted_for'] == False:
                    x_end = key['x'] + key['w']
                    y_end = key['y'] - key['h']
                    if x_end > max_x:
                        max_x = x_end 
                        max_x_min_y = y_end
                    elif x_end == max_x and y_end < max_x_min_y:
                        max_x_min_y = y_end

                    if y_end < min_y:
                        min_y = y_end
                        min_y_max_x = x_end
                    elif y_end == min_y and x_end > min_y_max_x:
                        min_y_max_x = x_end

            assembly += right(Cell.u(min_y_max_x)) ( forward(Cell.u(max_x_min_y)) ( down(30 / 2) ( cube([keyboard.support_bar_width, Cell.u(1), 30]) ) ) )

            for key in section:
                if key['accounted_for'] == False:
                    x_end = key['x'] + key['w']
                    y_end = key['y'] - key['h']

                    if max_x_min_y == y_end:
                        key['accounted_for'] = True

            logger.info('section: %d, max_x: %f, max_x_min_y: %f, min_y: %f, min_y_max_x: %f', idx, max_x, max_x_min_y, min_y, min_y_max_x)
            section_built = True
                

    section_objects = union()
    for idx, section in enumerate(keyboard.section_list):
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
            section_objects += up(idx * 8) ( section_item['object'] )

    

    assembly += section_objects
    # assembly += build_area

    scad_render_to_file(assembly, scad_output_file_name, file_header=f'$fn = {FRAGMENTS};')
    # scad_render_to_file(assembly, scad_output_file_name)

    if args.render:
        logger.info('Render STL from SCAD')
        os.system('openscad -o %s  %s' % (stl_output_file_name, scad_output_file_name))


if __name__ == "__main__":
    main()
