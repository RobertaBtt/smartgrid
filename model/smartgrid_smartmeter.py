# -*- coding: utf-8 -*-

from openerp import models, fields, api, _, SUPERUSER_ID
from ..api import SmartgridApi

from datetime import timedelta, date, datetime, time

import logging

_logger = logging.getLogger(__name__)


PHASES = [
    ('1', 'Single-phase'),
    ('3', 'Three-phase')
]

SMART_METER_TYPES = [('w', 'Withdrawal'),        # Prelievo
                     ('e', 'Exchange'),          # Scambio
                     ('p', 'Production'),        # Produzione
                     ('op', 'Only Production')  # Solo produzione
                     ]


class SmartMeter(models.Model):
    """
    Represents the Smart Meter of the Smart Grid
    """
    _name = "sg.smartmeter"

    name = fields.Char(string='Serial Number', index=True, readonly=False, required=True, size=256)
    model_number = fields.Integer(string='Model Number', required=True, default=0)
    heroltd_serial_number = fields.Char(string='Heroltd Serial Number', required=False)
    type = fields.Selection(SMART_METER_TYPES, string='Smart Meter Type', required=True)
    is_weather_station = fields.Boolean(string='Is Weather Station')
    latitude = fields.Char(string='Latitude', size=32)
    longitude = fields.Char(string='Longitude', size=32)
    description = fields.Text(string='Description')
    phases = fields.Selection(PHASES, string="Phases", required=True, default="1")
    zone_ids = fields.Many2many('sg.zone', string='SmartGrid Zone', required=True)

    # Offset group

    # Active Energy
    offset_active_IMP_r = fields.Float(string="Active Energy Import R")
    offset_active_IMP_s = fields.Float(string="Active Energy Import S")
    offset_active_IMP_t = fields.Float(string="Active Energy Import T")
    offset_active_IMP_sum = fields.Float(string="Active Energy Import Sum")

    # mono-phase
    offset_active_IMP = fields.Float(string="Active Energy Import")

    offset_active_EXP_r = fields.Float(string="Active Energy Export R")
    offset_active_EXP_s = fields.Float(string="Active Energy Export S")
    offset_active_EXP_t = fields.Float(string="Active Energy Export T")
    offset_active_EXP_sum = fields.Float(string="Active Energy Export Sum")

    # mono-phase
    offset_active_EXP = fields.Float(string="Active Energy Export")

    # Reactive Energy
    offset_reactive_IMP_r = fields.Float(string="Reactive Energy Import R")
    offset_reactive_IMP_s = fields.Float(string="Reactive Energy Import S")
    offset_reactive_IMP_t = fields.Float(string="Reactive Energy Import T")
    offset_reactive_IMP_sum = fields.Float(string="Reactive Energy Import Sum")

    # mono-phase
    offset_reactive_IMP = fields.Float(string="Reactive Energy Import")

    offset_reactive_EXP_r = fields.Float(string="Reactive Energy Export R")
    offset_reactive_EXP_s = fields.Float(string="Reactive Energy Export S")
    offset_reactive_EXP_t = fields.Float(string="Reactive Energy Export T")
    offset_reactive_EXP_sum = fields.Float(string="Reactive Energy Export Sum")

    offset_reactive_EXP = fields.Float(string="Reactive Energy Export")

    contract_id = fields.Many2one('ep.contract', "Contratto")

    _sql_constraints = [ ('name_uniq', 'unique(name)', 'Serial Number must be unique!'),]

    @api.model
    def get_smartmeters(self):

        smartgridApi  = SmartgridApi.SmartgridApi()

        user = self.env['res.users'].search([('id', '=', self._uid)])
        mono_fase_table = 'sg_21'
        tri_fase_table = 'sg_18'
        new_smartmeters = []
        smartmeters_mono = smartgridApi.getAllSmartmeters(self.env, user.id, mono_fase_table)
        for s in smartmeters_mono:
            sender_id = s[1]
            smartmeter = self.env['sg.smartmeter'].search([('name', '=', sender_id)])
            if smartmeter.id  is False:
                new = self.env['sg.smartmeter'].create({
                    'name': sender_id,
                    'type': 'w'
                })
                new_smartmeters.append(new.id)


        smartmeters_tri = smartgridApi.getAllSmartmeters(self.env, user.id, tri_fase_table)
        for s in smartmeters_tri:
            sender_id = s[1]
            smartmeter = self.env['sg.smartmeter'].search([('name', '=', sender_id)])
            if smartmeter.id is False:
                new = self.env['sg.smartmeter'].create({
                    'name': sender_id,
                    'type': 'w'
                })
                new_smartmeters.append(new.id)


        #For every smartmeter, add if the sender id does no exist
        return new_smartmeters


    def get_data_from_smartgrid_db(self, sender_id, data_da, data_a):
        new_smartmeters_data = []

        smartmeter = self.env['sg.smartmeter'].search([('name', '=', sender_id.name)])
        if smartmeter.phases == '1':
            table = 'sg_21'
        elif smartmeter.phases == '3':
            table = 'sg_18'

        smartgridApi  = SmartgridApi.SmartgridApi()

        user = self.env['res.users'].search([('id', '=', self._uid)])

        smartmeter_data = smartgridApi.getSmartmeterData(self.env, user.id, table, smartmeter.name, data_da, data_a)
        #esempio:
        # [u'3614BBBK4274', u'2017-03-01T14:36:42.689', 0.000375306990463287, 0.000344074]

        for sm_data in smartmeter_data:
            new = self.env['sg.data'].create({
                'sender_id': sm_data[0],
                'measurement_ts': sm_data[1],
                'energia_attiva_prelievo' : sm_data[2],
                'potenza_attiva':  sm_data[3] })

            new_smartmeters_data.append(new.id)
        return new_smartmeters_data

    def get_transmission_count_from_smartgrid_db(self, data_da, data_a):

        smartgridApi  = SmartgridApi.SmartgridApi()

        user = self.env['res.users'].search([('id', '=', self._uid)])
        mono_fase_table = 'sg_21'
        tri_fase_table = 'sg_18'
        new_smartmeters_data = []

        smartmeters_mono_count = smartgridApi.getTransmissionsCount(self.env, user.id, mono_fase_table, data_da, data_a)
        for s in smartmeters_mono_count:
            sender_id = s[0]
            count = s[1]
            smartmeter = self.env['sg.smartmeter'].search([('name', '=', sender_id)])
            if smartmeter.id is not False:
                new = self.env['sg.data'].create({
                'sender_id': sender_id,
                'count':  count })
                new_smartmeters_data.append(new.id)

        smartmeters_tri_count = smartgridApi.getTransmissionsCount(self.env, user.id, tri_fase_table, data_da, data_a)
        for s in smartmeters_tri_count:
            sender_id = s[0]
            count = s[1]
            smartmeter = self.env['sg.smartmeter'].search([('name', '=', sender_id)])
            if smartmeter.id is not False:
                new = self.env['sg.data'].create({
                'sender_id': sender_id,
                'count':  count })

                new_smartmeters_data.append(new.id)
        return new_smartmeters_data


    def get_last_transmission_from_smartgrid_db(self, sender_id):
        new_smartmeters_data = []

        smartmeter = self.env['sg.smartmeter'].search([('name', '=', sender_id.name)])
        if smartmeter.phases == '1':
            table = 'sg_21'
        elif smartmeter.phases == '3':
            table = 'sg_18'

        smartgridApi  = SmartgridApi.SmartgridApi()

        user = self.env['res.users'].search([('id', '=', self._uid)])

        smartmeter_data = smartgridApi.getLastTransmission(self.env, user.id, table, smartmeter.name)
        #esempio:
        # [u'3614BBBK4274', u'2017-03-01T14:36:42.689', 0.000375306990463287, 0.000344074]

        for sm_data in smartmeter_data:
            new = self.env['sg.data'].create({
                'sender_id': sm_data[0],
                'measurement_ts': sm_data[1],
                'energia_attiva_prelievo' : sm_data[2],
                'potenza_attiva':  sm_data[3] })

            new_smartmeters_data.append(new.id)
        return new_smartmeters_data



