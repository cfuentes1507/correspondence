
# -*- coding: utf-8 -*-

from odoo import models, fields

class res_users(models.Model):
    _inherit = 'res.users'

    department_id = fields.Many2one(
        'correspondence_department',
        string='Departamento de Correspondencia'
    )