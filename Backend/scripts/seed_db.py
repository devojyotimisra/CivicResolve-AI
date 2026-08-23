import argparse
import base64
import os
import random
import sys
from datetime import datetime, timedelta, timezone

from application.extensions import db_extn
from application.extensions.db_extn import Base, init_engine
from application.extensions.security_extn import hash_password
from application.helpers.config import Config
from application.helpers.models import (
    BillType,
    Complaint,
    ComplaintUpdate,
    Department,
    Facility,
    FacilityBooking,
    FacilityType,
    Notification,
    Role,
    User,
    UtilityBill,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


IST = timezone(timedelta(hours=5, minutes=30))

DUMMY_IMAGE_B64 = (
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)


def create_dummy_image(directory, prefix="img"):
    os.makedirs(directory, exist_ok=True)
    filename = f"{prefix}_{random.randint(1000, 9999)}.png"
    filepath = os.path.join(directory, filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(DUMMY_IMAGE_B64))
    return f"uploads/{os.path.basename(directory)}/{filename}"


INDIAN_FIRST_NAMES_M = [
    "Aarav",
    "Vihaan",
    "Aditya",
    "Arjun",
    "Sai",
    "Rohan",
    "Vikram",
    "Rahul",
    "Karthik",
    "Sanjay",
    "Deepak",
    "Manoj",
    "Gaurav",
    "Suresh",
    "Ramesh",
    "Kiran",
    "Tarun",
]
INDIAN_FIRST_NAMES_F = [
    "Priya",
    "Ananya",
    "Riya",
    "Diya",
    "Neha",
    "Sneha",
    "Pooja",
    "Gita",
    "Anita",
    "Divya",
    "Kavya",
    "Swati",
    "Shruti",
    "Meera",
]
INDIAN_LAST_NAMES = [
    "Sharma",
    "Singh",
    "Patel",
    "Kumar",
    "Iyer",
    "Reddy",
    "Gupta",
    "Desai",
    "Joshi",
    "Mehta",
    "Verma",
    "Nair",
    "Rao",
    "Chakraborty",
    "Pillai",
    "Bhat",
    "Das",
    "Tiwari",
    "Sen",
    "Menon",
    "Patil",
    "Gokhale",
    "Bose",
    "Banerjee",
    "Srinivasan",
]


def generate_indian_name(gender=None):
    if not gender:
        gender = random.choice(["M", "F"])
    first = (
        random.choice(INDIAN_FIRST_NAMES_M)
        if gender == "M"
        else random.choice(INDIAN_FIRST_NAMES_F)
    )
    last = random.choice(INDIAN_LAST_NAMES)
    return f"{first} {last}"


INDIAN_LOCATIONS = [
    "Anna Nagar, Chennai",
    "Jayanagar, Bengaluru",
    "Banjara Hills, Hyderabad",
    "Andheri West, Mumbai",
    "Connaught Place, New Delhi",
    "Salt Lake, Kolkata",
    "Koramangala, Bengaluru",
    "T Nagar, Chennai",
    "Bandra, Mumbai",
    "Vasant Kunj, New Delhi",
    "Gachibowli, Hyderabad",
    "Indiranagar, Bengaluru",
    "Powai, Mumbai",
    "Mylapore, Chennai",
]

FACILITIES_DATA = [
    {"name": "Swami Vivekananda Community Hall", "type": "Community Hall"},
    {"name": "Gandhi Maidan", "type": "Sports Ground"},
    {"name": "Nehru Park", "type": "Public Park"},
    {"name": "Tagore Kala Mandir", "type": "Auditorium"},
    {"name": "Sardar Patel Sports Complex", "type": "Sports Ground"},
    {"name": "Indira Gandhi Auditorium", "type": "Auditorium"},
    {"name": "Shivaji Park", "type": "Public Park"},
    {"name": "Anna Nagar Tower Park", "type": "Public Park"},
    {"name": "Jubilee Hills Community Centre", "type": "Community Hall"},
    {"name": "Besant Nagar Beach Pavilion", "type": "Community Hall"},
]


def add_notification(
    db, title, message, notif_type="info", created_at=None, user_id=None, target_role=None
):
    if not created_at:
        created_at = datetime.now(IST)

    if user_id:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notif_type=notif_type,
            created_at=created_at,
            is_read=random.random() > 0.5,
        )
        db.add(notif)

    if target_role:
        users = db.query(User).filter(User.roles.any(Role.name == target_role)).all()
        for u in users:
            if u.id != user_id:
                notif = Notification(
                    user_id=u.id,
                    title=title,
                    message=message,
                    notif_type=notif_type,
                    created_at=created_at,
                    is_read=random.random() > 0.5,
                )
                db.add(notif)


def seed(clear=True):
    init_engine(Config.SQLALCHEMY_DATABASE_URI)

    if clear:
        Base.metadata.drop_all(bind=db_extn.engine)

    from app import create_app

    app = create_app()

    db = db_extn.SessionLocal()

    try:
        roles = {r.name: r for r in db.query(Role).all()}
        if not roles:
            return

        dept_names = [
            "Water & Sanitation",
            "Roads & Transport",
            "Electricity",
            "Public Health",
            "Parks & Recreation",
        ]
        departments = [Department(name=name) for name in dept_names]
        db.add_all(departments)
        db.commit()

        bill_type_names = ["Water Bill", "Property Tax", "Electricity Bill", "Garbage Collection"]
        bill_types = [BillType(name=name) for name in bill_type_names]
        db.add_all(bill_types)
        db.commit()

        facility_type_names = ["Community Hall", "Sports Ground", "Auditorium", "Public Park"]
        facility_types = [FacilityType(name=name) for name in facility_type_names]
        db.add_all(facility_types)
        db.commit()

        officers = []
        officer_counter = 1
        for dept in departments:
            for sl_no in range(1, 6):
                badge = f"OFF-{dept.id}{sl_no:02d}"
                officer = User(
                    email=f"officer{officer_counter}@cr.com",
                    password=hash_password(badge),
                    name=generate_indian_name(),
                    role="field_officer",
                    badge_id=badge,
                    department_id=dept.id,
                    phone=f"9876543{officer_counter:03d}",
                    is_active=True,
                )
                officer.roles.append(roles["field_officer"])
                db.add(officer)
                officers.append(officer)
                officer_counter += 1
        db.commit()

        citizens = []
        for i in range(1, 21):
            citizen = User(
                email=f"citizen{i}@cr.com",
                password=hash_password("Citizen@123"),
                name=generate_indian_name(),
                role="citizen",
                phone=f"99988877{i:02d}",
                address=f"{random.randint(1, 150)}, {random.choice(INDIAN_LOCATIONS)}",
                pincode=f"600{random.randint(10, 99)}",
                is_active=True,
            )
            citizen.roles.append(roles["citizen"])
            db.add(citizen)
            citizens.append(citizen)
        db.commit()

        facilities = []
        for f_data in FACILITIES_DATA:
            facility = Facility(
                name=f_data["name"],
                facility_type=f_data["type"],
                address=random.choice(INDIAN_LOCATIONS),
                pincode=f"600{random.randint(10, 99)}",
                price_per_day=random.choice([500.0, 1000.0, 2000.0, 5000.0]),
                capacity=random.choice([50, 100, 500, 1000]),
                description=f"A very nice {f_data['type'].lower()} available for public booking.",
                amenities=["Parking", "Restrooms", "Drinking Water"]
                if "Hall" in f_data["type"] or "Auditorium" in f_data["type"]
                else ["Open Space"],
                is_active=random.random() > 0.2,
            )
            db.add(facility)
            facilities.append(facility)
        db.commit()

        severities = ["Normal", "Critical"]
        statuses = [
            "Assigned",
            "En Route",
            "On Site",
            "In Progress",
            "Resolved",
            "Closed",
        ]

        upload_base = "uploads"

        for i in range(1, 501):
            citizen = random.choice(citizens)
            dept = random.choice(departments)
            dept_officers = [o for o in officers if o.department_id == dept.id]
            officer = random.choice(dept_officers)
            created_dt = datetime.now(IST) - timedelta(
                days=random.randint(1, 30), hours=random.randint(0, 23)
            )
            status = random.choices(statuses, weights=[10, 10, 10, 20, 25, 25])[0]

            photos = []
            if random.random() > 0.3:
                photos.append(create_dummy_image(f"{upload_base}/complaints", "comp"))

            related = []
            sev = random.choice(severities)
            if random.random() > 0.8:
                num_dupes = random.randint(1, 3)
                related = [f"CRA-{20000 + i}{d}" for d in range(num_dupes)]
                sev = "Critical"

            complaint = Complaint(
                token=f"CRA-{10000 + i}",
                title=f"Issue regarding {dept.name.lower()}",
                description=f"There is a major problem at {random.choice(INDIAN_LOCATIONS)}. Please resolve it ASAP.",
                location=random.choice(INDIAN_LOCATIONS),
                department_id=dept.id,
                department=dept.name,
                severity=sev,
                status=status,
                created_at=created_dt,
                updated_at=created_dt,
                submitted_photos=photos,
                assigned_officer_id=officer.id,
                assigned_officer_name=officer.name,
                related_tokens=related,
            )
            ai_update = ComplaintUpdate(
                complaint=complaint,
                updated_by_id=None,
                old_status="Processing",
                new_status="Assigned",
                note=f"Routed to {dept.name}, assigned to {officer.name}",
                created_at=created_dt,
            )
            db.add(ai_update)
            add_notification(
                db,
                title="New Complaint Filed",
                message=f"Complaint #{complaint.token}: {complaint.title}",
                notif_type="info",
                created_at=created_dt,
                target_role="commissioner",
            )
            add_notification(
                db,
                title="New Ticket Assigned",
                message=f"You have been auto-assigned to complaint #{complaint.token}",
                notif_type="info",
                created_at=created_dt,
                user_id=officer.id,
            )

            current_dt = created_dt
            current_status = "Assigned"

            if status in ["En Route", "On Site", "In Progress", "Resolved", "Closed"]:
                current_dt += timedelta(hours=random.randint(1, 5))
                step_status = status if status in ["En Route", "On Site"] else "In Progress"
                update_prog = ComplaintUpdate(
                    complaint=complaint,
                    updated_by_id=officer.id,
                    old_status=current_status,
                    new_status=step_status,
                    note=f"Status updated to {step_status}.",
                    created_at=current_dt,
                )
                db.add(update_prog)
                complaint.updated_at = current_dt
                current_status = step_status

                add_notification(
                    db,
                    title="Complaint Updated",
                    message=f"Your complaint #{complaint.token} is now {step_status}",
                    notif_type="info",
                    created_at=current_dt,
                    user_id=citizen.id,
                )

            if status in ["Resolved", "Closed"]:
                current_dt += timedelta(days=random.randint(1, 5))
                res_photos = []
                if random.random() > 0.2:
                    res_photos.append(create_dummy_image(f"{upload_base}/resolutions", "res"))

                complaint.resolution_note = (
                    "The issue has been completely fixed by the team. Attached photographic proof."
                )
                complaint.resolution_photos = res_photos
                complaint.resolved_at = current_dt
                complaint.updated_at = current_dt

                update_res = ComplaintUpdate(
                    complaint=complaint,
                    updated_by_id=officer.id,
                    old_status=current_status,
                    new_status="Resolved",
                    note="Resolved successfully.",
                    created_at=current_dt,
                )
                current_status = "Resolved"
                db.add(update_res)

                add_notification(
                    db,
                    title="Complaint Resolved",
                    message=f"Your complaint #{complaint.token} has been marked as Resolved",
                    notif_type="success",
                    created_at=current_dt,
                    user_id=citizen.id,
                )

            if status == "Closed":
                current_dt += timedelta(days=random.randint(1, 3))
                complaint.closed_at = current_dt
                complaint.updated_at = current_dt

                update_close = ComplaintUpdate(
                    complaint=complaint,
                    updated_by_id=citizen.id,
                    old_status=current_status,
                    new_status="Closed",
                    note="Citizen confirmed resolution.",
                    created_at=current_dt,
                )
                db.add(update_close)

                add_notification(
                    db,
                    title="Ticket Closed",
                    message=f"Ticket #{complaint.token} was closed by the citizen.",
                    notif_type="success",
                    created_at=current_dt,
                    user_id=officer.id,
                )

            db.add(complaint)

        db.commit()

        for i in range(1, 501):
            citizen = random.choice(citizens)
            btype = random.choice(bill_types)

            gen_dt = datetime.now(IST).date() - timedelta(days=random.randint(5, 60))
            gen_dt_time = datetime.combine(gen_dt, datetime.min.time()).replace(tzinfo=IST)
            due_dt = gen_dt + timedelta(days=15)

            status = random.choices(["Pending", "Paid"], weights=[50, 50])[0]

            bill = UtilityBill(
                user_id=citizen.id,
                bill_type_id=btype.id,
                bill_type=btype.name,
                bill_number=f"BILL-{10000 + i}",
                amount=round(random.uniform(200.0, 3000.0), 2),
                period=f"{gen_dt.strftime('%b %Y')}",
                generated_at=gen_dt,
                due_date=due_dt,
                status=status,
            )

            add_notification(
                db,
                title="Bill Generated",
                message=f"A new {btype.name} bill is available.",
                notif_type="info",
                created_at=gen_dt_time,
                user_id=citizen.id,
            )

            if bill.status == "Paid":
                paid_dt = datetime.now(IST) - timedelta(days=random.randint(1, 10))
                bill.paid_at = paid_dt
                bill.payment_ref = f"PAY-{random.randint(100000, 999999)}"

                add_notification(
                    db,
                    title="Payment Successful",
                    message=f"Your payment for {btype.name} was successful.",
                    notif_type="success",
                    created_at=paid_dt,
                    user_id=citizen.id,
                )

            db.add(bill)
        db.commit()

        for i in range(1, 201):
            citizen = random.choice(citizens)
            facility = random.choice(facilities)

            book_date = datetime.now(IST).date() + timedelta(days=random.randint(-15, 30))
            created_dt = datetime.combine(
                datetime.now(IST).date() - timedelta(days=random.randint(1, 5)), datetime.min.time()
            ).replace(tzinfo=IST)

            booking = FacilityBooking(
                user_id=citizen.id,
                facility_id=facility.id,
                facility_name=facility.name,
                booking_reference=f"BKG-{10000 + i}",
                booked_date=book_date,
                amount_paid=facility.price_per_day,
                payment_ref=f"PAY-{random.randint(100000, 999999)}",
                purpose="Community Event",
                created_at=created_dt,
            )
            db.add(booking)

            add_notification(
                db,
                title="Booking Confirmed",
                message=f"Your booking for {facility.name} on {book_date} is confirmed.",
                notif_type="success",
                created_at=created_dt,
                user_id=citizen.id,
            )
        db.commit()

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Seed the database with dummy data.")
    parser.add_argument("--no-clear", action="store_true", help="Do not clear existing data")
    args = parser.parse_args()

    seed(clear=not args.no_clear)


if __name__ == "__main__":
    main()
