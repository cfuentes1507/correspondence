# -*- coding: utf-8 -*-

from odoo import models, fields, api


class correspondence_department(models.Model):
    _name = 'correspondence_department'
    _description = 'Departamento de Correspondencia'

    name = fields.Char(string='Nombre del Departamento', required=True)
    user_ids = fields.One2many('res.users', 'department_id', string='Usuarios')
    director_history_ids = fields.One2many('correspondence.department.director', 'department_id', string='Historial de Directores')
    current_director_id = fields.Many2one('res.users', string='Director Actual', compute='_compute_current_director', store=True)

    @api.depends('director_history_ids.director_id', 'director_history_ids.date_start', 'director_history_ids.date_end')
    def _compute_current_director(self):
        for department in self:
            # Búsqueda optimizada del director actual
            today = fields.Date.today()
            current_director_record = self.env['correspondence.department.director'].search([
                ('department_id', '=', department.id),
                ('date_start', '<=', today),
                '|',
                ('date_end', '=', False),
                ('date_end', '>=', today)
            ], order='date_start desc', limit=1)
            department.current_director_id = current_director_record.director_id if current_director_record else False
