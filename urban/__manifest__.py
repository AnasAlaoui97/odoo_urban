# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Urban',
    'version': '1.0',
    'sequence': 170,
    'category': 'Extra tools',
    'summary': 'Differents nouveaux fontionalités pour URBAN Electronics',
    'description': """ Module for urban""",
    'website': '',
    'depends': ['purchase','sale'],
    'data': [
        'views/purchase_urban_views.xml',
        'data/ir_sequence_data.xml',
        'report/urban_report_templates.xml',
        'report/urban_report.xml',
        'views/sale_order_FE_views.xml',
        'report/sale_FE_report_templates.xml',
        'report/sale_FE_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
