

import logging

from cell import Cell

class SwitchConfig():

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

    def __init__(self, kerf = 0.0,  switch_type = 'mx_openable', stabilizer_type = 'cherry_costar', custom_shape = False, custum_shape_points = None, custom_shape_path = None):

        self.logger = logging.getLogger('generator.' + __name__)

        self.kerf = kerf
        self.pos_kerf = self.kerf
        self.neg_kerf = -self.kerf

        self.switch_type = switch_type
        self.stabilizer_type = stabilizer_type

        # The type of switch that should be rendered
        # Default os mx_openable: The standard cutout to allow opening a switch when it is soldered to a PCB
        # Options:
        #       mx_openable: cutout that allows opening pcb mounted switches
        #       mx: best for hand wiring. Cannot open PCB mounted switches
        #       mx_alps: supports mx and alps switches. Allows opening PCB mounted mx switches
        #       alps: standar alps cutout
        self.switch_type = switch_type

        self.switch_type_function_dict = {
            'mx_openable': self.mx_openable_switch_cutout,
            'mx': self.mx_switch_cutout,
            'mx_alps': self.mx_alps_switch_cutout,
            'alps': self.alps_switch_cutout
        }

        # The type of stabilizer that should be rendered:
        # Defailt as cherry_costar
        # Options:
        #       cherry_costar: support for both cherry and costart stabilizers
        #       cherry: support for just cherry stabilizers
        #       costar: support for just costar stabilizers
        #       alps: suport for the alsp stabilizer
        self.stabilizer_type = stabilizer_type

        self.stab_type_function_dict = {
            'cherry_costar': self.cherry_costar_stab_cutout,
            'cherry': self.cherry_stab_cutout,
            'costar': self.costar_stab_cutout,
            'alps': self.alps_stab_cutout
        }


        self.cherry_support_cutout_h = 3.5
        self.cherry_stab_bar_width = 2.5

    
    def get_switch_poly_info(self):
        if self.switch_type in self.switch_type_function_dict.keys():
            return self.switch_type_function_dict[self.switch_type]()
        else:
            raise ValueError('switch type %s is not a valid switch type' % (self.switch_type))



    def get_stab_poly_info(self, key_width = 1.0):
        if self.stabilizer_type in self.stab_type_function_dict.keys():
            return self.stab_type_function_dict[self.stabilizer_type](key_width)
        else:
            raise ValueError('stabilizer type %s is not a valid stabilizer type' % (self.stabilizer_type))
        

    

    def mx_openable_switch_cutout(self):
        poly_points = [
            [self.SQUARE_SIZE_HALF + self.kerf, -self.SQUARE_SIZE_HALF -  self.kerf], # 0
            [self.SQUARE_SIZE_HALF + self.kerf, -self.CLIP_NOTCH_Y_MAX -  self.kerf], # 1
            [self.CLIP_NOTCH_X + self.kerf, -self.CLIP_NOTCH_Y_MAX -  self.kerf], # 2
            [self.CLIP_NOTCH_X + self.kerf, -self.CLIP_NOTCH_Y_MIN + self.kerf], # 3
            [self.SQUARE_SIZE_HALF + self.kerf, -self.CLIP_NOTCH_Y_MIN + self.kerf], # 4
            [self.SQUARE_SIZE_HALF + self.kerf, self.CLIP_NOTCH_Y_MIN -  self.kerf], # 5
            [self.CLIP_NOTCH_X + self.kerf, self.CLIP_NOTCH_Y_MIN -  self.kerf], # 6
            [self.CLIP_NOTCH_X + self.kerf, self.CLIP_NOTCH_Y_MAX + self.kerf], # 7
            [self.SQUARE_SIZE_HALF + self.kerf, self.CLIP_NOTCH_Y_MAX + self.kerf], # 8
            [self.SQUARE_SIZE_HALF + self.kerf, self.SQUARE_SIZE_HALF + self.kerf], # 9
            [-self.SQUARE_SIZE_HALF -  self.kerf, self.SQUARE_SIZE_HALF + self.kerf], # 10
            [-self.SQUARE_SIZE_HALF -  self.kerf, self.CLIP_NOTCH_Y_MAX + self.kerf], # 11
            [-self.CLIP_NOTCH_X -  self.kerf, self.CLIP_NOTCH_Y_MAX + self.kerf], # 12
            [-self.CLIP_NOTCH_X -  self.kerf, self.CLIP_NOTCH_Y_MIN -  self.kerf], # 13
            [-self.SQUARE_SIZE_HALF -  self.kerf, self.CLIP_NOTCH_Y_MIN -  self.kerf], # 14
            [-self.SQUARE_SIZE_HALF -  self.kerf, -self.CLIP_NOTCH_Y_MIN + self.kerf], # 15
            [-self.CLIP_NOTCH_X -  self.kerf, -self.CLIP_NOTCH_Y_MIN + self.kerf], # 16
            [-self.CLIP_NOTCH_X -  self.kerf, -self.CLIP_NOTCH_Y_MAX -  self.kerf], # 17
            [-self.SQUARE_SIZE_HALF -  self.kerf, -self.CLIP_NOTCH_Y_MAX -  self.kerf], # 18
            [-self.SQUARE_SIZE_HALF -  self.kerf, -self.SQUARE_SIZE_HALF -  self.kerf] # 19
        ]

        # x_right = self.kerf + self.SQUARE_SIZE_HALF - self.CORNER_CIRCLE_EDGE_OFFSET
        # x_left = self.kerf - self.SQUARE_SIZE_HALF + self.CORNER_CIRCLE_EDGE_OFFSET
        # y_top = self.kerf + self.SQUARE_SIZE_HALF - self.CORNER_CIRCLE_EDGE_OFFSET
        # y_bottom = self.kerf - self.SQUARE_SIZE_HALF + self.CORNER_CIRCLE_EDGE_OFFSET

        return poly_points

        # d = polygon(poly_points, poly_path)
        # d += right(x_right) ( forward(y_top) ( circle(r = .4) ) )
        # d += right(x_right) ( forward(y_bottom) ( circle(r = .4) ) )
        # d += right(x_left) ( forward(y_bottom) ( circle(r = .4) ) )
        # d += right(x_left) ( forward(y_top) ( circle(r = .4) ) )



    def mx_switch_cutout(self):
        poly_points = [
            [7 + self.kerf, -7 -  self.kerf], # 0
            [7 + self.kerf, 7 + self.kerf], # 1
			[-7 -  self.kerf, 7 + self.kerf], # 2
            [-7 -  self.kerf, -7 -  self.kerf] # 3
            
        ]

        return poly_points



    def mx_alps_switch_cutout(self):
        poly_points = [
            [7 + self.kerf, -7 -  self.kerf], # 0
            [7 + self.kerf, -6.4 -  self.kerf], # 1
            [7.8 + self.kerf, -6.4 -  self.kerf], # 2
            [7.8 + self.kerf, 6.4 + self.kerf], # 3
			[7 + self.kerf, 6.4 + self.kerf], # 4
            [7 + self.kerf, 7 + self.kerf], # 5
            [-7 -  self.kerf, 7 + self.kerf], # 6
            [-7 -  self.kerf, 6.4 + self.kerf], # 7
			[-7.8 -  self.kerf, 6.4 + self.kerf], # 8
            [-7.8 -  self.kerf, -6.4 -  self.kerf], # 9
            [-7 -  self.kerf, -6.4 -  self.kerf], # 10
            [-7 -  self.kerf, -7 -  self.kerf] # 11
        ]

        return poly_points

    
    def alps_switch_cutout(self):
        poly_points = [
            [7.8 + self.kerf, -6.4 -  self.kerf], # 0
            [7.8 + self.kerf, 6.4 + self.kerf], # 1
			[-7.8 -  self.kerf, 6.4 + self.kerf], # 2
            [-7.8 -  self.kerf, -6.4 -  self.kerf] # 3
        ]

        return poly_points




    def get_cherry_stab_cutout_spacing(self, key_width = 1.0):
        
        if key_width >= 2.0 and key_width < 3.0: # 2u, 2.25u, 2.5u, 2.75u
            return 11.9
        elif key_width == 3: # 3u
            return 19.05
        elif key_width == 4: # 4u
            return 28.575
        elif key_width == 4.5: # 4.5u
            return 34.671
        elif key_width == 5.5: # 5.5u
            return 42.8625
        elif key_width == 6: # 6u
            return 47.5
        elif key_width == 6.25: # 6.25u
            return 50
        elif key_width == 6.5: # 6.5u
            return 52.38
        elif key_width == 7: # 7u
            return 57.15
        elif key_width == 8: # 8u
            return 66.675
        elif key_width == 9: # 9u
            return 66.675
        elif key_width == 10: # 10u
            return 66.675
        else:
            return -1


    def get_alps_stab_cutout_spacing(self, key_width = 1.0):

        if key_width == 1.75:
            return 11.938
        elif key_width == 2.0:
            return 14.096
        elif key_width == 2.25:
            return 14.096,
        elif key_width == 2.75:
            return 14.096
        elif key_width == 6.25:
            return 41.859
        elif key_width == 6.5:
            return 45.3
        else:
            return -1


    def cherry_costar_stab_cutout(self, key_width = 1.0):
        support_cutout_poly_points = None

        s = self.get_cherry_stab_cutout_spacing(key_width = key_width)

        if s != -1:
            poly_points = [
                [s - self.MAIN_BODY_SWITCH_SIDE_X_OFFSET -  self.kerf, -self.BAR_BOTTOM_Y -  self.kerf], # 0
                [s - self.MAIN_BODY_SWITCH_SIDE_X_OFFSET -  self.kerf, -self.MAIN_BODY_BOTTOM_Y -  self.kerf], # 1
                [s - self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET -  self.kerf, -self.MAIN_BODY_BOTTOM_Y -  self.kerf], # 2
                [s - self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET -  self.kerf, -self.BOTTOM_NOTCH_BOTTOM_Y -  self.kerf], # 3
                [s + self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET + self.kerf, -self.BOTTOM_NOTCH_BOTTOM_Y -  self.kerf], # 4
                [s + self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET + self.kerf, -self.MAIN_BODY_BOTTOM_Y -  self.kerf], # 5
                [s + self.MAIN_BODY_SWITCH_SIDE_X_OFFSET + self.kerf, -self.MAIN_BODY_BOTTOM_Y -  self.kerf], # 6
                [s + self.MAIN_BODY_SWITCH_SIDE_X_OFFSET + self.kerf, -self.BAR_BOTTOM_Y -  self.kerf], # 7
                [s + self.SIDE_NOTCH_FAR_SIDE_X_OFFSET + self.kerf, -self.BAR_BOTTOM_Y -  self.kerf], # 8
                [s + self.SIDE_NOTCH_FAR_SIDE_X_OFFSET + self.kerf, self.SIDE_NOTCH_TOP_Y + self.kerf], # 9
                [s + self.MAIN_BODY_SWITCH_SIDE_X_OFFSET + self.kerf, self.SIDE_NOTCH_TOP_Y + self.kerf], # 10
                [s + self.MAIN_BODY_SWITCH_SIDE_X_OFFSET + self.kerf, self.MAIN_BODY_TOP_Y + self.kerf], # 11
                [s + self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET + self.kerf, self.MAIN_BODY_TOP_Y + self.kerf], # 12
                [s + self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET + self.kerf, self.TOP_NOTCH_TOP_Y + self.kerf], # 13
                [s - self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET -  self.kerf, self.TOP_NOTCH_TOP_Y + self.kerf], # 14
                [s - self.COSTAR_NOTCH_SWITCH_SIDE_X_OFFSET -  self.kerf, self.MAIN_BODY_TOP_Y + self.kerf], # 15
                [s - self.MAIN_BODY_SWITCH_SIDE_X_OFFSET -  self.kerf, self.MAIN_BODY_TOP_Y + self.kerf], # 16
                [s - self.MAIN_BODY_SWITCH_SIDE_X_OFFSET -  self.kerf, self.BAR_BOTTOM_Y + self.kerf], # 17
                [-s + self.MAIN_BODY_SWITCH_SIDE_X_OFFSET + self.kerf, self.BAR_BOTTOM_Y + self.kerf], # 18
                [-s + self.MAIN_BODY_SWITCH_SIDE_X_OFFSET + self.kerf, -self.BAR_BOTTOM_Y -  self.kerf] #19
            ]

            support_cutout_x = s - 3.375 -  (self.kerf * 2 )
            support_cutout_y = 7.97 + (self.kerf * 2 )
            support_cutout_w = (s + 4.375 + (self.kerf * 2 )) - (s - 4.375 -  (self.kerf * 2 ))
            support_cutout_h = self.cherry_support_cutout_h + (self.kerf * 2 )
            stab_bar_width = self.cherry_stab_bar_width + (self.kerf * 2 )

            support_cutout_poly_points = [
                [(s - 4.375 -  (self.kerf * 2 )), (6.77 + (self.kerf * 2 ) + stab_bar_width)],
                [(s - 4.375 -  (self.kerf * 2 )), (6.77 + (self.kerf * 2 )) + support_cutout_h],
                [(s + 4.375 + (self.kerf * 2 )), (6.77 + (self.kerf * 2 )) + support_cutout_h],
                [(s + 4.375 + (self.kerf * 2 )), (6.77 + (self.kerf * 2 ))],
                [(-s + 3.375 + (self.kerf * 2 )), (6.77 + (self.kerf * 2 ))],
                [(-s + 3.375 + (self.kerf * 2 )), (6.77 + (self.kerf * 2 ) + stab_bar_width)]
            ]

            self.logger.debug(support_cutout_poly_points)

            return poly_points, support_cutout_poly_points

        else:
            return None, None

    

    def cherry_stab_cutout(self, key_width = 1.0):
        support_cutout_poly_points = None

        s = self.get_cherry_stab_cutout_spacing(key_width = key_width)

        if s != -1:
            poly_points = [
                [s - 3.375 -  self.kerf, -2.3 -  self.kerf], # 0
                [s - 3.375 -  self.kerf, -5.53 -  self.kerf], # 1
                [s + 3.375 + self.kerf, -5.53 -  self.kerf], # 2
                [s + 3.375 + self.kerf, -2.3 -  self.kerf], # 3
                [s + 4.2 + self.kerf, -2.3 -  self.kerf], # 4
                [s + 4.2 + self.kerf, 0.5 + self.kerf], # 5
                [s + 3.375 + self.kerf, 0.5 + self.kerf], # 6
                [s + 3.375 + self.kerf, 6.77 + self.kerf], # 7
                [s + 1.65 + self.kerf, 6.77 + self.kerf], # 8
                [s + 1.65 + self.kerf, 7.97 + self.kerf], # 9
                [s - 1.65 -  self.kerf, 7.97 + self.kerf], # 10
                [s - 1.65 -  self.kerf, 6.77 + self.kerf], # 11
                [s - 3.375 -  self.kerf, 6.77 + self.kerf], # 12
                [s - 3.375 -  self.kerf, 2.3 + self.kerf], # 13

                [-s + 3.375 + self.kerf, 2.3 + self.kerf], # 14
                # [-s + 3.375 + self.kerf, 6.77 + self.kerf], # 15
                # [-s + 1.65 + self.kerf, 6.77 + self.kerf], # 16
                # [-s + 1.65 + self.kerf, 7.97 + self.kerf], # 17
                # [-s - 1.65 -  self.kerf, 7.97 + self.kerf], # 18
                # [-s - 1.65 -  self.kerf, 6.77 + self.kerf], # 19
                # [-s - 3.375 -  self.kerf, 6.77 + self.kerf], # 20
                # [-s - 3.375 -  self.kerf, 0.5 + self.kerf], #21
                # [-s - 4.2 -  self.kerf, 0.5 + self.kerf], # 22
                # [-s - 4.2 -  self.kerf, -2.3 -  self.kerf], # 23
                # [-s - 3.375 -  self.kerf, -2.3 -  self.kerf], # 24
                # [-s - 3.375 -  self.kerf, -5.53 -  self.kerf], # 25
                [-s + 3.375 + self.kerf, -5.53 -  self.kerf], # 26
                [-s + 3.375 + self.kerf, -2.3 -  self.kerf], # 27
            ]
            
            support_cutout_x = s - 3.375 -  (self.kerf * 2 )
            support_cutout_y = 7.97 + (self.kerf * 2 )
            support_cutout_w = (s + 4.375 + (self.kerf * 2 )) - (s - 4.375 -  (self.kerf * 2 ))
            support_cutout_h = self.cherry_support_cutout_h + (self.kerf * 2 )
            stab_bar_width = self.cherry_stab_bar_width + (self.kerf * 2 )

            support_cutout_poly_points = [
                [(s - 4.375 -  (self.kerf * 2 )), (6.77 + (self.kerf * 2 ) + stab_bar_width)],
                [(s - 4.375 -  (self.kerf * 2 )), (6.77 + (self.kerf * 2 )) + support_cutout_h],
                [(s + 4.375 + (self.kerf * 2 )), (6.77 + (self.kerf * 2 )) + support_cutout_h],
                [(s + 4.375 + (self.kerf * 2 )), (6.77 + (self.kerf * 2 ))],
                [(-s + 3.375 + (self.kerf * 2 )), (6.77 + (self.kerf * 2 ))],
                [(-s + 3.375 + (self.kerf * 2 )), (6.77 + (self.kerf * 2 ) + stab_bar_width)]
            ]

            self.logger.debug(support_cutout_poly_points)

            return poly_points, support_cutout_poly_points

        else:
            return None, None



    def costar_stab_cutout(self, key_width = 1.0):
        support_cutout_poly_points = None

        s = self.get_cherry_stab_cutout_spacing(key_width = key_width)

        if s != -1:
            poly_points = [
                [s - 1.65 -  self.kerf, -6.45 -  self.kerf], # 0
                [s + 1.65 + self.kerf, -6.45 -  self.kerf], # 1
                [s + 1.65 + self.kerf, 7.75 + self.kerf], # 2
                [s - 1.65 -  self.kerf, 7.75 + self.kerf] # 3
            ]

            return poly_points, support_cutout_poly_points

        else:
            return None, None


    def alps_stab_cutout(self, key_width = 1.0):
        support_cutout_poly_points = None

        s = self.get_alps_stab_cutout_spacing(key_width = key_width)

        if s != -1:
            poly_points = [
                [s - 1.333 -  self.kerf, 3.873 -  self.kerf], # 0
                [s + 1.333 + self.kerf, 3.873 -  self.kerf], # 1
			    [s + 1.333 + self.kerf, 9.08 + self.kerf], # 2
                [s - 1.333 -  self.kerf, 9.08 + self.kerf] # 3
            ]

            support_cutout_x = s - 2.133 - (self.kerf * 2)
            support_cutout_y = 9.08 - (self.kerf * 2) - 2
            support_cutout_w = (s + 2.133 + (self.kerf * 2)) - (s - 2.133 -  (self.kerf * 2))
            support_cutout_h = 1.5 + (self.kerf * 2) + 2

            # support_cutout_poly_points = [
            #     [(s - 4.375 -  (self.kerf * 2 )), (6.77 + (self.kerf * 2 ) + stab_bar_width)],
            #     [(s - 4.375 -  (self.kerf * 2 )), (6.77 + (self.kerf * 2 )) + support_cutout_h],
            #     [(s + 4.375 + (self.kerf * 2 )), (6.77 + (self.kerf * 2 )) + support_cutout_h],
            #     [(s + 4.375 + (self.kerf * 2 )), (6.77 + (self.kerf * 2 ))],
            #     [(-s + 3.375 + (self.kerf * 2 )), (6.77 + (self.kerf * 2 ))],
            #     [(-s + 3.375 + (self.kerf * 2 )), (6.77 + (self.kerf * 2 ) + stab_bar_width)]
            # ]

            support_cutout_poly_points = [
                [support_cutout_x, support_cutout_y],
                [support_cutout_x, support_cutout_y + support_cutout_h],
                [support_cutout_x + support_cutout_w, support_cutout_y + support_cutout_h],
                [support_cutout_x + support_cutout_w, support_cutout_y]
            ]

            self.logger.debug(support_cutout_poly_points)
            return poly_points, support_cutout_poly_points

        else:
            return None, None