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

        self.default_parameter_dict = {
            'plate_supports': True,
            
            'x_build_size' : 200,
            'y_build_size' : 200,

            'switch_type': 'mx_openable',
            'stabilizer_type': 'cherry',

            'custom_shape': False, 
            'custom_shape_points': None,
            'custom_shape_path': None,

            'kerf' : 0.00,

            'top_margin' : 8,
            'bottom_margin' : 8,
            'left_margin' : 8,
            'right_margin' : 8,
            'case_height' : 10,
            # 'plate_wall_thickness' : 2.0,
            'case_wall_thickness' : 2.0,
            'plate_thickness' : 1.511,
            'plate_corner_radius' : 4,
            'bottom_cover_thickness': 2,

            'support_bar_height' : 3.0,
            'support_bar_width' : 1.0,
            'tilt': 0.0,

            'simple_test': False,

            'screw_count': 8,
            'screw_diameter': 4,
            'screw_edge_inset': 6.5,

            'cable_hole': False,
            'hole_width': 10,
            'hole_height': 10,
            'cable_hole_down_offset': 1
        }


        self.paramater_alternate_dict = {
            'plate_wall_thickness': 'case_wall_thickness'
        }

        self.switch_spacing = 19.05

        self.plate_supports = True
        
        self.x_build_size = 200
        self.y_build_size = 200

        self.switch_type = 'mx_openable'
        self.stabilizer_type = 'cherry'

        # Custom Switch Cutout Attributes
        self.custom_shape = False 
        self.custom_shape_points = None
        self.custom_shape_path = None

        self.kerf = 0.00

        self.top_margin = 8
        self.bottom_margin = 8
        self.left_margin = 8
        self.right_margin = 8
        self.case_height = 10
        self.case_wall_thickness = 2.0
        self.plate_thickness = 1.511
        self.plate_corner_radius = 4
        self.bottom_cover_thickness = 2

        self.support_bar_height = 3.0
        self.support_bar_width = 1.0
        self.tilt = 0.0

        self.simple_test = False

        self.screw_count = 8
        self.screw_diameter = 4
        self.screw_edge_inset = 6.5
        self.screw_hole_body_wall_width = 2
        self.screw_hole_body_support_x_factor = 4

        self.cable_hole = False
        self.cable_diameter = 4
        self.cable_hole_width = 10
        self.cable_hole_height = 10
        self.cable_hole_up_offset = 1
        self.cable_hole_down_offset = 1

        self.switch_config = None

        self.custom_polygons = None

        self.test_block = False
        self.test_block_x_start = 0
        self.test_block_x_end = 0
        self.test_block_y_start = 0
        self.test_block_y_end = 0
        self.test_block_z_start = 0
        self.test_block_z_end = 0

        self.case_height_extra = 30

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

        self.min_x = 0.0
        self.max_x = 0.0
        self.min_y = 0.0
        self.max_y = 0.0

        self.real_max_x = 0.0
        self.real_max_y = 0.0
        self.real_case_width = 0.0
        self.real_case_height = 0.0

        # self.build_attr_from_dict(self.default_parameter_dict)
        
        if self.parameter_dict is not None:
            self.build_attr_from_dict(self.parameter_dict)

        # self.validate_parameters()
        

    def U(self, u_value):
        return u_value * self.switch_spacing


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
        this_function_name = sys._getframe(  ).f_code.co_name
        logger = self.logger.getChild(this_function_name)

        self.max_x = max_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        logger.debug('min_x: %f, max_x: %f, max_y: %f, min_y: %f', self.min_x, self.max_x, self.max_y, self.min_y)

        # Get rhe calculated real max and y sizes of the board
        self.real_max_x = self.U(self.max_x)
        self.real_max_y = self.U(abs(self.min_y))

        self.real_case_width = self.real_max_x + self.left_margin + self.right_margin
        self.real_case_height = self.real_max_y + self.top_margin + self.bottom_margin

        logger.debug('real_max_x: %d, real_max_y: %s', self.real_max_x, self.real_max_y)

        self.update_calculated_attributes()



    def build_attr_from_dict(self, parameter_dict):
        this_function_name = sys._getframe(  ).f_code.co_name
        logger = self.logger.getChild(this_function_name)

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
                    logger.warning('Custom Switch defined but no "path" list defined. Points in "ponts" list will be used in defined order')
                
                self.custom_shape = True
                

            if ignore_deprecated == False:
                setattr(self, param, value)

            


        self.switch_config = SwitchConfig(kerf = self.kerf, switch_type = self.switch_type, stabilizer_type = self.stabilizer_type, custom_shape = self.custom_shape, custom_shape_points = self.custom_shape_points, custom_shape_path = self.custom_shape_path)

        self.update_calculated_attributes()

        self.validate_parameters()
    
    
    def set_parameter_dict(self, parameter_dict):
        self.parameter_dict = parameter_dict
        self.build_attr_from_dict(self.parameter_dict)
    
    
    def get_param(self, paramaeter_name):

        if self.parameter_dict is not None and paramaeter_name in self.parameter_dict.keys():
            return self.parameter_dict[paramaeter_name]
        elif paramaeter_name in self.default_parameter_dict.keys():
            return self.default_parameter_dict[paramaeter_name]
        else:
            raise ValueError('No paramter exists with name %s' % (paramaeter_name))



    def validate_parameters(self):
        parameter_error = False
        error_message = ''
        if self.screw_edge_inset < self.case_wall_thickness + self.screw_hole_body_radius:
            parameter_error = True
            error_message += 'Screw Edge Inset %f must be greater than case_wall_thickness: %f + screw_hole_body_radius: %f = %f\n' % (self.screw_edge_inset, self.case_wall_thickness, self.screw_hole_body_radius, self.case_wall_thickness + self.screw_hole_body_radius)
        
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

