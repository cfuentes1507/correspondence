
# -*- coding: utf-8 -*-

from odoo import models, fields


class correspondence(models.Model):
    _name = 'correspondence'
    _description = 'correspondence'

    name = fields.Char('Asunto')
    type = fields.Many2one('correspondence_type', string='Tipo de Correspondencia')
    department_transmitter = fields.Many2one('correspondence_department', string='Emisor')
    department_receiver = fields.Many2many('correspondence_department', string='Receptores')

#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
