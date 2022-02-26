from solid import *
from solid.utils import *

import logging
import math
import json


class Cell:
    # Switch Dimensions
    SWITCH_SPACING = 19.05
    # SQUARE_SIZE = 14
    # SQUARE_SIZE_HALF = SQUARE_SIZE / 2
    # # NOTCH_HEIGHT = 3.5
    # NOTCH_WIDTH = 0.8
    # CLIP_NOTCH_X = SQUARE_SIZE_HALF + NOTCH_WIDTH
    # CLIP_NOTCH_Y_MAX = 6
    # CLIP_NOTCH_Y_MIN = 2.9
    # NOTCH_VERT_SPACING = 5
    # NOTCH_VERT_SPACING_HALF = NOTCH_VERT_SPACING / 2
    # NOTCH_EDGE_OFFSET = 1
    # CORNER_CIRCLE_EDGE_OFFSET = 0.0


    # # #[Stab Dimensions]
    # BAR_BOTTOM_Y = 2.3
    # MAIN_BODY_BOTTOM_Y = 5.53
    # BOTTOM_NOTCH_BOTTOM_Y = 6.45
    # SIDE_NOTCH_TOP_Y = 0.5
    # MAIN_BODY_TOP_Y = 6.77
    # TOP_NOTCH_TOP_Y = 7.75
    # MAIN_BODY_SWITCH_SIDE_X_OFFSET = 3.375
    # COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET = 1.65
    # SIDE_NOTCH_FAR_SIDE_X_OFFSET = 4.2

    def __init__(self, x: float, y: float, w: float, h: float, rotation = 0.0,  r_x_offset = 0.0, r_y_offset = 0.0, cell_value = ''):
        
        self.logger = logging.getLogger('generator.' + __name__)
        
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.x_min = self.x
        self.x_max = self.x + self.w
        self.y_min = self.y - self.h
        self.y_max = self.y

        self.center_x = self.x + (self.w / 2)
        self.center_y = self.y - (self.h / 2)

        self.rotaton = rotation

        self.rotation_info = {
            'top_left': {
                'order': 0
            },
            'top_right': {
                'order': 1
            },
            'bottom_left': {
                'order': 3
            },
            'bottom_right': {
                'order': 2
            }
        }

        self.corner_order = ['top_left', 'top_right', 'bottom_right', 'bottom_left']

        self.end_x = self.x + self.w
        self.end_y = self.y - self.h

        self.x_start_mm = self.u(x)
        self.x_end_mm = self.x_start_mm + self.u(w)

        self.y_start_mm = self.u(y)
        self.y_end_mm = self.y_start_mm + self.u(h)

        self.switch_length = self.w
        if self.h > self.w:
            self.switch_length = self.h

        self.vertical = False

        if self.h > self.w:
            self.vertical = True
        
        self.cell_value = cell_value

        if self.rotaton != 0.0:
            self.build_rotation_info()

        
            
    @staticmethod
    def u(u_value):
        return u_value * Cell.SWITCH_SPACING

    def __str__(self):
        return '%s (%f, %f)' % (self.cell_value, self.x, self.y)
    
    def get(self):
        return self.solid

    def get_moved(self):
        return right(self.u(self.x)) ( forward(self.u(self.y)) ( self.solid ) )

    def get_start_x(self) -> float: 
        if self.rotaton == 0.0:
            return self.x
        else:
            return self.get_rotated_start_x()

    
    def get_start_y(self) -> float:
        if self.rotaton == 0.0:
            return self.y
        else:
            return self.get_rotated_start_y()

    def get_end_x(self) -> float: 
        if self.rotaton == 0.0:
            return self.end_x
        else:
            return self.get_rotated_end_x()

    
    def get_end_y(self) -> float:
        if self.rotaton == 0.0:
            return self.end_y
        else:
            return self.get_rotated_end_y()

    def get_rotated_start_x(self) -> float:
        min_x = 1000.0
        for corner_name in self.corner_order:
            if 'rotated_x' in self.rotation_info[corner_name].keys():
                rotated_x = float(self.rotation_info[corner_name]['rotated_x'])
                if rotated_x < min_x:
                    min_x = rotated_x

        return min_x

    def get_rotated_end_x(self) -> float:
        max_x = -1000.0
        for corner_name in self.corner_order:
            if 'rotated_x' in self.rotation_info[corner_name].keys():
                rotated_x = float(self.rotation_info[corner_name]['rotated_x'])
                if rotated_x > max_x:
                    max_x = rotated_x

        return max_x

    def get_rotated_start_y(self) -> float:
        max_y = -1000.0
        for corner_name in self.corner_order:
            if 'rotated_y' in self.rotation_info[corner_name].keys():
                rotated_y = float(self.rotation_info[corner_name]['rotated_y'])
                if rotated_y > max_y:
                    max_y = rotated_y
        
        return max_y

    def get_rotated_end_y(self) -> float:
        min_y = 1000.0
        for corner_name in self.corner_order:
            if 'rotated_y' in self.rotation_info[corner_name].keys():
                rotated_y = float(self.rotation_info[corner_name]['rotated_y'])
                if rotated_y < min_y:
                    min_y = rotated_y
        
        return min_y

    def hypotenuse(self, adjacent, opposite):
        return math.sqrt((float(adjacent) ** 2) + (float(opposite) ** 2))

    def get_hypotenuse_start_angle(self, adjacent, opposite):
        try:
            tan = float(opposite) / float(adjacent)
        except ZeroDivisionError:
            
            # angle = 90
            if self.rotaton < 0.0:
                angle = 90
            else:
                angle = -90
            
            return angle

        angle = math.atan( tan )
        angle = math.degrees(angle)
        return angle

    def get_opposite(self, angle, hypotenuse):
        sin_angle = math.sin(math.radians(angle))
        opposite = sin_angle * hypotenuse
        if self.rotaton < 0.0:
            opposite = -(opposite)
        
        return opposite

    def get_adjacent(self, angle, hypotenuse):
        cos_angle = math.cos(math.radians(angle))
        adjacent = cos_angle * hypotenuse
        if self.rotaton < 0.0:
            adjacent = -(adjacent)
        
        return adjacent


    def get_rotation_info_points(self):
        points_orig = []
        points = []
        
        for corner_name in self.corner_order:
            # self.logger.debug(corner_name)
            points_orig.append([self.rotation_info[corner_name]['rotated_x'], self.rotation_info[corner_name]['rotated_y']])
            points.append([Cell.u(self.rotation_info[corner_name]['rotated_x']), Cell.u(self.rotation_info[corner_name]['rotated_y'])])
            
        return points
    
    
    def build_rotation_info(self):

        if self.cell_value in ('CC', 'DD', 'HH', 'II', 'JJ', 'LL'):
            self.logger.debug('Build Rotation Info for key %s', str(self))

        for corner_name in self.rotation_info.keys():
            adjacent = 0
            opposite = 0
            if corner_name == 'top_left':
                adjacent = self.x_min
                opposite = self.y_max
            elif corner_name == 'top_right':
                adjacent = self.x_max
                opposite = self.y_max
            elif corner_name == 'bottom_left':
                adjacent = self.x_min
                opposite = self.y_min
            elif corner_name == 'bottom_right':
                adjacent = self.x_max
                opposite = self.y_min

            hypotenuse = self.hypotenuse(adjacent, opposite)
            hypotenuse_start_angle = self.get_hypotenuse_start_angle(adjacent, opposite)
            hypotenuse_rotated_angle = hypotenuse_start_angle - self.rotaton

            self.rotation_info[corner_name]['x'] = adjacent
            self.rotation_info[corner_name]['y'] = opposite
            self.rotation_info[corner_name]['hypotenuse'] = hypotenuse
            self.rotation_info[corner_name]['hypotenuse_start_angle'] = hypotenuse_start_angle
            self.rotation_info[corner_name]['hypotenuse_rotated_angle'] = hypotenuse_rotated_angle
            self.rotation_info[corner_name]['rotated_x'] = self.get_adjacent(hypotenuse_rotated_angle, hypotenuse)
            self.rotation_info[corner_name]['rotated_y'] = self.get_opposite(hypotenuse_rotated_angle, hypotenuse)


