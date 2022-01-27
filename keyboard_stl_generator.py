

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
    parser.add_argument('-x', '--x-fill', help = 'Pad empty spaces to the left of keys', default = False, action = 'store_true')
    parser.add_argument('-b', '--blank-fill', help = 'Pad empty spaces to the left of keys', default = False, action = 'store_true')


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

    assembly = keyboard.get_assembly()

    keyboard.split_keyboard()

    section_objects = union()
    for idx, section in enumerate(keyboard.section_list):
        section_objects += up(idx * 8) ( section.get_moved_union() )
    
    for section_number in range(len(keyboard.section_list)):
        assembly +=keyboard.get_section(section_number)

    #  keyboard.get_section(0)


    # for idx, section in enumerate(keyboard.section_list):
    #     section_built = False
    #     for i in range(len(section)):
    #         max_x = 0.0
    #         max_x_y = 0.0
    #         max_x_min_y = 0.0
    #         min_y = 0.0
    #         min_y_x = 0.0
    #         min_y_max_x = 0.0
    #         for key in section:
    #             if key['accounted_for'] == False:
    #                 x_end = key['x'] + key['w']
    #                 y_end = key['y'] - key['h']
    #                 if x_end > max_x:
    #                     max_x = x_end 
    #                     max_x_min_y = y_end
    #                 elif x_end == max_x and y_end < max_x_min_y:
    #                     max_x_min_y = y_end

    #                 if y_end < min_y:
    #                     min_y = y_end
    #                     min_y_max_x = x_end
    #                 elif y_end == min_y and x_end > min_y_max_x:
    #                     min_y_max_x = x_end

    #         assembly += right(Cell.u(min_y_max_x)) ( forward(Cell.u(max_x_min_y)) ( down(30 / 2) ( cube([keyboard.support_bar_width, Cell.u(1), 30]) ) ) )

    #         for key in section:
    #             if key['accounted_for'] == False:
    #                 x_end = key['x'] + key['w']
    #                 y_end = key['y'] - key['h']

    #                 if max_x_min_y == y_end:
    #                     key['accounted_for'] = True

    #         logger.info('section: %d, max_x: %f, max_x_min_y: %f, min_y: %f, min_y_max_x: %f', idx, max_x, max_x_min_y, min_y, min_y_max_x)
    #         section_built = True
                

    
    
    # for 
    # keyboard.section_list[0].set_item_neighbors()

    assembly += section_objects
    # assembly += build_area

    scad_render_to_file(assembly, scad_output_file_name, file_header=f'$fn = {FRAGMENTS};')
    # scad_render_to_file(assembly, scad_output_file_name)

    if args.render:
        logger.info('Render STL from SCAD')
        os.system('openscad -o %s  %s' % (stl_output_file_name, scad_output_file_name))


if __name__ == "__main__":
    main()
