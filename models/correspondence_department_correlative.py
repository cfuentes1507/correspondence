# -*- coding: utf-8 -*-

from odoo import models, fields


class DepartmentCorrelative(models.Model):
    _name = 'correspondence.department.correlative'
    _description = 'Correlativo por Departamento y Tipo'
    _rec_name = 'correspondence_type_id'

    department_id = fields.Many2one(
        'correspondence_department',
        string='Departamento',
        required=True,
        ondelete='restrict')
    correspondence_type_id = fields.Many2one(
        'correspondence_type',
        string='Tipo de Correspondencia',
        required=True,
        ondelete='restrict')
    last_sequence = fields.Integer(string='Última Secuencia', default=0, required=True)

    _sql_constraints = [
        ('department_type_uniq', 'unique(department_id, correspondence_type_id)',
        'Solo puede haber una secuencia por tipo de documento en cada departamento.')
    ]