from odoo import models, api
from datetime import datetime, timedelta


class PensionNotificationCronJob(models.Model):
    _name = 'hr.employee.pension.nofitication.cron.job'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _get_employee_list_with_pension(self):
        """
        It returns a list of employees who are going to retire within the next 60 days
        """
        employees_with_pension = []

        employees_list = self.env['hr.employee'].search([])
        for employee in employees_list:
            d = (datetime.now() + timedelta(days=60)).date()
            i = (datetime.now() + timedelta(days=30)).date()
            if employee.pension_date:
                date_object = datetime.strptime(
                    employee.pension_date, '%Y-%m-%d').date()
                if date_object >= i and date_object < d:
                    employees_with_pension.append(employee)

        return employees_with_pension

    def _get_receivers(self, employee):
        """
        It returns a list of the employee's linear manager and the HR manager of the employee's company
        """
        hr_manager = self.env['res.company'].search(
            [('name', '=', employee.company_id.name)], limit=1).hr_manager
        return [hr_manager.employee_id, employee.parent_id]

    @api.model
    def pension_cron_job(self):
        """
        It sends an email to the employee's linear manager and HR manager when the employee's pension date is
        in 30 days
        """
        employees = self._get_employee_list_with_pension()

        for employee in employees:
            receivers = self._get_receivers(employee)

            for receiver in receivers:
                if receiver.work_email:
                    receiver.message_post(
                        subject="Уведомление о прекращении трудового договора связи достижением пенсионного возраста",
                        body='Уведомление о прекращении трудового договора связи достижением пенсионного возраста. У ' +
                        f'{employee.full_name} ({employee.formated_pension_date})',
                        partner_ids=[receiver.user_id.partner_id.id]
                    )