# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CorrespondencePhysicalLocation(models.Model):
    _name = 'correspondence.physical.location'
    _description = 'Ubicación Física de Archivo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nombre', required=True, tracking=True, help="Ejemplo: Estante A, Caja 3")
    code = fields.Char(string='Código', tracking=True, help="Código corto para referencia o etiquetado")
    description = fields.Text(string='Descripción', help="Detalles adicionales sobre la ubicación")
    active = fields.Boolean(string='Activo', default=True, tracking=True)

    parent_id = fields.Many2one('correspondence.physical.location', string='Ubicación Padre', index=True, ondelete='cascade')
    
    _sql_constraints = [
        ('name_parent_uniq', 'unique(name, parent_id)', 'El nombre de la ubicación debe ser único por ubicación padre.')
    ]

    @api.depends('name', 'parent_id.display_name')
    def _compute_display_name(self):
        for location in self:
            names = []
            current = location
            while current:
                names.append(current.name or "")
                current = current.parent_id
            location.display_name = " / ".join(reversed(names))

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('¡Error! No puedes crear ubicaciones recursivas.')
