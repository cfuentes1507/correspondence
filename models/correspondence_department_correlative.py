# -*- coding: utf-8 -*-

from odoo import models, fields

class CorrespondenceDepartmentCorrelative(models.Model):
    _name = 'correspondence.department.correlative'
    _description = 'Correlativo por Departamento y Tipo de Documento'

    department_id = fields.Many2one('hr.department', string='Departamento', required=True, ondelete='cascade')
    correspondence_type_id = fields.Many2one('correspondence_type', string='Tipo de Correspondencia', required=True)
    last_sequence = fields.Integer(string='Última Secuencia', default=0)
    _sql_constraints = [('department_type_uniq', 'unique (department_id, correspondence_type_id)', 'Solo puede existir un correlativo por tipo de documento en cada departamento.')]