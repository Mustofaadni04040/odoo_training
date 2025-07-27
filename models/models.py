# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from random import randint
from datetime import timedelta, datetime, date


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
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Training Kursus'

    ref = fields.Char(string="Referensi", readonly=True, default="/")

    @api.model_create_multi # memberikan nomor sequence ketika record pertama kali dibuka dengan menekan tombol save/pindah fokus window maka method create dijalankan
    def create(self, vals_list):
        for vals in vals_list:
            vals["ref"] = self.env["ir.sequence"].next_by_code("training.course")
        return super().create(vals_list)

    def copy(self, default=None):
        default = dict(default or {})
        name = self.name
        x = 1
        while self.search_count([("name", "=", f"{name} ({x})")]):
            x += 1
        default.update(name=f"{name} ({x})")
        return super().copy(default)

    def get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Judul', required=True, tracking=True)
    description = fields.Text(string='Keterangan', tracking=True)
    user_id = fields.Many2one("res.users", string="Penanggung Jawab", tracking=True)
    session_line = fields.One2many("training.session", "course_id", string="Sesi", tracking=True)
    product_ids = fields.Many2many("product.product", "course_product_rel", "course_id", "product_id", string="Cindera Mata", tracking=True)
    level = fields.Selection([("basic", "Dasar"), ("advanced", "Lanjutan")], string="Tingkatan", default="basic")
    color = fields.Integer("Warna", default=get_default_color)
    email = fields.Char(string="Email", related="user_id.login")

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

    @api.depends("start_date", "duration")
    def get_end_date(self):
        for sesi in self:
            if not sesi.start_date:
                sesi.end_date = sesi.start_date
                continue

            start = fields.Date.from_string(sesi.start_date)
            sesi.end_date = start + timedelta(days=sesi.duration)

    def set_end_date(self):
        for sesi in self:
            if not (sesi.start_date and sesi.end_date):
                continue

            start_date = fields.Datetime.from_string(sesi.start_date)
            end_date = fields.Datetime.from_string(sesi.end_date)
            sesi.duration = (end_date - start_date).days + 1

    course_id = fields.Many2one("training.course", string="Judul Kursus", required=True, ondelete="cascade")
    name = fields.Char(string="Nama", required=True)
    start_date = fields.Date(string="Tanggal", default=fields.Date.context_today)
    duration= fields.Float(string="Durasi", help="Jumlah Hari Training", default=3)
    seats = fields.Integer(string="Kursi", help="Jumlah Kuota Kursi", default=10)
    partner_id = fields.Many2one("res.partner", string="Instruktur", domain=["|", ("instructor", "=", True), ("category_id.name", "ilike", "Pengajar")], default=default_partner_id)
    attendee_ids = fields.Many2many("training.attendee", "session_attendee_rel", "session_id", "attendee_id", "Peserta")
    taken_seats = fields.Float(string="Kursi Terisi", compute="compute_taken_seats")
    end_date = fields.Date(string="Tanggal Selesai", compute="get_end_date", inverse="set_end_date", store=True)
    attendees_count = fields.Integer(string="Jumlah Peserta", compute="get_attendees_count", store=True)

    @api.depends("attendee_ids")
    def get_attendees_count(self):
        for sesi in self:
            sesi.attendees_count = len(sesi.attendee_ids)

    @api.constrains("seats", "attendee_ids")
    def check_seats_and_attendees(self):
        for r in self:
            if r.seats < len(r.attendee_ids):
                raise ValidationError("Jumlah peserta melebihi kuota yang disediakan")
            
    @api.onchange("duration")
    def verify_valid_duration(self):
        if self.duration <= 0:
            self.duration = 1 # field ototmatis terupdate ke 1 jika diisi 0 atau negatif
            return {"warning": {"title": "Perhatian", "message": "Durasi Hari Training Tidak Boleh 0 atau Negatif"}}

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