# Notification Primer

A drop-in Frappe custom app that fixes timing reliability issues in the built-in date-driven notifications by polling every minute and deduplicating sends.  

---

## 🚀 Features

- **Minute-level polling** via a cron hook to ensure timely delivery  
- Configurable **days before/after** date triggers  
- Conditional filters (Python expressions) for advanced targeting  
- Safe, idempotent sends with a **Sent Notification Log** to prevent duplicates  
- Uses Frappe’s built-in **Notification Log** for delivery and history  

---

## 🏗 Architecture

1. **`Notification Manage` Doctype**  
   - Fields: target doctype & date field, offset days, direction (Before/After/Same), condition, message template, recipients (user, role).

2. **Scheduler Hook**  
   ```python
   # in hooks.py
   scheduler_events = {
     "cron": {
       "* * * * *": ["notif_primer.scripts.trigger_notifications.run"]
     }
   }
   ```

3. **`trigger_notifications.run()`**  
   - Loads all enabled `Notification Manage` records  
   - Calculates “target date” = `date_field ± days`  
   - Queries the target doctype for matching records  
   - Applies optional `condition` via `frappe.safe_eval`  
   - Queues creation of a **Notification Log** for each recipient  
   - Records each send in **Sent Notification Log** to avoid repeats

4. **Delivery Flow**  
   - Inserting a **Notification Log** record fires Frappe’s standard notification delivery (email, desktop alert, push, etc.).  

---

## 📥 Installation

1. **Get the app**  
   ```bash
   cd frappe-bench/apps
   git clone https://github.com/your-org/notif_primer.git
   ```

2. **Install on your site**  
   ```bash
   bench --site yoursite install-app notif_primer
   bench --site yoursite migrate
   ```

3. **Configure Notifications**  
   - Go to **Notification Manage** in your desk.  
   - Create a new record, fill target doctype, date field, days offset, condition (optional), subject & message, and add recipients.  
   - Enable the record and save.

4. **Ensure Scheduler is Running**  
   - In development: `bench start`  
   - In production: configure a supervisor/unit to run `bench schedule`.

---

## ⚙️ Tips & Best Practices

- Use **frappe.safe_eval** for conditions to avoid arbitrary code execution.  
- Monitor **Error Log** for any exceptions in `trigger_notifications.run`.  
- For high-volume scenarios, consider offloading heavy loops with `frappe.enqueue`.  

---

## 📜 License

MIT © [Your Name / Org]
