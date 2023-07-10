from odoo import models, fields


class EmployeeShiftInfo(models.Model):
    _inherit = "hr.employee"

    shift_date_from = fields.Date(
        string="Shift start date"
    )
    shift_date_until = fields.Date(
        string="Shift end date"
    )
    work_arrival_time = fields.Date(
        string="Arrived at work"
    )
    work_left_time = fields.Date(
        string="Left from work"
    )