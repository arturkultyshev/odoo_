from odoo import models, fields, api


class EmployeeWorkInfo(models.Model):
    _inherit = "hr.employee"

    # Work Information
    work_schedule = fields.Selection(
        selection=[
            ("5/2", "5/2"),
            ("6/1", "6/1"),
            ("14/14", "14/14"),
            ("15/15", "15/15"),
            ("28/28", "28/28"),
            ("30/30", "30/30"),
        ],
        string="Schedule",
        default="5/2",
        tracking=True,
    )
    work_schedule_type = fields.Selection(
        selection=[
            ("five_days", "Five days"),
            ("six_days", "Six days"),
            ("shift", "Shift"),
            ("remote", "Remote"),
            ("hybrid", "Hybrid"),
            ("changing", "Changing"),
        ],
        string="Schedule Type",
        compute="_compute_work_schedule_type",
        store=True,
        tracking=True,
        readonly=False,
    )
    employment_contract_id = fields.Many2one(
        'hr.contract',
        string='Primary Contract',
        compute='_compute_employment_contract',
        store=True,
        readonly=False,
    )
    employment_type = fields.Selection(
        selection=[
            ("primary_employment", "Primary Employment"),
            ("combination", "Combination"),
        ],
        string="Employment Type",
        default="primary_employment",
        tracking=True,
    )
    
    @api.depends("work_schedule")
    def _compute_work_schedule_type(self):
        for employee in self:
            if employee.work_schedule == "5/2":
                employee.work_schedule_type = "five_days"
            elif employee.work_schedule == "6/1":
                employee.work_schedule_type = "six_days"
            elif (
                    employee.work_schedule == "14/14"
                    or employee.work_schedule == "15/15"
                    or employee.work_schedule == "28/28"
                    or employee.work_schedule == "30/30"
            ):
                employee.work_schedule_type = "shift"
            else:
                employee.work_schedule_type = False

    @api.depends('contract_ids', 'contract_ids.contract_type', 'contract_ids.state')
    def _compute_employment_contract(self):
        for employee in self:
            employee.employment_contract_id = False
            for contract in employee.contract_ids:
                if contract.contract_type == 'primary' and contract.state == 'open':
                    employee.employment_contract_id = contract.id
                    break