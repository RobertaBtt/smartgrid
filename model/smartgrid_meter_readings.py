# -*- coding: utf-8 -*-


from openerp import models, fields, api, _, SUPERUSER_ID
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
from openerp.tools import (    DEFAULT_SERVER_DATETIME_FORMAT as DSDF)
from ..api import SmartgridApi
import logging

_logger = logging.getLogger(__name__)




class SmartgridMeterReadings(models.Model):

    _name = "sg.meter_readings"

    measurement_ts = fields.Char(string="Measurement_ts")
    sender_id = fields.Char(string="Sender_id")
    energia_attiva_prelievo = fields.Char(string="Lettura")
    contract_id = fields.Many2one('ep.contract', "Contratto")
    partner_id = fields.Many2one('res.partner', "Cliente")



    @api.model
    def _update(self):
        """ Richiesta generica get data per tabelle sg_21 monofase o sg_18 trifase"""
        #per ogni contratto con prepagata e smartmeter, aggiorna i dati, scrivi nella tabella delle letture
        contracts_to_update = self.env['ep.contract'].search([('abilitazione_prepagata', '=', True)])
        for contract in contracts_to_update:
            rel_smartmeter = contract.smartmeter_contract_ids
            for smartmeter in rel_smartmeter:
                if smartmeter.smartmeter_id.type == 'w':
                    values = self.get_meter_data(smartmeter.smartmeter_id)
                    self.addValue(values, smartmeter.smartmeter_id)

    def addValue(self, values, objSenderId):

        vals = {}

        if 'data' in values and len(values['data']) > 0:
            vals['sender_id'] = objSenderId.name
            if 'measurement_ts' in values['data']:
                vals['measurement_ts'] = values['data']['measurement_ts']
            if 'valore' in values['data']:
                vals['energia_attiva_prelievo'] = values['data']['valore']

            vals['contract_id'] = objSenderId.contract_id.id
            vals['partner_id'] = objSenderId.contract_id.partner_id.id

            dataObject = self.env['sg.meter_readings'].search([
                ('measurement_ts', '=', vals['measurement_ts']),
                ('sender_id', '=', vals['sender_id']),
                ('energia_attiva_prelievo', '=', vals['energia_attiva_prelievo'])])

            if not dataObject:
                #sto aggiungendo una lettura, elimino la precedente ?
                #voglio lasciare solo le ultime due di un contratto ?
                #altrimenti diventano troppe

                return super(SmartgridMeterReadings, self).create(vals)
        else:
            print "Add Value : Something strange happened creating smartgrid data"
            return



    def get_meter_data(self, smartmeterObject):
        """
        :return: dictionary with measurements_ts, sender_id, value
        """

        smartgridApi  = SmartgridApi.SmartgridApi()

        user = self.env['res.users'].search([('id', '=', self._uid)])
        values = smartgridApi.getUltimaLetturaSmartmeter(self.env, user.id, smartmeterObject)

        _logger.info(values)

        return values