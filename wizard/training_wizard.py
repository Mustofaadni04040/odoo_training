from odoo import api, fields, models

class TrainingWizard(models.TransientModel):
    _name = "training.wizard"
    _description = "Training Wizard"

    def _default_sesi(self):
        return self.env["training.session"].browse(self._context.get("active_ids"))
    
    session_id = fields.Many2one("training.session", string="Sesi", default=_default_sesi)
    attendee_ids = fields.Many2many("training.attendee", string="Peserta")

    def tambah_peserta(self):
        self.session_id.attendee_ids |= self.attendee_ids