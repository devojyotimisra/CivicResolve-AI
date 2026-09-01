from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class UserSchema(CamelModel):
    id: int
    email: str
    name: str
    role: str
    badge_id: Optional[str] = None
    department_id: Optional[int] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    is_active: bool
    active: Optional[bool] = None
    is_password_empty: Optional[bool] = None

    def model_post_init(self, __context: Any) -> None:
        if self.active is None:
            object.__setattr__(self, "active", self.is_active)


class DepartmentSchema(CamelModel):
    id: int
    name: str


class ComplaintUpdateSchema(CamelModel):
    id: int
    old_status: Optional[str] = None
    new_status: str
    note: Optional[str] = None
    created_at: Optional[datetime] = None


class ComplaintSchema(CamelModel):
    id: int
    token: str
    related_tokens: Optional[List[str]] = None
    assigned_officer_id: Optional[int] = None
    assigned_officer_name: Optional[str] = None
    department_id: Optional[int] = None
    department: Optional[str] = None
    title: str
    description: str
    location: Optional[str] = None
    submitted_photos: Optional[List[str]] = None
    status: str
    severity: str
    resolution_photos: Optional[List[str]] = None
    resolution_note: Optional[str] = None
    is_manually_reassigned: Optional[bool] = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


class TrackComplaintResponse(CamelModel):
    redirect_to_token: Optional[str] = None
    complaint: Optional[ComplaintSchema] = None
    updates: Optional[List[ComplaintUpdateSchema]] = None


class NotificationSchema(CamelModel):
    id: int
    user_id: Optional[int] = None
    title: str
    message: str
    notif_type: str
    is_read: bool
    created_at: Optional[datetime] = None


class UtilityBillSchema(CamelModel):
    id: int
    user_id: Optional[int] = None
    citizen_name: Optional[str] = None
    bill_type_id: Optional[int] = None
    bill_type: str
    bill_number: str
    amount: float
    due_date: date
    period: Optional[str] = None
    status: str
    generated_at: date
    paid_at: Optional[datetime] = None
    payment_ref: Optional[str] = None
    created_at: Optional[datetime] = None


class FacilitySchema(CamelModel):
    id: int
    name: str
    facility_type: str
    address: str
    pincode: str
    price_per_day: float
    capacity: Optional[int] = None
    description: Optional[str] = None
    amenities: Optional[Any] = None
    is_active: bool


class FacilityBookingSchema(CamelModel):
    id: int
    user_id: Optional[int] = None
    facility_id: Optional[int] = None
    citizen_name: Optional[str] = None
    facility_name: Optional[str] = None
    booking_reference: str
    booked_date: date
    amount_paid: float
    payment_ref: Optional[str] = None
    purpose: Optional[str] = None
    status: str = "Confirmed"
    created_at: Optional[datetime] = None


class AuthUserResponse(CamelModel):
    id: int
    email: str
    name: str
    role: str
    badge_id: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    is_password_empty: Optional[bool] = None


class AuthResponse(CamelModel):
    message: str
    token: str
    user: AuthUserResponse


class PasswordUpdateRequest(CamelModel):
    current_password: str
    new_password: str


class CitizenDashboardResponse(CamelModel):
    user_name: str
    total_bills_due: int
    upcoming_bookings_count: int
    pending_bills: List[UtilityBillSchema]
    upcoming_bookings: List[FacilityBookingSchema]


class CitizenPaymentReceiptSchema(CamelModel):
    bill_number: str
    bill_type: str
    amount: float
    paid_at: str
    transaction_id: str


class CitizenFacilityBookRequest(CamelModel):
    booked_date: Optional[str] = None
    purpose: Optional[str] = None


class CitizenFacilityBookResponse(CamelModel):
    message: str
    booking: FacilityBookingSchema


class CitizenBillPayResponse(CamelModel):
    message: str
    receipt: CitizenPaymentReceiptSchema


class CitizenFacilityDetailResponse(CamelModel):
    facility: FacilitySchema
    booked_dates: List[str]
    my_booked_dates: List[str]


class CitizenProfileUpdateRequest(CamelModel):
    email: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None


class CommissionerAssignOfficerRequest(CamelModel):
    officer_id: Optional[int] = None
    severity: Optional[str] = None


class CommissionerMergeRequest(CamelModel):
    master_id: int


class CommissionerBillAddRequest(CamelModel):
    user_id: Optional[int] = None
    citizen_id: Optional[int] = None
    bill_type: Optional[str] = None
    amount: Optional[float] = None
    due_date: Optional[str] = None
    period: Optional[str] = None


class CommissionerBillTypeRequest(CamelModel):
    name: Optional[str] = None


class CommissionerBillTypeResponse(CamelModel):
    message: str
    id: int
    name: str


class BillTypeSchema(CamelModel):
    id: int
    name: str


class CommissionerFacilityTypeRequest(CamelModel):
    name: Optional[str] = None


class CommissionerFacilityTypeResponse(CamelModel):
    message: str
    id: int
    name: str


class FacilityTypeSchema(CamelModel):
    id: int
    name: str


class CommissionerCategoryAddRequest(CamelModel):
    name: Optional[str] = None
    id: Optional[int] = None


class CommissionerComplaintDetailResponse(CamelModel):
    complaint: ComplaintSchema
    updates: List[ComplaintUpdateSchema]


class NameCount(CamelModel):
    name: str
    count: int


class StatusCount(CamelModel):
    status: str
    count: int


class TrendData(CamelModel):
    day: str
    filed: int
    resolved: int


class CommissionerDashboardResponse(CamelModel):
    total_complaints: int
    pending_complaints: int
    resolved_complaints: int
    closed_complaints: int
    critical_complaints: int
    total_officers: int
    total_citizens: int
    total_revenue: float
    bill_revenue: float
    booking_revenue: float
    complaints_by_category: List[NameCount]
    complaints_by_status: List[StatusCount]
    trend: List[TrendData]


class CommissionerFacilityRequest(CamelModel):
    name: Optional[str] = None
    facility_type: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    price_per_day: Optional[str | float] = None
    capacity: Optional[int] = None
    amenities: Optional[Any] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CommissionerOfficerAddRequest(CamelModel):
    email: Optional[str] = None
    name: Optional[str] = None
    badge_id: Optional[str] = None
    department: Optional[str] = None
    department_id: Optional[int] = None
    jurisdiction_zone: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None


class CommissionerOfficerUpdateRequest(CamelModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    active: Optional[bool] = None
    department: Optional[str | int] = None
    department_id: Optional[int] = None
    jurisdiction_zone: Optional[str] = None
    badge_id: Optional[str] = None


class AnonymousComplaintResponse(CamelModel):
    message: str
    tracking_token: str
    complaint_id: int


class OfficerDashboardResponse(CamelModel):
    officer_name: str
    department: Optional[str] = None
    jurisdiction_zone: Optional[str] = None
    assigned_tickets: List[ComplaintSchema]
    total_assigned: int


class OfficerHistoryResponse(CamelModel):
    history: List[ComplaintSchema]


class OfficerTicketDetailResponse(CamelModel):
    complaint: ComplaintSchema
    updates: List[ComplaintUpdateSchema]


class OfficerTicketUpdateStatusRequest(CamelModel):
    status: Optional[str] = None
    note: Optional[str] = None


class MessageResponse(CamelModel):
    message: str
