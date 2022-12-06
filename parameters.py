import logging
import math
import sys
from pathlib import PurePath

from switch_config import SwitchConfig
# from cell import Cell



class Parameters():

    # SWITCH_SPACING = 19.05

    def __init__(self, parameter_dict: dict = None):

        self.logger = logging.getLogger(__name__)

        self.parameter_dict = parameter_dict

        # self.default_parameter_dict = {
        #     'plate_supports': True,
            
        #     'x_build_size' : 200,
        #     'y_build_size' : 200,

        #     'switch_type': 'mx_openable',
        #     'stabilizer_type': 'cherry',

        #     'custom_shape': False, 
        #     'custom_shape_points': None,
        #     'custom_shape_path': None,

        #     'kerf' : 0.00,

        #     'top_margin' : 0,
        #     'bottom_margin' : 0,
        #     'left_margin' : 0,
        #     'right_margin' : 0,
        #     'case_height' : 10,
        #     # 'plate_wall_thickness' : 2.0,
        #     'case_wall_thickness' : 0.0,
        #     'plate_thickness' : 1.111,
        #     'plate_corner_radius' : 0,
        #     'bottom_cover_thickness': 0,

        #     'support_bar_height' : 3.0,
        #     'support_bar_width' : 1.0,
        #     'tilt': 0.0,

        #     'simple_test': False,

        #     'screw_count': 0,
        #     'screw_diameter': 0,
        #     'screw_edge_inset': 0,

        #     'cable_hole': False,
        #     'hole_width': 10,
        #     'hole_height': 10,
        #     'cable_hole_down_offset': 1
        # }


        self.paramater_alternate_dict = {
            'plate_wall_thickness': 'case_wall_thickness'
        }

        self.switch_spacing = 19.05

        self.x_build_size = 200
        self.y_build_size = 200
        self.kerf = 0.00

        self.switch_type = 'mx_openable'
        self.stabilizer_type = 'cherry'

        # Custom Switch Cutout Attributes
        self.custom_shape = False 
        self.custom_shape_points = None
        self.custom_shape_path = None

        self.plate_supports = True
        self.support_bar_height = 3.0
        self.support_bar_width = 1.0

        self.top_margin = 0
        self.bottom_margin = 0
        self.left_margin = 0
        self.right_margin = 0

        self.case_height = self.support_bar_height
        self.case_wall_thickness = 0
        self.plate_thickness = 1.111
        self.plate_corner_radius = 0
        self.bottom_cover_thickness = 1
        self.tilt = 0.0

        self.simple_test = False

        self.screw_count = 0
        self.screw_diameter = 0
        self.screw_edge_inset = 0
        self.screw_edge_x_inset = None
        self.screw_edge_y_inset = None
        self.screw_hole_body_wall_width = 2
        self.screw_hole_body_support_x_factor = 4

        self.custom_screw_hole_coordinates_origin = [0, 0]
        self.custom_screw_hole_coordinates = None

        self.cable_hole = False
        self.cable_diameter = 4
        self.cable_hole_width = 10
        self.cable_hole_height = 10
        self.cable_hole_up_offset = 1
        self.cable_hole_down_offset = 1

        self.custom_polygons = None

        self.custom_pcb = None
        self.pcb_width = None
        self.pcb_height = None
        self.pcb_top_left_coordinates = None
        self.pcb_left_switch_center_x_coordinate = None
        self.pcb_top_switch_center_y_coordinate = None
        self.pcb_case_top_margin = None
        self.pcb_case_bottom_margin = None
        self.pcb_case_right_margin = None
        self.pcb_case_left_margin = None

        self.test_block = False
        self.test_block_x_start = 0
        self.test_block_x_end = 0
        self.test_block_y_start = 0
        self.test_block_y_end = 0
        self.test_block_z_start = 0
        self.test_block_z_end = 0

        self.switch_config = None
        
        self.min_x = 0.0
        self.max_x = 0.0
        self.min_y = 0.0
        self.max_y = 0.0

        self.real_max_x = 0.0
        self.real_max_y = 0.0
        self.real_case_width = 0.0
        self.real_case_height = 0.0

        self.case_height_extra = 50

        # Calculated attributes
        self.case_height_base_removed = None
        self.case_height_extra_fill = None
        self.side_margin_diff = None
        self.top_margin_diff = None
        self.screw_tap_hole_diameter = None
        self.screw_hole_body_diameter = None
        self.screw_hole_body_radius = None
        self.x_screw_width = None
        self.y_screw_width = None
        self.bottom_section_count = None
        self.screw_hole_body_support_end_x = None

        if self.parameter_dict is not None:
            self.build_attr_from_dict(self.parameter_dict)

        # self.validate_parameters()
        

    def __repr__(self):
        output = 'Parameters:\n'
        ignore_attr_names = [
            'logger', 'parameter_dict', 'switch_config', 
            'min_x', 'max_x', 'min_y', 'max_y', 
            'real_max_x', 'real_max_y', 
            # 'real_case_width', 'real_case_height', 
            'case_height_extra', 'case_height_base_removed', 'case_height_extra_fill', 'side_margin_diff', 
            'top_margin_diff', 'screw_tap_hole_diameter', 'screw_hole_body_diameter', 'screw_hole_body_radius', 
            'x_screw_width', 'y_screw_width', 'bottom_section_count', 'screw_hole_body_support_end_x',
            'test_block', 'test_block_x_start', 'test_block_x_end', 'test_block_y_start',
            'test_block_y_end', 'test_block_z_start', 'test_block_z_end'
        ]
        for attr_name in self.__dict__:
            if attr_name not in ignore_attr_names:
                output += '%s: %s\n' % (attr_name, str(self.__dict__[attr_name]))

        return output

    
    def U(self, u_value):
        return u_value * self.switch_spacing


    def update_calculated_attributes(self):
        # Calculated attributes
        if self.screw_edge_x_inset is None:
            self.screw_edge_x_inset = self.screw_edge_inset
        if self.screw_edge_y_inset is None:
            self.screw_edge_y_inset = self.screw_edge_inset
        
        self.case_height_base_removed = self.case_height - self.bottom_cover_thickness
        self.case_height_extra_fill = self.case_height + self.case_height_extra
        self.side_margin_diff = self.right_margin - self.left_margin
        self.top_margin_diff = self.bottom_margin - self.top_margin
        self.screw_tap_hole_diameter = self.screw_diameter - 0.35
        self.screw_hole_body_diameter = self.screw_diameter + (self.screw_hole_body_wall_width * 2)
        self.screw_hole_body_radius = self.screw_hole_body_diameter / 2
        self.x_screw_width = self.real_case_width - ((self.screw_edge_x_inset * 2))# + self.screw_diameter)
        self.y_screw_width = self.real_case_height - ((self.screw_edge_y_inset * 2))# + self.screw_diameter)
        self.bottom_section_count = math.ceil(self.real_case_width / self.x_build_size)
        self.screw_hole_body_support_end_x = (self.case_height_extra_fill / self.screw_hole_body_support_x_factor) + self.screw_hole_body_radius


    def set_dimensions(self, max_x, min_y, min_x, max_y):
        

        self.max_x = max_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.logger.debug('min_x: %f, max_x: %f, max_y: %f, min_y: %f', self.min_x, self.max_x, self.max_y, self.min_y)

        # Get rhe calculated real max and y sizes of the board
        self.real_max_x = self.U(self.max_x)
        self.real_max_y = self.U(abs(self.min_y))

        self.real_case_width = self.real_max_x + self.left_margin + self.right_margin
        self.real_case_height = self.real_max_y + self.top_margin + self.bottom_margin

        if self.custom_screw_hole_coordinates is not None:
            self.screw_edge_x_inset = 0
            self.screw_edge_y_inset = 0
            self.logger.debug('Custom Screw Default: screw_edge_x_inset: %f, screw_edge_y_inset: %f', self.screw_edge_x_inset, self.screw_edge_y_inset)

        if self.custom_pcb == True:
            half_u = self.U(1) / 2

            # Get the top left coordinates for the PCB itself.
            pcb_x_coordinate = 0
            pcb_y_coordinate = 0
            if self.pcb_top_left_coordinates is not None:
                pcb_x_coordinate = self.pcb_top_left_coordinates[0]
                pcb_y_coordinate = self.pcb_top_left_coordinates[1]
            
            # Get the x any y coordinates of the top reference switch and left reference switch
            left_switch_left_x_coordinate = self.pcb_left_switch_center_x_coordinate - half_u
            top_switch_top_y_coordinate = self.pcb_top_switch_center_y_coordinate - half_u
            
            # Get the margin built into the left and top of the PCB
            pcb_left_margin = left_switch_left_x_coordinate - pcb_x_coordinate
            pcb_top_margin = top_switch_top_y_coordinate - pcb_y_coordinate

            pcb_right_margin = self.pcb_width - (pcb_left_margin + self.real_max_x)
            pcb_bottom_margin = self.pcb_height - (pcb_top_margin + self.real_max_y)

            self.left_margin = self.case_wall_thickness + self.pcb_case_left_margin + pcb_left_margin
            self.right_margin = self.case_wall_thickness + self.pcb_case_right_margin + pcb_right_margin
            self.top_margin = self.case_wall_thickness + self.pcb_case_top_margin + pcb_top_margin
            self.bottom_margin = self.case_wall_thickness + self.pcb_case_bottom_margin + pcb_bottom_margin

            if self.custom_screw_hole_coordinates is not None:
                screw_hole_origin_x = self.custom_screw_hole_coordinates_origin[0]
                screw_hole_origin_y = self.custom_screw_hole_coordinates_origin[1]

                screw_hole_pcb_origin_x_offset = screw_hole_origin_x - pcb_x_coordinate
                screw_hole_pcb_origin_y_offset = (pcb_y_coordinate + self.pcb_height) - screw_hole_origin_y

                self.screw_edge_x_inset = self.case_wall_thickness + self.pcb_case_left_margin + screw_hole_pcb_origin_x_offset
                self.screw_edge_y_inset = self.case_wall_thickness + self.pcb_case_bottom_margin + screw_hole_pcb_origin_y_offset
                self.logger.debug('PCB settings: screw_edge_x_inset: %f, screw_edge_y_inset: %f', self.screw_edge_x_inset, self.screw_edge_y_inset)


        self.logger.debug('real_max_x: %d, real_max_y: %s', self.real_max_x, self.real_max_y)

        self.update_calculated_attributes()



    def build_attr_from_dict(self, parameter_dict):

        for param in parameter_dict.keys():
            ignore_deprecated = False
            value = parameter_dict[param]

            # If the current parameter has been deprecated by another parameter get the new parameter name
            if param in self.paramater_alternate_dict.keys():
                alt_param = self.paramater_alternate_dict[param]
                # If the new version of the parameter is not in the paramter dict then us the value in the deprectaed parameter
                if alt_param not in parameter_dict.keys():
                    param = alt_param
                else:
                    # If the new version of the parameter is in the dict then ignore the current deprecated parameter
                    ignore_deprecated = True

            if param == 'custom_switch':
                if 'points' not in value.keys():
                    raise AttributeError('A set of "points" must exist in the "custom_switch" to use a custom switch')
                
                self.custom_shape_points = value['points']

                if 'path' in value.keys():
                    self.custom_shape_path = value['path']
                else:
                    self.logger.warning('Custom Switch defined but no "path" list defined. Points in "ponts" list will be used in defined order')
                
                self.custom_shape = True
                

            if ignore_deprecated == False:
                setattr(self, param, value)

            


        self.switch_config = SwitchConfig(kerf = self.kerf, switch_type = self.switch_type, stabilizer_type = self.stabilizer_type, custom_shape = self.custom_shape, custom_shape_points = self.custom_shape_points, custom_shape_path = self.custom_shape_path)

        self.update_calculated_attributes()

        self.validate_parameters()
    
    
    def set_parameter_dict(self, parameter_dict):
        self.parameter_dict = parameter_dict
        self.build_attr_from_dict(self.parameter_dict)
    
    
    # def get_param(self, paramaeter_name):

    #     if self.parameter_dict is not None and paramaeter_name in self.parameter_dict.keys():
    #         return self.parameter_dict[paramaeter_name]
    #     elif paramaeter_name in self.default_parameter_dict.keys():
    #         return self.default_parameter_dict[paramaeter_name]
    #     else:
    #         raise ValueError('No paramter exists with name %s' % (paramaeter_name))



    def validate_parameters(self):
        parameter_error = False
        error_message = ''
        # if self.screw_edge_inset < self.case_wall_thickness + self.screw_hole_body_radius:
        #     parameter_error = True
        #     error_message += 'Screw Edge Inset %f must be greater than case_wall_thickness: %f + screw_hole_body_radius: %f = %f\n' % (self.screw_edge_inset, self.case_wall_thickness, self.screw_hole_body_radius, self.case_wall_thickness + self.screw_hole_body_radius)
        
        if self.screw_count > 0 :
            if self.screw_count < 4:
                parameter_error = True
                error_message += 'Screw count must be at least 4\n'
            if self.screw_count % 2 != 0:
                parameter_error = True
                error_message +=  'Screw count must be even\n'
            
        if self.switch_type not in self.switch_config.switch_type_function_dict.keys():
            parameter_error = True
            error_message += 'switch type %s is not a valid switch type' % (self.switch_type)

        if self.stabilizer_type not in self.switch_config.stab_type_function_dict.keys():
            parameter_error = True
            error_message += 'stabilizer type %s is not a valid stabilizer type' % (self.stabilizer_type)

        if parameter_error == True:
            print('ERROR:', error_message)
            exit(1)

