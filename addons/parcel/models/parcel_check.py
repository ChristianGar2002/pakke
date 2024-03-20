# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

# Define the logger
_logger = logging.getLogger(__name__)

class parcel_check(models.Model):
    _name= 'parcel.check'
    _description = 'parcel.check'

    name = fields.Char(string="Nombre del registro")