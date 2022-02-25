#!/usr/bin/env python3

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

# import graphviz


from solid import *
from solid.utils import *

from parameters import Parameters
from keyboard import Keyboard
from cable import Cable

graph = False

logger = logging.getLogger('generator')
logger.setLevel(logging.INFO)

# create console handler and set level to info
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# add formatter to console_handler
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)



script_location = Path(os.path.dirname(os.path.realpath(__file__)))
log_file_name = 'log.txt'
log_file_path = script_location / log_file_name

# create file handler and set level to info
file_handler = logging.FileHandler(log_file_path, mode = 'w')
file_handler.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# add formatter to file_handler
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


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
    # parser.add_argument('-o', '--output-folder', metavar = 'scad', help = 'A path to a folder to store the generated open scad file')
    parser.add_argument('-p', '--parameter-file', metavar = 'parameters.json', help = 'A JSON file containing paramters for the object buing made', default = None, action=CheckExt({'json'}))
    parser.add_argument('-s', '--section', metavar = 'section_num', help = 'The number of the section that should be built', type = int, default = -1)
    parser.add_argument('-a', '--all-sections', help = 'Output all the parts for all possible sections in separate files', default = False, action = 'store_true')
    parser.add_argument('-e', '--exploded', help = 'Create test file with each section shown as an exploded view', default = False, action = 'store_true')
    parser.add_argument('-f', '--fragments', metavar = 'num_fragments', help = 'The number of fragments to be used when creating curves', type = int, default = 8)
    parser.add_argument('-r', '--render', help = 'Render an STL from the generated scad file', default = False, action = 'store_true')
    parser.add_argument('--switch-type-in-filename', help = 'Add the switch type name and stabilizer type name to the filname', default = False, action = 'store_true')

    
    rendered_object_dict = {}

    args = parser.parse_args()
    # logger.debug(vars(args))

    # Create Path object from input file argument
    input_file_path = Path(args.input_file)

    # Get base folder path
    base_path = input_file_path.parent

    # Get input file name onle
    file_name_only = input_file_path.name
    
    # Get layout name from file name
    layout_name = input_file_path.stem

    # Generate output scad and stl output folder paths
    output_base_folder = base_path / layout_name
    scad_folder_path = output_base_folder / 'scad'
    stl_folder_path = output_base_folder / 'stl'
    # graph_folder_path = output_base_folder / 'graph'

    if output_base_folder.is_dir() == False:
        output_base_folder.mkdir()

    if scad_folder_path.is_dir() == False:
        scad_folder_path.mkdir()

    if stl_folder_path.is_dir() == False:
        stl_folder_path.mkdir()

    # if graph == True and graph_folder_path.is_dir() == False:
    #     graph_folder_path.mkdir()

    logger.debug('layout_name: %s', str(layout_name))
    logger.debug('base_path: %s', str(base_path))
    logger.debug('file_name_only: %s', str(file_name_only))
    

    scad_postfix = '.scad'
    stl_postfix  = '.stl'
    gv_postfix  = '.gv'

    section_postfix = ''
    if args.section > -1:
        section_postfix = '_section_%d' % (args.section)

    scad_file_name = scad_folder_path / (layout_name + section_postfix + scad_postfix)
    stl_file_name = stl_folder_path / (layout_name + section_postfix + stl_postfix)

    logger.debug('Read layout from file %s', input_file_path)

    # Set fragments per circle
    FRAGMENTS = args.fragments
    logger.debug('\tFragments: %d', FRAGMENTS)

    json_key_pattern = '([{,])([xywha1]+):'
    json_key_replace = '\\1"\\2":'

    try:
        f = open(input_file_path, encoding="utf-8")
    except:
        logger.info('Failed to open file with utf-8 encoding specified. Try opening without specifying an encoding')
        try:
            f = open(input_file_path)
        except:
            logger.error('Failed to open file both spefifying utf-8 andcoding and not specifying any encodeing. Exiting')
            exit(1)

    keyboard_layout = f.read()

    keyboard_layout_dict = None

    # Load keyboard layout dictionary
    try:
        keyboard_layout_dict = json.loads(keyboard_layout)
        logger.debug('Valid Json Parsed')
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

    
    # Read parameter file
    parameter_dict = None
    if args.parameter_file is not None:
        f = open(args.parameter_file)

        parameter_file_text = f.read()

        try:
            parameter_dict = json.loads(parameter_file_text)
            logger.debug('Valid Json Parsed')
        except:
            logger.error('Failed to parse json after attempt at correction.')
            raise

    # Set parameters from imput file
    parameters = Parameters(parameter_dict)
    
    # Create Keyboard instance
    keyboard = Keyboard(parameters)

    if args.section > -1:
        keyboard.set_section(args.section)

    # Process the keyboard layout object
    keyboard.process_keyboard_layout(keyboard_layout_dict)

    logger.debug('kerf: %f', keyboard.kerf)

    if args.all_sections == True:
        for section in range(keyboard.get_top_section_count()):
            keyboard.set_section(section)
            rendered_object_dict[section] = {}
            rendered_object_dict[section]['top'] = keyboard.get_assembly(top = True)
            if section < keyboard.get_bottom_section_count():
                rendered_object_dict[section]['bottom'] = keyboard.get_assembly(bottom = True)
            rendered_object_dict[section]['all'] = keyboard.get_assembly(all = True)
            rendered_object_dict[section]['plate'] = keyboard.get_assembly(plate_only = True)
    elif args.exploded == True:
        rendered_object_dict[-1] = {}
        rendered_object_dict[-1]['top'] = union()
        rendered_object_dict[-1]['bottom'] = union()
        for section in range(keyboard.get_top_section_count()):
            keyboard.set_section(section)
            rendered_object_dict[-1]['top'] += up(5 * section) ( right(10 * section) ( keyboard.get_assembly(top = True) ) )
            if section < keyboard.get_bottom_section_count():
                rendered_object_dict[-1]['bottom'] += up(5 * section) ( right(10 * section) ( keyboard.get_assembly(bottom = True) ) )
    elif args.section > -1:
        # Get the full keyboard assembly
        rendered_object_dict[args.section] = {}
        rendered_object_dict[args.section]['top'] = keyboard.get_assembly(top = True)
        rendered_object_dict[args.section]['bottom'] = keyboard.get_assembly(bottom = True)
        rendered_object_dict[args.section]['all'] = keyboard.get_assembly(all = True)
        rendered_object_dict[args.section]['plate'] = keyboard.get_assembly(plate_only = True)
    elif args.section == -1:
        rendered_object_dict[args.section] = {}
        rendered_object_dict[args.section]['top'] = keyboard.get_assembly(top = True)
        rendered_object_dict[args.section]['bottom'] = keyboard.get_assembly(bottom = True)
        rendered_object_dict[args.section]['all'] = keyboard.get_assembly(all = True)
        rendered_object_dict[args.section]['plate'] = keyboard.get_assembly(plate_only = True)
        
    logger.info('Case Height: %f, Case Width: %f', parameters.real_case_height, parameters.real_case_width)
    logger.info('Sections In Top: %d', keyboard.get_top_section_count())
    logger.info('Sections In Bottom: %d', keyboard.get_bottom_section_count())

    # Remove all sections but the one desired if section option used
    # if args.section > -1:
    #     assembly -= keyboard.get_section_remove_block(args.section)



    ############################################################
    # Render SCAD and STL files
    ############################################################
    subprocess_dict = {}

    switch_type_for_filename = ''
    stab_type_for_filename = ''

    if args.switch_type_in_filename == True:
        switch_type_for_filename = '_' + parameters.switch_type
        stab_type_for_filename = '_' + parameters.stabilizer_type

    # if graph == True:
    #     gv_file_name = graph_folder_path / (layout_name + gv_postfix)
    #     logger.info('Global: %s', gv_file_name)
    #     keyboard.switch_collection.neighbor_check('global', gv_file_name)

    for section in rendered_object_dict.keys():
        section_postfix = ''
        if section > -1:
            section_postfix = '_section_%d' % (section)

        if args.exploded == True:
            section_postfix = '_exploded'

        # if graph == True and section_postfix != '':
        #     gv_file_name = graph_folder_path / (layout_name + section_postfix + gv_postfix)
        #     logger.info('Local: %s', gv_file_name)
        #     keyboard.switch_section_list[section].neighbor_check('local', gv_file_name)

        for part_name in rendered_object_dict[section].keys():
            part_name_formatted = '_' + part_name
            scad_file_name = scad_folder_path / (layout_name + section_postfix + part_name_formatted + switch_type_for_filename + stab_type_for_filename + scad_postfix)
            stl_file_name = stl_folder_path / (layout_name + section_postfix + part_name_formatted + switch_type_for_filename + stab_type_for_filename + stl_postfix)
            if rendered_object_dict[section][part_name] is not None:
                logger.info('Generate scad file with name %s', scad_file_name)
                # Generate SCAD file from assembly
                scad_render_to_file(rendered_object_dict[section][part_name], scad_file_name, file_header=f'$fn = {FRAGMENTS};')
                
                # Render STL if option is chosen
                if args.render:
                    logger.debug('Render STL from SCAD')
                    logger.info('Generate stl file with name %s from %s', stl_file_name, scad_file_name)


                    openscad_command_list = ['openscad', '-o', '%s' % (stl_file_name), '%s' % (scad_file_name)]
                    subprocess_dict[stl_file_name] = subprocess.Popen(openscad_command_list)

    if parameters.cable_hole == True:
        cable = Cable(parameters)

        side = 'main'
        scad_file_name = scad_folder_path / (layout_name + '_cable_holder_' + side + scad_postfix)
        stl_file_name = stl_folder_path / (layout_name + '_cable_holder_' + side + stl_postfix)
        logger.info('Generate scad file with name %s', scad_file_name)
        scad_render_to_file(cable.holder_main(), scad_file_name, file_header=f'$fn = {FRAGMENTS};')
        if args.render:
            openscad_command_list = ['openscad', '-o', '%s' % (stl_file_name), '%s' % (scad_file_name)]
            subprocess_dict[stl_file_name] = subprocess.Popen(openscad_command_list)


        side = 'clamp'
        scad_file_name = scad_folder_path / (layout_name + '_cable_holder_' + side + scad_postfix)
        stl_file_name = stl_folder_path / (layout_name + '_cable_holder_' + side + stl_postfix)
        logger.info('Generate scad file with name %s', scad_file_name)
        scad_render_to_file(cable.holder_clamp(), scad_file_name, file_header=f'$fn = {FRAGMENTS};')
        if args.render:
            openscad_command_list = ['openscad', '-o', '%s' % (stl_file_name), '%s' % (scad_file_name)]
            subprocess_dict[stl_file_name] = subprocess.Popen(openscad_command_list)

        scad_file_name = scad_folder_path / (layout_name + '_cable_holder_all' + scad_postfix)
        stl_file_name = scad_folder_path / (layout_name + '_cable_holder_all' + stl_postfix)
        logger.info('Generate scad file with name %s', scad_file_name)
        scad_render_to_file(cable.holder_all(), scad_file_name, file_header=f'$fn = {FRAGMENTS};')
        if args.render:
            openscad_command_list = ['openscad', '-o', '%s' % (stl_file_name), '%s' % (scad_file_name)]
            subprocess_dict[stl_file_name] = subprocess.Popen(openscad_command_list)



    ################################################################
    #  Wait for render processes to complete
    ################################################################
    if args.render:
        logger.debug(subprocess_dict)
        running = True
        while running == True:
            running = False
            for stl_file_name in subprocess_dict.keys():
                p = subprocess_dict[stl_file_name]
                if p is not None:
                    # running = True
                    rcode = None
                    try:
                        rcode = p.wait(.1)
                    except subprocess.TimeoutExpired as err:
                        logger.debug('Wait Timeout: %s', str(err))
                        running = True
                    if rcode is not None:
                        logger.info('Render Complete: file: %s', stl_file_name)
                        subprocess_dict[stl_file_name] = None
            # time.sleep(1)



    logger.info('Generation Complete')

if __name__ == "__main__":
    main()
