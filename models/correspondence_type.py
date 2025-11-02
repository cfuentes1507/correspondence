
# -*- coding: utf-8 -*-

from odoo import models, fields


class correspondence_type(models.Model):
    _name = 'correspondence_type'
    _description = 'Tipos de Correspondencia'
    """Modelo para catalogar los diferentes tipos de correspondencia que se pueden generar.
    Ejemplos: Memorando, Circular, Oficio, etc."""

    name = fields.Char('Nombre')
