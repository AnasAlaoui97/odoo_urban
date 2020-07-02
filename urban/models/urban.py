# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from psycopg2 import OperationalError, Error

from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

import logging

_logger = logging.getLogger(__name__)


# inherit product for code
class ProductTemplate(models.Model):
    _inherit = "product.template"

    default_code = fields.Char(
        'Code Article', compute='_compute_default_code',
        inverse='_set_default_code', store=True)


 # consommation
class StockMove(models.Model):
    _inherit = "stock.move"

    value = fields.Monetary('Value', compute='_compute_value', store=True)
    currency_id = fields.Many2one(related='product_id.currency_id')

    qty_sale = fields.Float('Q.vendue', compute='_compute_Qty_sale', store=True)
    qty_prch = fields.Float('Q.achetée', compute='_compute_Qty_prch', store=True)
    qty_rebus = fields.Float('Q.En Rebus', compute='_compute_Qty_rebus', store=True)
    qty_imput = fields.Float('Imputation', compute='_compute_Qty_transit_prod', store=True)
    qty_retour = fields.Float('Retour.Imputation', compute='_compute_Qty_transit_stock', store=True)
    qty_consom = fields.Float('C.interne', compute='_compute_Qty_consommee', store=True)
    qty_prod = fields.Float('Q.produite', compute='_compute_Qty_prod', store=True)
    qty_consom_externe = fields.Float('C.Externe', compute='_compute_Qty_consom_externe', store=True)

    @api.depends('product_id', 'currency_id')
    def _compute_value(self):
        for mv in self:
            mv.value = mv.quantity_done * mv.product_id.standard_price

    @api.depends('quantity_done', 'location_id')
    def _compute_Qty_prch(self):
        for mv in self:
            if mv.location_id.usage == 'supplier':
                mv.qty_prch = mv.quantity_done
            else:
                mv.qty_prch = 0.0

    @api.depends('quantity_done', 'location_dest_id')
    def _compute_Qty_sale(self):
        for mv in self:
            if mv.location_dest_id.usage == 'customer':
                mv.qty_sale = mv.quantity_done
            else:
                mv.qty_sale = 0.0

    @api.depends('quantity_done', 'location_dest_id', 'location_id')
    def _compute_Qty_transit_prod(self):
        for mv in self:
            if mv.location_id.usage == 'internal' and mv.location_dest_id.usage == 'transit':
                mv.qty_imput = mv.quantity_done
            else:
                mv.qty_imput = 0.0

    @api.depends('quantity_done', 'location_id', 'location_dest_id')
    def _compute_Qty_transit_stock(self):
        for mv in self:
            if mv.location_id.usage == 'transit' and mv.location_dest_id.usage == 'internal':
                mv.qty_retour = mv.quantity_done
            else:
                mv.qty_retour = 0.0

    @api.depends('quantity_done', 'location_id', 'location_dest_id')
    def _compute_Qty_prod(self):
        for mv in self:
            if mv.location_id.usage == 'production' and mv.location_dest_id.usage == 'internal':
                mv.qty_prod = mv.quantity_done
            else:
                mv.qty_prod = 0.0

    @api.depends('quantity_done', 'location_id', 'location_dest_id')
    def _compute_Qty_consommee(self):
        for mv in self:
            if mv.location_id.usage == 'transit' and mv.location_dest_id.usage == 'production':
                mv.qty_consom = mv.quantity_done
            else:
                mv.qty_consom = 0.0

    @api.depends('quantity_done', 'location_dest_id')
    def _compute_Qty_rebus(self):
        for mv in self:
            if mv.location_dest_id.usage == 'inventory':
                mv.qty_rebus = mv.quantity_done
            else:
                mv.qty_rebus = 0.0


    # @api.depends('qty_rebus','qty_imput', 'qty_retour', 'qty_prch')
    def _compute_Qty_consom_externe(self):
        for mv in self:
            stock = float(self.env['stock.quant']._get_stock_prod)
            mv.qty_consom_externe = ( mv.qty_rebus + mv.qty_imput ) - ( stock + mv.qty_retour )



# etat de stock
class StockQuant(models.Model):
    _inherit = "stock.quant"

    qty_stock_prod = fields.Float('En S.Production', compute='_compute_qty_stock_prod', store=True)
    qty_stock_mz = fields.Float('En S.Magasin', compute='_compute_qty_stock_mz', store=True)

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

    def _get_stock_prod(self):
        for mv in self:
            return mv.qty_stock_prod