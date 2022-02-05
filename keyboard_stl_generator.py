

import argparse
import json
import math
import re
import logging
import os
# import os.path

from solid import *
from solid.utils import *

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
    parser.add_argument('-f', '--fragments', metavar = 'num_fragments', help = 'The number of fragments to be used when creating curves', type = int, default = 8)
    parser.add_argument('-s', '--section', metavar = 'section_num', help = 'The number of the section that should be built', type = int, default = -1)
    parser.add_argument('-x', '--x-fill', help = 'Pad empty spaces to the left of keys', default = False, action = 'store_true')
    parser.add_argument('-b', '--blank-fill', help = 'Pad empty spaces to the left of keys', default = False, action = 'store_true')
    
    rendered_object_dict = {
        'top': None,
        'bottom': None,
        'all': None
    }

    args = parser.parse_args()
    # logger.debug(vars(args))

    layout_json_file_name = args.input_file

    # Generate Output Filenames from Input Filneamr
    if args.output_file is None:
        scad_output_file_name = layout_json_file_name.replace('.json', '_out.scad')
        stl_output_file_name = layout_json_file_name.replace('.json', '_out.stl')
    else:
        scad_output_file_name = args.output_file
        stl_output_file_name = scad_output_file_name.replace('.scad', '.stl')

    if args.section > -1:
        scad_output_file_name = scad_output_file_name.replace('_out.scad', '_section_%d_out.scad' % (args.section))
        stl_output_file_name = stl_output_file_name.replace('_out.stl', '_section_%d_out.stl' % (args.section))


    logger.info('Read layout from file %s write generated scad to %s. ', layout_json_file_name, scad_output_file_name)

    # Set fragments per circle
    FRAGMENTS = args.fragments
    logger.info('\tFragments: %d', FRAGMENTS)

    json_key_pattern = '([{,])([xywha1]+):'
    json_key_replace = '\\1"\\2":'

    f = open(layout_json_file_name)

    keyboard_layout = f.read()

    keyboard_layout_dict = None

    # Load keyboard layout dictionary
    try:
        keyboard_layout_dict = json.loads(keyboard_layout)
        logger.warning('Valid Json Parsed')
    except:
        keyboard_layout = '[%s]' % (keyboard_layout)
        json_replace_match = re.search(json_key_pattern, keyboard_layout)
        keyboard_layout = re.sub(json_key_pattern, json_key_replace, keyboard_layout)
        try:
            keyboard_layout_dict = json.loads(keyboard_layout)
            logger.info('Initial Json Invalid. Json modified and parsed')
        except:
            logger.error('Failed to parse json after attempt at correction.')
            raise

    logger.debug('keyboard_layout_dict:', keyboard_layout_dict)

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

    
    # Create Keyboard instance
    keyboard = Keyboard(parameter_dict)

    # Set parameters on Keyboard object
    # keyboard.set_parameter_dict(parameter_dict)

    if args.section > -1:
        keyboard.set_section(args.section)

    # Process the keyboar layout object
    keyboard.process_keyboard_layout(keyboard_layout_dict)

    # Get the full keyboard assembly
    # rendered_object_dict['top'] = keyboard.get_assembly(top = True)
    # rendered_object_dict['bottom'] = keyboard.get_assembly(bottom = True)
    # rendered_object_dict['all'] = keyboard.get_assembly(all = True)

    rendered_object_dict['top'] = union()
    for section in range(keyboard.get_section_count()):
        keyboard.set_section(section)
        rendered_object_dict['top'] += up(10 * section) ( keyboard.get_assembly(top = True) )


    # Remove all sections but the one desired if section option used
    # if args.section > -1:
    #     assembly -= keyboard.get_section_remove_block(args.section)

    for part_name in rendered_object_dict.keys():
        if rendered_object_dict[part_name] is not None:
            scad_file_name = scad_output_file_name.replace('_out.scad', '_%s_out.scad' % (part_name) )
            logger.info('Generate scad file with name %s', scad_file_name)
            # Generate SCAD file from assembly
            scad_render_to_file(rendered_object_dict[part_name], scad_file_name, file_header=f'$fn = {FRAGMENTS};')
            
            # Render STL if option is chosen
            if args.render:
                logger.info('Render STL from SCAD')
                stl_file_name = stl_output_file_name.replace('_out.stl', '_%s_out.stl' % (part_name) )
                logger.info('Generate stl file with name %s from %s', stl_file_name, scad_file_name)
                os.system('openscad -o %s  %s' % (stl_file_name, scad_file_name))


if __name__ == "__main__":
    main()
