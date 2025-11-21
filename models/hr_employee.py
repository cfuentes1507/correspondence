# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    director_description = fields.Html(string="Descripción del Cargo")
    director_signature = fields.Binary(string="Firma del Director", attachment=True)
    director_stamp = fields.Binary(string="Sello del Director", attachment=True)

    correspondence_director_history_ids = fields.One2many(
        'correspondence.department.director',
        'director_id',
        string="Historial de Director de Correspondencia"
    )

    is_correspondence_manager = fields.Boolean(
        string="Es Gerente de Correspondencia",
        compute='_compute_is_correspondence_manager',
        store=False, # No es necesario almacenar, se calcula al vuelo
        search='_search_is_correspondence_manager'
    )

    @api.depends('correspondence_director_history_ids.date_start', 'correspondence_director_history_ids.date_end')
    def _compute_is_correspondence_manager(self):
        today = fields.Date.today()
        for employee in self:
            # Verifica si hay algún registro de historial de director activo para este empleado
            active_director_history = employee.correspondence_director_history_ids.filtered(
                lambda h: h.date_start <= today and (not h.date_end or h.date_end >= today)
            )
            employee.is_correspondence_manager = bool(active_director_history)

    def _search_is_correspondence_manager(self, operator, value):
        today = fields.Date.today()
        # Encuentra todos los empleados que son directores activos actualmente
        active_directors_ids = self.env['correspondence.department.director'].search([
            ('date_start', '<=', today),
            '|', ('date_end', '=', False), ('date_end', '>=', today)
        ]).mapped('director_id').ids # Obtiene los IDs de los registros hr.employee

        if operator == '=':
            return [('id', 'in', active_directors_ids)] if value else [('id', 'not in', active_directors_ids)]
        elif operator == '!=':
            return [('id', 'not in', active_directors_ids)] if value else [('id', 'in', active_directors_ids)]
        return []