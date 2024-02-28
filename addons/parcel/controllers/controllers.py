# -*- coding: utf-8 -*-
# from odoo import http


# class Parcel(http.Controller):
#     @http.route('/parcel/parcel', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/parcel/parcel/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('parcel.listing', {
#             'root': '/parcel/parcel',
#             'objects': http.request.env['parcel.parcel'].search([]),
#         })

#     @http.route('/parcel/parcel/objects/<model("parcel.parcel"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('parcel.object', {
#             'object': obj
#         })

