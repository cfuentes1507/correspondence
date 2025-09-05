# -*- coding: utf-8 -*-
{
    'name': "Correspondencia Institucional",
    'summary': """
        Esto es un modulo diseñado para Odoo 15. Su funcion basica es el correcto envio, recepcion y almacenamiento, de la correspondencia institucional.
    """,
    'description': """
        Correspondencia Institucional
    """,
    'author': "Carlos Fuentes (CFuentes.Dev)",
    'website': "",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base'],
    # always loaded
    'data': [
        'security/correspondence_security.xml',
        'security/ir.model.access.csv',
        'views/menu_views.xml',
    ],
    'demo': [
    ],
}
