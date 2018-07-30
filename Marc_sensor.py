#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Yidong QIN'

"""
MARC Bridge with sensors.
Input all data into MongoDB.
"""

from BMS_BrIM import *

MARC = ProjGroups("MARC_sensor")
# 0. Parameter
span_num = Parameter(1, "span_num", 11)
x_spacing = Parameter(2, "x_spacing", 108.0)
y_spacing = Parameter(3, "y_spacing", 84)
z_height = Parameter(4, "z_height", 108)
MARC.prm_group.append(span_num, x_spacing, y_spacing, z_height)
# 1. Material
# 1.1 Steel for truss chord
steel = Material(1, 'Steel', d="0.0000007345", E="29000", Nu="0.3", a="0.0000065", Fy="50", Fu="65")
# 1.2 Concrete for deck
concrete = Material(2, 'Concrete', d='0.0000002248', E="3604.9965", a="0.0000055", Fc28="4")
MARC.mat_group.append(steel, concrete)
# 2. Sections
# 2.0 Section Parameters
# BottomChord_width = Parameter(11, 'BottomChord_width', 0)
# BottomChord_depth = Parameter(12, "BottomChord_depth", 6)
Chord_width = Parameter(14, "Chord_width", 6)
Chord_depth = Parameter(15, "Chord_depth", 6)
BottomChord_thickness = Parameter(13, "BottomChord_thickness", 0.375)
TopChord_thickness = Parameter(16, "TopChord_thickness", 0.3125)
VertiBeam_thickness = Parameter(20, "VertiBeam_thickness", 0.25)
deck_thick = Parameter(17, "deck_thick", "5")
# VertiBeam_width = Parameter(18, "VertiBeam_width", 6)
# VertiBeam_depth = Parameter(19, "VertiBeam_depth", 6)
WebRadius = Parameter(None, "WebRadius", 1)
MARC.prm_group.append(BottomChord_thickness, TopChord_thickness,
                      deck_thick,VertiBeam_thickness, WebRadius)

# 2.1 Shapes
# rectangle=6*6
rect_Out = Shape(1, 'Rect 6*6', RectangleOBShape, Chord_depth.value, Chord_width.value,is_cut=False)
# rectangle=(6-0.375)
rect_Bot_In = Shape(2, 'Rect_Bot_In 5.625*5.625', RectangleOBShape,
                    Chord_depth.value-BottomChord_thickness.value,
                    Chord_width.value-BottomChord_thickness.value,is_cut=True)
# rectangle=(6-0.3125)
rect_Top_In = Shape(3, 'Rect_Top_In 5.6875*5.6875', RectangleOBShape,
                    Chord_depth.value-TopChord_thickness.value,
                    Chord_width.value-TopChord_thickness.value,is_cut=True)
# rectangle=(6-0.25)
rect_Ver_In = Shape(4, 'Rect_Ver_In 5.75*5.75', RectangleOBShape,
                    Chord_depth.value-VertiBeam_thickness.value,
                    Chord_width.value-VertiBeam_thickness.value,is_cut=True)
# circle=1
cir_Web=Shape(5, 'CircleWeb', OBCircle, WebRadius.value)
MARC.sec_group.append(rect_Ver_In,rect_Bot_In,rect_Out,rect_Top_In,cir_Web)
# 2.2 bottom chord 6*6*0.375
sect_bottom = Section(None, 'BottomChord', rect_Out, rect_Bot_In)
# 2.3 top chord 6*6*0.3125
sect_top = Section(None, 'TopChord', rect_Out, rect_Top_In)
# 2.4 vertical chord 6*6*.025
sect_vert = Section(None, 'VerticalChord', rect_Out, rect_Ver_In)
# 2.5 web radius=1
sect_web=Section(None, 'Web', cir_Web)
MARC.sec_group.append(sect_bottom,sect_top,sect_vert,sect_web)
# 3. Nodes
# 4. Structure Elements = Mechanical View
# 5. Equipments = Geometry View
# 6.

ShowTree(MARC.openBrIM)
