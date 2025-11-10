# -*- coding: utf-8 -*-

from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    director_description = fields.Html(string="Descripción del Cargo")
    director_signature = fields.Binary(string="Firma del Director", attachment=True)
    director_stamp = fields.Binary(string="Sello del Director", attachment=True)