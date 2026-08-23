import io
import os
import subprocess
import tokenize
from pathlib import Path


def remove_comments(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    result = []
    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))

    has_comments = False
    for tok in tokens:
        token_type = tok[0]
        token_string = tok[1]
        if token_type == tokenize.COMMENT:
            has_comments = True
            continue
        result.append((token_type, token_string))

    if has_comments:
        new_source = tokenize.untokenize(result)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_source)


def process_directory(directory):
    for root, _, files in os.walk(directory):
        if ".venv" in root or "__pycache__" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py") and file != "pyproject.toml" and file != "generate_openapi.py":
                process_file = os.path.join(root, file)
                remove_comments(process_file)


def main():
    backend_dir = Path(__file__).resolve().parent.parent
    process_directory(backend_dir)
    subprocess.run(["uv", "run", "ruff", "check", "--fix", "."], cwd=backend_dir)
    subprocess.run(["uv", "run", "ruff", "format", "."], cwd=backend_dir)

    subprocess.run(
        [
            "uv",
            "run",
            "vulture",
            ".",
            "--ignore-names",
            "get_citizens,CommissionerSearchRequest,is_password_empty,google_login,ignore_aliases,get_commissioner_facility_types,upcoming_bookings_count,delete_commissioner_facility_type,officer_ticket_detail,commissioner_delete_facility,officer_profile_update,commissioner_required,citizen_respond_resolution,officer_history,citizen_profile_update,citizen_profile_fetch,citizen_search,updated_by_id,transaction_id,citizen_all_bookings_list,notifications,commissioner_bill_types_list,officer_update_ticket_status,commissioner_categories_list,citizen_bookings_list,set_sqlite_pragma,updated_by,citizen_required,model_post_init,commissioner_dashboard,citizen_facility_detail,commissioner_profile_update,updates,citizen_book_facility,commissioner_officers_list,sqlalchemy_integrity_error_handler,update_commissioner_facility_type,login,commissioner_create_bill_type,citizen_facilities_list,mark_all_as_read,commissioner_citizens_list,mark_as_unread,commissioner_complaints_list,officer_dashboard,add_commissioner_facility_type,commissioner_update_officer,generated_at,officer_name,list_notifications,complaints_by_status,commissioner_complaint_detail,citizen_name,day,officer_required,commissioner_update_bill_type,total_assigned,file_anonymous_complaint,receipt,officer_profile_fetch,officer_search,model_config,commissioner_profile_fetch,assigned_tickets,commissioner_update_facility,commissioner_bookings_list,user_name,citizen_dashboard,commissioner_assign_officer,booking_reference,commissioner_facilities_list,citizen_pay_bill,commissioner_delete_category,commissioner_add_officer,commissioner_delete_officer,commissioner_bills_list,commissioner_search,mark_as_read,history,commissioner_add_facility,connection_record,__context,commissioner_delete_bill_type,signup,commissioner_add_category,clear_all_notifications,delete_notification,redirect_to_token,citizen_bills_list,update_password,trend,officer_resolve_ticket,complaints_by_category,my_booked_dates,track_complaint,commissioner_issue_bill",
            "--exclude",
            ".venv,__pycache__,.ruff_cache,.pytest_cache,.git,tests",
        ],
        cwd=backend_dir,
    )


if __name__ == "__main__":
    main()
