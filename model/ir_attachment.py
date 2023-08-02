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
from openerp.tools.translate import _
from openerp.osv import fields,osv
from openerp import SUPERUSER_ID
import urlparse
import logging

_logger = logging.getLogger(__name__)

class IrAttachment(osv.Model):
    _inherit = "ir.attachment"

    def _file_write_sg_s3(self, cr, uid, fname, location, value):
        loc_parse = urlparse.urlparse(location)
        if loc_parse.scheme == 'amazons3':
            s3_bucket = self._s3_connection_and_bucket(cr, location)
            bin_value = value.decode('base64')

            s3_key = s3_bucket.get_key(fname)
            if not s3_key:
                s3_key = s3_bucket.new_key(fname)

            s3_key.set_contents_from_string(bin_value)
        else:
            fname = super(IrAttachment, self)._file_write(
                cr, uid, value)

        return fname

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        if not value:
            return True
        if context is None:
            context = {}
        location = self._storage(cr, uid, context)
        file_size = len(value.decode('base64'))
        attach = self.browse(cr, uid, id, context=context)
        fname_to_delete = attach.store_fname
        if location != 'db':
            if attach.amazons3:
                if attach.zone_id and attach.smartgrid_type:
                    fname = self._file_write_sg_s3(
                        cr,
                        uid,
                        attach.zone_id.name + '/' +
                        attach.smartgrid_type + '/' +
                        attach.zone_id.name + '_' +
                        attach.smartgrid_type +
                        '_curr.csv',
                        location,
                        value
                    )
                else:
                    fname = 'filestore/' + self._file_write_s3(cr,
                                                               uid,
                                                               location,
                                                               value)
            else:
                fname = super(IrAttachment, self)._file_write(cr,
                                                              uid,
                                                              value
                                                              )
            super(IrAttachment, self).write(cr, SUPERUSER_ID, [id],
                                            {'store_fname': fname,
                                             'file_size': file_size,
                                             'db_datas': False},
                                            context=context
                                            )
        else:
            super(IrAttachment, self).write(cr, SUPERUSER_ID, [id],
                                            {'db_datas': value,
                                             'file_size': file_size,
                                             'store_fname': False},
                                            context=context)

        # After de-referencing the file in the database, check whether we need
        # to garbage-collect it on the filesystem
        if fname_to_delete:
                if attach.amazons3:
                    self._file_delete_s3(cr, uid, location, fname_to_delete)
                else:
                    self._file_delete(cr, uid, fname_to_delete)
        return True

    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        location = self._storage(cr, uid, context)
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if attach.store_fname:
                if attach.amazons3:
                    result[attach.id] = self._file_read_s3(cr,
                                                           uid,
                                                           location,
                                                           attach.store_fname,
                                                           bin_size
                                                           )
                else:
                    result[attach.id] = self._file_read(cr,
                                                        uid,
                                                        attach.store_fname,
                                                        bin_size
                                                        )
            else:
                result[attach.id] = attach.db_datas
        return result

    _columns = {
        'smartgrid_type': fields.selection(
            [
                ('alarms', 'Active Alarms'),
                ('forecasts', 'Forecast Next 15 Days'),
                ('power_customers', 'Power for All Customers'),
                ('power_prosumer', 'Power for All Prosumers'),
                ('power_companies', 'Power for All Companies'),
            ],
            string='Smart Grid Type'),
        'zone_id': fields.many2one('sg.zone', string='SmartGrid Zone'),
        'datas': fields.function(_data_get,
                                 fnct_inv=_data_set,
                                 string='File Content',
                                 type="binary",
                                 nodrop=True),
    }

    def get_s3_file(self, cr, uid, ids, context=None):
        if ids and ids[0]:
            return {
                'name': _('Download S3 File'),
                'type': 'ir.actions.act_url',
                'url': '/web/binary/saveas?filename_field=name&'
                'model=ir.attachment&field=datas&id=%s' % str(ids[0])
            }

    def create(self, cr, uid, vals, context=None):
        """
            Force sg_zone permissions
        """
        if context is None:
            context = {}
        if 'zone_id' in vals and 'res_id' not in vals:
            vals['res_model'] = 'sg.zone'
            vals['res_id'] = vals['zone_id']
        _logger.info('create attach')
        return super(IrAttachment, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        """
            This method avoids manual changing of an S3 zone_id attachment
            It also avoids indexing of wrong data in database
        """
        if context is None:
            context = {}
        for attachment in self.browse(cr, uid, ids, context):
            if attachment.zone_id and attachment.smartgrid_type:
                raise osv.except_osv(_('WriteError'),
                                     _('This file is synchronized with S3!')
                                     )
        return super(IrAttachment, self).write(cr, uid, ids, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        """
            This method avoids manual deletion of an S3 zone_id attachment
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        for attachment in self.browse(cr, uid, ids, context=context):
            if attachment.zone_id and attachment.smartgrid_type \
                    and not uid == SUPERUSER_ID:
                raise osv.except_osv(_('DeleteError'),
                                     _('This file is synchronized with S3!')
                                     )
        return super(IrAttachment, self).unlink(cr, uid, ids, context)
