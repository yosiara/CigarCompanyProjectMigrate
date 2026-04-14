import json
from odoo import http
from odoo.http import content_disposition, request
from odoo.http import serialize_exception as _serialize_exception
from odoo.tools import html_escape

class XLSXReportController(http.Controller):
    """XlsxReport generating controller"""
    @http.route('/xlsx_reports', type='http', auth='user', methods=['POST'], csrf=False)
    def get_report_xlsx(self, model, options, output_format, report_name, **kw):
        """
        Generate an XLSX report based on the provided data and return it as a
        response.
        """
        uid = request.session.uid
        report_obj = request.env[model].with_user(uid)
        options = json.loads(options)
        token = 'dummy-because-api-expects-one'
        try:
            if output_format == 'xlsx':
                response = request.make_response(
                    None,
                    headers=[
                        ('Content-Type', 'application/vnd.ms-excel'),
                        ('Content-Disposition',
                         content_disposition(f"{report_name}.xlsx"))
                    ]
                )
                report_obj.generate_xlsx_report(options, response)
                response.set_cookie('fileToken', token)
                return response
            # elif output_format == 'pdf':
            #     response = request.make_response(
            #         None,
            #         headers=[
            #             ('Content-Type', 'application/pdf'),
            #             ('Content-Disposition',
            #              content_disposition(f"{report_name}.pdf"))
            #         ]
            #     )
            #     report_obj.generate_xlsx_report(options, response)
            #     response.set_cookie('fileToken', token)
            #     return
        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Odoo Server Error Trapped',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
