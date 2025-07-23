# Part of OpenEduCat. See LICENSE file for full copyright & licensing details.
#
##############################################################################
#
#    OpenEduCat Inc.
#    Copyright (C) 2009-TODAY OpenEduCat Inc(<http://www.openeducat.org>).
#
##############################################################################


import io
import json
import logging
import operator

from werkzeug.exceptions import InternalServerError

from odoo import http
from odoo.http import content_disposition, request
from odoo.tools import osutil, pycompat

from odoo.addons.web.controllers.export import ExportFormat, ExportXlsxWriter

_logger = logging.getLogger(__name__)


class ExportingClassForChart(ExportFormat, http.Controller):
    def base(self, data):
        params = json.loads(data)
        header, chart_data = operator.itemgetter("header", "chart_data")(params)
        chart_data = json.loads(chart_data)
        chart_data["labels"].insert(0, "Measure")
        columns_headers = chart_data["labels"]
        import_data = []

        for dataset in chart_data["datasets"]:
            dataset["data"].insert(0, dataset["label"])
            import_data.append(dataset["data"])

        return request.make_response(
            self.from_data(columns_headers, import_data),
            headers=[
                ("Content-Disposition", content_disposition(
                    osutil.clean_filename(self.filename(header) + self.extension()))),
                ("Content-Type", self.content_type),
            ]
        )

    def extension(self):
        return '.csv'


class ExportingClassForChartExcel(ExportingClassForChart, http.Controller):

    raw_data = True

    @http.route("/dashboard_pro/export/chart_xls", type="http", auth="user")
    def index(self, data):
        try:
            return self.base(data)
        except Exception as exc:
            _logger.exception("Exception during request handling.")
            payload = json.dumps({
                'code': 200,
                'message': "Odoo Server Error",
                'data': http.serialize_exception(exc)
            })
            raise InternalServerError(payload) from exc

    def extension(self):
        return '.xls'

    @property
    def content_type(self):
        return "application/vnd.ms-excel"

    def filename(self, base):
        return base

    def from_data(self, fields, rows):

        with ExportXlsxWriter(fields, len(rows)) as xlsx_writer:
            for row_index, row in enumerate(rows):
                for cell_index, cell_value in enumerate(row):
                    xlsx_writer.write_cell(row_index + 1, cell_index, cell_value)

        return xlsx_writer.value


class ExportingClassForChartCSV(ExportingClassForChart, http.Controller):
    @http.route("/dashboard_pro/export/chart_csv", type="http", auth="user")
    def index(self, data):
        try:
            return self.base(data)
        except Exception as exc:
            _logger.exception("Exception during request handling.")
            payload = json.dumps({
                'code': 200,
                'message': "Odoo Server Error",
                'data': http.serialize_exception(exc)
            })
            raise InternalServerError(payload) from exc

    def extension(self):
        return '.csv'

    @property
    def content_type(self):
        return "text/csv;charset=utf8"

    def filename(self, base):
        return base

    def from_data(self, fields, rows):
        fp = io.BytesIO()
        writer = pycompat.csv_writer(fp, quoting=1)

        writer.writerow(fields)

        for data in rows:
            row = []
            for d in data:
                if isinstance(d, str) and d.startswith(("=", "-", "+")):
                    d = "'" + d

                row.append(pycompat.to_text(d))
            writer.writerow(row)

        return fp.getvalue()


class ExportingClassForDashBoard(ExportFormat, http.Controller):
    def base(self, data):
        params = json.loads(data)
        header, dashboard_data = operator.itemgetter("header", "dashboard_data")(params)
        return request.make_response(
            self.from_data(dashboard_data),
            headers=[
                ("Content-Disposition", content_disposition(
                    osutil.clean_filename(self.filename(header) + self.extension())
                )),
                ("Content-Type", self.content_type),
            ],
        )

    def extension(self):
        return '.csv'

    def filename(self, base):
        return base


class ExportingClassForDashBoardJson(ExportingClassForDashBoard, http.Controller):
    @http.route("/dashboard_pro/export/dashboard_json", type="http", auth="user")
    def index(self, data):
        try:
            return self.base(data)
        except Exception as exc:
            _logger.exception("Exception during request handling.")
            payload = json.dumps({
                'code': 200,
                'message': "Odoo Server Error",
                'data': http.serialize_exception(exc)
            })
            raise InternalServerError(payload) from exc

    def extension(self):
        return '.json'

    @property
    def content_type(self):
        return "text/csv;charset=utf8"

    def filename(self, base):
        return base

    def from_data(self, dashboard_data):
        fp = io.StringIO()
        fp.write(json.dumps(dashboard_data))

        return fp.getvalue()


class ExportingClassForDashBoardElementJson(
    ExportingClassForDashBoard, http.Controller
):
    @http.route("/dashboard_pro/export/item_json", type="http", auth="user")
    def index(self, data):
        data = json.loads(data)
        element_id = data["element_id"]
        data["dashboard_data"] = request.env[
            "dashboard_pro.main_dashboard"
        ].element_export(element_id)
        data = json.dumps(data)
        try:
            return self.base(data)
        except Exception as exc:
            _logger.exception("Exception during request handling.")
            payload = json.dumps({
                'code': 200,
                'message': "Odoo Server Error",
                'data': http.serialize_exception(exc)
            })
            raise InternalServerError(payload) from exc

    def extension(self):
        return '.json'

    @property
    def content_type(self):
        return "text/csv;charset=utf8"

    def filename(self, base):
        return base

    def from_data(self, dashboard_data):
        fp = io.StringIO()
        fp.write(json.dumps(dashboard_data))

        return fp.getvalue()
