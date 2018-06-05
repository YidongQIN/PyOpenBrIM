#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Yidong QIN'

'''

'''

import math

from PyOpenBrIM import *


class CubeGeo(OBObjElmt):
    """plate with rectangle Surfaces, accept 3 dimension parameters instead of 4 points and a thickness """

    def __init__(self, length, width, thick, cube_name=''):
        super(CubeGeo, self).__init__('Volume', cube_name)
        self.thick = self.prm_to_value(thick)
        self.length = self.prm_to_value(length)
        self.width = self.prm_to_value(width)
        self.model = self.geom()

    def set_basepoint(self, x, y, z):
        """the base point is the center of the first Surface."""
        self.model.move_to(x, y, z)

    def geom(self):
        plate_geomodel = OBVolume(
            OBSurface(OBPoint(-self.width / 2, -self.length / 2, 0),
                      OBPoint(self.width / 2, -self.length / 2, 0),
                      OBPoint(self.width / 2, self.length / 2, 0),
                      OBPoint(-self.width / 2, self.length / 2, 0)),
            OBSurface(OBPoint(-self.width / 2, -self.length / 2, self.thick),
                      OBPoint(self.width / 2, -self.length / 2, self.thick),
                      OBPoint(self.width / 2, self.length / 2, self.thick),
                      OBPoint(-self.width / 2, self.length / 2, self.thick)))
        return plate_geomodel


class BoltedPlateGeo(OBObjElmt):

    def __init__(self, plate_name,
                 thick, length, width,
                 diameter, xclearance, yclearance,
                 column, row,
                 material='steel'):
        super(BoltedPlateGeo, self).__init__('Surface', plate_name)
        self.thick = self.prm_to_value(thick)
        self.length = self.prm_to_value(length)
        self.width = self.prm_to_value(width)
        self.diameter = self.prm_to_value(diameter)
        self.xclearance = self.prm_to_value(xclearance)
        self.yclearance = self.prm_to_value(yclearance)
        self.column = self.prm_to_value(column)
        self.row = self.prm_to_value(row)
        self.material = material
        self.x_sp = (self.length - 2 * self.xclearance) / (self.column - 1)
        self.y_sp = (self.width - 2 * self.yclearance) / (self.row - 1)
        self.model = self.geom()

    def geom(self):
        """a Surface Elmt, use real number not parameters"""
        plate_def = OBSurface(OBPoint(0, 0),
                              OBPoint(self.length, 0),
                              OBPoint(self.length, self.width),
                              OBPoint(0, self.width),
                              thick_par=self.thick,
                              material_obj=self.material,
                              surface_name=self.name)
        holes = []
        for i in range(self.column):
            for j in range(self.row):
                hole = OBCircle('hole_{}_{}'.format(i, j),
                                radius=self.diameter / 2,
                                x=self.xclearance + i * self.x_sp,
                                y=self.yclearance + j * self.y_sp)
                hole.sub(OBPrmElmt('IsCutout', 1))
                holes.append(hole)
        plate_def.sub(*holes)
        return plate_def


class PlateFEM(OBObjElmt):
    """FEM model of plate, either normal plate or bolted plate"""

    def __init__(self, length, width, thick, material, plate_name):
        super(PlateFEM, self).__init__('FESurface', plate_name)
        self.thick = self.prm_to_value(thick)
        self.length = self.prm_to_value(length)
        self.width = self.prm_to_value(width)
        self.material = material
        self.model = self.fem()

    def fem(self, *nodes):
        """4 FENodes and then the FESurface"""
        if nodes:
            return OBFESurface(*nodes, thick_par=self.thick, material_obj=self.material, fes_name=self.name)
        else:
            n1 = OBFENode(-self.width / 2, -self.length / 2, 0, 'N1P_{}'.format(self.name))
            n2 = OBFENode(self.width / 2, -self.length / 2, 0, 'N2P_{}'.format(self.name))
            n3 = OBFENode(self.width / 2, self.length / 2, 0, 'N3P_{}'.format(self.name))
            n4 = OBFENode(-self.width / 2, self.length / 2, 0, 'N4P_{}'.format(self.name))
            fes = OBFESurface(n1, n2, n3, n4, self.thick, self.material, self.name)
            return OBGroup(self.name, n1, n2, n3, n4, fes)

    # def set_node(self, x, y, z):
    #     self.sub(FENode(x, y, z))

    # def link_node(self, node: FENode):
    # """FESurface 不能接收多余4个FENode"""
    #     self.model.prm_refer(node)


class StraightBeamGeo(OBObjElmt):
    """beam with rectangle cross-section, accept length and 3 direction parameters instead of 2 points"""

    def __init__(self, length, direction_x, direction_y, direction_z, section, beam_name=''):
        super(StraightBeamGeo, self).__init__('Line', beam_name)
        self.length = self.prm_to_value(length)
        self.cos = direction_cos(direction_x, direction_y, direction_z)
        self.section = section
        self.model = self.geom()

    def geom(self):
        line = OBLine(OBPoint(0, 0, 0),
                      OBPoint(self.length * self.cos[0],
                              self.length * self.cos[1],
                              self.length * self.cos[2]),
                      self.section)
        return line


class StraightBeamFEM(OBObjElmt):
    """FEM for rectangle section beam"""

    def __init__(self, length, direction_x, direction_y, direction_z, section, beta_angle=0, beam_name=''):
        super(StraightBeamFEM, self).__init__('FELine', beam_name)
        self.length = self.prm_to_value(length)
        self.cos = direction_cos(direction_x, direction_y, direction_z)
        self.section = section
        self.angle = beta_angle
        self.model = self.fem()

    def fem(self, *nodes):
        if nodes:
            return OBFELine(*nodes, section=self.section, beta_angle=self.angle, feline_name=self.name)
        else:
            n1 = OBFENode(0, 0, 0)
            n2 = OBFENode(self.length * self.cos[0], self.length * self.cos[1], self.length * self.cos[2])
            fel = OBFELine(n1, n2, self.section, self.angle, self.name)
            return OBGroup(n1, n2, fel)


def direction_cos(x, y, z) -> tuple:
    square_root = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    # cos_x = x / square_root
    # cos_y = y / square_root
    # cos_z = z / square_root
    return x / square_root, y / square_root, z / square_root