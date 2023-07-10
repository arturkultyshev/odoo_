from odoo import fields, models


class HrPersonalDocument(models.Model):
    _name = "hr.employee.personal_document"
    _description = "Personal Document"

    employee_id = fields.Many2one(
        "hr.employee",
        "Employee",
        default=lambda self: self.env.context.get("active_id"),
    )
    document_type = fields.Selection(
        selection=[
            ("passport", "Passport"),
            ("id_card", "ID Card"),
            ("residence", "Residence"),
            ("foreigner_residence", "Residence permit of a foreigner"),
        ],
        string="Type",
        help="Document Type",
    )
    iin = fields.Char(
        string="IIN", 
        related="employee_id.iin", 
        store=True
    )
    serial_number = fields.Char(
        string="Serial Number"
    )
    document_number = fields.Char(
        string="Document Number"
    )
    issue_date = fields.Date(
        string="Issue Date"
    )
    issued_by = fields.Selection(
        selection=[
            ("mia", "Ministry of Internal Affairs"),
            ("mj", "Ministry of Justice"),
            ("roseau", "Roseau"),
            ("mRF", "Ministry of Internal Affairs of the Russian Federation"),
            ("jaipur", "Jaipur"),
            ("lucknow", "Lucknow"),
            ("delhi", "Delhi"),
            ("mumbai", "Mumbai"),
            ("baku", "Baku")
        ],
        string="Issued By",
    )
    id_scan = fields.Binary(
        string="ID scan"
    )


    class EmployeePersonalDocumentInfo(models.Model):
        _inherit = "hr.employee"

        private_documents = fields.One2many(
            comodel_name="hr.employee.personal_document", 
            inverse_name="employee_id"
        )
