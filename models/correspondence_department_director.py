# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class DepartmentDirector(models.Model):
    _name = 'correspondence.department.director'
    _description = 'Historial de Directores de Departamento'
    _order = 'date_start desc'

    department_id = fields.Many2one(
        'correspondence_department', 
        string='Departamento', 
        required=True, 
        ondelete='cascade')
    director_id = fields.Many2one('res.users', string='Director', required=True)
    date_start = fields.Date(string='Fecha de Inicio', required=True, default=fields.Date.context_today)
    date_end = fields.Date(string='Fecha de Fin')

    @api.constrains('date_start', 'date_end', 'department_id', 'director_id')
    def _check_dates(self):
        for record in self:
            if record.date_end and record.date_start > record.date_end:
                raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")
            
            # Búsqueda de solapamiento de fechas
            # Busca otros registros para el mismo departamento que se solapen en el tiempo.
            domain = [
                ('id', '!=', record.id),
                ('department_id', '=', record.department_id.id),
                # Un registro existente no puede terminar antes de que el nuevo comience
                # Y no puede comenzar después de que el nuevo termine.
                # Esto previene cualquier tipo de solapamiento.
            ]

            # Caso 1: El nuevo registro no tiene fecha de fin (es indefinido)
            # Buscamos cualquier otro registro que no tenga fecha de fin o que termine después de que el nuevo comience.
            overlap_domain = list(domain) # Copiamos el dominio base
            if record.date_end:
                overlap_domain.extend(['|', ('date_end', '=', False), ('date_end', '>', record.date_start)])
                overlap_domain.append(('date_start', '<', record.date_end))
            else: # El nuevo registro es indefinido
                overlap_domain.append(('date_end', '>=', record.date_start))
            if self.search_count(overlap_domain) > 0:
                raise ValidationError('No puede haber dos directores en el mismo período de tiempo para un departamento.')