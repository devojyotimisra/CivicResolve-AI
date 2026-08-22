import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from application.helpers.config import Config
from application.middlewares.init_config import init_config
from application.middlewares.init_db import initialize_database
from application.middlewares.init_exceptions import init_exceptions
from application.middlewares.init_token_refresh import refresh_token_middleware
from application.resources.citizen.citizen_all_bookings_list_resource import (
    router as citizen_all_bookings_router,
)
from application.resources.citizen.citizen_bill_pay_resource import (
    router as citizen_bill_pay_router,
)
from application.resources.citizen.citizen_bills_list_resource import (
    router as citizen_bills_router,
)
from application.resources.citizen.citizen_bookings_list_resource import (
    router as citizen_bookings_router,
)
from application.resources.citizen.citizen_dashboard_resource import (
    router as citizen_dash_router,
)
from application.resources.citizen.citizen_facilities_list_resource import (
    router as citizen_facilities_router,
)
from application.resources.citizen.citizen_facility_book_resource import (
    router as citizen_facility_book_router,
)
from application.resources.citizen.citizen_facility_detail_resource import (
    router as citizen_facility_detail_router,
)
from application.resources.citizen.citizen_profile_fetch_resource import (
    router as citizen_profile_fetch_router,
)
from application.resources.citizen.citizen_profile_update_resource import (
    router as citizen_profile_update_router,
)
from application.resources.citizen.citizen_search_resource import router as citizen_search_router
from application.resources.commissioner.commissioner_assign_officer_resource import (
    router as comm_assign_router,
)
from application.resources.commissioner.commissioner_bill_add_resource import (
    router as comm_bill_add_router,
)
from application.resources.commissioner.commissioner_bill_type_add_resource import (
    router as comm_bill_type_add_router,
)
from application.resources.commissioner.commissioner_bill_type_delete_resource import (
    router as comm_bill_type_delete_router,
)
from application.resources.commissioner.commissioner_bill_type_update_resource import (
    router as comm_bill_type_update_router,
)
from application.resources.commissioner.commissioner_bill_types_list_resource import (
    router as comm_bill_types_list_router,
)
from application.resources.commissioner.commissioner_bills_list_resource import (
    router as comm_bills_list_router,
)
from application.resources.commissioner.commissioner_bookings_list_resource import (
    router as comm_bookings_list_router,
)
from application.resources.commissioner.commissioner_categories_list_resource import (
    router as comm_categories_list_router,
)
from application.resources.commissioner.commissioner_category_add_resource import (
    router as comm_category_add_router,
)
from application.resources.commissioner.commissioner_category_delete_resource import (
    router as comm_category_delete_router,
)
from application.resources.commissioner.commissioner_citizens_resource import (
    router as comm_citizens_router,
)
from application.resources.commissioner.commissioner_complaint_detail_resource import (
    router as comm_complaint_detail_router,
)
from application.resources.commissioner.commissioner_complaints_list_resource import (
    router as comm_complaints_router,
)
from application.resources.commissioner.commissioner_dashboard_resource import (
    router as comm_dash_router,
)
from application.resources.commissioner.commissioner_facilities_list_resource import (
    router as comm_facilities_list_router,
)
from application.resources.commissioner.commissioner_facility_add_resource import (
    router as comm_facility_add_router,
)
from application.resources.commissioner.commissioner_facility_delete_resource import (
    router as comm_facility_delete_router,
)
from application.resources.commissioner.commissioner_facility_type_add_resource import (
    router as comm_facility_type_add_router,
)
from application.resources.commissioner.commissioner_facility_type_delete_resource import (
    router as comm_facility_type_delete_router,
)
from application.resources.commissioner.commissioner_facility_type_update_resource import (
    router as comm_facility_type_update_router,
)
from application.resources.commissioner.commissioner_facility_types_list_resource import (
    router as comm_facility_types_list_router,
)
from application.resources.commissioner.commissioner_facility_update_resource import (
    router as comm_facility_update_router,
)
from application.resources.commissioner.commissioner_officer_add_resource import (
    router as comm_officer_add_router,
)
from application.resources.commissioner.commissioner_officer_delete_resource import (
    router as comm_officer_delete_router,
)
from application.resources.commissioner.commissioner_officer_update_resource import (
    router as comm_officer_update_router,
)
from application.resources.commissioner.commissioner_officers_list_resource import (
    router as comm_officers_list_router,
)
from application.resources.commissioner.commissioner_profile_fetch_resource import (
    router as comm_profile_fetch_router,
)
from application.resources.commissioner.commissioner_profile_update_resource import (
    router as comm_profile_update_router,
)
from application.resources.commissioner.commissioner_search_resource import (
    router as comm_search_router,
)
from application.resources.general.anonymous_complaint_resource import (
    router as anon_complaint_router,
)
from application.resources.general.citizen_resolution_resource import (
    router as citizen_resolution_router,
)
from application.resources.general.login_resource import router as login_router
from application.resources.general.notification_clear_all_resource import (
    router as notification_clear_all_router,
)
from application.resources.general.notification_delete_resource import (
    router as notification_delete_router,
)
from application.resources.general.notification_list_resource import (
    router as notification_list_router,
)
from application.resources.general.notification_mark_all_read_resource import (
    router as notification_mark_all_read_router,
)
from application.resources.general.notification_mark_read_resource import (
    router as notification_mark_read_router,
)
from application.resources.general.notification_mark_unread_resource import (
    router as notification_mark_unread_router,
)
from application.resources.general.password_update_resource import (
    router as password_update_router,
)
from application.resources.general.signup_resource import router as signup_router
from application.resources.general.track_complaint_resource import (
    router as track_complaint_router,
)
from application.resources.officer.officer_dashboard_resource import (
    router as officer_dash_router,
)
from application.resources.officer.officer_history_resource import (
    router as officer_history_router,
)
from application.resources.officer.officer_profile_fetch_resource import (
    router as officer_profile_fetch_router,
)
from application.resources.officer.officer_profile_update_resource import (
    router as officer_profile_update_router,
)
from application.resources.officer.officer_search_resource import router as officer_search_router
from application.resources.officer.officer_ticket_detail_resource import (
    router as officer_ticket_detail_router,
)
from application.resources.officer.officer_ticket_resolve_resource import (
    router as officer_resolve_router,
)
from application.resources.officer.officer_ticket_update_status_resource import (
    router as officer_status_router,
)


def create_app():
    app = FastAPI(title="CivicResolve AI", version="0.1.0")

    init_config(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[app.state.config.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Refresh-Token"],
    )

    initialize_database(app)

    app.middleware("http")(refresh_token_middleware)

    init_exceptions(app)

    os.makedirs("uploads/complaints", exist_ok=True)
    os.makedirs("uploads/resolutions", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    prefix = "/api"

    app.include_router(login_router, prefix=prefix, tags=["auth"])
    app.include_router(signup_router, prefix=prefix, tags=["auth"])
    app.include_router(password_update_router, prefix=prefix, tags=["auth"])
    app.include_router(anon_complaint_router, prefix=prefix, tags=["public"])
    app.include_router(track_complaint_router, prefix=prefix, tags=["public"])
    app.include_router(citizen_resolution_router, prefix=prefix, tags=["public"])
    app.include_router(notification_list_router, prefix=prefix, tags=["notifications"])
    app.include_router(notification_mark_read_router, prefix=prefix, tags=["notifications"])
    app.include_router(notification_mark_unread_router, prefix=prefix, tags=["notifications"])
    app.include_router(notification_mark_all_read_router, prefix=prefix, tags=["notifications"])
    app.include_router(notification_delete_router, prefix=prefix, tags=["notifications"])
    app.include_router(notification_clear_all_router, prefix=prefix, tags=["notifications"])

    app.include_router(citizen_dash_router, prefix=prefix, tags=["citizen"])
    app.include_router(citizen_bills_router, prefix=prefix, tags=["citizen"])
    app.include_router(citizen_bill_pay_router, prefix=prefix, tags=["citizen"])
    app.include_router(citizen_facilities_router, prefix=prefix, tags=["citizen"])
    app.include_router(citizen_facility_detail_router, prefix=prefix, tags=["citizen"])
    app.include_router(citizen_facility_book_router, prefix=prefix, tags=["citizen"])
    app.include_router(citizen_bookings_router, prefix=prefix, tags=["citizen"])
    app.include_router(citizen_all_bookings_router, prefix=prefix, tags=["citizen"])
    app.include_router(citizen_search_router, prefix=prefix, tags=["citizen"])
    app.include_router(citizen_profile_fetch_router, prefix=prefix, tags=["citizen"])
    app.include_router(citizen_profile_update_router, prefix=prefix, tags=["citizen"])

    app.include_router(officer_dash_router, prefix=prefix, tags=["officer"])
    app.include_router(officer_ticket_detail_router, prefix=prefix, tags=["officer"])
    app.include_router(officer_status_router, prefix=prefix, tags=["officer"])
    app.include_router(officer_resolve_router, prefix=prefix, tags=["officer"])
    app.include_router(officer_history_router, prefix=prefix, tags=["officer"])
    app.include_router(officer_search_router, prefix=prefix, tags=["officer"])
    app.include_router(officer_profile_fetch_router, prefix=prefix, tags=["officer"])
    app.include_router(officer_profile_update_router, prefix=prefix, tags=["officer"])

    app.include_router(comm_dash_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_complaints_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_complaint_detail_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_assign_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_officers_list_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_officer_add_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_officer_update_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_officer_delete_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_facilities_list_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_facility_add_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_facility_update_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_facility_delete_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_facility_types_list_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_facility_type_add_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_facility_type_update_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_facility_type_delete_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_bookings_list_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_categories_list_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_category_add_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_category_delete_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_bills_list_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_bill_add_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_bill_types_list_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_bill_type_add_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_bill_type_update_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_bill_type_delete_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_citizens_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_search_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_profile_fetch_router, prefix=prefix, tags=["commissioner"])
    app.include_router(comm_profile_update_router, prefix=prefix, tags=["commissioner"])

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host=Config.HOST, port=Config.PORT, reload=True)
