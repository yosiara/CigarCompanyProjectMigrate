# -*- coding: utf-8 -*-

import xlwt
from xlwt import *

bold = Font()
bold.name = 'Arial'
bold.bold = True

normal = Font()
normal.height = 0x00B4

borders = Borders()
borders.left = 1
borders.right = 1
borders.top = 1
borders.bottom = 1

borders_left_right = Borders()
borders_left_right.left = 1
borders_left_right.right = 1

borders_left_right_top = Borders()
borders_left_right_top.left = 1
borders_left_right_top.right = 1
borders_left_right_top.top = 1

al = Alignment()
al.horz = Alignment.HORZ_CENTER
al.vert = Alignment.VERT_CENTER

center = Alignment()
center.horz = Alignment.HORZ_CENTER
center.vert = Alignment.VERT_CENTER

justified = Alignment()
justified.horz = Alignment.HORZ_JUSTIFIED
justified.vert = Alignment.VERT_CENTER

middle = Alignment()
middle.vert = Alignment.VERT_CENTER

style_warning = XFStyle()
style_warning.font = bold
style_warning.borders = borders
style_warning.alignment = al

pattern = Pattern()
pattern.pattern = Pattern.SOLID_PATTERN
pattern.pattern_fore_colour = xlwt.Style.colour_map['red']
style_warning.pattern = pattern

style_justified_normal = XFStyle()
style_justified_normal.font = normal
style_justified_normal.borders = borders
style_justified_normal.alignment = justified

style_center_normal = XFStyle()
style_center_normal.font = normal
style_center_normal.borders = borders
style_center_normal.alignment = center

style_middle_normal = XFStyle()
style_middle_normal.font = normal
style_middle_normal.borders = borders
style_middle_normal.alignment = middle

style_center_middle_normal_border_left_right = XFStyle()
style_center_middle_normal_border_left_right.font = normal
style_center_middle_normal_border_left_right.borders = borders_left_right
style_center_middle_normal_border_left_right.alignment = center

style_middle_normal_border_left_right = XFStyle()
style_middle_normal.font = normal
style_middle_normal.borders = borders_left_right
style_middle_normal.alignment = middle
