# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

# Define the logger
_logger = logging.getLogger(__name__)

class parcel_package_dimensions(models.Model):
    _name= 'parcel.package_dimensions'
    _description = 'parcel.parcel_package_dimensions'

    name = fields.Char(string="Nombre de la medida")
    length = fields.Integer(string="Longitud")
    width = fields.Integer(string="Ancho")
    height = fields.Integer(string="Altura")