
# -*- coding: utf-8 -*-

from odoo import models, fields


class correspondence_type(models.Model):
    _name = 'correspondence_type'
    _description = 'correspondence type'

    name = fields.Char('Nombre')
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
