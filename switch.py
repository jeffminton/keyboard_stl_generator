





from solid import *
from solid.utils import *

import logging

from cell import Cell

class Switch(Cell):
    def __init__(self, x, y, w, h, rotation = 0.0,  r_x_offset = 0.0, r_y_offset = 0.0, kerf = 0.0, cell_value = ''):
        super().__init__(x, y, w, h, rotation,  r_x_offset, r_y_offset, kerf, cell_value = cell_value)

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

        self.solid = self.switch_cutout()

        self.logger.debug('x: %f, y: %f, w: %f, h: %f, end_x: %f, end_y: %f', self.x, self.y, self.w, self.h, self.end_x, self.end_y) 

        self.section_neighbors = {
            'right': {
                'has_neighbor': None,
                'neighbor': None,
                'offset': None
            },
            'left': {
                'has_neighbor': None,
                'neighbor': None,
                'offset': None
            },
            'top': {
                'has_neighbor': None,
                'neighbor': None,
                'offset': None
            },
            'bottom': {
                'has_neighbor': None,
                'neighbor': None,
                'offset': None
            },
            'neighbor_check_complete': False
        }

        # self.right = None
        # self.left_in_section = None
        # self.up_in_section = None
        # self.down_in_section = None

        # self.neighbors
    
    # def u(self, u_value):
    #     return u_value * self.SWITCH_SPACING

    def __str__(self):
        return 'Switch: ' + super().__str__()

    def switch_cutout(self):
        poly_points = [
            [self.SQUARE_SIZE_HALF - self.kerf, -self.SQUARE_SIZE_HALF + self.kerf], # 0
            [self.SQUARE_SIZE_HALF - self.kerf, -self.CLIP_NOTCH_Y_MAX + self.kerf], # 1
            [self.CLIP_NOTCH_X - self.kerf, -self.CLIP_NOTCH_Y_MAX + self.kerf], # 2
            [self.CLIP_NOTCH_X - self.kerf, -self.CLIP_NOTCH_Y_MIN - self.kerf], # 3
            [self.SQUARE_SIZE_HALF - self.kerf, -self.CLIP_NOTCH_Y_MIN - self.kerf], # 4
            [self.SQUARE_SIZE_HALF - self.kerf, self.CLIP_NOTCH_Y_MIN + self.kerf], # 5
            [self.CLIP_NOTCH_X - self.kerf, self.CLIP_NOTCH_Y_MIN + self.kerf], # 6
            [self.CLIP_NOTCH_X - self.kerf, self.CLIP_NOTCH_Y_MAX - self.kerf], # 7
            [self.SQUARE_SIZE_HALF - self.kerf, self.CLIP_NOTCH_Y_MAX - self.kerf], # 8
            [self.SQUARE_SIZE_HALF - self.kerf, self.SQUARE_SIZE_HALF - self.kerf], # 9
            [-self.SQUARE_SIZE_HALF + self.kerf, self.SQUARE_SIZE_HALF - self.kerf], # 10
            [-self.SQUARE_SIZE_HALF + self.kerf, self.CLIP_NOTCH_Y_MAX - self.kerf], # 11
            [-self.CLIP_NOTCH_X + self.kerf, self.CLIP_NOTCH_Y_MAX - self.kerf], # 12
            [-self.CLIP_NOTCH_X + self.kerf, self.CLIP_NOTCH_Y_MIN + self.kerf], # 13
            [-self.SQUARE_SIZE_HALF + self.kerf, self.CLIP_NOTCH_Y_MIN + self.kerf], # 14
            [-self.SQUARE_SIZE_HALF + self.kerf, -self.CLIP_NOTCH_Y_MIN - self.kerf], # 15
            [-self.CLIP_NOTCH_X + self.kerf, -self.CLIP_NOTCH_Y_MIN - self.kerf], # 16
            [-self.CLIP_NOTCH_X + self.kerf, -self.CLIP_NOTCH_Y_MAX + self.kerf], # 17
            [-self.SQUARE_SIZE_HALF + self.kerf, -self.CLIP_NOTCH_Y_MAX + self.kerf], # 18
            [-self.SQUARE_SIZE_HALF + self.kerf, -self.SQUARE_SIZE_HALF + self.kerf] # 19
        ]

        poly_path = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]]

        x_right = self.kerf + self.SQUARE_SIZE_HALF - self.CORNER_CIRCLE_EDGE_OFFSET
        x_left = self.kerf - self.SQUARE_SIZE_HALF + self.CORNER_CIRCLE_EDGE_OFFSET
        y_top = self.kerf + self.SQUARE_SIZE_HALF - self.CORNER_CIRCLE_EDGE_OFFSET
        y_bottom = self.kerf - self.SQUARE_SIZE_HALF + self.CORNER_CIRCLE_EDGE_OFFSET

        d = polygon(poly_points, poly_path)
        d += right(x_right) ( forward(y_top) ( circle(r = .4) ) )
        d += right(x_right) ( forward(y_bottom) ( circle(r = .4) ) )
        d += right(x_left) ( forward(y_bottom) ( circle(r = .4) ) )
        d += right(x_left) ( forward(y_top) ( circle(r = .4) ) )
        stab = self.stab_cutout()

        if stab is not None:
            d += stab

        cutout = linear_extrude(height = 10, center = True)(d)

        # Rotate a key if it is taller than it is wide
        if self.vertical:
            cutout = rotate(a = 90, v = (0, 0, 1)) ( cutout )

        # if rotation != 0.0:
        #     cutout = rotate(a = -(rotation), v = (0, 0, 1)) ( cutout )

        # print('switch_cutout:', 'w / 2:', w / 2, 'h / 2', h / 2)
        offset_cutout = right(self.u(self.w / 2)) ( back(self.u(self.h / 2)) ( cutout ) )

        # return right(self.u(self.x)) ( forward(self.u(self.y)) ( offset_cutout ) )
        return offset_cutout


    def get_stab_cutout_spacing(self):
    
        if self.w >= 2.0 and self.w < 3.0: # 2u, 2.25u, 2.5u, 2.75u
            return 11.9
        elif self.w == 3: # 3u
            return 19.05
        elif self.w == 4: # 4u
            return 28.575
        elif self.w == 4.5: # 4.5u
            return 34.671
        elif self.w == 5.5: # 5.5u
            return 42.8625
        elif self.w == 6: # 6u
            return 47.5
        elif self.w == 6.25: # 6.25u
            return 50
        elif self.w == 6.5: # 6.5u
            return 52.38
        elif self.w == 7: # 7u
            return 57.15
        elif self.w == 8: # 8u
            return 66.675
        elif self.w == 9: # 9u
            return 66.675
        elif self.w == 10: # 10u
            return 66.675
        else:
            return -1

    def stab_cutout(self):

        s = self.get_stab_cutout_spacing()

        if s != -1:
            poly_points = [
                [s - self.MAIN_BODY_SWITCH_SIDE_X_OFFSET + self.kerf, -self.BAR_BOTTOM_Y + self.kerf], # 0
                [s - self.MAIN_BODY_SWITCH_SIDE_X_OFFSET + self.kerf, -self.MAIN_BODY_BOTTOM_Y + self.kerf], # 1
                [s - self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET + self.kerf, -self.MAIN_BODY_BOTTOM_Y + self.kerf], # 2
                [s - self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET + self.kerf, -self.BOTTOM_NOTCH_BOTTOM_Y + self.kerf], # 3
                [s + self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET - self.kerf, -self.BOTTOM_NOTCH_BOTTOM_Y + self.kerf], # 4
                [s + self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET - self.kerf, -self.MAIN_BODY_BOTTOM_Y + self.kerf], # 5
                [s + self.MAIN_BODY_SWITCH_SIDE_X_OFFSET - self.kerf, -self.MAIN_BODY_BOTTOM_Y + self.kerf], # 6
                [s + self.MAIN_BODY_SWITCH_SIDE_X_OFFSET - self.kerf, -self.BAR_BOTTOM_Y + self.kerf], # 7
                [s + self.SIDE_NOTCH_FAR_SIDE_X_OFFSET - self.kerf, -self.BAR_BOTTOM_Y + self.kerf], # 8
                [s + self.SIDE_NOTCH_FAR_SIDE_X_OFFSET - self.kerf, self.SIDE_NOTCH_TOP_Y - self.kerf], # 9
                [s + self.MAIN_BODY_SWITCH_SIDE_X_OFFSET - self.kerf, self.SIDE_NOTCH_TOP_Y - self.kerf], # 10
                [s + self.MAIN_BODY_SWITCH_SIDE_X_OFFSET - self.kerf, self.MAIN_BODY_TOP_Y - self.kerf], # 11
                [s + self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET - self.kerf, self.MAIN_BODY_TOP_Y - self.kerf], # 12
                [s + self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET - self.kerf, self.TOP_NOTCH_TOP_Y - self.kerf], # 13
                [s - self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET + self.kerf, self.TOP_NOTCH_TOP_Y - self.kerf], # 14
                [s - self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET + self.kerf, self.MAIN_BODY_TOP_Y - self.kerf], # 15
                [s - self.MAIN_BODY_SWITCH_SIDE_X_OFFSET + self.kerf, self.MAIN_BODY_TOP_Y - self.kerf], # 16
                [s - self.MAIN_BODY_SWITCH_SIDE_X_OFFSET + self.kerf, self.BAR_BOTTOM_Y - self.kerf], # 17
                [-s + self.MAIN_BODY_SWITCH_SIDE_X_OFFSET - self.kerf, self.BAR_BOTTOM_Y - self.kerf], # 18
                [-s + self.MAIN_BODY_SWITCH_SIDE_X_OFFSET - self.kerf, -self.BAR_BOTTOM_Y + self.kerf] #19
            ]

            poly_path = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]]

            d = polygon(poly_points, poly_path) + mirror([1, 0, 0]) ( polygon(poly_points, poly_path) )

            return d
        else:
            return None

    # def check_all_neighbors_set(self):


    def set_neighbor(self, neighbor = None, neighbor_name = '', offset = 0.0, has_neighbor = True):
        self.logger.info('nmeighbor_name: %s', neighbor_name)
        self.section_neighbors[neighbor_name] = {
                'has_neighbor': has_neighbor,
                'neighbor': neighbor,
                'offset': offset
            }

        if self.cell_value == 'K' and  has_neighbor == False:
            self.logger.info('switch %s. set has neighbor %s', str(self), str(has_neighbor))
            self.logger.info('neighbors: %s', str(self.section_neighbors))

    def set_right_neighbor(self, neighbor = None, offset = 0.0, has_neighbor = True):
        self.set_neighbor(neighbor, 'right', offset, has_neighbor)

    def set_left_neighbor(self, neighbor = None, offset = 0.0, has_neighbor = True):
        self.set_neighbor(neighbor, 'left', offset, has_neighbor)

    def set_top_neighbor(self, neighbor = None, offset = 0.0, has_neighbor = True):
        self.set_neighbor(neighbor, 'top', offset, has_neighbor)

    def set_bottom_neighbor(self, neighbor = None, offset = 0.0, has_neighbor = True):
        self.set_neighbor(neighbor, 'bottom', offset, has_neighbor)

    def has_neighbor(self, neighbor_name = ''):
        return self.section_neighbors[neighbor_name]['has_neighbor']