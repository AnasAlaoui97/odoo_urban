# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from psycopg2 import OperationalError, Error

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

import logging

_logger = logging.getLogger(__name__)



 
class StockMove(models.Model):
    _inherit = "stock.move"

    value = fields.Monetary('Value', compute='_compute_value', store=True)
    currency_id = fields.Many2one(related='product_id.currency_id')


    qty_sale = fields.Float('Quantité vendue' , compute='_compute_Qty_sale', store =True)
    qty_prch = fields.Float('Quantité achetée' , compute='_compute_Qty_prch', store =True)
    qty_imput = fields.Float('Imputation' , compute='_compute_Qty_transit_prod', store =True)
    qty_retour = fields.Float('Imputation Retour' , compute='_compute_Qty_transit_stock', store =True)
    qty_conso_ext = fields.Float('Quantité consommée (ext)' , compute='_compute_Qty_consu_ext', store =True)
    qty_conso_int = fields.Float('Quantité consommée (int)' , compute='_compute_Qty_consu_int', store =True)


    @api.depends( 'product_id', 'currency_id')
    def _compute_value(self):
        for mv in self:
             mv.value = mv.quantity_done * mv.product_id.standard_price
    
    @api.depends('quantity_done','location_id')
    def _compute_Qty_prch(self):
        for mv in self: 
            if mv.location_id.usage == 'supplier':
                mv.qty_prch =  mv.quantity_done
            else:
                mv.qty_prch = 0.0

    @api.depends('quantity_done','location_dest_id')
    def _compute_Qty_sale(self):
        for mv in self:
            if mv.location_dest_id.usage == 'customer':
                mv.qty_sale = mv.quantity_done
            else:
                mv.qty_sale= 0.0

    @api.depends('quantity_done', 'location_dest_id')
    def _compute_Qty_transit_prod(self):
        for mv in self: 
            if mv.location_dest_id.usage == 'transit' :
                mv.qty_imput =  mv.quantity_done
            else:
                mv.qty_imput = 0.0
    
    @api.depends('quantity_done','location_id')
    def _compute_Qty_transit_stock(self):
        for mv in self: 
            if mv.location_id.usage == 'transit' :
                mv.qty_retour =  mv.quantity_done
            else:
                mv.qty_retour = 0.0

    @api.depends('quantity_done','location_id')
    def _compute_Qty_consu_ext(self):
        for mv in self: 
            if mv.location_id.usage == 'production' :
                mv.qty_conso_ext =  mv.quantity_done
            else:
                mv.qty_conso_ext = 0.0

    @api.depends('quantity_done','location_dest_id', 'qty_imput', 'qty_retour', 'product_uom_qty')
    def _compute_Qty_consu_int(self):
        for mv in self: 
            if mv.location_dest_id.usage == 'production' :
                mv.qty_conso_int =  mv.qty_imput - mv.qty_retour - (mv.product_uom_qty - mv.quantity_done)
            else:
                mv.qty_conso_int =  mv.qty_imput - mv.qty_retour


class StockQuant(models.Model):
    _inherit = "stock.quant"

    qty_stock_prod = fields.Float('En S.Production' , compute='_compute_qty_stock_prod', store =True)
    qty_stock_mz = fields.Float('En S.Magasin' , compute='_compute_qty_stock_mz', store =True)
    qty_ach = fields.Float('Acheté' , compute='_compute_qty_stock_mz', store =True)
    qty_vendu = fields.Float('Vendu' , compute='_compute_qty_stock_mz', store =True)

    @api.depends('quantity', 'location_id')
    def _compute_qty_stock_prod(self):
        for mv in self:
            if mv.location_id.usage == 'transit':
                mv.qty_stock_prod = mv.quantity
            else:
                mv.qty_stock_prod = 0.0

    @api.depends('quantity', 'location_id')
    def _compute_qty_stock_mz(self):
        for mv in self:
            if mv.location_id.usage == 'internal':
                mv.qty_stock_mz = mv.quantity
            else:
                mv.qty_stock_mz = 0.0




