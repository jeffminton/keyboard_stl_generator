from solid import *
from solid.utils import *

import logging


from switch import Switch
from support import Support
from support_cutout import SupportCutout

from cell import Cell


class ItemCollection:
    def __init__(self, rotation = 0.0):

        self.logger = logging.getLogger('ItemCollection')
        self.logger.setLevel(logging.INFO)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # create formatter
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)

        self.collection = {}

        self.rotation = rotation

    def get_collection_dict(self, rx = 0.0, ry = 0.0):
        return self.collection[rx][ry]
    
    def add_item(self, x_offset, y_offset, cell: Cell, rx = 0.0, ry = 0.0):
        
        # if self.rotation == 0.0:
        #     if x_offset not in self.collection.keys():
        #         self.collection[x_offset] = {}

        #     # print('x_offset:', x_offset, 'y_offset:', y_offset)
        #     self.collection[x_offset][y_offset] = cell

        # elif self.rotation != 0.0:
        if rx not in self.collection.keys():
            self.collection[rx] = {}

        if ry not in self.collection[rx].keys():
            self.collection[rx][ry] = {}

        if x_offset not in self.collection[rx][ry].keys():
            self.collection[rx][ry][x_offset] = {}

        self.collection[rx][ry][x_offset][y_offset] = cell

    def get_item(self, x_offset, y_offset, rx = 0.0, ry = 0.0) -> Cell:
        # if self.rotation == 0.0:
        #     return self.collection[x_offset][y_offset]
        # elif self.rotation != 0.0:
        return self.collection[rx][ry][x_offset][y_offset]

    def get_moved_item(self, x_offset, y_offset, rx = 0.0, ry = 0.0) -> Cell:
        # if self.rotation == 0.0:
        #     return self.collection[x_offset][y_offset]
        # elif self.rotation != 0.0:
        return self.collection[rx][ry][x_offset][y_offset].get_moved()

    def get_rx_list(self):
        return self.collection.keys()

    def get_ry_list_in_rx(self, rx):
        return self.collection[rx].keys()

    def get_x_list_in_rx_ry(self, rx = 0.0, ry = 0.0):
        return self.collection[rx][ry].keys()

    def get_y_list_in_rx_ry_x(self, x, rx = 0.0, ry = 0.0):
        return self.collection[rx][ry][x].keys()

    def get_x_list(self, rx = 0.0, ry = 0.0):
        return self.collection[rx][ry].keys()

    def get_y_list_in_x(self, x, rx = 0.0, ry = 0.0):
        return self.collection[rx][ry][x].keys()

    def get_max_x(self, rx = 0.0, ry = 0.0):
        # print('self.collection:', self.collection)
        return max(self.collection[rx][ry].keys())
        
    def get_min_y(self, rx = 0.0, ry = 0.0):
        min_y = 0
        
        for x in self.collection[rx][ry].keys():
            col_min_y = min(self.collection[rx][ry][x].keys())

            if col_min_y < min_y:
                min_y = col_min_y    

        return min_y

    def get_collection_bounds(self):
        min_y = 0
        max_x = 0
        
        for x in self.get_x_list():
            for y in self.get_y_list_in_x(x):
                end_x = self.get_item(x, y).get_end_x()
                end_y = self.get_item(x, y).get_end_y()
                self.logger.debug('end_x: %f, end_y: %f', end_x, end_y)
                if end_x > max_x:
                    max_x = end_x

                if end_y < min_y:
                    min_y = end_y
                
        self.logger.info('max_x: %f, min_y: %f', max_x, min_y)
            # col_min_y = min(self.collection[rx][ry][x].keys())

            # if col_min_y < min_y:
            #     min_y = col_min_y    

        return (max_x, min_y)


    def get_moved_union(self, rx = 0.0, ry = 0.0):
        # print('rx:', rx, 'ry:', ry)
        solid = union()

        # print('\tself.collection[rx][ry]:', self.collection[rx][ry])
        for x in self.get_x_list_in_rx_ry(rx, ry):
            # print('\t\tx:', x)
            for y in self.get_y_list_in_rx_ry_x(x, rx, ry):
                # print('\t\t\ty:', y)
                temp_solid = self.get_moved_item(x, y, rx, ry)
                # print('\t\t\t\ttemp_solid:', temp_solid)
                solid += temp_solid
        
        return solid