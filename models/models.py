# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class training_odoo(models.Model):
#     _name = 'training_odoo.training_odoo'
#     _description = 'training_odoo.training_odoo'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

class TrainingCourse(models.Model):
    _name = 'training.course'
    _description = 'Training Course'

    name = fields.Char(string='Judul', required=True)
    description = fields.Text(string='Keterangan')