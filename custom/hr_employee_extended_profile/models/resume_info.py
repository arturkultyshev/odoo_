from odoo import models, fields, api
from datetime import date, datetime

class EmployeeT2Card(models.Model):
    _inherit = "hr.employee"

    current_date = str(date.today().strftime("%d-%m-%Y"))
    document_date = fields.Char(
        default=current_date, 
        string="Document Filling date"
    )
    experience_resume_line_ids = fields.One2many(
        "hr.resume.line", 
        compute="_compute_experience_fields"
    )
    education_ids = fields.One2many(
        comodel_name="hr.resume.line",
        inverse_name="employee_id",
        compute="_compute_education_fields",
    )
    # Fields for education display in template
    certificate_level = fields.Char(
        compute="_compute_certificate", 
        store=True
    )
    school_and_graduation_year = fields.Char(
        compute="_compute_school_and_graduation_year", 
        store=True
    )
    study_forms = fields.Char(
        compute="_compute_study_forms", 
        store=True
    )
    specialities = fields.Char(
        compute="_compute_specialities", 
        store=True
    )
    professions = fields.Char(
        compute="_compute_professions", 
        store=True
    )
    diploma_number = fields.Char(
        compute="_compute_diploma_number", 
        store=True
    )
    diploma_number_date = fields.Char(
        compute="_compute_diploma_number_date", 
        store=True
    )
    total_experience = fields.Char(
        string="Total Experience",
        compute='_compute_work_experience',
        store=True,
        default='0'
    )
    continuous_experience = fields.Char(
        string="Continuous experience",
        compute='_compute_work_experience',
        store=True,
        default='0'
    )

    @api.depends("experience_resume_line_ids.date_start", "experience_resume_line_ids.date_end")
    def _compute_work_experience(self):
        for record in self:
            number_of_days = 0
            continuous_number_of_days = 0
            for line in record.experience_resume_line_ids:
                if line.date_start:
                    start_date = line.date_start
                    end_date = line.date_end or datetime.now().date()
                    duration = (end_date - start_date).days
                    if str(line.company_name).lower() == 'teslatan':
                        continuous_number_of_days += duration
                    number_of_days += duration
            record.continuous_experience = self._format_duration(
                continuous_number_of_days)
            record.total_experience = self._format_duration(number_of_days)

    def _format_duration(self, number_of_days):
        years = number_of_days // 365
        months = (number_of_days - years * 365) // 30
        days = (number_of_days - years * 365 - months * 30)
        return f'{years} л. {months} м. {days} дн.'

    @api.depends("resume_line_ids")
    def _compute_experience_fields(self):
        for record in self:
            resumes = record.resume_line_ids.filtered(
                lambda resume: resume.line_type_id.name == "Experience"
            )
            record.experience_resume_line_ids = resumes

    @api.depends("resume_line_ids")
    def _compute_education_fields(self):
        for record in self:
            resumes = record.resume_line_ids.filtered(
                lambda resume: resume.line_type_id.name == "Education"
            )
            record.education_ids = resumes

    @api.depends("education_ids")
    def _compute_certificate(self):
        for record in self:
            certificate_level = []
            for line in record.education_ids:
                if line.certificate:
                    certificate_level.append(line.certificate)
            if len(certificate_level) != 0:
                record.certificate_level = ", ".join(certificate_level)
            else:
                record.certificate_level = ''

    @api.depends("education_ids")
    def _compute_professions(self):
        for record in self:
            professions = []
            for line in record.education_ids:
                if line.profession:
                    professions.append(line.profession)
            if len(professions) != 0:
                record.professions = ", ".join(professions)
            else:
                record.professions = ''

    @api.depends("education_ids")
    def _compute_study_forms(self):
        for record in self:
            study_forms = []
            for line in record.education_ids:
                if line.study_form:
                    study_forms.append(line.study_form)
            if len(study_forms) != 0:
                record.study_forms = ", ".join(study_forms)
            else:
                record.study_forms = ''


    @api.depends("education_ids")
    def _compute_specialities(self):
        for record in self:
            specialities = []
            for line in record.education_ids:
                if line.speciality:
                    specialities.append(line.speciality)
            if len(specialities) != 0:
                record.specialities = ", ".join(specialities)
            else:
                record.specialities = ''

    @api.depends("education_ids")
    def _compute_diploma_number(self):
        for record in self:
            for line in record.education_ids:
                if line.diploma_number:
                    record.diploma_number = line.diploma_number
                else:
                    record.diploma_number = ''

    @api.depends("education_ids")
    def _compute_diploma_number_date(self):
        for record in self:
            dates = []
            for line in record.education_ids:
                if line.date_end:
                    split_end_date = str(line.date_end).split("-")
                    date_end = (
                        split_end_date[2]
                        + "."
                        + split_end_date[1]
                        + "."
                        + split_end_date[0]
                    )
                    dates.append(date_end)
                else:
                    dates.append("")
                record.diploma_number_date = dates[0]

    @api.depends("education_ids")
    def _compute_school_and_graduation_year(self):
        for record in self:
            schools = []
            for line in record.education_ids:
                if line.study_school and line.date_end:
                    split_end_date = str(line.date_end).split("-")
                    date_end = (
                        split_end_date[2]
                        + "."
                        + split_end_date[1]
                        + "."
                        + split_end_date[0]
                    )
                    schools.append(f"{line.study_school}, {date_end}")
            if len(schools) != 0:
                record.school_and_graduation_year = "; ".join(schools)
            else:
                record.school_and_graduation_year = ''

    def correct_data(self):
        all_employee = self.env["hr.employee"].search(
            [("company_id", "=", self.env.company.id)]
        )

        for employee in all_employee:
            resume_line_ids = employee.resume_line_ids
            name_dict = {}
            for resume_line in resume_line_ids:
                if resume_line and resume_line.exists():
                    deleted = False
                    if resume_line.name:
                        if resume_line.name in name_dict:
                            resume_line.unlink()
                            deleted = True
                        else:
                            name_dict[resume_line.name] = True

                    if not deleted and not resume_line.line_type_id:
                        resume_line.line_type_id = self.env[
                            "hr.resume.line.type"
                        ].search([("name", "=", "Education")], limit=1)
        return True
