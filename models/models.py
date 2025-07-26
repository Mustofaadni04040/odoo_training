# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


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

    ref = fields.Char(string="Referensi", readonly=True, default="/")

    @api.model_create_multi # memberikan nomor sequence ketika record pertama kali dibuka dengan menekan tombol save/pindah fokus window maka method create dijalankan
    def create(self, vals_list):
        for vals in vals_list:
            vals["ref"] = self.env["ir.sequence"].next_by_code("training.course")
        return super().create(vals_list)

    name = fields.Char(string='Judul', required=True)
    description = fields.Text(string='Keterangan')
    user_id = fields.Many2one("res.users", string="Penanggung Jawab")
    session_line = fields.One2many("training.session", "course_id", string="Sesi")
    product_ids = fields.Many2many("product.product", "course_product_rel", "course_id", "product_id", string="Cindera Mata")

    _sql_constraints = [
        ("nama_kursus_unik", "UNIQUE(name)", "Judul kursus harus unik"),
        ("nama_keterangan_cek", "CHECK(name != description)", "Judul kursus dan keterangan tidak boleh sama")
    ]

class TrainingSession(models.Model):
    _name = "training.session"
    _description = "Training Sesi"

    def default_partner_id(self):
        instruktur = self.env["res.partner"].search(["|", ("instructor", "=", True), ("category_id.name", "ilike", "Pengajar")], limit=1)
        return instruktur

    @api.depends("seats", "attendee_ids") # methon akan selalu dijalankan setiap ada perubahan di field seats atau attendee_ids
    def compute_taken_seats(self):
        for sesi in self:
            sesi.taken_seats = 0
            if sesi.seats and sesi.attendee_ids:
                sesi.taken_seats = 100 * len(sesi.attendee_ids) / sesi.seats

    course_id = fields.Many2one("training.course", string="Judul Kursus", required=True, ondelete="cascade")
    name = fields.Char(string="Nama", required=True)
    start_date = fields.Date(string="Tanggal", default=fields.Date.context_today)
    duration= fields.Float(string="Durasi", help="Jumlah Hari Training", default=3)
    seats = fields.Integer(string="Kursi", help="Jumlah Kuota Kursi", default=10)
    partner_id = fields.Many2one("res.partner", string="Instruktur", domain=["|", ("instructor", "=", True), ("category_id.name", "ilike", "Pengajar")], default=default_partner_id)
    attendee_ids = fields.Many2many("training.attendee", "session_attendee_rel", "session_id", "attendee_id", "Peserta")
    taken_seats = fields.Float(string="Kursi Terisi", compute="compute_taken_seats")

    @api.constrains("seats", "attendee_ids")
    def check_seats_and_attendees(self):
        for r in self:
            if r.seats < len(r.attendee_ids):
                raise ValidationError("Jumlah peserta melebihi kuota yang disediakan")

class TrainingAttendee(models.Model):
    _name = "training.attendee"
    _description = "Training Peserta"
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one("res.partner", "Partner", required=True, ondelete="cascade")
    name = fields.Char(related="partner_id.name", inherited=True, readonly=False)
    sex = fields.Selection([("male", "Pria"), ("female", "Wanita")], string="Kelamin", required=True, help="Jenis Kelamin")
    marital = fields.Selection([
        ("single", "Belum Menikah"),
        ("married", "Menikah"),
        ("divorced", "Cerai")], 
        string="Pernikahan", help="Status Pernikahan")
    session_ids = fields.Many2many("training.session", "session_attendee_rel", "attendee_id", "session_id", "Sesi")