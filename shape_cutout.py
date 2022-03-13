from curses.textpad import rectangle
from solid import *
from solid.utils import *

import logging
import sys

from cell import Cell
from parameters import Parameters
from switch_config import SwitchConfig

class ShapeCutout(Cell):
    """
    Defines a Switch object that inherits from the Cell class

    ...

    Attributes
    ----------
    x : float
        The x coorinate of the top left of the switch in keyboard layout U units


    Methods
    -------
    switch_cutout()
        Get a switch soild that matches the attribute settings
    update_all_neighbors_set(neighbor_group = 'local')
        Check if all neighbors are defined where they exist and set the neighbor_check_complete value to match

    """

    NEIGHBOR_OPOSITE_DICT = {
        'right': 'left',
        'left': 'right',
        'top': 'bottom',
        'bottom': 'top'
    }


    def __init__(self, x, y, shape_type, shape_parameters, parameters: Parameters = Parameters()):
        super().__init__(x, y, parameters = parameters)

        self.logger = logging.getLogger().getChild(__name__)

        self.parameters: Parameters = parameters

        self.shape_type = shape_type
        self.shape_parameters = shape_parameters

        self.shape_type_function_dict = {
            'circle': self.circle_cutout,
            'rectangle': self.rectangle_cutout,
            'polygon': self.polygon_cutout
        }

        self.solid = self.get_shape_cutout()


    def __str__(self):
        return 'Switch: ' + super().__str__()

    def __repr__(self):
        global_neighbors_json = self.neighbors_formatted(self.global_neighbors, indent=4, current_indent=10)
        local_neighbors_json = self.neighbors_formatted(self.local_neighbors, indent=4, current_indent=10)
        return 'Switch: ' + super().__str__() + '\nglobal neighbors: \n' + global_neighbors_json + '\local neighbors: \n' + local_neighbors_json


    def get_shape_cutout(self):
        shape = self.shape_type_function_dict[self.shape_type]()

        return linear_extrude(height = 10, center = True)(shape)


    def get_moved(self):
        return right(self.x) ( forward(self.y) ( self.solid ) )
    
    def circle_cutout(self):
        this_function_name = sys._getframe().f_code.co_name
        self.logger = self.logger.getChild(this_function_name)

        if 'r' in self.shape_parameters.keys():
            radius = self.shape_parameters['r']
        elif 'd' in self.shape_parameters.keys():
            radius = self.shape_parameters['d'] / 2
        else:
            self.logger.error('Either a radius "r" or diameter "d" key and value must be set when createing a cutsom circle cutout')
            exit(1)

        return circle(r = radius)

    def rectangle_cutout(self):
        this_function_name = sys._getframe().f_code.co_name
        self.logger = self.logger.getChild(this_function_name)

        width = 0
        height = 0
        # Both width and height defined. Use both
        if 'width' in self.shape_parameters.keys() and 'height' in self.shape_parameters.keys():
            self.logger.warn('both height and width supplied')
            width = self.shape_parameters['width']
            height = self.shape_parameters['height']
        elif 'width' in self.shape_parameters.keys():
            self.logger.warn('only width supplied')
            width = self.shape_parameters['width']
            height = self.shape_parameters['width']
        elif 'height' in self.shape_parameters.keys():
            self.logger.warn('only height supplied')
            width = self.shape_parameters['height']
            height = self.shape_parameters['height']
        else:
            self.logger.error('At least a "width" or "height" must be provided for a custom rectangle cutout. Specifying only 1 of those will create a squatre')
            exit(1)

        self.logger.warn('height: %f, width: %f', height, width)

        return square([width, height])

    def polygon_cutout(self):
        this_function_name = sys._getframe().f_code.co_name
        self.logger = self.logger.getChild(this_function_name)

        points = None
        psth = None

        if 'points' in self.shape_parameters.keys():
            points = self.shape_parameters['points']
        else:
            self.logger.error('A list of points with key "points" must be provided for a custom polygon cutout')
            exit(1)

        if 'path' in self.shape_parameters.keys():
            path = [self.shape_parameters['path']]
        else:
            self.logger.info('No path provided for custom polygon. Will use points in order they were listed')
            path = [range(len(points))]
        
        return polygon(points, path)

