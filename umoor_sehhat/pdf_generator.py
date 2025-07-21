from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from xhtml2pdf import pisa
from io import BytesIO
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Service for generating various types of PDF documents"""
    
    @staticmethod
    def create_doctor_schedule_pdf(doctor, schedule_date, appointments):
        """Generate PDF for doctor's daily schedule"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor('#2c5530')
        )
        
        # Header
        title = f"Daily Schedule - {schedule_date.strftime('%B %d, %Y')}"
        story.append(Paragraph(title, title_style))
        
        # Doctor info
        doctor_info = f"""
        <b>Doctor:</b> Dr. {doctor.user.get_full_name()}<br/>
        <b>Specialty:</b> {doctor.user.specialty or 'General Practice'}<br/>
        <b>License:</b> {doctor.license_number}<br/>
        <b>Generated:</b> {timezone.now().strftime('%Y-%m-%d %H:%M')}
        """
        story.append(Paragraph(doctor_info, styles['Normal']))
        story.append(Spacer(1, 20))
        
        if appointments:
            # Appointments table
            data = [['Time', 'Patient', 'Reason', 'Status', 'Contact']]
            
            for appointment in appointments:
                data.append([
                    appointment.appointment_time.strftime('%H:%M'),
                    appointment.patient.user.get_full_name(),
                    appointment.reason_for_visit[:30] + '...' if len(appointment.reason_for_visit) > 30 else appointment.reason_for_visit,
                    appointment.get_status_display(),
                    appointment.patient.user.phone_number or 'N/A'
                ])
            
            table = Table(data, colWidths=[1*inch, 2*inch, 2.5*inch, 1*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5530')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Summary
            summary = f"""
            <b>Total Appointments:</b> {len(appointments)}<br/>
            <b>Duration:</b> Estimated {len(appointments) * 30} minutes<br/>
            <b>Notes:</b> Please arrive 10 minutes early for each appointment.
            """
            story.append(Paragraph(summary, styles['Normal']))
        else:
            story.append(Paragraph("No appointments scheduled for this day.", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def create_photo_gallery_pdf(album, photos):
        """Generate PDF for photo gallery/album"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            textColor=colors.HexColor('#2c5530'),
            alignment=1  # Center alignment
        )
        
        # Title
        story.append(Paragraph(f"Photo Gallery: {album.name}", title_style))
        
        # Album info
        album_info = f"""
        <b>Created:</b> {album.created_at.strftime('%B %d, %Y')}<br/>
        <b>Photos:</b> {photos.count()}<br/>
        <b>Description:</b> {album.description or 'No description available'}
        """
        story.append(Paragraph(album_info, styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Photos grid
        photos_per_row = 2
        current_row = []
        
        for i, photo in enumerate(photos):
            if photo.image and os.path.exists(photo.image.path):
                try:
                    img = Image(photo.image.path, width=2.5*inch, height=2*inch)
                    current_row.append(img)
                    
                    # Add caption
                    if photo.caption:
                        caption = Paragraph(f"<i>{photo.caption[:50]}...</i>" if len(photo.caption) > 50 else f"<i>{photo.caption}</i>", styles['Italic'])
                        current_row.append(caption)
                    
                    if len(current_row) >= photos_per_row * 2 or i == len(photos) - 1:
                        # Create table for this row
                        if len(current_row) == 1:
                            current_row.append('')  # Fill empty cell
                        
                        table = Table([current_row], colWidths=[3*inch, 3*inch])
                        table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]))
                        
                        story.append(table)
                        story.append(Spacer(1, 10))
                        current_row = []
                        
                except Exception as e:
                    logger.warning(f"Could not add image {photo.image.path} to PDF: {e}")
                    continue
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def create_survey_report_pdf(survey, analytics_data):
        """Generate PDF report for survey results"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#2c5530')
        )
        
        # Title
        story.append(Paragraph(f"Survey Report: {survey.title}", title_style))
        
        # Survey info
        survey_info = f"""
        <b>Created by:</b> {survey.created_by.get_full_name()}<br/>
        <b>Period:</b> {survey.start_date} to {survey.end_date}<br/>
        <b>Target Audience:</b> {', '.join(survey.target_audience)}<br/>
        <b>Status:</b> {'Active' if survey.is_active else 'Inactive'}<br/>
        <b>Generated:</b> {timezone.now().strftime('%Y-%m-%d %H:%M')}
        """
        story.append(Paragraph(survey_info, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Statistics
        stats_data = [
            ['Total Responses', str(analytics_data.get('total_responses', 0))],
            ['Target Users', str(analytics_data.get('target_users', 0))],
            ['Completion Rate', f"{analytics_data.get('completion_rate', 0)}%"],
        ]
        
        stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5530')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("<b>Survey Statistics</b>", styles['Heading2']))
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Question analysis
        story.append(Paragraph("<b>Question Analysis</b>", styles['Heading2']))
        
        for i, question_data in enumerate(analytics_data.get('question_analytics', [])):
            question = question_data['question']
            analysis = question_data['analysis']
            
            story.append(Paragraph(f"<b>Q{i+1}: {question['text']}</b>", styles['Heading3']))
            
            if analysis['type'] == 'multiple_choice':
                data = [['Option', 'Count', 'Percentage']]
                for option in analysis['options']:
                    data.append([option['text'], str(option['count']), f"{option['percentage']}%"])
                
                table = Table(data, colWidths=[3*inch, 1*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(table)
            
            elif analysis['type'] == 'rating':
                rating_info = f"Average Rating: {analysis['average']}/5 ({analysis['total_responses']} responses)"
                story.append(Paragraph(rating_info, styles['Normal']))
            
            elif analysis['type'] == 'text':
                text_info = f"Total Responses: {analysis['total_responses']}"
                story.append(Paragraph(text_info, styles['Normal']))
            
            story.append(Spacer(1, 15))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def create_moze_report_pdf(moze, stats, comments):
        """Generate PDF report for Moze"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#2c5530')
        )
        
        # Title
        story.append(Paragraph(f"Moze Report: {moze.name}", title_style))
        
        # Moze info
        moze_info = f"""
        <b>Location:</b> {moze.location}<br/>
        <b>Aamil:</b> {moze.aamil.get_full_name() if moze.aamil else 'Not assigned'}<br/>
        <b>Coordinator:</b> {moze.moze_coordinator.get_full_name() if moze.moze_coordinator else 'Not assigned'}<br/>
        <b>Established:</b> {moze.established_date or 'Not specified'}<br/>
        <b>Status:</b> {'Active' if moze.is_active else 'Inactive'}<br/>
        <b>Capacity:</b> {moze.capacity or 'Not specified'}<br/>
        <b>Generated:</b> {timezone.now().strftime('%Y-%m-%d %H:%M')}
        """
        story.append(Paragraph(moze_info, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Statistics
        stats_data = [
            ['Total Team Members', str(stats.get('total_members', 0))],
            ['Aamils', str(stats.get('aamils', 0))],
            ['Coordinators', str(stats.get('coordinators', 0))],
            ['Doctors', str(stats.get('doctors', 0))],
            ['Students', str(stats.get('students', 0))],
        ]
        
        stats_table = Table(stats_data, colWidths=[2.5*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5530')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("<b>Team Statistics</b>", styles['Heading2']))
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Recent comments
        if comments:
            story.append(Paragraph("<b>Recent Comments</b>", styles['Heading2']))
            
            for comment in comments[:10]:  # Limit to 10 comments
                comment_text = f"""
                <b>{comment.author.get_full_name()}</b> - {comment.created_at.strftime('%Y-%m-%d %H:%M')}<br/>
                {comment.content[:200]}{'...' if len(comment.content) > 200 else ''}
                """
                story.append(Paragraph(comment_text, styles['Normal']))
                story.append(Spacer(1, 10))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def create_user_report_pdf(users, title="User Report"):
        """Generate PDF report for users"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#2c5530')
        )
        
        # Title
        story.append(Paragraph(title, title_style))
        
        # Report info
        report_info = f"""
        <b>Total Users:</b> {users.count()}<br/>
        <b>Generated:</b> {timezone.now().strftime('%Y-%m-%d %H:%M')}
        """
        story.append(Paragraph(report_info, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Users table
        data = [['Name', 'Role', 'Email', 'Phone', 'Date Joined']]
        
        for user in users:
            data.append([
                user.get_full_name() or user.username,
                user.get_role_display(),
                user.email or 'N/A',
                user.phone_number or 'N/A',
                user.date_joined.strftime('%Y-%m-%d')
            ])
        
        table = Table(data, colWidths=[1.5*inch, 1*inch, 2*inch, 1.2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5530')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def create_response_with_pdf(buffer, filename):
        """Create HTTP response with PDF attachment"""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(buffer.getvalue())
        buffer.close()
        return response


class HTMLToPDFGenerator:
    """Alternative PDF generator using xhtml2pdf for complex HTML layouts"""
    
    @staticmethod
    def generate_from_template(template_name, context, filename):
        """Generate PDF from Django template"""
        try:
            # Render template to HTML
            html_string = render_to_string(template_name, context)
            
            # Create PDF
            buffer = BytesIO()
            pisa_status = pisa.CreatePDF(html_string, dest=buffer)
            
            if pisa_status.err:
                logger.error(f"Error generating PDF: {pisa_status.err}")
                return None
            
            buffer.seek(0)
            
            # Create response
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response.write(buffer.getvalue())
            buffer.close()
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate PDF: {str(e)}")
            return None
    
    @staticmethod
    def generate_prescription_pdf(prescription):
        """Generate prescription PDF"""
        context = {
            'prescription': prescription,
            'doctor': prescription.doctor,
            'patient': prescription.patient,
            'generated_date': timezone.now(),
        }
        
        return HTMLToPDFGenerator.generate_from_template(
            'pdf_templates/prescription.html',
            context,
            f'prescription_{prescription.id}.pdf'
        )
    
    @staticmethod
    def generate_medical_record_pdf(medical_record):
        """Generate medical record PDF"""
        context = {
            'medical_record': medical_record,
            'doctor': medical_record.doctor,
            'patient': medical_record.patient,
            'generated_date': timezone.now(),
        }
        
        return HTMLToPDFGenerator.generate_from_template(
            'pdf_templates/medical_record.html',
            context,
            f'medical_record_{medical_record.id}.pdf'
        )