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
    director_id = fields.Many2one('res.partner', string='Director (Contacto)', required=True, domain="[('is_company', '=', False)]")
    date_start = fields.Date(string='Fecha de Inicio', required=True, default=fields.Date.context_today)
    date_end = fields.Date(string='Fecha de Fin')

    @api.constrains('date_start', 'date_end', 'department_id', 'director_id')
    def _check_dates(self):
        for record in self:
            if record.date_end and record.date_start > record.date_end:
                raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")
            
            # Búsqueda de solapamiento de fechas.
            # Un solapamiento existe si otro registro para el mismo departamento cumple:
            # (otro.inicio <= self.fin) y (self.inicio <= otro.fin)
            # Si self.date_end no está definido, lo tratamos como infinito.
            # Si otro.date_end no está definido, lo tratamos como infinito.
            domain = [
                ('id', '!=', record.id),
                ('department_id', '=', record.department_id.id),
                '|',
                ('date_end', '=', False),
                ('date_end', '>=', record.date_start),
            ]
            if record.date_end:
                domain.append(('date_start', '<=', record.date_end))
            
            if self.search_count(domain) > 0:
                raise ValidationError('No puede haber dos directores en el mismo período de tiempo para un departamento.')