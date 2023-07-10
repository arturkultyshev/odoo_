from odoo import models, fields


class EmployeeAdditionalInfo(models.Model):
    _inherit = "hr.employee"

    # Additional info
    medical_examination_date = fields.Date(
        string="Date of medical examination"
    )
    show_information = fields.Boolean()
    disability_group = fields.Selection(
        selection=[
            ("first", "First"), 
            ("second", "Second"),
            ("third", "Third")
        ], 
        string="Disability Group",
    )
    disability_description = fields.Char(
        string="Disability description",
    )
    reference_series = fields.Char(
        string="Reference Series"
    )
    series_number = fields.Char(
        string="Number Series"
    )
    issue_date = fields.Date(
        string="Issue Date"
    )
    validity_period = fields.Date(
        string="Certificate Validity Period"
    )
    validity_begin_date = fields.Date(
        string="Valid from"
    )
    no_pension_right = fields.Selection(
        selection=[
            ("yes", "Yes"), 
            ("no", "No")
        ],
        string="No right for pension"
    )
    no_social_insurance = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No")
        ], 
        string="No social insurance"
    )
    no_social_medical_insurance = fields.Selection(
        selection=[
            ("yes", "Yes"),
              ("no", "No")
            ], 
        string="No social medical insurance"
    )
    no_foreign_resident = fields.Selection(
        selection=[
            ("yes", "Yes"),
            ("no", "No")
        ], 
        string="Not a foreign resident"
    )