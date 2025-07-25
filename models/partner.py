from odoo import api, fields, models

class Partner(models.Model):
    _inherit = "res.partner"

    instructor = fields.Boolean(string="Instruktur")
    session_line = fields.One2many("training.session", "partner_id", string="Daftar Mengajar Sesi", readonly=True)