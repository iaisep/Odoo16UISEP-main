# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import xlwt
from xlwt import easyxf
import io
from docutils.nodes import line
from odoo.exceptions import UserError, Warning

 
class PayslipBatches(models.Model):
    
    _inherit = 'hr.payslip.run'

    def export_report_xlsx(self):
        import base64
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Listado de nomina')
        header_style = easyxf('font:height 200; align: horiz center; font:bold True;' "borders: top thin,left thin,right thin,bottom thin")
        text_bold_left = easyxf('font:height 200; font:bold True; align: horiz left;' "borders: top thin,bottom thin")
        text_left = easyxf('font:height 200; align: horiz left;' "borders: top thin,bottom thin")
        text_right = easyxf('font:height 200; align: horiz right;' "borders: top thin,bottom thin")
        text_bold_right = easyxf('font:height 200;font:bold True; align: horiz right;' "borders: top thin,bottom thin")
        worksheet.write(0, 0, 'Cod', header_style)
        worksheet.write(0, 1, 'Empleado', header_style)
        worksheet.write(0, 2, 'Dias Pag', header_style)
        col_nm = 3

        noms = self.slip_ids
        for nom in noms:
            if not nom.employee_id.department_id:
                raise UserError(_('%s no tiene departamento configurado') % (nom.employee_id.name))

        all_column = self.get_all_columns()
        all_col_dict = all_column[0]
        all_col_list = all_column[1]
        for col in all_col_list:
            worksheet.write(0, col_nm, all_col_dict[col], header_style)
            col_nm += 1
        for t in ['Total Efectivo', 'Total Especie']:
            worksheet.write(0, col_nm, t, header_style)
            col_nm += 1

        payslip_group_by_department = self.get_payslip_group_by_department()
        row = 1
        grand_total = {}
        for dept in self.env['hr.department'].browse(payslip_group_by_department.keys()).sorted(lambda x:x.name):
            row += 1
            worksheet.write_merge(row, row, 0, 2, dept.name, text_bold_left)
            total = {}
            row += 1
            slip_sorted_by_employee={}
            hr_payslips=[]
            value = 1
            for slip in payslip_group_by_department[dept.id]:
                if slip.employee_id and not slip.employee_id.no_empleado in slip_sorted_by_employee.values():
                    slip_sorted_by_employee[slip.id]=slip.employee_id.no_empleado or '0'
                else:
                    slip_sorted_by_employee[slip.id]=slip.employee_id.no_empleado + str(value) or '0' + str(value)
                    value += 1
            #Cambio hecho el 7/11/2023, Eduardo Antillon
            key_list=list(slip_sorted_by_employee.keys())         
            hr_payslips = self.env['hr.payslip'].browse(key_list)
            #Ordenado o agrupado por employee_id.id
            #hr_payslips=sorted(hr_payslips,key=lambda x:x.employee_id.id,reverse=True)

            for slip in hr_payslips:
                if slip.state == "cancel":
                    continue
                if slip.employee_id.no_empleado:
                    worksheet.write(row, 0, slip.employee_id.no_empleado, text_left)
                #imprime nombre del empleado    
                worksheet.write(row, 1, slip.employee_id.name, text_left)
                work_day = slip.get_total_work_days()
                worksheet.write(row, 2, work_day, text_right)
                code_col = 3
                for code in all_col_list:
                    amt = 0
                    if code in total.keys():
                        for line in slip.line_ids:
                           if line.code == code:
                               amt = round(line.total,2)
#                        amt = slip.get_amount_from_rule_code(code)
#                        if amt:
                               grand_total[code] = grand_total.get(code) + amt
                               total[code] = total.get(code) + amt
                    else:
                        #amt = slip.get_amount_from_rule_code(code)
                        for line in slip.line_ids:
                           if line.code == code:
                               amt = round(line.total,2)
                               total[code] = amt or 0
                        if code in grand_total.keys():
                            grand_total[code] = amt + grand_total.get(code) or 0.0
                        else:
                            grand_total[code] = amt or 0
                    worksheet.write(row, code_col, amt, text_right)
                    code_col += 1
                worksheet.write(row, code_col, slip.get_total_code_value('001'), text_right)
                code_col += 1
                worksheet.write(row, code_col, slip.get_total_code_value('002'), text_right)
                row += 1
            worksheet.write_merge(row, row, 0, 2, 'Total Departamento', text_bold_left)
            code_col = 3
            for code in all_col_list:
                worksheet.write(row, code_col, total.get(code), text_bold_right)
                code_col += 1
        row += 1
        worksheet.write_merge(row, row, 0, 2, 'Gran Total', text_bold_left)
        code_col = 3
        for code in all_col_list:
            worksheet.write(row, code_col, grand_total.get(code), text_bold_right)
            code_col += 1

        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        self.write({'file_data': base64.b64encode(data)})
        action = {
            'name': 'Journal Entries',
            'type': 'ir.actions.act_url',
            'url': "/web/content/?model=hr.payslip.run&id=" + str(self.id) + "&field=file_data&download=true&filename=Listado_de_nomina.xls",
            'target': 'self',
            }
        return action
