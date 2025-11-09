# -*- coding: utf-8 -*-

from odoo import models, fields, api


class correspondence_department(models.Model):
    _name = 'correspondence_department'
    _description = 'Departamento de Correspondencia'

    name = fields.Char(string='Nombre del Departamento', required=True)
    correlative_prefix = fields.Char(string='Prefijo de Correlativo', help="Prefijo usado para generar el correlativo de los documentos de este departamento (ej. 'FIN' para Finanzas).", required=True)
    user_ids = fields.One2many('res.users', 'department_id', string='Usuarios')
    director_history_ids = fields.One2many('correspondence.department.director', 'department_id', string='Historial de Directores')
    current_director_id = fields.Many2one('res.partner', string='Director Actual', compute='_compute_current_director', store=True)
    correlative_ids = fields.One2many('correspondence.department.correlative', 'department_id', string='Correlativos')

    @api.depends('director_history_ids.director_id', 'director_history_ids.date_start', 'director_history_ids.date_end')
    def _compute_current_director(self):
        for department in self:
            # Busca el director actual (sin fecha de fin o con fecha de fin en el futuro)
            current_director = department.director_history_ids.filtered(
                lambda h: not h.date_end or h.date_end >= fields.Date.today()
            )
            department.current_director_id = current_director[0].director_id if current_director else False
