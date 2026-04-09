"""
PDF Generator — Creates patient bills and daily schedules.
"""

import logging
from datetime import date
from io import BytesIO
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from app.core.storage import storage
from app.features.booking.models import Booking

logger = logging.getLogger("careremind.pdf_generator")


class PDFGenerator:
    """Generates PDF documents for bookings and schedules."""

    @staticmethod
    async def generate_patient_bill(
        booking: Booking,
        patient_name: str,
        doctor_name: str,
        clinic_name: str,
    ) -> Optional[str]:
        """
        Generate a PDF bill for a confirmed booking.
        
        Returns:
            URL of the uploaded PDF, or None if failed
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=1,  # Center
            )
            story.append(Paragraph("Payment Receipt", title_style))
            story.append(Spacer(1, 0.3 * inch))

            # Clinic details
            clinic_style = ParagraphStyle(
                'Clinic',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#4a4a4a'),
                alignment=1,
            )
            story.append(Paragraph(f"<b>{clinic_name}</b>", clinic_style))
            story.append(Paragraph(f"Dr. {doctor_name}", clinic_style))
            story.append(Spacer(1, 0.5 * inch))

            # Booking details table
            data = [
                ['Booking ID:', booking.id[:8]],
                ['Patient Name:', patient_name],
                ['Date:', booking.booking_date.strftime('%d %B %Y')],
                ['Time:', booking.slot_time.strftime('%I:%M %p')],
                ['Serial Number:', f"#{booking.serial_number}" if booking.serial_number else "Pending"],
                ['Amount Paid:', f"₹{float(booking.amount):.2f}"],
                ['Payment ID:', booking.razorpay_payment_id or "N/A"],
                ['Status:', 'CONFIRMED'],
            ]

            table = Table(data, colWidths=[2 * inch, 4 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))

            story.append(table)
            story.append(Spacer(1, 0.5 * inch))

            # Footer
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#666666'),
                alignment=1,
            )
            story.append(Paragraph("Thank you for booking with us!", footer_style))
            story.append(Paragraph(f"Generated on {date.today().strftime('%d %B %Y')}", footer_style))

            # Build PDF
            doc.build(story)
            buffer.seek(0)

            # Upload to storage
            filename = f"bills/booking_{booking.id}.pdf"
            pdf_url = await storage.save(filename, buffer.read(), booking.tenant_id)

            logger.info("Generated patient bill PDF: %s", pdf_url)
            return pdf_url

        except Exception as e:
            logger.error("Failed to generate patient bill: %s", e, exc_info=True)
            return None

    @staticmethod
    async def generate_daily_schedule(
        schedule_date: date,
        clinic_name: str,
        doctor_name: str,
        bookings: List[Booking],
        walk_in_slots: int,
        tenant_id: str,
        clinic_location_id: str,
    ) -> Optional[str]:
        """
        Generate a daily schedule PDF with online bookings and walk-in slots.
        
        Returns:
            URL of the uploaded PDF, or None if failed
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=10,
                alignment=1,
            )
            story.append(Paragraph(f"Daily Appointment Schedule", title_style))
            
            # Date and clinic
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Normal'],
                fontSize=14,
                textColor=colors.HexColor('#4a4a4a'),
                alignment=1,
            )
            story.append(Paragraph(f"{schedule_date.strftime('%A, %d %B %Y')}", subtitle_style))
            story.append(Paragraph(f"{clinic_name} - Dr. {doctor_name}", subtitle_style))
            story.append(Spacer(1, 0.3 * inch))

            # Online bookings section
            if bookings:
                section_style = ParagraphStyle(
                    'Section',
                    parent=styles['Heading2'],
                    fontSize=14,
                    textColor=colors.HexColor('#2563eb'),
                    spaceAfter=10,
                )
                story.append(Paragraph("ONLINE BOOKINGS (Priority)", section_style))

                # Bookings table
                booking_data = [['Serial', 'Time', 'Patient Name', 'Phone']]
                
                for booking in bookings:
                    # Decrypt patient phone for display
                    from app.core.security import encryption_service
                    try:
                        phone = encryption_service.decrypt(booking.patient.phone_encrypted)
                        phone_display = f"...{phone[-4:]}"  # Show last 4 digits only
                    except:
                        phone_display = "N/A"
                    
                    booking_data.append([
                        f"#{booking.serial_number}",
                        booking.slot_time.strftime('%I:%M %p'),
                        booking.patient.name,
                        phone_display,
                    ])

                booking_table = Table(booking_data, colWidths=[0.8 * inch, 1.2 * inch, 2.5 * inch, 1.5 * inch])
                booking_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                ]))

                story.append(booking_table)
                story.append(Spacer(1, 0.4 * inch))

            # Walk-in slots section
            story.append(Paragraph("WALK-IN SLOTS", section_style))
            
            walk_in_data = [['Slot', 'Status']]
            for i in range(1, walk_in_slots + 1):
                walk_in_data.append([f"Walk-in #{i}", '[ ]'])

            walk_in_table = Table(walk_in_data, colWidths=[2 * inch, 2 * inch])
            walk_in_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#64748b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))

            story.append(walk_in_table)
            story.append(Spacer(1, 0.3 * inch))

            # Footer
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#666666'),
                alignment=1,
            )
            story.append(Paragraph(
                f"Total Online Bookings: {len(bookings)} | Walk-in Slots: {walk_in_slots}",
                footer_style
            ))
            story.append(Paragraph(
                f"Generated at {date.today().strftime('%d %B %Y')} 12:00 AM",
                footer_style
            ))

            # Build PDF
            doc.build(story)
            buffer.seek(0)

            # Upload to storage
            filename = f"schedules/{schedule_date.isoformat()}_clinic_{clinic_location_id}.pdf"
            pdf_url = await storage.save(filename, buffer.read(), tenant_id)

            logger.info("Generated daily schedule PDF: %s", pdf_url)
            return pdf_url

        except Exception as e:
            logger.error("Failed to generate daily schedule: %s", e, exc_info=True)
            return None


pdf_generator = PDFGenerator()

