# -*- coding: utf-8 -*-


from openerp.tools.translate import _
from openerp import models, fields, api, SUPERUSER_ID


class ResPartner(models.Model):
    _inherit = 'res.partner'

    has_smartmeter = fields.Boolean(String="Has smartmeter", compute="_has_smartmeter", search='_search_has_smartmeter' )

    @api.one
    def _has_smartmeter(self):
        hasSmartmeter = False

        if not isinstance(self.id, models.NewId):

            contracts = self.contract_ids
            for contract in contracts:
                if contract.has_smartmeter:
                    self.has_smartmeter = True
                    return hasSmartmeter

        else: self.has_smartmeter = hasSmartmeter

        return hasSmartmeter


    @api.one
    def _search_has_smartmeter(self):
        rows = self.env('res.partner').search([('has_smartmeter', '=', True)])
        # rows = []
        # for result in results
        #     rows.append(result)
        res =  [('ids', 'in', rows)]
        return res
