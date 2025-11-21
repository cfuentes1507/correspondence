# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CorrespondenceDepartmentDirector(models.Model):
    _name = 'correspondence.department.director'
    _description = 'Historial de Directores por Departamento'

    department_id = fields.Many2one('hr.department', string='Departamento', required=True, ondelete='cascade')
    director_id = fields.Many2one('hr.employee', string='Gerente', required=True)
    date_start = fields.Date(string='Fecha de Inicio', required=True, default=fields.Date.context_today)
    date_end = fields.Date(string='Fecha de Fin')

    def _update_department_manager(self):
        """
        Busca el director actual de los departamentos afectados y actualiza su gerente.
        """
        # Evita la recursión si la llamada proviene de hr.department.write
        if self.env.context.get('bypass_manager_sync_from_department_write'):
            return

        for department in self.mapped('department_id'):
            department._set_current_director_as_manager()

    @api.model_create_multi
    def create(self, vals_list):
        """
        Al crear un nuevo director, actualiza el gerente del departamento si es necesario.
        """
        records = super().create(vals_list)
        records._update_department_manager()
        return records

    def write(self, vals):
        """
        Al modificar un historial (ej. fecha de fin), actualiza el gerente del departamento.
        """
        res = super().write(vals)
        self._update_department_manager()
        return res

    def unlink(self):
        departments_to_update = self.mapped('department_id')
        res = super().unlink()
        departments_to_update._set_current_director_as_manager()
        return res