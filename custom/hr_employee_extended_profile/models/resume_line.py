from dateutil.relativedelta import relativedelta
from odoo import fields, models, api


class ResumeLineExtended(models.Model):
    _inherit = "hr.resume.line"

    name = fields.Char(
        required=False,
        store=True
    )
    date_start = fields.Date(
        required=False, 
        store=True
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee", 
        string="Employee"
    )
    company_name = fields.Char(
        string="Company", 
        compute="_compute_company_name", 
        store=True
    )
    job_position = fields.Char(
        string="Job position",
        compute="_compute_job_position",
        readonly=False,
        store=True,
    )
    job_responsibilities = fields.Text(
        string="Job responsibilities", 
        store=True
    )
    total_year = fields.Integer(
        string="Year", 
        compute="_compute_experience", 
        store=True
    )
    total_month = fields.Integer(
        string="Month", 
        compute="_compute_experience", 
        store=True
    )
    total_day = fields.Integer(
        string="Day", 
        compute="_compute_experience", 
        store=True
    )
    dismissal_reason = fields.Selection(
        selection=[
            ('reason_1',
             'p.2 of Art.51 of the Labor Code of the Republic of Kazakhstan Expiration of the term of the '
             'employment contract.'),
            ('reason_2', 'p.1 of Art.49 of the Labor Code of the Republic of Kazakhstan (by agreement of the parties)'),
            ('reason_3',
             'p.1 of Art.49, p.3 of Art.50 of the Labor Code of the Republic of Kazakhstan (by agreement of the '
             'parties)'),
        ], string="Reason for dismissal"
    )
    # Education
    certificate = fields.Selection(
        [
            ("incomplete_higher", "Incomplete higher education"),
            ("graduate", "Graduate"),
            ("bachelor", "Bachelor"),
            ("master", "Master"),
            ("doctor", "Doctor"),
            ("sve", "Secondary vocational education"),
            ("ste", "Secondary technical education"),
            ("other", "Other"),
        ],
        "Certificate Level",
        default="other",
        store=True,
    )
    study_field = fields.Char(
        "Field of Study", 
        store=True
    )
    study_school = fields.Char(
        "School", 
        store=True
    )
    speciality = fields.Char(
        "Speciality", 
        store=True
    )
    profession = fields.Char(
        "Profession", 
        store=True
    )
    diploma_number = fields.Char(
        "Diploma number", 
        store=True
    )
    diploma_scan = fields.Binary(
        string="Diploma scan", 
        store=True
    )
    study_form = fields.Selection(
        selection=[
            ("full_time", "Full-time"),
            ("correspondence", "Correspondence"),
            ("distance", "Distance"),
            ("evening", "Evening"),
            ("external", "External"),
        ],
        string="Form of study",
        store=True,
    )
    graduation_year = fields.Integer(
        string="Graduation Date", 
        store=True
    )
    type_name = fields.Char(
        compute="_compute_type_name", 
        store=True
    )

    @api.depends("name")
    def _compute_company_name(self):
        for record in self:
            record.company_name = record.name

    @api.depends("description")
    def _compute_job_position(self):
        for record in self:
            record.job_position = record.description

    @api.depends("date_start", "date_end")
    def _compute_experience(self):
        for line in self:
            total_year, total_month, total_day = 0, 0, 0
            if line.date_start and line.date_end:
                total_year += relativedelta(
                    fields.Date.from_string(line.date_end),
                    fields.Date.from_string(line.date_start),
                ).years
                total_month += relativedelta(
                    fields.Date.from_string(line.date_end),
                    fields.Date.from_string(line.date_start),
                ).months
                total_day += relativedelta(
                    fields.Date.from_string(line.date_end),
                    fields.Date.from_string(line.date_start),
                ).days
            line.total_year, line.total_month, line.total_day = (
                total_year,
                total_month,
                total_day,
            )

    @api.depends("line_type_id")
    def _compute_type_name(self):
        for line in self:
            line.type_name = line.line_type_id.name


class ResumeLineTypeExtended(models.Model):
    _inherit = "hr.resume.line.type"
    name = fields.Char(translate=True)


class HrSkillTypeExtended(models.Model):
    _inherit = "hr.skill.type"
    name = fields.Char(translate=True)
