# -*- coding: utf-8 -*-
{
    'name': "Correspondencia Institucional",
    'summary': """
        Correspondencia Institucional
    """,
    'description': """
        Esto es un modulo diseñado para Odoo 15. Su funcion basica es el correcto envio, recepcion y almacenamiento, de la correspondencia institucional.
    """,
    'author': "Carlos Fuentes (CFuentes.Dev)",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','mail'],
    'data': [
        'security/correspondence_security.xml',
        'security/ir.model.access.csv',
        'views/menu_views.xml',
        'views/correspondence_document_view_form.xml'
    ],
    'demo': [
    ],
}
