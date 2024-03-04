# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

# Define the logger
_logger = logging.getLogger(__name__)

class order_control_shipments(models.Model):
    _inherit = "sale.order"

    courier_code = fields.Char(string="Codigo de mensajeria", compute="quote_table_data")
    courier_service_id = fields.Char(string="Id del servicio de mensajeria", compute="quote_table_data")
    reseller_reference = fields.Char(string="Referencia personalizada del paquete")
    content = fields.Char(string="Contenido", compute="get_data_shipments")
    coupon_code = fields.Char(string="Codigo de cupón")
    insured_amount = fields.Float(string="Valor declarado del paquete")
    
    #Campos para la parte del Dirección​ ​de​ ​Envío
    address_from_zipcode = fields.Char(string="Código Postal")
    address_from_state = fields.Char(string="Estado")
    address_from_city = fields.Char(string="Ciudad")
    address_from_neighborhood = fields.Char(string="Vecindario")
    address_from_address1 = fields.Char(string="Dirección 1")
    address_from_address2 = fields.Char(string="Dirección 2")
    address_from_residential = fields.Boolean(string="Residencial")
    
    #Campos para la parte del Dirección de entrega
    address_to_zipcode = fields.Char(string="Código Postal")
    address_to_state = fields.Char(string="Estado")
    address_to_city = fields.Char(string="Ciudad")
    address_to_neighborhood = fields.Char(string="Vecindario")
    address_to_address1 = fields.Char(string="Dirección 1")
    address_to_address2 = fields.Char(string="Dirección 2")
    address_to_residential = fields.Boolean(string="Residencial")
    
    #Campos para la parte del paquete
    parcel_length = fields.Integer(string="Longitud")
    parcel_width = fields.Integer(string="Ancho")
    parcel_height = fields.Integer(string="Altura")
    parcel_weight = fields.Integer(string="Peso")
    
    #Campos para la parte del remitente
    sender_weight = fields.Char(string="Nombre")
    sender_phone1 = fields.Char(string="Telefono 1")
    sender_phone2 = fields.Char(string="Telefono 2")
    sender_phone3 = fields.Char(string="Telefono 3")
    sender_email = fields.Char(string="Correo electronico")
    
    #Campos para la parte del destinatario
    recipient_name = fields.Char(string="Nombre")
    recipient_company_name = fields.Char(string="Nombre de la empresa")
    recipient_phone1 = fields.Char(string="Telefono 1")
    recipient_email = fields.Char(string="Correo electronico")
    
    #Campos relacionados con quote_couriers
    id_couriers_selection = fields.Many2one("parcel.pakke", string="Selecciona al mensajero", domain="[('name_shipments', '=', name_orders)]")
    id_couriers_table = fields.One2many("parcel.pakke", "id_shipments", string="Tabla de cotización", compute="quote_table")
    
    name_orders = fields.Char(string="Nombre del pedido")#Campo para filtrar por nombre de pedidos
    
    @api.onchange("name")
    def get_data_shipments(self):#Metodo para obtener los datos que ya estan registrados
        
        for data in self:
            
            data.content = data.user_id.name
            
    def quote(self):#Metodo para cotizar la api de pakke
        for quote in self:
            
            #Almaceno el nombre de cada registro del modelo
            name_shipments = quote.name
            new_quotes = []
            
            #Obtengo los datos de la api
            quotes_data = [{'CourierCode':'STF', 'CourierName':'Estafeta', 'CourierServiceId':'ESTAFETA_TERRESTRE_CONSUMO', 'CourierServiceName':'Terrestre Consumo', 'DeliveryDays':'2-5 días hab.', 'CouponCode':None, 'DiscountAmount':0, 'TotalPrice':85.83, 'EstimatedDeliveryDate':'2019-07-04','BestOption':True},
            {'CourierCode':'FDX', 'CourierName':'FedEx', 'CourierServiceId':'FEDEX_EXPRESS_SAVER', 'CourierServiceName':'Express Saver', 'DeliveryDays':'3 días hab.', 'CouponCode':None, 'DiscountAmount':0, 'TotalPrice':134.75, 'EstimatedDeliveryDate':'2019-07-04','BestOption':False}]
            
            # Itera sobre los datos de la cotizacion de la api de pakke, y capturar sus datos
            for quote_data in quotes_data:  
                quote_courier_code = quote_data['CourierCode']
                quote_courier_name = quote_data['CourierName']
                quote_courier_service_id = quote_data['CourierServiceId']
                quote_courier_service_name = quote_data['CourierServiceName']
                quote_delivery_days = quote_data['DeliveryDays']
                quote_coupon_code = quote_data['CouponCode']
                quote_discount_amount = quote_data['DiscountAmount']
                quote_total_price = quote_data['TotalPrice']
                quote_estimated_delivery_date = quote_data['EstimatedDeliveryDate']
                quote_best_option = quote_data['BestOption']
                
                #Buscar si ya existe esa cotización
                quote_couriers = self.env['parcel.pakke'].search([('name_shipments', '=', name_shipments), ('courier_code', '=', quote_courier_code), ('name', '=', quote_courier_name), ('courier_service_id', '=', quote_courier_service_id), ('courier_service_name', '=', quote_courier_service_name), ('delivery_days', '=', quote_delivery_days), ('coupon_code', '=', quote_coupon_code), ('discount_amount', '=', quote_discount_amount), ('total_price', '=', quote_total_price), ('estimated_delivery_date', '=', quote_estimated_delivery_date), ('best_option', '=', quote_best_option)], limit=1)  # 
                
                if not quote_couriers:  # Si la cotizacion no existe
                    new_quotes.append({  # Agrega la nueva cotizacion a la lista
                        'name_shipments': name_shipments,
                        'courier_code': quote_courier_code,
                        'name': quote_courier_name,
                        'courier_service_id': quote_courier_service_id,
                        'courier_service_name': quote_courier_service_name,
                        'delivery_days': quote_delivery_days,
                        'coupon_code': quote_coupon_code,
                        'discount_amount': quote_discount_amount,
                        'total_price': quote_total_price,
                        'estimated_delivery_date': quote_estimated_delivery_date,
                        'best_option': quote_best_option,
                    })
                    
                else:
                    
                    _logger.info("La cotización ya existe")
                    
            if new_quotes:  # Si hay nuevas cotizaciones
                with self.env.cr.savepoint():  # Crea un punto de guardado en la transacción de base de datos actual
                    self.env['parcel.pakke'].create(new_quotes)  # Crea nuevas cotizaciones
                _logger.info(f"Cotizaciones {new_quotes}")
                
            quote.name_orders = name_shipments #Para filtrar por el nombre del pedido

    @api.onchange("id_couriers_selection")
    def quote_table_data(self):#Para colocar la información en el One2many y del mensajero que se elija
        
        for quote_many_data in self:
            
            name_shipments=quote_many_data.name
        
            registros_b = self.env['parcel.pakke'].search([('name_shipments', '=', name_shipments)])#Buscar los registros con el nombre del registro del modelo
            
            # Actualiza el campo One2many con los registros obtenidos
            self.id_couriers_table = [(6, 0, registros_b.ids)]
            
            #Colocar los datos del mensajero
            quote_many_data.courier_code = quote_many_data.id_couriers_selection.courier_code
            
            quote_many_data.courier_service_id = quote_many_data.id_couriers_selection.courier_service_id

    
    
    
   

