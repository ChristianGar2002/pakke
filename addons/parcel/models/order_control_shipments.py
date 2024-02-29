# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

# Define the logger
_logger = logging.getLogger(__name__)

class order_control_shipments(models.Model):
    _inherit = "sale.order"

    CourierCode = fields.Char(string="Codigo de mensajeria", compute="get_data_shipments")
    CourierServiceId = fields.Char(string="Id del servicio de mensajeria")
    ResellerReference = fields.Char(string="Referencia del distribuidor")
    Content = fields.Char(string="Contenido")
    CouponCode = fields.Char(string="Codigo de cupón")
    InsuredAmount = fields.Float(string="Valor declarado del paquete")
    
    #Campos para la parte del Dirección​ ​de​ ​Envío
    AddressFrom_ZipCode = fields.Char(string="Código Postal")
    AddressFrom_State = fields.Char(string="Estado")
    AddressFrom_City = fields.Char(string="Ciudad")
    AddressFrom_Neighborhood = fields.Char(string="Vecindario")
    AddressFrom_Address1 = fields.Char(string="Dirección 1")
    AddressFrom_Address2 = fields.Char(string="Dirección 2")
    AddressFrom_Residential = fields.Boolean(string="Residencial")
    
    #Campos para la parte del Dirección de entrega
    AddressTo_ZipCode = fields.Char(string="Código Postal")
    AddressTo_State = fields.Char(string="Estado")
    AddressTo_City = fields.Char(string="Ciudad")
    AddressTo_Neighborhood = fields.Char(string="Vecindario")
    AddressTo_Address1 = fields.Char(string="Dirección 1")
    AddressTo_Address2 = fields.Char(string="Dirección 2")
    AddressTo_Residential = fields.Boolean(string="Residencial")
    
    #Campos para la parte del paquete
    Parcel_Length = fields.Integer(string="Longitud")
    Parcel_Width = fields.Integer(string="Ancho")
    Parcel_Height = fields.Integer(string="Altura")
    Parcel_Weight = fields.Integer(string="Peso")
    
    #Campos para la parte del remitente
    Sender_Weight = fields.Char(string="Nombre")
    Sender_Phone1 = fields.Char(string="Telefono 1")
    Sender_Phone2 = fields.Char(string="Telefono 2")
    Sender_Phone3 = fields.Char(string="Telefono 3")
    Sender_Email = fields.Char(string="Correo electronico")
    
    #Campos para la parte del destinatario
    Recipient_Name = fields.Char(string="Nombre")
    Recipient_CompanyName = fields.Char(string="Nombre de la empresa")
    Recipient_Phone1 = fields.Char(string="Telefono 1")
    Recipient_Email = fields.Char(string="Correo electronico")
        
    @api.onchange("CourierServiceId")
    def get_data_shipments(self):#Metodo para obtener los datos que ya estan registrados
        
        for data in self:
                       
            data.CourierCode = data.user_id.name
            
    def quote(self):
        
        _logger.error("Cotizando")

    
    
    
   

