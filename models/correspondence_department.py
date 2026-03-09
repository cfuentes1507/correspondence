# -*- coding: utf-8 -*-
#
# ============================================================================
# DEPRECATED / CÓDIGO OBSOLETO
# ============================================================================
# Este modelo fue el diseño original para gestionar departamentos dentro del
# módulo de correspondencia. Toda su funcionalidad fue migrada al modelo
# estándar de Odoo 'hr.department' (ver: models/hr_department.py), que se
# extiende con los campos necesarios (correlative_prefix, director_history_ids,
# can_receive_correspondence, etc.).
#
# Este archivo NO está importado en __init__.py, por lo que Odoo no lo carga
# ni registra el modelo. Se conserva únicamente como referencia histórica.
#
# Se puede eliminar de forma segura sin ningún impacto en el módulo.
# ============================================================================

from odoo import models, fields, api


class correspondence_department(models.Model):
    _name = 'correspondence_department'
    _description = 'Departamento de Correspondencia [DEPRECATED - usar hr.department]'

    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    name = fields.Char(string='Nombre del Departamento', required=True)
    correlative_prefix = fields.Char(string='Prefijo de Correlativo', help="Prefijo usado para generar el correlativo de los documentos de este departamento (ej. 'FIN' para Finanzas).", required=True)
    user_ids = fields.One2many('res.users', 'department_id', string='Usuarios')
    director_history_ids = fields.One2many('correspondence.department.director', 'department_id', string='Historial de Directores')    
    current_director_id = fields.Many2one(
        'res.partner', 
        string='Director Actual', 
        compute='_compute_current_director', 
        search='_search_current_director'
    )
    correlative_ids = fields.One2many('correspondence.department.correlative', 'department_id', string='Correlativos')

    def _compute_current_director(self):
        """
        Calcula el director actual basado en la fecha de hoy.
        Este campo no se almacena para asegurar que siempre esté actualizado.
        """
        today = fields.Date.today()
        for department in self:
            # Busca el director activo hoy (sin fecha de fin, o con fecha de fin en el futuro)
            current_director = department.director_history_ids.filtered(
                lambda h: h.date_start <= today and (not h.date_end or h.date_end >= today)
            )
            department.current_director_id = current_director[0].director_id if current_director else False

    def _search_current_director(self, operator, value):
        """
        Permite buscar departamentos por su director actual.
        """
        today = fields.Date.today()
        # Buscamos historiales de director que estén activos hoy
        active_directors = self.env['correspondence.department.director'].search([
            ('date_start', '<=', today),
            '|', ('date_end', '=', False), ('date_end', '>=', today)
        ])
        # Devolvemos los departamentos que tienen esos historiales y cuyo director coincide con el valor de búsqueda
        return [('director_history_ids', 'in', active_directors.ids), ('director_history_ids.director_id', operator, value)]
