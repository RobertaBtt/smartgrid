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

from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class SgZoneAttachment(models.Model):
    _name = 'ir.attachment'
    _inherit = 'ir.attachment'
    
    smartgrid_type = fields.Selection([
                ('alarms', 'Active Alarms'),
                ('forecasts', 'Forecast Next 15 Days'),
                ('power_customers', 'Power for All Customers'),
                ('power_prosumer', 'Power for All Prosumers'),
                ('power_companies', 'Power for All Companies'),
            ], required=True, string='Smart Grid Type')
    zone_id = fields.Many2one('sg.zone', required=True, string='SmartGrid Zone')
    res_model = fields.Char(string='Resource Model', readonly=True, help="The database object this attachment will be attached to")
    
    @api.onchange('zone_id','smartgrid_type')
    def _onchange_zone_id_smartgrid_type(self):
        if self.zone_id and self.smartgrid_type:
            self.res_id = self.zone_id.id
            self.store_fname = (self.zone_id.name + '/' + self.smartgrid_type + '/' +
                self.zone_id.name + '_' + self.smartgrid_type + '_curr.csv')
    
