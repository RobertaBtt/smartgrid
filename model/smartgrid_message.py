# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Innoviu srl (<http://www.innoviu.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
from openerp.tools import (
    DEFAULT_SERVER_DATETIME_FORMAT as DSDF)
import requests
import dateutil.parser
import logging
import time

class SmartGridMessage(models.Model):
    _name = "sg.message"
    _order = "name"

    name = fields.Char(
        string='Subject',
        required=True,
        readonly=False)
    creation_date = fields.Datetime(
        string='Creation Date',
        required=False,
        readonly=True
        )
    message = fields.Html(
        string='Message',
        required=True,
        readonly=False)
    to_all = fields.Boolean('To all Customers',
        default=True)
    zone_id = fields.Many2one(
        'sg.zone',
        'SmartGrid Zone',
        required=True,
        readonly=False)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        change_default=True,
        domain=[('customer', '=', True)],
        required=False,
        readonly=False,
        track_visibility='always')

    @api.multi
    def onchange_to_all(self, to_all):
        if to_all:
            return {'value': {
                'partner_id': False,
            }}

    @api.model
    def create(self, vals):
        vals.update({'creation_date': time.strftime(DSDF)})
        return super(SmartGridMessage, self).create(vals)


