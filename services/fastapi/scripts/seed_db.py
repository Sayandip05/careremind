"""
Database seeding script — Creates sample data for demo/testing.

Usage:
    python -m scripts.seed_db
"""

import asyncio
import sys
from pathlib import Path
from datetime import date, time, timedelta
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from app.core.database import async_session
from app.core.security import get_password_hash, encryption_service
import app.models  # Import all models to ensure relationships are resolved
from app.features.auth.models import Tenant, PlanType
from app.features.patients.models import Patient, PreferredChannel
from app.features.appointments.models import Appointment, UploadSource
from app.features.reminders.models import Reminder, ReminderStatus, ChannelType
from app.features.clinics.models import ClinicLocation
from app.features.booking.models import Booking, BookingStatus, PaymentStatus


async def seed_database():
    """Seed the database with sample data."""
    print("🌱 Seeding database...")
    
    async with async_session() as db:
        try:
            # Check if data already exists
            result = await db.execute(select(Tenant).where(Tenant.email == "demo@careremind.com"))
            if result.scalar_one_or_none():
                print("⚠️  Demo data already exists. Skipping...")
                return
            
            # 1. Create Demo Tenant (Doctor)
            print("Creating demo tenant...")
            tenant = Tenant(
                id=str(uuid.uuid4()),
                doctor_name="Dr. Rajesh Sharma",
                clinic_name="Sharma Clinic",
                email="demo@careremind.com",
                phone="+919876543210",
                specialty="general",
                language_preference="english",
                whatsapp_number="+919876543210",
                hashed_password=get_password_hash("Demo@123"),
                plan=PlanType.PRO,
                is_active=True,
                street="123 MG Road",
                city="Mumbai",
                pincode="400001",
                state="Maharashtra",
            )
            db.add(tenant)
            await db.flush()
            
            # 2. Create Clinic Locations
            print("Creating clinic locations...")
            clinic1 = ClinicLocation(
                id=str(uuid.uuid4()),
                tenant_id=tenant.id,
                clinic_name="Main Clinic - MG Road",
                address_line="123 MG Road, Fort",
                city="Mumbai",
                pincode="400001",
                state="Maharashtra",
                phone="+919876543210",
                is_active=True,
            )
            db.add(clinic1)
            
            clinic2 = ClinicLocation(
                id=str(uuid.uuid4()),
                tenant_id=tenant.id,
                clinic_name="Branch Clinic - Andheri",
                address_line="456 SV Road, Andheri West",
                city="Mumbai",
                pincode="400058",
                state="Maharashtra",
                phone="+919876543211",
                is_active=True,
            )
            db.add(clinic2)
            await db.flush()
            
            # 3. Create Sample Patients
            print("Creating sample patients...")
            patients_data = [
                {"name": "Ramesh Kumar", "phone": "+919876543201"},
                {"name": "Sita Devi", "phone": "+919876543202"},
                {"name": "Arjun Patel", "phone": "+919876543203"},
                {"name": "Priya Singh", "phone": "+919876543204"},
                {"name": "Vijay Reddy", "phone": "+919876543205"},
                {"name": "Lakshmi Iyer", "phone": "+919876543206"},
                {"name": "Suresh Gupta", "phone": "+919876543207"},
                {"name": "Anjali Mehta", "phone": "+919876543208"},
                {"name": "Karthik Rao", "phone": "+919876543209"},
                {"name": "Deepa Nair", "phone": "+919876543210"},
            ]
            
            patients = []
            for patient_data in patients_data:
                phone_hash = encryption_service.hash_phone(patient_data["phone"])
                phone_encrypted = encryption_service.encrypt(patient_data["phone"])
                
                patient = Patient(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant.id,
                    name=patient_data["name"],
                    phone_encrypted=phone_encrypted,
                    phone_hash=phone_hash,
                    preferred_channel=PreferredChannel.WHATSAPP,
                    has_whatsapp=True,
                    language_preference="english",
                    is_optout=False,
                )
                db.add(patient)
                patients.append(patient)
            
            await db.flush()
            
            # 4. Create Sample Appointments
            print("Creating sample appointments...")
            today = date.today()
            
            appointments = []
            for i, patient in enumerate(patients[:7]):
                visit_date = today - timedelta(days=30 - i * 3)
                next_visit_date = today + timedelta(days=7 + i * 2)
                
                appointment = Appointment(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant.id,
                    patient_id=patient.id,
                    visit_date=visit_date,
                    next_visit_date=next_visit_date,
                    source=UploadSource.EXCEL,
                )
                db.add(appointment)
                appointments.append(appointment)
            
            await db.flush()
            
            # 5. Create Sample Reminders
            print("Creating sample reminders...")
            for i, appointment in enumerate(appointments):
                # First reminder (7 days after visit)
                reminder1 = Reminder(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant.id,
                    patient_id=appointment.patient_id,
                    appointment_id=appointment.id,
                    reminder_number=1,
                    status=ReminderStatus.SENT if i < 3 else ReminderStatus.PENDING,
                    channel=ChannelType.WHATSAPP,
                    scheduled_at=appointment.visit_date + timedelta(days=7),
                    sent_at=appointment.visit_date + timedelta(days=7) if i < 3 else None,
                )
                db.add(reminder1)
                
                # Second reminder (30 days after visit)
                reminder2 = Reminder(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant.id,
                    patient_id=appointment.patient_id,
                    appointment_id=appointment.id,
                    reminder_number=2,
                    status=ReminderStatus.PENDING,
                    channel=ChannelType.WHATSAPP,
                    scheduled_at=appointment.visit_date + timedelta(days=30),
                )
                db.add(reminder2)
            
            await db.flush()
            
            # 6. Create Sample Bookings — spread across yesterday, today, tomorrow
            print("Creating sample bookings...")

            from datetime import datetime as dt, timezone as tz

            # (days_offset, patient_idx, clinic, hour, minute, serial, status)
            booking_schedule = [
                # Yesterday — completed
                (-1, 0, clinic1, 9,  0,  1, BookingStatus.COMPLETED),
                (-1, 1, clinic1, 9,  30, 2, BookingStatus.COMPLETED),
                (-1, 2, clinic2, 10, 0,  1, BookingStatus.COMPLETED),
                (-1, 3, clinic2, 10, 30, 2, BookingStatus.COMPLETED),
                (-1, 4, clinic1, 11, 0,  3, BookingStatus.COMPLETED),
                (-1, 5, clinic1, 11, 30, 4, BookingStatus.COMPLETED),
                (-1, 6, clinic2, 14, 0,  3, BookingStatus.COMPLETED),
                # Today — confirmed (shows on dashboard by default)
                (0,  7, clinic1, 9,  0,  1, BookingStatus.CONFIRMED),
                (0,  8, clinic1, 9,  30, 2, BookingStatus.CONFIRMED),
                (0,  9, clinic2, 10, 0,  1, BookingStatus.CONFIRMED),
                (0,  0, clinic1, 10, 30, 3, BookingStatus.CONFIRMED),
                (0,  1, clinic2, 11, 0,  2, BookingStatus.CONFIRMED),
                (0,  2, clinic1, 14, 0,  4, BookingStatus.CONFIRMED),
                (0,  3, clinic2, 14, 30, 3, BookingStatus.CONFIRMED),
                # Tomorrow — confirmed (upcoming)
                (1,  4, clinic1, 9,  0,  1, BookingStatus.CONFIRMED),
                (1,  5, clinic1, 9,  30, 2, BookingStatus.CONFIRMED),
                (1,  6, clinic2, 10, 0,  1, BookingStatus.CONFIRMED),
                (1,  7, clinic1, 11, 0,  3, BookingStatus.CONFIRMED),
                (1,  8, clinic2, 11, 30, 2, BookingStatus.CONFIRMED),
            ]

            total_bookings = 0
            for idx, (days_off, p_idx, clinic, hour, minute, serial, bstatus) in enumerate(booking_schedule):
                target_date = today + timedelta(days=days_off)
                pat = patients[p_idx]
                is_done = bstatus == BookingStatus.COMPLETED
                b = Booking(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant.id,
                    patient_id=pat.id,
                    clinic_location_id=clinic.id,
                    booking_date=target_date,
                    slot_time=time(hour, minute),
                    serial_number=serial,
                    status=bstatus,
                    payment_status=PaymentStatus.COMPLETED,
                    amount=200.00,
                    razorpay_order_id=f"order_demo_{idx}",
                    razorpay_payment_id=f"pay_demo_{idx}",
                    confirmed_at=dt.now(tz.utc) - timedelta(days=abs(days_off), hours=2),
                    completed_at=dt.now(tz.utc) - timedelta(days=abs(days_off)) if is_done else None,
                )
                db.add(b)
                total_bookings += 1

            await db.commit()
            
            print("✅ Database seeded successfully!")
            print("\n📊 Created:")
            print(f"  - 1 Demo Tenant (Doctor)")
            print(f"  - 2 Clinic Locations (Main + Branch)")
            print(f"  - {len(patients)} Patients")
            print(f"  - {len(appointments)} Appointments")
            print(f"  - {len(appointments) * 2} Reminders")
            print(f"  - {total_bookings} Bookings (yesterday: 7, today: 7, tomorrow: 5)")
            print("\n🔑 Demo Credentials:")
            print("  Email: demo@careremind.com")
            print("  Password: Demo@123")
            print("\n🚀 You can now login and explore the system!")
            
        except Exception as e:
            print(f"❌ Error seeding database: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())

