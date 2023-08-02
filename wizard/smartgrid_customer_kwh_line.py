# -*- coding: utf-8 -*-


from openerp import fields, models, api, _, SUPERUSER_ID

import logging

_logger = logging.getLogger(__name__)


class CustomerKwhLine(models.TransientModel):
    """Smartgrid Customer kWh Line"""
    _name = "sg.customer.kwh.line.wizard"
    _order = "sequence asc"
    _rec_name = 'measure_time'

    measure_time = fields.Integer(string="Time of measure",
                                  required=True)
    kwh = fields.Float(string="kWh",digits=(6, 8),required=True)

    day = fields.Selection([('yesterday', 'kWh Yesterday'),('today', 'kWh Today')],string='Day', readonly=True, copy=False)
    sequence = fields.Integer(string="Seq.")
    wizard_id = fields.Many2one('sg.customer.kwh.wizard',  'Depends on', required=True, ondelete='cascade')

