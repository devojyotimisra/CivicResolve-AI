import base64
import json
import os

if not os.path.exists("dummy.jpg"):
    dummy_jpg_base64 = "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA="
    with open("dummy.jpg", "wb") as f:
        f.write(base64.b64decode(dummy_jpg_base64))
import re

collection = {
    "info": {
        "name": "CivicResolve AI - Exhaustive Automated Tests",
        "description": "Exhaustive tests covering all API endpoints mapped exactly from the codebase.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    },
    "item": [],
    "variable": [{"key": "base_url", "value": "http://127.0.0.1:8000", "type": "string"}],
}

base_url = "{{base_url}}"
items = collection["item"]
req_counter = 1


def req(
    name,
    method,
    url_path,
    token_var=None,
    body=None,
    test_script=None,
    pre_script=None,
    skip_default_test=False,
):
    global req_counter
    if url_path.startswith("http"):
        parts = url_path.replace("https://", "").split("/")
        url_dict = {"raw": url_path, "protocol": "https", "host": [parts[0]], "path": parts[1:]}
    else:
        url_dict = {
            "raw": f"{base_url}{url_path}",
            "host": ["{{base_url}}"],
            "path": [p for p in url_path.split("/") if p],
        }

    r = {
        "name": f"{req_counter}. {name}",
        "request": {"method": method.upper(), "header": [], "url": url_dict},
        "response": [],
    }
    req_counter += 1

    if token_var:
        r["request"]["auth"] = {
            "type": "bearer",
            "bearer": [{"key": "token", "value": f"{{{{{token_var}}}}}", "type": "string"}],
        }
    if body is not None:
        raw_body = json.dumps(body, indent=4)
        raw_body = re.sub(r'"(\{\{.*?\}\})"', r"\1", raw_body)
        r["request"]["body"] = {
            "mode": "raw",
            "raw": raw_body,
            "options": {"raw": {"language": "json"}},
        }

    events = []
    if pre_script:
        events.append(
            {
                "listen": "prerequest",
                "script": {
                    "exec": [line for line in pre_script.split("\n") if line.strip()],
                    "type": "text/javascript",
                },
            }
        )

    if skip_default_test:
        full_script = test_script or ""
    else:
        default_test = 'pm.test("Status code is 2xx", function () { pm.response.to.be.success; });'
        full_script = default_test + ("\n" + test_script if test_script else "")
    events.append(
        {
            "listen": "test",
            "script": {
                "exec": [line for line in full_script.split("\n") if line.strip()],
                "type": "text/javascript",
            },
        }
    )
    r["event"] = events
    items.append(r)
    return r


req(
    "Commissioner Login",
    "POST",
    "/api/login",
    body={"email": "comm@cr.com", "password": "COM-001"},
    test_script='pm.collectionVariables.set("comm_token", pm.response.json().token);',
)

req("Commissioner Profile", "GET", "/api/commissioner/profile", "comm_token")

req(
    "Commissioner Edit Profile",
    "PUT",
    "/api/commissioner/edit_profile",
    "comm_token",
    body={"name": "Head Commissioner", "phone": "1111111111"},
)

req(
    "Commissioner Update Password",
    "PUT",
    "/api/update_password",
    "comm_token",
    body={"currentPassword": "COM-001", "newPassword": "COM@001-Updated"},
)

req(
    "Commissioner Re-Login",
    "POST",
    "/api/login",
    body={"email": "comm@cr.com", "password": "COM@001-Updated"},
    test_script='pm.collectionVariables.set("comm_token", pm.response.json().token);',
)

req("Commissioner Dashboard", "GET", "/api/commissioner/dash", "comm_token")


req("Get Categories", "GET", "/api/commissioner/categories", "comm_token")

req(
    "Create Category 1 (Roads)",
    "POST",
    "/api/commissioner/category",
    "comm_token",
    body={"name": "Roads"},
)


req(
    "Fetch Category 1 ID",
    "GET",
    "/api/commissioner/categories",
    "comm_token",
    test_script='var cats = pm.response.json().categories;\nvar found = cats.find(function(c){ return c.name === "Roads"; });\nif(found) pm.collectionVariables.set("category_id", found.id);',
)

req(
    "Create Category 2 (Garbage)",
    "POST",
    "/api/commissioner/category",
    "comm_token",
    body={"name": "Garbage"},
)

req(
    "Fetch Category 2 ID",
    "GET",
    "/api/commissioner/categories",
    "comm_token",
    test_script='var cats = pm.response.json().categories;\nvar found = cats.find(function(c){ return c.name === "Garbage"; });\nif(found) pm.collectionVariables.set("temp_cat_id", found.id);',
)

req(
    "Update Category 2",
    "POST",
    "/api/commissioner/category",
    "comm_token",
    body={"id": "{{temp_cat_id}}", "name": "Garbage Updated"},
)

req("Delete Category 2", "DELETE", "/api/commissioner/category/{{temp_cat_id}}", "comm_token")


req("Get Facility Types", "GET", "/api/commissioner/facility-types", "comm_token")

req(
    "Create Facility Type 1",
    "POST",
    "/api/commissioner/facility-type",
    "comm_token",
    body={"name": "Community Hall"},
    test_script='pm.collectionVariables.set("fac_type_id", pm.response.json().id);',
)

req(
    "Create Facility Type 2",
    "POST",
    "/api/commissioner/facility-type",
    "comm_token",
    body={"name": "Park"},
    test_script='pm.collectionVariables.set("temp_fac_type", pm.response.json().id);',
)

req(
    "Update Facility Type 2",
    "PUT",
    "/api/commissioner/facility-type/{{temp_fac_type}}",
    "comm_token",
    body={"name": "Updated Park"},
)

req(
    "Delete Facility Type 2",
    "DELETE",
    "/api/commissioner/facility-type/{{temp_fac_type}}",
    "comm_token",
)


req("Get Facilities", "GET", "/api/commissioner/facilities", "comm_token")

req(
    "Create Facility 1 (Town Hall)",
    "POST",
    "/api/commissioner/facility",
    "comm_token",
    body={
        "name": "Town Hall",
        "description": "Town hall description",
        "address": "Center Street 1",
        "pincode": "111111",
        "facilityType": "Community Hall",
        "capacity": 500,
        "pricePerDay": 100,
    },
)

req(
    "Fetch Facility 1 ID",
    "GET",
    "/api/commissioner/facilities",
    "comm_token",
    test_script='var facs = pm.response.json().facilities;\nvar found = facs.find(function(f){ return f.name === "Town Hall"; });\nif(found) pm.collectionVariables.set("fac_id", found.id);',
)

req(
    "Create Facility 2 (Temp Hall)",
    "POST",
    "/api/commissioner/facility",
    "comm_token",
    body={
        "name": "Temp Hall",
        "description": "Temp hall description",
        "address": "Center Street 2",
        "pincode": "222222",
        "facilityType": "Park",
        "capacity": 100,
        "pricePerDay": 50,
    },
)

req(
    "Fetch Facility 2 ID",
    "GET",
    "/api/commissioner/facilities",
    "comm_token",
    test_script='var facs = pm.response.json().facilities;\nvar found = facs.find(function(f){ return f.name === "Temp Hall"; });\nif(found) pm.collectionVariables.set("temp_fac", found.id);',
)

req(
    "Update Facility 2",
    "PUT",
    "/api/commissioner/facility/{{temp_fac}}",
    "comm_token",
    body={
        "name": "Temp Hall Updated",
        "description": "Temp hall updated",
        "address": "Center Street 2",
        "pincode": "222222",
        "facilityType": "Park",
        "capacity": 150,
        "pricePerDay": 60,
    },
    test_script="""
pm.test("Facility updated successfully", function () { pm.expect(pm.response.json().message).to.eql("Facility updated successfully"); });
""",
)

req("Delete Facility 2", "DELETE", "/api/commissioner/facility/{{temp_fac}}", "comm_token")


req("Get Bill Types", "GET", "/api/commissioner/bill_types", "comm_token")

req(
    "Create Bill Type 1",
    "POST",
    "/api/commissioner/bill_type",
    "comm_token",
    body={"name": "Water Tax"},
    test_script='pm.collectionVariables.set("bill_type_id", pm.response.json().id);',
)

req(
    "Create Bill Type 2",
    "POST",
    "/api/commissioner/bill_type",
    "comm_token",
    body={"name": "Temp Tax"},
    test_script='pm.collectionVariables.set("temp_bill_type", pm.response.json().id);',
)

req(
    "Update Bill Type 2",
    "PUT",
    "/api/commissioner/bill_type/{{temp_bill_type}}",
    "comm_token",
    body={"name": "Temp Tax Updated"},
)

req("Delete Bill Type 2", "DELETE", "/api/commissioner/bill_type/{{temp_bill_type}}", "comm_token")


req(
    "Get Officers",
    "GET",
    "/api/commissioner/officers",
    "comm_token",
    test_script="""
pm.test("Has officers array", function () { pm.expect(pm.response.json().officers).to.be.an("array"); });
""",
)

req(
    "Create Officer 1",
    "POST",
    "/api/commissioner/officer",
    "comm_token",
    body={
        "name": "Officer One",
        "email": "officer1@cr.com",
        "password": "Password@123",
        "phone": "1234567890",
        "departmentId": "{{category_id}}",
        "department": "Roads",
        "badgeId": "OFF-1",
    },
)


req(
    "Fetch Officer 1 ID",
    "GET",
    "/api/commissioner/officers",
    "comm_token",
    test_script='var offs = pm.response.json().officers;\nvar found = offs.find(function(o){ return o.email === "officer1@cr.com"; });\nif(found) pm.collectionVariables.set("officer_id", found.id);',
)

req(
    "Create Officer 2",
    "POST",
    "/api/commissioner/officer",
    "comm_token",
    body={
        "name": "Officer Two",
        "email": "officer2@cr.com",
        "password": "Password@123",
        "phone": "1234567891",
        "departmentId": "{{category_id}}",
        "department": "Roads",
        "badgeId": "OFF-2",
    },
)

req(
    "Fetch Officer 2 ID",
    "GET",
    "/api/commissioner/officers",
    "comm_token",
    test_script='var offs = pm.response.json().officers;\nvar found = offs.find(function(o){ return o.email === "officer2@cr.com"; });\nif(found) pm.collectionVariables.set("temp_off", found.id);',
)

req(
    "Update Officer 2",
    "PUT",
    "/api/commissioner/officer/{{temp_off}}",
    "comm_token",
    body={"name": "Officer Two Upd", "phone": "1234567892"},
)

req("Delete Officer 2", "DELETE", "/api/commissioner/officer/{{temp_off}}", "comm_token")


req(
    "Create Officer 3",
    "POST",
    "/api/commissioner/officer",
    "comm_token",
    body={
        "name": "Officer Three",
        "email": "officer3@cr.com",
        "password": "Password@123",
        "phone": "1234567895",
        "departmentId": "{{category_id}}",
        "department": "Roads",
        "badgeId": "OFF-3",
    },
)

req(
    "Fetch Officer 3 ID",
    "GET",
    "/api/commissioner/officers",
    "comm_token",
    test_script='var offs = pm.response.json().officers;\nvar found = offs.find(function(o){ return o.email === "officer3@cr.com"; });\nif(found) pm.collectionVariables.set("officer3_id", found.id);',
)


req(
    "Citizen Signup",
    "POST",
    "/api/signup",
    body={
        "email": "cit@cr.com",
        "password": "Password@123",
        "name": "Citizen Test",
        "phone": "9999999999",
        "address": "Street 123",
        "pincode": "123456",
    },
    test_script='pm.collectionVariables.set("cit_token", pm.response.json().token);\npm.collectionVariables.set("cit_id", pm.response.json().user.id);',
)

req(
    "Citizen Login",
    "POST",
    "/api/login",
    body={"email": "cit@cr.com", "password": "Password@123"},
    test_script='pm.collectionVariables.set("cit_token", pm.response.json().token);',
)

req(
    "Citizen Profile",
    "GET",
    "/api/citizen/profile",
    "cit_token",
    test_script="""
pm.test("Profile has email", function () { pm.expect(pm.response.json().email).to.exist; });
""",
)
req(
    "Citizen Edit Profile",
    "PUT",
    "/api/citizen/edit_profile",
    "cit_token",
    body={
        "name": "Citizen Updated",
        "phone": "9876543210",
        "address": "123 Citizen St",
        "pincode": "654321",
    },
    test_script="""
pm.test("Profile updated successfully", function () { pm.expect(pm.response.json().message).to.eql("Profile updated successfully"); });
""",
)

req(
    "Citizen Update Password",
    "PUT",
    "/api/update_password",
    "cit_token",
    body={"currentPassword": "Password@123", "newPassword": "Password@1234"},
)

req(
    "Citizen Re-Login",
    "POST",
    "/api/login",
    body={"email": "cit@cr.com", "password": "Password@1234"},
    test_script='pm.collectionVariables.set("cit_token", pm.response.json().token);',
)

req("Citizen Dashboard", "GET", "/api/citizen/dash", "cit_token")


req("Citizen View Facilities", "GET", "/api/citizen/facilities", "cit_token")
req("Citizen View Facility Details", "GET", "/api/citizen/facility/{{fac_id}}", "cit_token")


book_r = req(
    "Citizen Book Facility",
    "POST",
    "/api/citizen/book_facility/{{fac_id}}",
    "cit_token",
    test_script='pm.collectionVariables.set("booking_id", pm.response.json().booking.id);',
    pre_script='var d = new Date(); d.setDate(d.getDate() + 3); var ds = d.toISOString().split("T")[0];\npm.request.body.raw = JSON.stringify({ bookedDate: ds, purpose: "Community Event" });',
)
book_r["request"]["body"] = {"mode": "raw", "raw": "{}", "options": {"raw": {"language": "json"}}}

req(
    "Citizen View Bookings",
    "GET",
    "/api/citizen/bookings",
    "cit_token",
    test_script="""
pm.test("Has bookings array", function () { pm.expect(pm.response.json().bookings).to.be.an("array"); });
""",
)
req(
    "Citizen View All Bookings",
    "GET",
    "/api/citizen/all_bookings",
    "cit_token",
    test_script="""
pm.test("Has bookings array", function () { pm.expect(pm.response.json().bookings).to.be.an("array"); });
""",
)
req(
    "Commissioner View Bookings",
    "GET",
    "/api/commissioner/bookings",
    "comm_token",
    test_script="""
pm.test("Has bookings array", function () { pm.expect(pm.response.json().bookings).to.be.an("array"); });
""",
)


req(
    "Commissioner View Citizens",
    "GET",
    "/api/commissioner/citizens",
    "comm_token",
    test_script="""
pm.test("Has citizens array", function () { pm.expect(pm.response.json().citizens).to.be.an("array"); });
""",
)

bill_r = req(
    "Commissioner Generate Bill",
    "POST",
    "/api/commissioner/bill",
    "comm_token",
    test_script="""
var resp = pm.response.json();
pm.collectionVariables.set("bill_id", resp.id || (resp.bill && resp.bill.id) || 1);
""",
    pre_script='var d = new Date(); d.setDate(d.getDate() + 30); var ds = d.toISOString().split("T")[0];\nvar citId = parseInt(pm.collectionVariables.get("cit_id"));\npm.request.body.raw = JSON.stringify({ citizenId: citId, billType: "Water Tax", amount: 100, dueDate: ds });',
)
bill_r["request"]["body"] = {"mode": "raw", "raw": "{}", "options": {"raw": {"language": "json"}}}

req("Commissioner View Bills", "GET", "/api/commissioner/bills", "comm_token")
req(
    "Citizen View Bills",
    "GET",
    "/api/citizen/bills",
    "cit_token",
    test_script="""
pm.test("Has bills array", function () { pm.expect(pm.response.json().bills).to.be.an("array"); });
""",
)
req(
    "Citizen Pay Bill",
    "POST",
    "/api/citizen/pay_bill/{{bill_id}}",
    "cit_token",
    test_script="""
pm.test("Payment successful message", function () { pm.expect(pm.response.json().message).to.eql("Payment successful"); });
pm.test("Receipt exists", function () { pm.expect(pm.response.json().receipt).to.exist; });
""",
)


anon_r = req(
    "File Anonymous Complaint",
    "POST",
    "/api/complaint/anonymous",
    test_script='var resp = pm.response.json();\npm.collectionVariables.set("complaint_token", resp.trackingToken);\npm.collectionVariables.set("complaint_id", resp.complaintId);',
)
anon_r["request"]["body"] = {
    "mode": "formdata",
    "formdata": [
        {"key": "title", "value": "Road pothole near market", "type": "text"},
        {
            "key": "description",
            "value": "There is a large pothole near the main market causing accidents",
            "type": "text",
        },
        {"key": "categoryId", "value": "{{category_id}}", "type": "text"},
        {"key": "addressText", "value": "Main Market Road, Block A", "type": "text"},
    ],
}

req("Wait 10s for AI Processing (1)", "GET", "https://postman-echo.com/delay/10")
req("Wait 10s for AI Processing (2)", "GET", "https://postman-echo.com/delay/10")
req("Wait 10s for AI Processing (3)", "GET", "https://postman-echo.com/delay/10")
req("Wait 10s for AI Processing (4)", "GET", "https://postman-echo.com/delay/10")


anon_r2 = req(
    "File Duplicate Anonymous Complaint",
    "POST",
    "/api/complaint/anonymous",
    test_script='var resp = pm.response.json();\npm.collectionVariables.set("duplicate_token", resp.trackingToken);',
)
anon_r2["request"]["body"] = anon_r["request"]["body"]

req("Wait 10s for AI Processing (1)", "GET", "https://postman-echo.com/delay/10")
req("Wait 10s for AI Processing (2)", "GET", "https://postman-echo.com/delay/10")
req("Wait 10s for AI Processing (3)", "GET", "https://postman-echo.com/delay/10")
req("Wait 10s for AI Processing (4)", "GET", "https://postman-echo.com/delay/10")


req(
    "Track Duplicate Complaint (Check Redirect)",
    "GET",
    "/api/complaint/track/{{duplicate_token}}",
    test_script="""
var resp = pm.response.json();
pm.test("Redirects to Master", function () { pm.expect(resp.redirectToToken).to.exist; });
if (resp.redirectToToken) pm.collectionVariables.set("complaint_token", resp.redirectToToken);
""",
)

req(
    "Track Master Complaint (Critical)",
    "GET",
    "/api/complaint/track/{{complaint_token}}",
    test_script="""
var resp = pm.response.json();
pm.test("Severity is Critical", function () { pm.expect(resp.complaint.severity).to.eql("Critical"); });
pm.collectionVariables.set("complaint_id", resp.complaint.id);
""",
)


req(
    "Commissioner View Complaints",
    "GET",
    "/api/commissioner/complaints",
    "comm_token",
    test_script="""
pm.test("Has complaints array", function () { pm.expect(pm.response.json().complaints).to.be.an("array"); });
var resp = pm.response.json();
if (resp.complaints && resp.complaints.length > 0) pm.collectionVariables.set("complaint_id", resp.complaints[0].id);
""",
)

req(
    "Commissioner View Complaint Detail",
    "GET",
    "/api/commissioner/complaint/{{complaint_id}}",
    "comm_token",
    test_script="""
pm.test("Complaint has id", function () { pm.expect(pm.response.json().complaint.id).to.exist; });
""",
)


req(
    "Commissioner Assign Complaint",
    "PUT",
    "/api/commissioner/assign/{{complaint_id}}",
    "comm_token",
    body={"officerId": "{{officer3_id}}"},
)


req(
    "Officer Login",
    "POST",
    "/api/login",
    body={"email": "officer3@cr.com", "password": "Password@123"},
    test_script='pm.collectionVariables.set("off_token", pm.response.json().token);',
)

req(
    "Officer Profile",
    "GET",
    "/api/officer/profile",
    "off_token",
    test_script="""
pm.test("Profile has email", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.email).to.exist;
});
""",
)
req(
    "Officer Edit Profile",
    "PUT",
    "/api/officer/edit_profile",
    "off_token",
    body={"phone": "9876543211"},
    test_script="""
pm.test("Profile updated successfully", function () { pm.expect(pm.response.json().message).to.eql("Profile updated successfully"); });
""",
)
req("Officer Dashboard", "GET", "/api/officer/dash", "off_token")
req("Officer History", "GET", "/api/officer/history", "off_token")


req("Officer View Ticket", "GET", "/api/officer/ticket/{{complaint_id}}", "off_token")

req(
    "Officer Mark En Route",
    "PUT",
    "/api/officer/ticket/{{complaint_id}}/status",
    "off_token",
    body={"status": "En Route", "note": "Heading to location"},
)

req(
    "Officer Mark On Site",
    "PUT",
    "/api/officer/ticket/{{complaint_id}}/status",
    "off_token",
    body={"status": "On Site", "note": "Arrived at location"},
)

req(
    "Officer Mark In Progress",
    "PUT",
    "/api/officer/ticket/{{complaint_id}}/status",
    "off_token",
    body={"status": "In Progress", "note": "Started work"},
)

resolve_r = req(
    "Officer Resolve Ticket", "POST", "/api/officer/ticket/{{complaint_id}}/resolve", "off_token"
)
resolve_r["request"]["body"] = {
    "mode": "formdata",
    "formdata": [
        {"key": "resolution_note", "value": "Fixed the pothole", "type": "text"},
        {"key": "resolution_photo", "type": "file", "src": "dummy.jpg"},
    ],
}


req(
    "Citizen Verify Resolution",
    "PUT",
    "/api/complaint/track/{{complaint_token}}/resolution",
    body={"accept": True, "note": "Thanks"},
)


req(
    "Citizen View Notifications",
    "GET",
    "/api/notifications",
    "cit_token",
    test_script='var notifs = pm.response.json().notifications;\nif (notifs && notifs.length > 0) pm.collectionVariables.set("notif_id", notifs[0].id);\nelse pm.collectionVariables.set("notif_id", 99999);',
)

req(
    "Mark Notification Unread",
    "PATCH",
    "/api/notifications/{{notif_id}}/unread",
    "cit_token",
    test_script='pm.test("Status code is 200 or 404", function () { pm.expect(pm.response.code).to.be.oneOf([200, 404]); });',
    skip_default_test=True,
)
req(
    "Mark Notification Read",
    "PATCH",
    "/api/notifications/{{notif_id}}/read",
    "cit_token",
    test_script='pm.test("Status code is 200 or 404", function () { pm.expect(pm.response.code).to.be.oneOf([200, 404]); });',
    skip_default_test=True,
)
req("Mark All Notifications Read", "PATCH", "/api/notifications/read-all", "cit_token")
req(
    "Delete Notification",
    "DELETE",
    "/api/notifications/{{notif_id}}",
    "cit_token",
    test_script='pm.test("Status code is 200 or 404", function () { pm.expect(pm.response.code).to.be.oneOf([200, 404]); });',
    skip_default_test=True,
)
req("Clear All Notifications", "DELETE", "/api/notifications", "cit_token")


req(
    "Google Login (Dummy Token)",
    "POST",
    "/api/google-login",
    body={"token": "dummy_invalid_token"},
    test_script='pm.test("Status code is 400 (invalid token)", function () { pm.response.to.have.status(400); });',
    skip_default_test=True,
)


environment = {
    "id": "12345678-1234-1234-1234-123456789012",
    "name": "SE Project Local Env",
    "values": [
        {"key": "base_url", "value": "http://localhost:8000", "type": "default", "enabled": True}
    ],
    "_postman_variable_scope": "environment",
}

with open("postman_collection.json", "w") as f:
    json.dump(collection, f, indent=4)

with open("postman_environment.json", "w") as f:
    json.dump(environment, f, indent=4)

print(f"Generated {req_counter - 1}-step Postman Collection.")
