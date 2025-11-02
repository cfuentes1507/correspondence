# -*- coding: utf-8 -*-
{
    'name': "Correspondencia Institucional",
    'summary': """
        Gestión de correspondencia y comunicados internos.
    """,
    'description': """
        Este módulo tiene como objetivo digitalizar y centralizar el proceso de envío, recepción, seguimiento y archivo de documentos y comunicados internos entre los diferentes departamentos de una organización.
    """,
    'author': "Carlos Fuentes (CFuentes.Dev)",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','mail'],
    'data': [
        'security/correspondence_security.xml',
        'data/correspondence_department_data.xml',
        'data/correspondence_type_data.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'wizard/upload_signed_document_wizard_view.xml',
        'views/menu_views.xml',
        'views/correspondence_department_view.xml',
        'views/correspondence_document_view_form.xml',
        'report/correspondence_report.xml',
    ],
    'demo': [
    ],
}
