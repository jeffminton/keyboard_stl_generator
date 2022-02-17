from solid import *
from solid.utils import *

import logging

from cell import Cell
from parameters import Parameters
from switch_config import SwitchConfig

class Switch(Cell):
    """
    Defines a Switch object that inherits from the Cell class

    ...

    Attributes
    ----------
    x : float
        The x coorinate of the top left of the switch in keyboard layout U units

    y : float
        The y coorinate of the top left of the switch in keyboard layout U units

    w : float
        The width of the switch in keyboard layout U units

    h : float
        The height of the switch in keyboard layout U units

    rotation : float, default 0.0
        The angle the switch will be rotated to

    r_x_offset : float, default 0.0
        The x offset from origin tha tthe rotation oriin will be moved to

    r_y_offset : float, default 0.0
        The y offset from origin tha tthe rotation oriin will be moved to

    cell_value : float, default ''
        The actual text of the key

    switch_type : float, default 'mx_openable'
        The switch type to create a cutout for

    stabilizer_type : float, default 'cherry_costar'
        The stabilizer type to create a cutout for

    Methods
    -------
    switch_cutout()
        Get a switch soild that matches the attribute settings
    update_all_neighbors_set(neighbor_group = 'local')
        Check if all neighbors are defined where they exist and set the neighbor_check_complete value to match
    get_all_neighbors_set(neighbor_group = 'local')
        Get the value of neighbor_check_complete for the passed in neughbor group
    get_neighbor(neighbor_name, neighbor_group = 'local')
        Get the neighbor Switch object for the name and group passed in
    set_neighbor(neighbor = None, neighbor_name = '', offset = 0.0, has_neighbor = True, neighbor_group = 'local', perp_offset = 0.0)
        Set a neighbor for the switch object
    has_neighbor(neighbor_name = '', neighbor_group = 'local')
        Return True if switch has a neigbor with name and group passed in. False if no neighbor
    get_neighbor_offset(neighbor_name = '', neighbor_group = 'local')
        Get the x offset to the neighbor for the name and group passed in
    get_neighbor_perp_offset(neighbor_name = '', neighbor_group = 'local')
        Get the perpendicular offset to the neighbor for the name and group passed in
    get_neighbor_direction_list()
        Helper to get list of neighbor direction names
    """

    NEIGHBOR_OPOSITE_DICT = {
        'right': 'left',
        'left': 'right',
        'top': 'bottom',
        'bottom': 'top'
    }



    def __init__(self, x, y, w, h, rotation = 0.0,  r_x_offset = 0.0, r_y_offset = 0.0, cell_value = '', switch_config = None, parameters = None):
        super().__init__(x, y, w, h, rotation,  r_x_offset, r_y_offset, cell_value = cell_value)

        self.logger = logging.getLogger('Switch')
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

        self.switch_config = switch_config
        if self.switch_config is None:
            self.switch_config = SwitchConfig()

        self.parameters: Parameters = parameters

        self.solid = self.switch_cutout()

        self.logger.debug('x: %f, y: %f, w: %f, h: %f, end_x: %f, end_y: %f', self.x, self.y, self.w, self.h, self.end_x, self.end_y) 

        self.global_neighbors = {
            'right': {
            },
            'left': {
            },
            'top': {
            },
            'bottom': {
            },
            'neighbor_check_complete': False
        }

        self.local_neighbors = {
            'right': {
            },
            'left': {
            },
            'top': {
            },
            'bottom': {
            },
            'neighbor_check_complete': False
        }

        # self.right = None
        # self.left_in_section = None
        # self.up_in_section = None
        # self.down_in_section = None

        # self.neighbors
    

    def neighbors_formatted(self, obj, indent = 2, current_indent = 0):
        current_output = ''
        current_indent_str = ' ' * current_indent
        if isinstance(obj, dict):
            for i, key in enumerate(obj.keys()):
                value = obj[key]
                current_output += current_indent_str + key + ': '

                if isinstance(value, dict):
                    current_output += '{\n'

                current_output += str(self.neighbors_formatted(value, indent, current_indent + indent))


                if isinstance(value, dict):
                    current_output += current_indent_str+ '}'

                if i < len(obj.keys()) - 1:
                    current_output += ','

                current_output += '\n'

        else:
            current_output += str(obj)

        return current_output


    def __str__(self):
        return 'Switch: ' + super().__str__()

    def __repr__(self):
        global_neighbors_json = self.neighbors_formatted(self.global_neighbors, indent=4, current_indent=10)
        local_neighbors_json = self.neighbors_formatted(self.local_neighbors, indent=4, current_indent=10)
        return 'Switch: ' + super().__str__() + '\nglobal neighbors: \n' + global_neighbors_json + '\local neighbors: \n' + local_neighbors_json


    def switch_cutout(self):
        """
        Return the polygon that will be used to cutout a place in the plate for a switch

        Returns
        -------
        OpenSCADObject
            The OpenSCADObject for the cutout
        """

        self.logger.debug('switch %s, switch type: %s, stab type: %s', self.cell_value, self.switch_config.switch_type, self.switch_config.stabilizer_type)
        
        # switch_poly_points, switch_poly_path = self.switch_config.get_switch_poly_info()
        # stab_poly_points, stab_poly_path = self.switch_config.get_stab_poly_info(key_width = self.switch_length)

        switch_poly_points = self.switch_config.get_switch_poly_info()
        switch_poly_path = [range(len(switch_poly_points))]

        stab_poly_points, support_cutout_poly_points = self.switch_config.get_stab_poly_info(key_width = self.switch_length)
        stab_poly_path = [range(len(stab_poly_points))]
        support_cutout_poly_path = [range(len(support_cutout_poly_points))]
        
        self.logger.debug('\tswitch_poly_points: %d, switch_poly_path: %d', len(switch_poly_points), len(switch_poly_path))

        # Create swtch cutout polygon
        cutout_polygon = polygon(switch_poly_points, switch_poly_path)

        # Create stab polygon if it is defined
        if stab_poly_points is not None and stab_poly_path is not None:
            self.logger.debug('\t\tstab_poly_points: %d, stab_poly_path: %d', len(stab_poly_points), len(stab_poly_path))
            stab = polygon(stab_poly_points, stab_poly_path) + mirror([1, 0, 0]) ( polygon(stab_poly_points, stab_poly_path) )
            # stab = polygon(stab_poly_points, stab_poly_path)# + mirror([1, 0, 0]) ( polygon(stab_poly_points, stab_poly_path) )
            if support_cutout_poly_points is not None:
                support_cutout = polygon(support_cutout_poly_points, support_cutout_poly_path) + mirror([1, 0, 0]) ( polygon(support_cutout_poly_points, support_cutout_poly_path) )
            cutout_polygon += stab

        cutout = linear_extrude(height = 10, center = True)(cutout_polygon)

        if support_cutout_poly_points is not None:
            cutout += down( (10 / 2) + (self.parameters.plate_thickness / 2) ) (
                linear_extrude(height = 10, center = True)(support_cutout)
            )


        cutout = rotate(a = 180, v = (0, 0, 1)) ( cutout )

        # Rotate a key if it is taller than it is wide
        if self.vertical:
            
            cutout = rotate(a = -90, v = (0, 0, 1)) ( cutout )

        offset_cutout = right(self.u(self.w / 2)) ( back(self.u(self.h / 2)) ( cutout ) )

        return offset_cutout



    def update_all_neighbors_set(self, neighbor_group = 'local'):

        if neighbor_group == 'local':
            neighbor_dict = self.local_neighbors
        elif neighbor_group == 'global':
            neighbor_dict =  self.global_neighbors

            
        all_neighbors_set = True
        for direction in neighbor_dict.keys():
            if direction != 'neighbor_check_complete':
                if len(neighbor_dict[direction].keys()) == 0:
                    all_neighbors_set = False

        neighbor_dict['neighbor_check_complete'] = all_neighbors_set


    def get_all_neighbors_set(self, neighbor_group = 'local'):

        if neighbor_group == 'local':
            neighbor_dict = self.local_neighbors
        elif neighbor_group == 'global':
            neighbor_dict =  self.global_neighbors

        return neighbor_dict['neighbor_check_complete']


    def get_neighbor(self, neighbor_name, neighbor_group = 'local'):
        
        neighbor = None

        if neighbor_group == 'local':
            neighbor = self.local_neighbors[neighbor_name]['neighbor']
        elif neighbor_group == 'global':
            neighbor =  self.global_neighbors[neighbor_name]['neighbor']

        return neighbor

    def set_neighbor(self, neighbor = None, neighbor_name = '', offset = 0.0, has_neighbor = True, neighbor_group = 'local', perp_offset = 0.0):
        
        temp_dict = {
            'has_neighbor': has_neighbor,
            'neighbor': neighbor,
            'offset': offset,
            'perp_offset': perp_offset
        }
        
        if neighbor_group == 'local':
            self.local_neighbors[neighbor_name] = temp_dict
        elif neighbor_group == 'global':
            self.global_neighbors[neighbor_name] = temp_dict
        
    # def set_right_neighbor(self, neighbor = None, offset = 0.0, has_neighbor = True, neighbor_group = 'local', perp_offset = 0.0):
    #     self.set_neighbor(neighbor, 'right', offset, has_neighbor, neighbor_group, perp_offset)

    # def set_left_neighbor(self, neighbor = None, offset = 0.0, has_neighbor = True, neighbor_group = 'local', perp_offset = 0.0):
    #     self.set_neighbor(neighbor, 'left', offset, has_neighbor, neighbor_group, perp_offset)

    # def set_top_neighbor(self, neighbor = None, offset = 0.0, has_neighbor = True, neighbor_group = 'local', perp_offset = 0.0):
    #     self.set_neighbor(neighbor, 'top', offset, has_neighbor, neighbor_group, perp_offset)

    # def set_bottom_neighbor(self, neighbor = None, offset = 0.0, has_neighbor = True, neighbor_group = 'local', perp_offset = 0.0):
    #     self.set_neighbor(neighbor, 'bottom', offset, has_neighbor, neighbor_group, perp_offset)

    def has_neighbor(self, neighbor_name = '', neighbor_group = 'local'):
        if neighbor_group == 'local':
            return self.local_neighbors[neighbor_name]['has_neighbor']
        elif neighbor_group == 'global':
            return self.global_neighbors[neighbor_name]['has_neighbor']
    
    def get_neighbor_offset(self, neighbor_name = '', neighbor_group = 'local'):
        if neighbor_group == 'local':
            return self.local_neighbors[neighbor_name]['offset']
        elif neighbor_group == 'global':
            return self.global_neighbors[neighbor_name]['offset']

    def get_neighbor_perp_offset(self, neighbor_name = '', neighbor_group = 'local'):
        if neighbor_group == 'local':
            return self.local_neighbors[neighbor_name]['perp_offset']
        elif neighbor_group == 'global':
            return self.global_neighbors[neighbor_name]['perp_offset']

    def get_neighbor_direction_list(self):

        name_list = []

        for neighbor_name in self.local_neighbors.keys():
            if isinstance(self.local_neighbors[neighbor_name], dict):
                name_list.append(neighbor_name)

        return name_list