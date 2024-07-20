# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import time
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
from docxtpl_formats import Formats

logger = logging.getLogger(__name__)


class IrActionsReportXml(models.Model):
    """ Inherit from ir.actions.report.xml to allow customizing the template
    file. The user cam chose a template from a list.
    """

    _inherit = 'ir.actions.report.xml'

    @api.multi
    @api.constrains("docxtpl_filetype", "report_type")
    def _check_docxtpl_filetype(self):
        for report in self:
            if report.report_type == "docxtpl" and not report.docxtpl_filetype:
                raise ValidationError(_(
                    "Field 'Output Format' is required for Docx report"))

    @api.model
    def _get_docxtpl_filetypes(self):
        formats = Formats()
        names = formats.get_known_format_names()
        selections = []
        for name in names:
            description = name
            if formats.get_format(name).native:
                description = description + " " + _("(Native)")
            selections.append((name, description))
        return selections

    docxtpl_filetype = fields.Selection(
        selection="_get_docxtpl_filetypes",
        string="Output Format")
    docxtpl_template_id = fields.Many2one(
        'docxtpl.template',
        "Template")
    module = fields.Char(
        "Module",
        help="The implementer module that provides this report")
    docxtpl_template_fallback = fields.Char(
        "Fallback",
        size=128,
        help=(
            "If the user does not provide a template this will be used "
            "it should be a relative path to root of YOUR module "
            "or an absolute path on your server."
        ))
    report_type = fields.Selection(selection_add=[('docxtpl', "Docx")])
    docxtpl_multi_in_one = fields.Boolean(
        string='Multiple Records in a Single Report',
        help="If you execute a report on several records, "
        "by default Odoo will generate a ZIP file that contains as many "
        "files as selected records. If you enable this option, Odoo will "
        "generate instead a single report for the selected records.")

    @api.model
    def get_from_report_name(self, report_name, report_type):
        return self.search(
            [("report_name", "=", report_name),
             ("report_type", "=", report_type)])

    @api.model
    def render_report(self, res_ids, name, data):
        action_docxtpl_report = self.get_from_report_name(name, "docxtpl")
        if action_docxtpl_report:
            return self.env['docxtpl.report'].create({
                'ir_actions_report_xml_id': action_docxtpl_report.id
            }).create_report(res_ids, data)
        return super(IrActionsReportXml, self).render_report(
            res_ids, name, data)

    @api.multi
    def gen_report_download_filename(self, res_ids, data):
        """Override this function to change the name of the downloaded report
        """
        self.ensure_one()
        report = self.get_from_report_name(self.report_name, self.report_type)
        if report.print_report_name and not len(res_ids) > 1:
            obj = self.env[self.model].browse(res_ids)
            return safe_eval(report.print_report_name,{'object': obj, 'time': time})
        return "%s.%s" % (self.name, self.docxtpl_filetype)
