from odoo import api, fields, models
 
class CourseXlsx(models.AbstractModel):
    _name = 'report.training_odoo.report_course'
    _inherit = 'report.report_xlsx.abstract'
 
    def generate_xlsx_report(self, workbook, data, obj):
        sheet = workbook.add_worksheet('Course %s' % obj.name)
        text_top_style = workbook.add_format({'font_size': 12, 'bold': True ,'font_color' : 'white', 'bg_color': '#b904bf', 'valign': 'vcenter', 'text_wrap': True})
        text_header_style = workbook.add_format({'font_size': 12, 'bold': True ,'font_color' : 'white', 'bg_color': '#b904bf', 'valign': 'vcenter', 'text_wrap': True, 'align': 'center'})
        text_style = workbook.add_format({'font_size': 12, 'valign': 'vcenter', 'text_wrap': True, 'align': 'center'})
        number_style = workbook.add_format({'num_format': '#,##0', 'font_size': 12, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True})
 
        sheet.merge_range(0, 0, 0, 1, "Reference", text_top_style)
        sheet.write(0, 2, obj.ref)
        sheet.merge_range(1, 0, 1, 1, "Course Title", text_top_style)
        sheet.write(1, 2, obj.name)
        sheet.merge_range(2, 0, 2, 1, "Level", text_top_style)
        sheet.write(2, 2, obj.level.capitalize() if obj.level else '')
        sheet.merge_range(3, 0, 3, 1, "Responsible", text_top_style)
        sheet.write(3, 2, obj.user_id.name)
 
        row = 5
        sheet.freeze_panes(6, 10)
        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 9, 15)
        header = ['No', 'Session', 'Instructor', 'Start Date', 'End Date','Duration', 'Seats', 'Attendees','Taken Seats(%)','Status']
        sheet.write_row(row, 0, header, text_header_style)
         
        no_list = []
        session = []
        partner = []
        start_date = []
        end_date = []
        duration = []
        seats = []
        attendees = []
        taken_seats = []
        status = []
 
        no = 1
        for x in obj.session_line:
            no_list.append(no)
            session.append(x.name or '')
            partner.append(x.partner_id.name if x.partner_id and x.partner_id.name else '')
            start_date.append(x.start_date.strftime('%d-%m-%Y') if x.start_date else '')
            end_date.append(x.end_date.strftime('%d-%m-%Y') if x.end_date else '')
            duration.append(x.duration or '')
            seats.append(x.seats or '')
            attendees.append(x.attendees_count)
            taken_seats.append(x.taken_seats)
            status.append(x.state.capitalize())
            no+=1
 
        row += 1
        sheet.write_column(row, 0, no_list, text_style)
        sheet.write_column(row, 1, session, text_style)
        sheet.write_column(row, 2, partner, text_style)
        sheet.write_column(row, 3, start_date, text_style)
        sheet.write_column(row, 4, end_date, text_style)
        sheet.write_column(row, 5, duration, text_style)
        sheet.write_column(row, 6, seats, number_style)
        sheet.write_column(row, 7, attendees, number_style)
        sheet.write_column(row, 8, taken_seats, number_style)
        sheet.write_column(row, 9, status, text_style)