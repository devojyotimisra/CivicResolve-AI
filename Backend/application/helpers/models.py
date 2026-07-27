from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from application.extensions.db_extn import Base


IST = timezone(timedelta(hours=5, minutes=30))

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'))
)


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password = Column(String(256), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(50),  default='citizen', nullable=False, index=True)
    badge_id = Column(String(50), unique=True, nullable=True, index=True)
    department_id = Column(Integer, ForeignKey('departments.id', ondelete='SET NULL'), nullable=True, index=True)
    _department = Column('department', String(100), nullable=True, index=True)
    phone = Column(String(50),  nullable=True)
    address = Column(String(500), nullable=True)
    pincode = Column(String(20),  nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    roles = relationship('Role', secondary=user_roles, backref='users')
    department_rel = relationship('Department', backref='users_in_dept')

    @hybrid_property
    def department(self):
        if self.department_rel and self.department_rel.name:
            return self.department_rel.name
        return self._department

    @department.setter
    def department(self, value):
        self._department = value

    @department.expression
    def department(cls):
        return cls._department

    def has_role(self, role_name):
        return self.role == role_name or any(r.name == role_name for r in self.roles)


class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)


class BillType(Base):
    __tablename__ = 'bill_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)


class Complaint(Base):
    __tablename__ = 'complaints'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(20), unique=True, nullable=False, index=True)
    assigned_officer_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    assigned_officer_name = Column(String(100), nullable=True)
    department_id = Column(Integer, ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    department = Column(String(100), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(500), nullable=True)
    submitted_photo = Column(String(500), nullable=True)
    status = Column(String(50),  default='Submitted', nullable=False)
    severity = Column(String(50),  default='Normal',    nullable=False)
    resolution_photo = Column(String(500), nullable=True)
    resolution_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))
    updated_at = Column(DateTime, default=lambda: datetime.now(IST), onupdate=lambda: datetime.now(IST))
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    department_rel = relationship('Department', backref='complaints')
    assigned_officer = relationship('User', foreign_keys=[assigned_officer_id], backref='assigned_complaints')
    updates = relationship('ComplaintUpdate', backref='complaint',
                           order_by='ComplaintUpdate.created_at.asc()',
                           cascade='all, delete-orphan')


class ComplaintUpdate(Base):
    __tablename__ = 'complaint_updates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(Integer, ForeignKey('complaints.id', ondelete='CASCADE'), nullable=False)
    updated_by_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    updated_by_name = Column(String(100), nullable=True)
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))

    updated_by = relationship('User')


class UtilityBill(Base):
    __tablename__ = 'utility_bills'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    citizen_name = Column(String(100), nullable=True)
    bill_type_id = Column(Integer, ForeignKey('bill_types.id', ondelete='SET NULL'), nullable=True)
    bill_type = Column(String(100), nullable=False)
    bill_number = Column(String(50),  unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(Date, nullable=False)
    period = Column(String(200), nullable=True)
    status = Column(String(50),  default='Pending', nullable=False)
    generated_at = Column(Date, nullable=False, default=lambda: datetime.now(IST).date())
    paid_at = Column(DateTime, nullable=True)
    payment_ref = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))

    type_rel = relationship('BillType', backref='bills')
    user = relationship('User', backref='bills')


class Facility(Base):
    __tablename__ = 'facilities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    facility_type = Column(String(100), nullable=False)
    address = Column(String(500), nullable=False)
    pincode = Column(String(20),  nullable=False)
    price_per_day = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    amenities = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)


class FacilityBooking(Base):
    __tablename__ = 'facility_bookings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    facility_id = Column(Integer, ForeignKey('facilities.id', ondelete='SET NULL'), nullable=True)
    citizen_name = Column(String(100), nullable=True)
    facility_name = Column(String(200), nullable=True)
    booking_reference = Column(String(20),  unique=True, nullable=False)
    booked_date = Column(Date, nullable=False)
    amount_paid = Column(Float, nullable=False)
    purpose = Column(String(500), nullable=True)
    status = Column(String(50),  default='Confirmed', nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))

    user = relationship('User',     backref='bookings')
    facility = relationship('Facility', backref='bookings')


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    target_role = Column(String(50), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notif_type = Column(String(50),  default='info', nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(IST))

    user = relationship('User', backref='notifications')
