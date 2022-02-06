

import argparse
from asyncio import subprocess
import json
import math
import re
import logging
import os
# import os.path
import subprocess
import time

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
    parser.add_argument('-o', '--output-folder', metavar = 'scad', help = 'A path to a folder to store the generated open scad file')
    parser.add_argument('-p', '--parameter-file', metavar = 'parameters.json', help = 'A JSON file containing paramters for the object buing made', default = None, action=CheckExt({'json'}))
    parser.add_argument('-r', '--render', help = 'Render an STL from the generated scad file', default = False, action = 'store_true')
    parser.add_argument('-f', '--fragments', metavar = 'num_fragments', help = 'The number of fragments to be used when creating curves', type = int, default = 8)
    parser.add_argument('-s', '--section', metavar = 'section_num', help = 'The number of the section that should be built', type = int, default = -1)
    parser.add_argument('-x', '--x-fill', help = 'Pad empty spaces to the left of keys', default = False, action = 'store_true')
    parser.add_argument('-b', '--blank-fill', help = 'Pad empty spaces to the left of keys', default = False, action = 'store_true')
    
    rendered_object_dict = {}

    args = parser.parse_args()
    # logger.debug(vars(args))

    layout_json_file_name = args.input_file

    # Generate Output Filenames from Input Filename
    file_name_parts = layout_json_file_name.split('/')
    base_path = '/'.join(file_name_parts[:-1]) + '/'
    scad_folder_path = base_path + 'scad/'
    stl_folder_path = base_path + 'stl/'

    if os.path.isdir(scad_folder_path) == False:
        os.mkdir(scad_folder_path)

    if os.path.isdir(stl_folder_path) == False:
        os.mkdir(stl_folder_path)

    file_name_only = file_name_parts[-1]
    
    base_file_name = '.'.join(file_name_only.split('.')[:-1])

    logger.info('file_name_parts: %s', str(file_name_parts))
    logger.info('base_path: %s', str(base_path))
    logger.info('file_name_only: %s', str(file_name_only))
    logger.info('base_file_name: %s', str(base_file_name))

    scad_postfix = '.scad'
    stl_postfix  = '.stl'

    # scad_output_file_name = base_file_name + scad_postfix
    # stl_output_file_name = base_file_name + stl_postfix

    section_postfix = ''
    if args.section > -1:
        section_postfix = '_section_%d' % (args.section)

    scad_file_name = scad_folder_path + base_file_name + section_postfix + scad_postfix
    stl_file_name = stl_folder_path + base_file_name + section_postfix + stl_postfix

    logger.info('Read layout from file %s write generated scad to %s. ', layout_json_file_name, scad_file_name)

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

    if args.section > -1:
        # Get the full keyboard assembly
        rendered_object_dict[args.section] = {}
        rendered_object_dict[args.section]['top'] = keyboard.get_assembly(top = True)
        rendered_object_dict[args.section]['bottom'] = keyboard.get_assembly(bottom = True)
        rendered_object_dict[args.section]['all'] = keyboard.get_assembly(all = True)
    elif args.section == -1:
        rendered_object_dict[args.section] = {}
        rendered_object_dict[args.section]['top'] = keyboard.get_assembly(top = True)
        rendered_object_dict[args.section]['bottom'] = keyboard.get_assembly(bottom = True)
        rendered_object_dict[args.section]['all'] = keyboard.get_assembly(all = True)
    elif args.section == -2:
        for section in range(keyboard.get_section_count()):
            keyboard.set_section(section)
            rendered_object_dict[section] = {}
            rendered_object_dict[section]['top'] = keyboard.get_assembly(top = True)
            rendered_object_dict[section]['bottom'] = keyboard.get_assembly(bottom = True)
            rendered_object_dict[section]['all'] = keyboard.get_assembly(all = True)
    elif args.section == -3:
        rendered_object_dict[-1] = {}
        rendered_object_dict[-1]['top'] = union()
        rendered_object_dict[-1]['bottom'] = union()
        for section in range(keyboard.get_section_count()):
            keyboard.set_section(section)
            rendered_object_dict[-1]['top'] += up(5 * section) ( keyboard.get_assembly(top = True) )
            rendered_object_dict[-1]['bottom'] += up(5 * section) ( keyboard.get_assembly(bottom = True) )


    # Remove all sections but the one desired if section option used
    # if args.section > -1:
    #     assembly -= keyboard.get_section_remove_block(args.section)

    subprocess_dict = {}

    for section in rendered_object_dict.keys():
        section_postfix = ''
        if section > -1:
            section_postfix = '_section_%d' % (section)

        for part_name in rendered_object_dict[section].keys():
            part_name_formatted = '_' + part_name
            scad_file_name = scad_folder_path + base_file_name + section_postfix + part_name_formatted + scad_postfix
            stl_file_name = stl_folder_path + base_file_name + section_postfix + part_name_formatted + stl_postfix
            if rendered_object_dict[section][part_name] is not None:
                logger.info('Generate scad file with name %s', scad_file_name)
                # Generate SCAD file from assembly
                scad_render_to_file(rendered_object_dict[section][part_name], scad_file_name, file_header=f'$fn = {FRAGMENTS};')
                
                # Render STL if option is chosen
                if args.render:
                    logger.info('Render STL from SCAD')
                    logger.info('Generate stl file with name %s from %s', stl_file_name, scad_file_name)


                    openscad_command_list = ['openscad', '-o', '%s' % (stl_file_name), '%s' % (scad_file_name)]
                    # openscad_command = 'openscad -o %s  %s' % (stl_file_name, scad_file_name)

                    subprocess_dict[stl_file_name] = subprocess.Popen(openscad_command_list)

                    # os.system(openscad_command)

    if args.render:
        logger.info(subprocess_dict)
        running = True
        while running == True:
            running = False
            for stl_file_name in subprocess_dict.keys():
                p = subprocess_dict[stl_file_name]
                if p is not None:
                    running = True
                    rcode = p.poll()
                    if rcode is not None:
                        logger.info('file: %s, process: %s complete, return code %s', stl_file_name, str(p), str(rcode))
                        subprocess_dict[stl_file_name] = None
            time.sleep(1)


if __name__ == "__main__":
    main()
