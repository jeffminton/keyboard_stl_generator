from solid import *
from solid.utils import *

import logging



class Cell:
    # Switch Dimensions
    SWITCH_SPACING = 19.05
    SQUARE_SIZE = 14
    SQUARE_SIZE_HALF = SQUARE_SIZE / 2
    # NOTCH_HEIGHT = 3.5
    NOTCH_WIDTH = 0.8
    CLIP_NOTCH_X = SQUARE_SIZE_HALF + NOTCH_WIDTH
    CLIP_NOTCH_Y_MAX = 6
    CLIP_NOTCH_Y_MIN = 2.9
    NOTCH_VERT_SPACING = 5
    NOTCH_VERT_SPACING_HALF = NOTCH_VERT_SPACING / 2
    NOTCH_EDGE_OFFSET = 1
    CORNER_CIRCLE_EDGE_OFFSET = 0.0


    # #[Stab Dimensions]
    BAR_BOTTOM_Y = 2.3
    MAIN_BODY_BOTTOM_Y = 5.53
    BOTTOM_NOTCH_BOTTOM_Y = 6.45
    SIDE_NOTCH_TOP_Y = 0.5
    MAIN_BODY_TOP_Y = 6.77
    TOP_NOTCH_TOP_Y = 7.75
    MAIN_BODY_SWITCH_SIDE_X_OFFSET = 3.375
    COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET = 1.65
    SIDE_NOTCH_FAR_SIDE_X_OFFSET = 4.2

    def __init__(self, x: float, y: float, w: float, h: float, rotation = 0.0,  r_x_offset = 0.0, r_y_offset = 0.0, kerf = 0.0):
        
        self.logger = logging.getLogger('Cell')
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
        
        self.x = x
        self.y = y
        self.w = w
        self.h = h

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

        self.kerf = kerf

        
            
    @staticmethod
    def u(u_value):
        return u_value * Cell.SWITCH_SPACING

    
    def get(self):
        return self.solid

    def get_moved(self):
        return right(self.u(self.x)) ( forward(self.u(self.y)) ( self.solid ) )

    def get_end_x(self):
        return self.end_x
    
    def get_end_y(self):
        return self.end_y
   