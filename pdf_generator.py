import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from PIL import Image as PILImage
import io


class PDFReportGenerator:
    def __init__(self, output_dir="assets/reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Get base stylesheet
        self.styles = getSampleStyleSheet()
        
        # Initialize custom styles - STRICT one-page formatting
        self._initialize_styles()

    def _initialize_styles(self):
        """Initialize custom styles for strict one-page medical report"""
        
        # ================== HEADER STYLES ==================
        # Main Report Title - Large, centered
        if 'ReportMainTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ReportMainTitle',
                parent=self.styles['Heading1'],
                fontSize=20,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceAfter=4,
                fontName='Helvetica-Bold',
                leading=24
            ))
        
        # System Name - Medium, centered
        if 'SystemName' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SystemName',
                parent=self.styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#2d3748'),
                alignment=TA_CENTER,
                spaceAfter=2,
                leading=14
            ))
        
        # Report Date - Small, centered
        if 'ReportDate' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ReportDate',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=8,
                leading=10
            ))
        
        # ================== PATIENT INFO STYLES ==================
        # Compact info label
        if 'CompactLabel' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CompactLabel',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#4a5568'),
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
                leading=10
            ))
        
        # Compact info value
        if 'CompactValue' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CompactValue',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.black,
                alignment=TA_LEFT,
                leading=10
            ))
        
        # ================== DIAGNOSIS STYLES ==================
        # Diagnosis Name - Prominent but compact
        if 'DiagnosisName' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='DiagnosisName',
                parent=self.styles['Heading1'],
                fontSize=18,
                textColor=colors.black,
                alignment=TA_CENTER,
                spaceBefore=12,
                spaceAfter=2,
                fontName='Helvetica-Bold',
                leading=20
            ))
        
        # Confidence Percentage - Clean number only
        if 'ConfidenceNumber' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ConfidenceNumber',
                parent=self.styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#1a365d'),
                alignment=TA_CENTER,
                spaceAfter=16,
                fontName='Helvetica-Bold',
                leading=18
            ))
        
        # ================== CLINICAL CONTENT STYLES ==================
        # Section Title
        if 'SectionTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionTitle',
                parent=self.styles['Heading3'],
                fontSize=11,
                textColor=colors.HexColor('#1a365d'),
                alignment=TA_LEFT,
                spaceBefore=12,
                spaceAfter=4,
                fontName='Helvetica-Bold',
                leading=12
            ))
        
        # Clinical Text - VERY compact
        if 'ClinicalText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ClinicalText',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceAfter=2,
                leading=10
            ))
        
        # Bullet Text - Compact
        if 'BulletText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='BulletText',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.black,
                alignment=TA_LEFT,
                leftIndent=10,
                spaceAfter=0,
                leading=10,
                bulletIndent=5
            ))
        
        # ================== FOOTER STYLES ==================
        # Footer text - small, centered
        if 'FooterText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='FooterText',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceBefore=4,
                spaceAfter=2,
                leading=9
            ))

    def add_footer(self, canvas, doc):
        """Add footer at bottom of page with proper spacing"""
        canvas.saveState()
        
        # Draw thin horizontal line above footer
        line_y = 50  # Position from bottom
        canvas.setStrokeColor(colors.HexColor('#d1d5db'))
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, line_y, doc.width + doc.leftMargin, line_y)
        
        # Add footer text in 3 clean lines
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#6b7280'))
        
        # Line 1: Disclaimer
        canvas.drawCentredString(
            doc.width/2 + doc.leftMargin, 
            35, 
            "This report is generated using AI-based clinical decision support."
        )
        
        # Line 2: Warning
        canvas.drawCentredString(
            doc.width/2 + doc.leftMargin, 
            25, 
            "It does not replace professional medical diagnosis or treatment."
        )
        
        # Line 3: Copyright
        canvas.drawCentredString(
            doc.width/2 + doc.leftMargin, 
            15, 
            "© 2025 DiagnoSight AI | Apex Intelligence Group | All rights reserved."
        )
        
        canvas.restoreState()

    def generate_report_pdf(self, report_data, doctors_data=None, output_filename=None, image_path=None):
        """Generate EXACT ONE-PAGE professional medical report with uploaded image"""
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"medical_report_{timestamp}.pdf"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Create document with proper margins
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=36,    # 0.5 inch
            leftMargin=36,     # 0.5 inch
            topMargin=36,      # 0.5 inch
            bottomMargin=60    # Increased for footer space
        )
        
        story = []
        
        # ================== 1. HEADER (EXACT SPEC) ==================
        story.append(Paragraph("Medical Diagnostic Report", self.styles['ReportMainTitle']))
        story.append(Paragraph("DiagnoSight AI – Clinical Decision Support System", 
                              self.styles['SystemName']))
        story.append(Paragraph(f"Report Generated on: {datetime.now().strftime('%Y-%m-%d | %H:%M')}", 
                              self.styles['ReportDate']))
        
        # Thin horizontal separator
        header_line = Table([[""]], colWidths=[7.5*inch])
        header_line.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (0,0), 0.5, colors.HexColor('#d1d5db')),
            ('BOTTOMPADDING', (0,0), (0,0), 8),
        ]))
        story.append(header_line)
        story.append(Spacer(1, 12))
        
        # ================== 2. PATIENT & REPORT METADATA (COMPACT GRID) ==================
        patient_info = Table([
            [
                Paragraph("Patient Name:", self.styles['CompactLabel']),
                Paragraph(report_data.get("username", "Not specified"), self.styles['CompactValue']),
                Paragraph("Report ID:", self.styles['CompactLabel']),
                Paragraph(f"#{report_data.get('report_id', 'N/A')}", self.styles['CompactValue'])
            ],
            [
                Paragraph("AI Model Version:", self.styles['CompactLabel']),
                Paragraph("DiagnoSight AI v2.0", self.styles['CompactValue']),
                Paragraph("", self.styles['CompactLabel']),
                Paragraph("", self.styles['CompactValue'])
            ]
        ], colWidths=[1.1*inch, 2.2*inch, 1.1*inch, 2.2*inch])
        
        patient_info.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
        ]))
        
        story.append(patient_info)
        story.append(Spacer(1, 20))
        
        # ================== 3. DIAGNOSIS RESULT (EXACT SPEC) ==================
        disease_name = report_data.get("disease_name", "Unknown Diagnosis")
        confidence = report_data.get("confidence", 0)
        
        # Diagnosis Name - centered, bold
        story.append(Paragraph(disease_name.upper(), self.styles['DiagnosisName']))
        
        # Model Confidence - percentage only, no labels
        story.append(Paragraph(f"{confidence:.1f}%", self.styles['ConfidenceNumber']))
        story.append(Spacer(1, 20))
        
        # ================== 4. CLINICAL SUMMARY (MAX 8 LINES) ==================
        story.append(Paragraph("Clinical Summary", self.styles['SectionTitle']))
        
        # Get data for clinical summary
        description = report_data.get("description", "No description available.")
        symptoms = report_data.get("symptoms", [])
        causes = report_data.get("causes", ["Unknown"])
        treatments = report_data.get("treatment", [])
        
        # Create exactly 8 lines or less
        clinical_lines = []
        
        # Line 1-2: Condition Overview (2-3 lines)
        # Truncate description to fit
        desc_lines = description[:150] if len(description) > 150 else description
        clinical_lines.append(Paragraph(desc_lines, self.styles['ClinicalText']))
        clinical_lines.append(Spacer(1, 4))
        
        # Line 3-4: Key Symptoms (max 2 items)
        if symptoms and len(symptoms) >= 2:
            clinical_lines.append(Paragraph("Key Symptoms:", self.styles['ClinicalText']))
            symptoms_text = f"• {symptoms[0]} • {symptoms[1]}"
            clinical_lines.append(Paragraph(symptoms_text, self.styles['ClinicalText']))
            clinical_lines.append(Spacer(1, 4))
        elif symptoms:
            clinical_lines.append(Paragraph("Key Symptoms:", self.styles['ClinicalText']))
            clinical_lines.append(Paragraph(f"• {symptoms[0]}", self.styles['ClinicalText']))
            clinical_lines.append(Spacer(1, 4))
        
        # Line 5: Probable Cause / Risk Factor (1 line)
        if causes:
            cause_text = causes[0][:80] if len(causes[0]) > 80 else causes[0]
            clinical_lines.append(Paragraph(f"Probable Cause: {cause_text}", 
                                           self.styles['ClinicalText']))
            clinical_lines.append(Spacer(1, 4))
        
        # Line 6-7: Initial Care / Treatment Overview (1-2 lines)
        if treatments:
            treatment_text = treatments[0][:100] if len(treatments[0]) > 100 else treatments[0]
            clinical_lines.append(Paragraph("Initial Care:", self.styles['ClinicalText']))
            clinical_lines.append(Paragraph(f"• {treatment_text}", self.styles['ClinicalText']))
        
        # Ensure we don't exceed 8 visual lines
        if len(clinical_lines) > 8:
            clinical_lines = clinical_lines[:8]
        
        # Add all clinical lines
        for line in clinical_lines:
            story.append(line)
        
        story.append(Spacer(1, 20))
        
        # ================== 5. CLINICAL NOTES (1-2 LINES MAX) ==================
        story.append(Paragraph("Clinical Notes", self.styles['SectionTitle']))
        
        severity = report_data.get("severity", "Unknown")
        # Determine if immediate consultation is needed
        immediate_consult = severity.lower() in ["high", "severe", "critical"]
        
        notes_text = f"Condition severity: {severity}. "
        notes_text += "Immediate consultation advised." if immediate_consult else "Routine follow-up recommended."
        
        story.append(Paragraph(notes_text, self.styles['ClinicalText']))
        story.append(Spacer(1, 20))
        
        # ================== 6. RECOMMENDED DOCTORS TABLE (MAX 3) ==================
        if doctors_data and len(doctors_data) > 0:
            story.append(Paragraph("Recommended Specialists", self.styles['SectionTitle']))
            story.append(Spacer(1, 8))
            
            # Prepare table data - MAX 3 DOCTORS
            doctors_table_data = [
                [
                    Paragraph("Doctor Name", self.styles['CompactLabel']),
                    Paragraph("Specialty", self.styles['CompactLabel']),
                    Paragraph("Hospital / City", self.styles['CompactLabel']),
                    Paragraph("Contact", self.styles['CompactLabel'])
                ]
            ]
            
            # Add exactly 3 doctors or fewer
            for doctor in doctors_data[:3]:
                doctors_table_data.append([
                    Paragraph(doctor.get('name', 'N/A'), self.styles['ClinicalText']),
                    Paragraph(doctor.get('specialization', 'N/A'), self.styles['ClinicalText']),
                    Paragraph(f"{doctor.get('hospital', 'N/A')}, {doctor.get('city', 'N/A')}", 
                            self.styles['ClinicalText']),
                    Paragraph(doctor.get('contact', 'N/A'), self.styles['ClinicalText'])
                ])
            
            # Calculate column widths for perfect fit
            col_widths = [1.6*inch, 1.4*inch, 2.2*inch, 1.4*inch]
            
            doctors_table = Table(doctors_table_data, colWidths=col_widths)
            doctors_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1a365d')),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                # Subtle row alternation
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fafafa')])
            ]))
            
            story.append(doctors_table)
            story.append(Spacer(1, 15))
        
        # ================== 7. UPLOADED IMAGE SECTION ==================
        if image_path and os.path.exists(image_path):
            try:
                # Add image section title
                story.append(Paragraph("Uploaded Skin Image", self.styles['SectionTitle']))
                story.append(Spacer(1, 8))
                
                # Load and resize image for PDF
                pil_image = PILImage.open(image_path)
                
                # Calculate dimensions to fit within PDF (max 3.5 inches width)
                max_width = 3.5 * 72  # Convert inches to points
                max_height = 2.5 * 72  # Convert inches to points
                
                # Get original dimensions
                orig_width, orig_height = pil_image.size
                
                # Calculate aspect ratio
                aspect_ratio = orig_width / orig_height
                
                # Calculate new dimensions while maintaining aspect ratio
                if aspect_ratio > 1:
                    # Image is wider than tall
                    new_width = min(max_width, orig_width)
                    new_height = new_width / aspect_ratio
                else:
                    # Image is taller than wide
                    new_height = min(max_height, orig_height)
                    new_width = new_height * aspect_ratio
                
                # Ensure dimensions don't exceed maximums
                if new_width > max_width:
                    new_width = max_width
                    new_height = new_width / aspect_ratio
                
                if new_height > max_height:
                    new_height = max_height
                    new_width = new_height * aspect_ratio
                
                # Convert to ReportLab Image with proper dimensions
                img = ReportLabImage(image_path, width=new_width, height=new_height)
                
                # Center the image in a table
                img_table = Table([[img]], colWidths=[7.5*inch])
                img_table.setStyle(TableStyle([
                    ('ALIGN', (0,0), (0,0), 'CENTER'),
                    ('VALIGN', (0,0), (0,0), 'MIDDLE'),
                    ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f8fafc')),
                    ('GRID', (0,0), (0,0), 0.5, colors.HexColor('#d1d5db')),
                    ('TOPPADDING', (0,0), (0,0), 8),
                    ('BOTTOMPADDING', (0,0), (0,0), 8),
                    ('LEFTPADDING', (0,0), (0,0), 0),
                    ('RIGHTPADDING', (0,0), (0,0), 0),
                ]))
                
                story.append(img_table)
                
                # Add image caption
                image_filename = os.path.basename(image_path)
                caption_text = f"Image: {image_filename} | Analyzed for: {disease_name}"
                caption = Paragraph(caption_text, self.styles['ClinicalText'])
                caption_table = Table([[caption]], colWidths=[7.5*inch])
                caption_table.setStyle(TableStyle([
                    ('ALIGN', (0,0), (0,0), 'CENTER'),
                    ('VALIGN', (0,0), (0,0), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (0,0), 4),
                    ('BOTTOMPADDING', (0,0), (0,0), 12),
                ]))
                story.append(caption_table)
                
            except Exception as e:
                # If image can't be loaded, show a placeholder message
                print(f"Error loading image for PDF: {e}")
                error_msg = "⚠️ Image could not be included in report"
                story.append(Paragraph(error_msg, self.styles['ClinicalText']))
                story.append(Spacer(1, 10))
        
        # ================== 8. ADD FLEXIBLE SPACER ==================
        # Add some space before footer starts
        story.append(Spacer(1, 30))
        
        # ================== BUILD PDF WITH FOOTER ==================
        try:
            doc.build(story, onFirstPage=self.add_footer, onLaterPages=self.add_footer)
            return output_path, output_filename
        except Exception as e:
            print(f"Adjusting layout for one-page fit: {e}")
            return self._build_compact_pdf(doc, story, output_path, output_filename)
    
    def _build_compact_pdf(self, doc, story, output_path, output_filename):
        """Build a more compact version if content overflows"""
        # Reduce spacing in all elements by 20%
        for element in story:
            if hasattr(element, 'spaceBefore'):
                element.spaceBefore = max(2, element.spaceBefore * 0.8)
            if hasattr(element, 'spaceAfter'):
                element.spaceAfter = max(2, element.spaceAfter * 0.8)
            if isinstance(element, Spacer):
                element.height = element.height * 0.8
        
        # Rebuild with tighter spacing
        doc.build(story, onFirstPage=self.add_footer, onLaterPages=self.add_footer)
        return output_path, output_filename


# Singleton instance
pdf_generator = PDFReportGenerator()