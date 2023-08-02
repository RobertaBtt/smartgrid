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

import logging

_logger = logging.getLogger(__name__)



class SmartGridUrl(models.Model):
     _name = "sg.url"
     _order = "name"

     name = fields.Char(
         string='Name',
         required=True,
         readonly=False)

     link = fields.Char(
         string='Url Link',
         required=True,
         readonly=False)

     zone_id = fields.Many2one(
         'sg.zone',
         'SmartGrid Zone',
         required=True,
         readonly=False)

     @api.multi
     def open_url(self):
         if len(self) and self[0].link:
             return {
                 'target': 'new',
                 'type': 'ir.actions.act_url',
                 'url': self[0].link
             }
