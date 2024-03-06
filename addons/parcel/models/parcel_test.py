# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

# Define the logger
_logger = logging.getLogger(__name__)

class parcel_test(models.Model):
    _name= 'parcel.test'
    _description = 'parcel.prueba'

    name = fields.Char(string="Nombre del registro")
    
    id_shipments = fields.Many2one("sale.order")
    
    test_pdf = fields.Binary(string="Prueba pdf")
    
    file_name = fields.Char()#Para el nombre del archivo pdf