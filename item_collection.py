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

        if not self.logger.hasHandlers():
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

        self.get_collection_bounds_call_count = 0
        self.get_moved_union_call_count = 0

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

    def get_min_x(self, rx = 0.0, ry = 0.0):
        return min(self.collection[rx][ry].keys())

    def get_max_x(self, rx = 0.0, ry = 0.0):
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
        return (max_x, min_y)


    def get_moved_union(self, rx = 0.0, ry = 0.0):
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

    def set_item_neighbors(self):
        for rx in self.get_rx_list():
            for ry in self.get_ry_list_in_rx(rx):
                for x in self.get_x_list_in_rx_ry(rx, ry):
                    for y in self.get_y_list_in_rx_ry_x(x, rx, ry):
                        current_switch = self.get_item(x, y, rx, ry)
                        
                        x_min = current_switch.x
                        x_max = current_switch.x + current_switch.w
                        y_min = current_switch.y - current_switch.h
                        y_max = current_switch.y

                        self.logger.info('x_min: %f, x_max: %f, y_min: %f, y_max: %s', x_min, x_max, y_min, y_max)

                        right_neighbor_list = []
                        for sib_rx in self.get_rx_list():
                            for sib_ry in self.get_ry_list_in_rx(sib_rx):
                                for sib_x in self.get_x_list_in_rx_ry(sib_rx, sib_ry):
                                    for sib_y in self.get_y_list_in_rx_ry_x(sib_x, sib_rx, sib_ry):
                                        sibling_switch = self.get_item(sib_x, sib_y, sib_rx, sib_ry)

                                        sib_x_min = sibling_switch.x
                                        sib_x_max = sibling_switch.x + sibling_switch.w
                                        sib_y_min = sibling_switch.y - sibling_switch.h
                                        sib_y_max = sibling_switch.y

                                        # self.logger.info('\tsib_x_min: %f, sib_x_max: %f, sib_y_min: %f, sib_y_max: %s', sib_x_min, sib_x_max, sib_y_min, sib_y_max)

                                        # check right neighbor
                                        
                                        if sib_y_max > y_min and sib_y_min < y_max and sib_x_min > x_max:
                                            right_neighbor_list.append(sibling_switch)
                                            self.logger.info('\tswitch (%f, %f) has right neightbor at (%f, %f)', x, y, sib_x, sib_y) 
                        
                        self.logger.info('\t\tright_neighbor_list: %s', str(right_neighbor_list))
