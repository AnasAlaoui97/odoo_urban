# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare



class ProductTemplate(models.Model):
    _inherit = "product.template"

    prod_code_P = fields.Char('Code article', index=True)


class ProductProduct(models.Model):
    _inherit = "product.product"

    prod_code_V = fields.Char('Code article', compute='_compute_product_code_product', index=True)

    @api.depends('product_tmpl_id.prod_code_P','product_template_attribute_value_ids')
    def _compute_product_code_product(self):
        for product in self:
            s = []
            p = '_'.join(map(str, product.product_template_attribute_value_ids.mapped('product_attribute_value_id.code_value')))
            s.append(product.product_tmpl_id.prod_code_P or '')
            s.append(p or '')
            # s += '%s_%s' % (str(product.code_values) or '', str(Prod.prod_code_P) or '')
            product.prod_code_V = '_'.join(s)


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    code_value = fields.Char('Code_Valeur')

