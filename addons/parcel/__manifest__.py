# -*- coding: utf-8 -*-
{
    'name': "parcel",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """ Modulo para la implementacion de las api Pakke
    """,

    'author': "Christian Garcia Vazquez",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'installable':True,
    'auto_installable':False,

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management'],#Se coloca el modulo del que depende, El modulo api_pakke dependeria del modulo brokers_base

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views_shipments_pakke.xml',
    ],
}

