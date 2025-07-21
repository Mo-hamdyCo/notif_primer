import frappe
from frappe.utils import get_datetime, now_datetime, add_days

def run():
    print("🚀 Starting Notification Job...")
    notifications = frappe.get_all("Notification Mange", filters={"enabled": 1})
    print(f"🔍 Found {len(notifications)} active notifications")

    for n in notifications:
        doc = frappe.get_doc("Notification Mange", n.name)
        print(f"\n📄 Processing Notification: {doc.name}")

        if not doc.target_doctype or not doc.target_date_field:
            print("⚠️ Missing required fields, skipping...")
            continue

        offset = doc.days or 0
        today = get_datetime(now_datetime()).date()

        if doc.direction == "Before":
            target_date = add_days(today, offset)
        elif doc.direction == "After":
            target_date = add_days(today, -offset)
        else:  # "Same" or "Equal"
            target_date = today

        print(f"📆 Looking for {doc.target_doctype} where {doc.target_date_field} = {target_date}")
        filters = {doc.target_date_field: target_date}

        try:
            target_docs = frappe.get_all(doc.target_doctype, filters=filters)
            print(f"✅ Found {len(target_docs)} matching document(s)")
        except Exception as e:
            frappe.log_error(f"Error fetching documents: {e}")
            continue

        for td in target_docs:
            target_doc = frappe.get_doc(doc.target_doctype, td.name)
            print(f"➡️ Processing Document: {target_doc.name}")

            if doc.condition:
                try:
                    if not eval(doc.condition, {"doc": target_doc.as_dict()}):
                        continue
                except Exception as e:
                    frappe.log_error(f"Condition Error in {doc.name}: {e}")
                    continue

            for r in doc.reciver:
                recipients = []

                if r.receiver_by_document_field:
                    email = target_doc.get(r.receiver_by_document_field)
                    if email:
                        recipients.append(email)

                if r.receiver_by_role:
                    user_roles = frappe.get_all("Has Role", filters={"role": r.receiver_by_role}, fields=["parent"])
                    for ur in user_roles:
                        user_email = frappe.db.get_value("User", ur.parent, "email")
                        if user_email:
                            recipients.append(user_email)

                for email in recipients:
                    if already_sent(doc.name, td.name, doc.target_doctype, email):
                        print(f"⏭️ Already sent to {email}, skipping...")
                        continue

                    try:
                        final_msg = frappe.render_template(doc.message or "", {"doc": target_doc})
                        # Send system notification
                        if frappe.db.exists("User", email):
                            frappe.get_doc({
                                "doctype": "Notification Log",
                                "subject": doc.subject,
                                "email_content": final_msg,
                                "for_user": email,
                                "type": "Alert",
                                "document_type": doc.target_doctype,
                                "document_name": target_doc.name
                            }).insert(ignore_permissions=True)
                            print(f"✅ System notification created for {email}")
                        else:
                            print(f"⚠️ User {email} not found")

                        log_sent(doc.name, td.name, doc.target_doctype, email)

                    except Exception as e:
                        frappe.log_error(f"System notification failed to {email}: {e}")


def already_sent(notification_ref, docname, doctype, recipient):
    return frappe.db.exists("Sent Notification Log", {
        "notification_ref": notification_ref,
        "target_docname": docname,
        "target_doctype": doctype,
        "recipient": recipient
    })


def log_sent(notification_ref, docname, doctype, recipient):
    frappe.get_doc({
        "doctype": "Sent Notification Log",
        "notification_ref": notification_ref,
        "target_docname": docname,
        "target_doctype": doctype,
        "recipient": recipient,
        "sent_on": now_datetime()
    }).insert(ignore_permissions=True)
