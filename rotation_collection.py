from solid import *
from solid.utils import *

import logging

from switch import Switch
from support import Support
from support_cutout import SupportCutout

from item_collection import ItemCollection
from cell import Cell


class RotationCollection:
    def __init__(self):

        self.logger = logging.getLogger().getChild(__name__)

        self.rotation_collection = {}
       
    # def add_collection(self, x_offset, y_offset, cell: Cell, rx = None, ry = None)

    def get_rotation_list(self):
        return self.rotation_collection.keys()

    def get_collection_dict(self):
        return self.rotation_collection
    
    def add_item(self, rotation, x_offset, y_offset, cell: Cell, rx = None, ry = None):
        if rotation not in self.rotation_collection.keys():
            self.rotation_collection[rotation] = ItemCollection(rotation)

        self.rotation_collection[rotation].add_item(x_offset, y_offset, cell, rx, ry)
        
    def get_item(self, rotation, x_offset, y_offset, rx = None, ry = None) -> Cell:
        return self.rotation_collection[rotation].get_item(rotation, x_offset, y_offset, rx, ry)

    def get_rx_list(self, rotation):
        return self.rotation_collection[rotation].get_rx_list()

    def get_ry_list_in_rx(self, rotation, rx):
        return self.rotation_collection[rotation].get_ry_list_in_rx(rx)

    def get_x_list_in_rx_ry(self, rotation, rx = 0.0, ry = 0.0):
        return self.rotation_collection[rotation].get_x_list_in_rx_ry(rx, ry)

    def get_y_list_in_rx_ry_x(self, rotation, x, rx = 0.0, ry = 0.0):
        return self.rotation_collection[rotation].get_y_list_in_rx_ry_x(x, rx, ry)

    def get_x_list(self, rotation):
        return self.rotation_collection[rotation].get_x_list()

    def get_y_list_in_x(self, x, rotation):
        return self.rotation_collection[rotation].get_y_list_in_x(x)

    def get_max_x(self, rotation, rx = 0.0, ry = 0.0):
        return self.rotation_collection[rotation].get_max_x(rx, ry)
        
    def get_min_y(self, rotation, rx = 0.0, ry = 0.0):
        return self.rotation_collection[rotation].get_min_y(rx, ry)
    
    # def get_moved_(self, rotation, rx, ry):
    #     return 

    def get_real_collection_bounds(self):
        real_min_y = 1000.0
        real_max_y = -1000.0
        real_max_x = -1000.0
        real_min_x = 1000.0

        for rotation in self.get_rotation_list():
            for rx in self.get_rx_list(rotation):
                for ry in self.get_ry_list_in_rx(rotation, rx):
                    (min_x, max_x, max_y, min_y) = self.rotation_collection[rotation].get_collection_bounds(rx, ry)

                    min_x += rx
                    max_x += rx
                    min_y += -(ry)
                    max_y += -(ry)

                    # logger.debug('rx: %f, ry: %f, min_x: %f, max_x: %f, max_y: %f, min_y: %f', rx, ry, min_x, max_x, max_y, min_y)

                    if min_x < real_min_x:
                        real_min_x = min_x
                    if max_x > real_max_x:
                        real_max_x = max_x
                    if min_y < real_min_y:
                        real_min_y = min_y
                    if max_y > real_max_y:
                        real_max_y = max_y

        return (real_min_x, real_max_x, real_max_y, real_min_y)

    def get_union(self, rotation):
        solid = union()

        for rx in self.get_rx_list(rotation):
            for ry in self.get_ry_list_in_rx(rotation, rx):
                # for x in self.get_x_list_in_rx_ry(rotation, rx, ry)
                #     for y in self.get_y_list_in_rx_ry_x(rotation, x, rx, ry)
                solid += self.rotation_collection[rotation].get_moved_union(rx, ry)
                return solid

    def get_rotated_union(self, rotation):
        solid = union()

        for rx in self.get_rx_list(rotation):
            for ry in self.get_ry_list_in_rx(rotation, rx):
                # for x in self.get_x_list_in_rx_ry(rotation, rx, ry)
                #     for y in self.get_y_list_in_rx_ry_x(rotation, x, rx, ry)
                solid += self.rotation_collection[rotation].get_moved_union(rx, ry)
        

                solid = rotate(a = -(rotation), v = (0, 0, 1)) ( solid )
                return solid

    def get_rotated_moved_union(self, rotation):
        solid = union()

        for rx in self.get_rx_list(rotation):
            for ry in self.get_ry_list_in_rx(rotation, rx):
                # for x in self.get_x_list_in_rx_ry(rotation, rx, ry)
                #     for y in self.get_y_list_in_rx_ry_x(rotation, x, rx, ry)
                solid += self.rotation_collection[rotation].get_moved_union(rx, ry)
        

                solid = rotate(a = -(rotation), v = (0, 0, 1)) ( solid )
                solid = right(self.parameters.U(rx)) ( back(self.parameters.U(ry)) ( solid ) )
        
        return solid


    def draw_rotated_items(self, rotation):
        solid = union()

        for rx in self.get_rx_list(rotation):
            for ry in self.get_ry_list_in_rx(rotation, rx):
                # for x in self.get_x_list_in_rx_ry(rotation, rx, ry)
                #     for y in self.get_y_list_in_rx_ry_x(rotation, x, rx, ry)
                solid = self.rotation_collection[rotation].draw_rotated_items(rx, ry)
        
        return solid