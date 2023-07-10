from odoo import fields, models, api


class EmployeeProfessionalCertificate(models.Model):
    _name = "hr.employee.professional_certificate"
    _description = "Professional Certificate"

    qualification = fields.Char(string="Qualification")
    badge_training = fields.Selection(
        [
            ("passed", "Passed"),
            ("not_passed", "Not Passed"),
        ],
        "Badge Training",
        default="not_passed",
    )
    date_passed = fields.Date(string="Pass date")
    tco_certification = fields.Selection(
        [
            ("passed", "Passed"),
            ("not_passed", "Not Passed"),
        ],
        "Certificates",
        default="not_passed",
    )
    certificate_scan = fields.Binary(string="Certificate scan")
    employee_id = fields.Many2one("hr.employee", "Employee")


class EmployeeEducationInfo(models.Model):
    _inherit = "hr.employee"

    language_ids = fields.One2many(
        comodel_name="hr.employee.language",
        inverse_name="employee_id"
    )
    professional_certification_ids = fields.One2many(
        comodel_name="hr.employee.professional_certificate", 
        inverse_name="employee_id"
    )
    computer_skills = fields.Char(
        string="Computer skills"
    )
    language_and_level = fields.Char(
        string="Language and level", 
        compute="_compute_language_and_level"
    )

    @api.depends("language_ids")
    def _compute_language_and_level(self):
        languages, levels = [], []
        res = []
        for record in self:
            for line in record.language_ids:
                for language in line.language:
                    languages.append(language.name)
                for level in line.language_level:
                    levels.append(level.name)
            for language, level in zip(languages, levels):
                string = f'{language} ({level})'
                res.append(string)
            record.language_and_level = ", ".join(res)