import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
import plotly.express as px
from datetime import date, datetime


# Session initialization

def init_state():
    ss = st.session_state
    ss.setdefault("logged_in", False)
    ss.setdefault("role", None)         # "Admin", "Inventor", "Reviewer"
    ss.setdefault("user_id", None)
    ss.setdefault("username", None)
    ss.setdefault("show_login", False)
    ss.setdefault("show_inv_register", False)
    ss.setdefault("show_rev_register", False)
    ss.setdefault("show_opposition", False)
    ss.setdefault("_guest_page", None)

init_state()


# DB connection helper

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="svarsha08112005",
            database="patent_system",
            autocommit=False
        )
        return conn
    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None


# Query helpers

def df_from_query(conn, query, params=None, columns=None):
    cur = conn.cursor()
    cur.execute(query, params or ())
    rows = cur.fetchall()
    if not rows:
        return pd.DataFrame(columns=columns) if columns else pd.DataFrame()
    if columns:
        return pd.DataFrame(rows, columns=columns)
    else:
        cols = [c[0] for c in cur.description] if cur.description else None
        return pd.DataFrame(rows, columns=cols) if cols else pd.DataFrame(rows)

def get_total_patents(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Patents")
    return cur.fetchone()[0]

def get_active_patents(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Patents WHERE Status='Granted'")
    return cur.fetchone()[0]

def get_expired_patents(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Patents WHERE Status='Expired'")
    return cur.fetchone()[0]

def get_upcoming_renewals(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM Renewals
        WHERE Expiry_Date > CURDATE() AND Expiry_Date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
    """)
    return cur.fetchone()[0]

def get_domains(conn):
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT Domain FROM Patents WHERE Domain IS NOT NULL ORDER BY Domain")
    return [r[0] for r in cur.fetchall()]

def get_patent_list(conn):
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT P_ID, Title, Filing_Date, Domain, Status, Patent_Type, Appl_Name FROM Patents ORDER BY Title")
    return cur.fetchall()


# Guest UI

def render_guest_shell(conn):
    with st.sidebar:
        st.markdown("### Navigation")
        view = st.radio("Go to:", ["Home", "Public Stats"])
        st.markdown("---")
        st.markdown("### Quick Actions")
        if st.button("👨‍🔧 Register Inventor"):
            st.session_state.show_inv_register = True
            st.rerun()
        if st.button("👨⚖ Register Reviewer"):
            st.session_state.show_rev_register = True
            st.rerun()
        if st.button("⚖ File Opposition"):
            st.session_state.show_opposition = True
            st.rerun()

        st.markdown("---")
        # Functions & Procedure & Query viewers visible to guest
        st.markdown("### Functions & Queries")
        if st.button("📆 Patent Age Calculator (Guest)"):
            st.session_state._guest_page = "age_calc"
            st.rerun()
        if st.button("📂 Get Patents by Domain (Guest)"):
            st.session_state._guest_page = "domain_proc"
            st.rerun()
        if st.button("🔗 Join Query Viewer (Guest)"):
            st.session_state._guest_page = "join_view"
            st.rerun()
        if st.button("🧩 Nested Query Viewer (Guest)"):
            st.session_state._guest_page = "nested_view"
            st.rerun()
        if st.button("📊 Aggregate Query Viewer (Guest)"):
            st.session_state._guest_page = "agg_view"
            st.rerun()

        st.markdown("---")
        if st.button("🔐 Login Access"):
            st.session_state.show_login = True
            st.rerun()

    # Routing for guest flows
    if st.session_state.show_inv_register:
        render_inventor_register(conn)
        return
    if st.session_state.show_rev_register:
        render_reviewer_register(conn)
        return
    if st.session_state.show_opposition:
        render_public_opposition(conn)
        return
    if st.session_state.show_login:
        render_login(conn)
        return

    # Guest pages
    if st.session_state._guest_page == "age_calc":
        age_calculator_ui(conn, allow_inventor=False)  # guest mode
        return
    if st.session_state._guest_page == "domain_proc":
        domain_procedure_ui(conn)
        return
    if st.session_state._guest_page == "join_view":
        join_query_view(conn)
        return
    if st.session_state._guest_page == "nested_view":
        nested_query_view(conn)
        return
    if st.session_state._guest_page == "agg_view":
        aggregate_query_view(conn)
        return

    if view == "Home":
        render_home_page()
    else:
        render_public_stats(conn)

def render_home_page():
    st.title("📜 Patent Lifecycle Management System")
    st.write("Use the sidebar to navigate. Guest sidebar contains Patent Age Calculator, Get Patents by Domain and query viewers.")
    st.markdown("---")
    st.write("You can register as Inventor/Reviewer or log in from the sidebar.")

def render_public_stats(conn):
    st.title("📊 Public Patent Statistics")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Patents", get_total_patents(conn))
    c2.metric("Active (Granted)", get_active_patents(conn))
    c3.metric("Expired", get_expired_patents(conn))
    c4.metric("Renewals (30d)", get_upcoming_renewals(conn))

    st.markdown("---")
    df_dom = df_from_query(conn, "SELECT Domain, COUNT(*) as Count FROM Patents GROUP BY Domain", columns=["Domain","Count"])
    df_type = df_from_query(conn, "SELECT Patent_Type, COUNT(*) as Count FROM Patents GROUP BY Patent_Type", columns=["Patent_Type","Count"])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Patents by Domain")
        if not df_dom.empty:
            st.plotly_chart(px.pie(df_dom, names="Domain", values="Count", title="By Domain"), use_container_width=True)
        else:
            st.info("Not enough data for domain chart.")
    with col2:
        st.subheader("Patents by Type")
        if not df_type.empty:
            st.plotly_chart(px.bar(df_type, x="Patent_Type", y="Count", title="By Type"), use_container_width=True)
        else:
            st.info("Not enough data for type chart.")


# Registration / Login / Opposition

def render_inventor_register(conn):
    st.header("👨‍🔧 Register as Inventor")
    with st.form("inv_reg"):
        name = st.text_input("Full Name")
        org = st.text_input("Organization")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register")
    if not submitted:
        return

    if not name or not email or not password:
        st.error("Name, Email and Password are required.")
        return
    if password != confirm:
        st.error("Passwords do not match.")
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Inventors WHERE Email=%s", (email,))
        if cur.fetchone()[0] > 0:
            st.error("Email already registered as inventor.")
            return
        cur.execute("""
            INSERT INTO Inventors (Name, Organization, Email, Phone_No, Password)
            VALUES (%s,%s,%s,%s,%s)
        """, (name, org, email, phone, password))
        conn.commit()
        st.success("Inventor registered successfully. You can login from the sidebar.")
        st.session_state.show_inv_register = False
        st.rerun()
    except Exception as e:
        st.error(f"Registration failed: {e}")

def render_reviewer_register(conn):
    st.header("👨⚖ Register as Reviewer")
    with st.form("rev_reg"):
        name = st.text_input("Full Name")
        designation = st.text_input("Designation")
        org = st.text_input("Organisation")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register")
    if not submitted:
        return

    if not name or not designation or not email or not password:
        st.error("All fields are required.")
        return
    if password != confirm:
        st.error("Passwords do not match.")
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Reviewers WHERE Email=%s", (email,))
        if cur.fetchone()[0] > 0:
            st.error("Email already registered as reviewer.")
            return
        cur.execute("""
            INSERT INTO Reviewers (Email, Name, Designation, Organisation, Comment, Password, Is_Active)
            VALUES (%s,%s,%s,%s,%s,%s,TRUE)
        """, (email, name, designation, org, "", password))
        conn.commit()
        st.success("Reviewer registered successfully. You can login from the sidebar.")
        st.session_state.show_rev_register = False
        st.rerun()
    except Exception as e:
        st.error(f"Registration failed: {e}")

def render_public_opposition(conn):
    st.header("⚖ File an Opposition")
    with st.form("opp_form"):
        email = st.text_input("Your Email")
        patent_title = st.text_input("Patent Title (exact title or copy-paste)")
        reason = st.text_area("Reason / Details")
        submitted = st.form_submit_button("Submit")
    if not submitted:
        return
    if not email or not patent_title or not reason:
        st.error("Email, Patent Title and Reason are required.")
        return
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO Patents_Opposition (Email, Patent_Title, O_Date, Reason) VALUES (%s,%s,CURDATE(),%s)",
                    (email, patent_title, reason))
        conn.commit()
        st.success("Opposition submitted successfully.")
        st.session_state.show_opposition = False
        st.rerun()
    except Exception as e:
        st.error(f"Failed to submit opposition: {e}")

def render_login(conn):
    st.header("🔐 Login")
    with st.form("login_form"):
        role = st.selectbox("Login as", ["Admin", "Inventor", "Reviewer"])
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
    if not submitted:
        return

    try:
        if role == "Admin":
            # Admin credentials (simple static check)
            if email == "admin@system.com" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.role = "Admin"
                st.session_state.username = "Administrator"
                st.success("Logged in as Admin")
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error("Invalid admin credentials.")
            return

        if role == "Inventor":
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT I_ID, Name FROM Inventors WHERE Email=%s AND Password=%s", (email, password))
            row = cur.fetchone()
            if not row:
                st.error("Invalid inventor email or password.")
                return
            st.session_state.logged_in = True
            st.session_state.role = "Inventor"
            st.session_state.user_id = row["I_ID"]
            st.session_state.username = row["Name"]
            st.session_state.show_login = False
            st.success(f"Welcome, {row['Name']}!")
            st.rerun()
            return

        if role == "Reviewer":
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT R_ID, Name FROM Reviewers WHERE Email=%s AND Password=%s", (email, password))
            row = cur.fetchone()
            if not row:
                st.error("Invalid reviewer email or password.")
                return
            st.session_state.logged_in = True
            st.session_state.role = "Reviewer"
            st.session_state.user_id = row["R_ID"]
            st.session_state.username = row["Name"]
            st.session_state.show_login = False
            st.success(f"Welcome, {row['Name']}!")
            st.rerun()
            return

    except Exception as e:
        st.error(f"Login failed: {e}")


# Logged-in shell (role-specific sidebars)

def render_logged_in_shell(conn):
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.role} Menu")
        st.caption(f"Logged in as: {st.session_state.username}")

        if st.session_state.role == "Admin":
            page = st.radio("Go to:", ["Overview", "Assign Reviewers", "Update Patent Status"])
        elif st.session_state.role == "Inventor":
            page = st.radio("Go to:", ["Inventor Overview", "My Patents", "Add New Patent", "Patent Age Calculator"])
        else:  # Reviewer
            page = st.radio("Go to:", ["Reviewer Overview", "Assigned Reviews", "Review History"])

        st.markdown("---")
        if st.button("🚪 Logout"):
            logout()
            st.rerun()

    # Route pages
    if st.session_state.role == "Admin":
        if page == "Overview":
            admin_overview(conn)
        elif page == "Assign Reviewers":
            admin_assign_reviewers(conn)
        elif page == "Update Patent Status":
            admin_update_patent_status(conn)
    elif st.session_state.role == "Inventor":
        if page == "Inventor Overview":
            inventor_overview(conn)
        elif page == "My Patents":
            inventor_my_patents(conn)
        elif page == "Add New Patent":
            inventor_add_patent(conn)
        else:  # Patent Age Calculator for inventor
            age_calculator_ui(conn, allow_inventor=True)
    else:  # Reviewer
        if page == "Reviewer Overview":
            reviewer_overview(conn)
        elif page == "Assigned Reviews":
            reviewer_assigned_reviews(conn)
        else:
            reviewer_history(conn)


# Admin pages

def admin_overview(conn):
    st.title("Admin — Overview")
    # Top metrics
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Patents", get_total_patents(conn))
    c2.metric("Active (Granted)", get_active_patents(conn))
    c3.metric("Expired", get_expired_patents(conn))
    c4.metric("Renewals (30d)", get_upcoming_renewals(conn))

    st.markdown("### Manage Patents (editable)")
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT P_ID, Appl_Name, Filing_Date, Domain, Status, Patent_Type, Title, Description FROM Patents ORDER BY P_ID")
    rows = cur.fetchall() or []
    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=["P_ID","Appl_Name","Filing_Date","Domain","Status","Patent_Type","Title","Description"])

    edited = st.data_editor(df, key="admin_patents_editor", num_rows="dynamic")

    if st.button("Save Patent Changes"):
        try:
            cur2 = conn.cursor()
            for r in edited.to_dict("records"):
                cur2.execute("""
                    UPDATE Patents SET Appl_Name=%s, Filing_Date=%s, Domain=%s, Status=%s, Patent_Type=%s, Title=%s, Description=%s
                    WHERE P_ID=%s
                """, (
                    r.get("Appl_Name"),
                    r.get("Filing_Date"),
                    r.get("Domain"),
                    r.get("Status"),
                    r.get("Patent_Type"),
                    r.get("Title"),
                    r.get("Description"),
                    r.get("P_ID")
                ))
            conn.commit()
            st.success("Patent changes saved (DB triggers will fire on update).")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to save changes: {e}")

    st.markdown("---")
    st.markdown("### Reviewer performance (simple)")
    try:
        df_work = df_from_query(conn, """
            SELECT R.R_ID, R.Name, R.Email,
              SUM(CASE WHEN PR.Review_Status='Completed' THEN 1 ELSE 0 END) AS CompletedReviews,
              SUM(CASE WHEN PR.Review_Status <> 'Completed' AND PR.Review_Status IS NOT NULL THEN 1 ELSE 0 END) AS PendingReviews
            FROM Reviewers R
            LEFT JOIN Patent_Reviewers PR ON R.R_ID = PR.R_ID
            GROUP BY R.R_ID, R.Name, R.Email
            ORDER BY PendingReviews DESC
        """)
        if not df_work.empty:
            st.dataframe(df_work, use_container_width=True)
        else:
            st.info("No reviewer assignments yet.")
    except Exception:
        st.info("Reviewer workload info not available.")

    st.markdown("---")
    st.markdown("### Oppositions (latest)")
    try:
        df_opp = df_from_query(conn, """
            SELECT O.O_ID, O.Email, O.Patent_Title, O.O_Date, O.Reason
            FROM Patents_Opposition O
            ORDER BY O.O_Date DESC LIMIT 20
        """, columns=["O_ID","Email","Patent_Title","O_Date","Reason"])
        if not df_opp.empty:
            st.dataframe(df_opp, use_container_width=True)
        else:
            st.info("No oppositions logged.")
    except Exception:
        st.info("Opposition table not accessible.")

def admin_assign_reviewers(conn):
    st.title("Assign Reviewers to Patent")
    # Load patents and reviewers
    patents = get_patent_list(conn)
    if not patents:
        st.info("No patents found.")
        return
    patent_map = {f"{p['Title']} (ID:{p['P_ID']})": p['P_ID'] for p in patents}
    sel_patent_label = st.selectbox("Select Patent", list(patent_map.keys()))
    p_id = patent_map[sel_patent_label]

    # reviewers list
    reviewers_df = df_from_query(conn, "SELECT R_ID, Name, Email FROM Reviewers WHERE Is_Active=TRUE ORDER BY Name", columns=["R_ID","Name","Email"])
    if reviewers_df.empty:
        st.info("No active reviewers available.")
        return

    st.markdown("Select one or more reviewers to assign:")
    rev_options = {f"{r['Name']} ({r['Email']})": r['R_ID'] for _, r in reviewers_df.iterrows()}
    chosen = st.multiselect("Choose reviewers", list(rev_options.keys()))
    if st.button("Assign Selected Reviewers"):
        if not chosen:
            st.error("Select at least one reviewer.")
        else:
            try:
                cur = conn.cursor()
                assigned = 0
                for ch in chosen:
                    r_id = rev_options[ch]
                    # Insert only if not already assigned
                    cur.execute("SELECT COUNT(*) FROM Patent_Reviewers WHERE P_ID=%s AND R_ID=%s", (p_id, r_id))
                    if cur.fetchone()[0] == 0:
                        cur.execute("""
                            INSERT INTO Patent_Reviewers (P_ID, R_ID, Reviewer_Name, Assignment_Date, Review_Status)
                            VALUES (%s, %s, (SELECT Name FROM Reviewers WHERE R_ID=%s), CURDATE(), 'Assigned')
                        """, (p_id, r_id, r_id))
                        assigned += 1
                conn.commit()
                st.success(f"Assigned {assigned} reviewer(s) to the patent.")
                st.rerun()
            except Exception as e:
                st.error(f"Assignment failed: {e}")

    st.markdown("Current assignments for this patent:")
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT PR.R_ID, PR.Reviewer_Name, PR.Assignment_Date, PR.Review_Status, PR.Review_Date, PR.Decision
        FROM Patent_Reviewers PR
        WHERE PR.P_ID=%s
        ORDER BY PR.Assignment_Date DESC
    """, (p_id,))
    rows = cur.fetchall() or []
    st.dataframe(rows, use_container_width=True)

def admin_update_patent_status(conn):
    st.title("Update Patent Status")
    patents = get_patent_list(conn)
    if not patents:
        st.info("No patents found.")
        return
    patent_map = {f"{p['Title']} (ID:{p['P_ID']})": p['P_ID'] for p in patents}
    sel_patent_label = st.selectbox("Select Patent", list(patent_map.keys()))
    p_id = patent_map[sel_patent_label]

    # fetch current status
    cur = conn.cursor()
    cur.execute("SELECT Status FROM Patents WHERE P_ID=%s", (p_id,))
    cur_status_row = cur.fetchone()
    current_status = cur_status_row[0] if cur_status_row else None

    st.write(f"Current status: **{current_status}**")
    new_status = st.selectbox("Set new status", ["Pending", "Under Review", "In Progress", "Approved", "Rejected", "Granted", "Expired", "Withdrawn"])
    if st.button("Update Status"):
        try:
            cur2 = conn.cursor()
            cur2.execute("UPDATE Patents SET Status=%s WHERE P_ID=%s", (new_status, p_id))
            conn.commit()
            st.success("Patent status updated (DB trigger will log change).")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to update status: {e}")


# Patent Age Calculator (used by Guest and Inventor)

def age_calculator_ui(conn, allow_inventor=False):
    st.header("Patent Age Calculator (years & months)")
    # If allow_inventor True and user is inventor, show only their patents; else show all
    if allow_inventor and st.session_state.get("role") == "Inventor" and st.session_state.get("user_id"):
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT P.P_ID, P.Title, P.Filing_Date
            FROM Patents P
            JOIN Inventor_Patents IP ON P.P_ID = IP.P_ID
            WHERE IP.I_ID = %s
            ORDER BY P.Title
        """, (st.session_state.user_id,))
        patents = cur.fetchall()
    else:
        patents = get_patent_list(conn)

    if not patents:
        st.info("No patents available.")
        return

    mapping = {f"{p['Title']} (ID:{p['P_ID']})": p for p in patents}
    selected = st.selectbox("Select Patent", list(mapping.keys()))
    rec = mapping[selected]
    filing = rec.get("Filing_Date")
    if not filing:
        st.error("Filing date missing.")
        return

    if isinstance(filing, str):
        try:
            filing_date = datetime.strptime(filing, "%Y-%m-%d").date()
        except Exception:
            st.error("Invalid filing date format.")
            return
    elif isinstance(filing, datetime):
        filing_date = filing.date()
    elif isinstance(filing, date):
        filing_date = filing
    else:
        st.error("Unknown filing date format.")
        return

    today = date.today()
    years = today.year - filing_date.year
    months = today.month - filing_date.month
    days = today.day - filing_date.day
    if days < 0:
        months -= 1
    if months < 0:
        years -= 1
        months += 12

    st.success(f"**{rec['Title']}** — Filing Date: {filing_date.isoformat()}")
    st.write(f"**Age:** {years} years and {months} months")


# Procedure page available only to Guest

def domain_procedure_ui(conn):
    st.header("Get Patents by Domain (Procedure)")
    domains = get_domains(conn)
    if not domains:
        st.info("No domains available.")
        return
    selected_domain = st.selectbox("Select Domain", domains)
    if st.button("Run Procedure"):
        cur = conn.cursor()
        try:
            cur.callproc("GetPatentsByDomain", [selected_domain])
            results = []
            cols = None
            for result in cur.stored_results():
                results = result.fetchall()
                cols = [c[0] for c in result.description] if result.description else None
            if results:
                df = pd.DataFrame(results, columns=cols) if cols else pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Procedure returned no rows.")
        except Exception:
            # fallback
            try:
                df = df_from_query(conn, "SELECT P_ID, Title, Appl_Name, Filing_Date, Status, All_Reviews_Complete FROM Patents WHERE Domain=%s ORDER BY Filing_Date DESC", (selected_domain,))
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No patents found for that domain.")
            except Exception as e:
                st.error(f"Procedure and fallback query both failed: {e}")


# Join / Nested / Aggregate viewers (Guest)

def join_query_view(conn):
    st.header("Join Query Viewer")
    st.write("Example: patent reviewers joined with patent and reviewer info.")
    try:
        df = df_from_query(conn, """
            SELECT PR.P_ID, P.Title AS Patent, PR.R_ID AS Reviewer_ID, R.Name AS Reviewer_Name, PR.Review_Status
            FROM Patent_Reviewers PR
            JOIN Patents P ON PR.P_ID = P.P_ID
            JOIN Reviewers R ON PR.R_ID = R.R_ID
            ORDER BY P.Title
        """)
        if df.empty:
            st.info("No join rows to display.")
        else:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Join query failed: {e}")

def nested_query_view(conn):
    st.header("Nested Query Viewer")
    st.write("Example: reviewers who reviewed patents that are 'Granted'.")
    try:
        df = df_from_query(conn, """
            SELECT DISTINCT R.R_ID, R.Name, R.Email
            FROM Reviewers R
            WHERE R.R_ID IN (
                SELECT PR.R_ID FROM Patent_Reviewers PR
                WHERE PR.P_ID IN (
                    SELECT P_ID FROM Patents WHERE Status='Granted'
                )
            )
            ORDER BY R.Name
        """)
        if df.empty:
            st.info("No nested-query results.")
        else:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Nested query failed: {e}")

def aggregate_query_view(conn):
    st.header("Aggregate Query Viewer")
    st.write("Example: patents with at least two paid renewals.")
    try:
        df = df_from_query(conn, """
            SELECT P_ID, COUNT(R_No) AS NumberOfRenewals
            FROM Renewals
            WHERE Fee_Status LIKE '%Paid%'
            GROUP BY P_ID
            HAVING COUNT(R_No) >= 2
        """, columns=["P_ID","NumberOfRenewals"])
        if df.empty:
            st.info("No patents with >= 2 paid renewals found.")
        else:
            # join to show titles
            cur = conn.cursor()
            cur.execute("SELECT P_ID, Title FROM Patents WHERE P_ID IN (%s)" % ",".join(str(x) for x in df["P_ID"].tolist()))
            titles = cur.fetchall()
            titles_map = {t[0]: t[1] for t in titles}
            df["Title"] = df["P_ID"].map(titles_map)
            st.dataframe(df[["P_ID","Title","NumberOfRenewals"]], use_container_width=True)
    except Exception as e:
        st.error(f"Aggregate query failed: {e}")


# Inventor pages: overview, my patents, add patent

def inventor_overview(conn):
    st.title("Inventor — Overview")
    if not st.session_state.user_id:
        st.info("No inventor session found.")
        return
    inv_id = st.session_state.user_id
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(DISTINCT IP.P_ID) FROM Inventor_Patents IP WHERE IP.I_ID = %s", (inv_id,))
        total = cur.fetchone()[0]
        st.metric("My Patents", total)
    except Exception:
        st.info("Unable to fetch inventor stats.")

    st.markdown("### My Patents (quick view)")
    inventor_my_patents(conn)

def inventor_my_patents(conn):
    if not st.session_state.user_id:
        st.info("No inventor session.")
        return
    inv_id = st.session_state.user_id
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT P.P_ID, P.Title, P.Status, P.Filing_Date, P.Domain, P.Patent_Type
        FROM Patents P
        JOIN Inventor_Patents IP ON P.P_ID = IP.P_ID
        WHERE IP.I_ID = %s
        ORDER BY P.Filing_Date DESC
    """, (inv_id,))
    rows = cur.fetchall() or []
    st.dataframe(rows, use_container_width=True)

def inventor_add_patent(conn):
    st.title("Add New Patent")
    with st.form("add_patent"):
        title = st.text_input("Title")
        description = st.text_area("Short Description")
        domain = st.text_input("Domain")
        patent_type = st.selectbox("Patent Type", ["Utility", "Design", "Plant"])
        filing_date = st.date_input("Filing Date", value=date.today())
        appl_name = st.text_input("Applicant Name (Your org/company)")
        submitted = st.form_submit_button("Add Patent")
    if not submitted:
        return
    if not title or not description or not domain or not appl_name:
        st.error("Title, Description, Domain and Applicant are required.")
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Patents (Appl_Name, Filing_Date, Domain, Status, Patent_Type, Title, Description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (appl_name, filing_date.isoformat(), domain, "Pending", patent_type, title, description))
        new_p_id = cur.lastrowid
        cur.execute("INSERT INTO Inventor_Patents (I_ID, P_ID) VALUES (%s, %s)", (st.session_state.user_id, new_p_id))
        conn.commit()
        st.success(f"Patent added (P_ID={new_p_id}) and linked to your profile.")
        st.rerun()
    except Exception as e:
        st.error(f"Failed to add patent: {e}")


# Reviewer pages: overview, assigned reviews, history

def reviewer_overview(conn):
    st.title("Reviewer — Overview")
    reviewer_assigned_reviews(conn)

def reviewer_assigned_reviews(conn):
    if not st.session_state.user_id:
        st.info("No reviewer session.")
        return
    r_id = st.session_state.user_id
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT PR.P_ID, P.Title, PR.Assignment_Date, PR.Review_Status, PR.Review_Date, PR.Decision, PR.Comments
        FROM Patent_Reviewers PR
        JOIN Patents P ON PR.P_ID = P.P_ID
        WHERE PR.R_ID = %s
        ORDER BY PR.Assignment_Date DESC
    """, (r_id,))
    rows = cur.fetchall() or []
    st.dataframe(rows, use_container_width=True)

    pending = [r for r in rows if r.get("Review_Status") != "Completed"]
    if pending:
        st.markdown("### Perform Review")
        opts = {f"{p['Title']} (P:{p['P_ID']})": p for p in pending}
        sel = st.selectbox("Select pending review", list(opts.keys()))
        rec = opts[sel]
        with st.form("review_submit"):
            decision = st.selectbox("Decision", ["Approved", "Rejected", "Needs Revision"])
            comments = st.text_area("Comments")
            submit = st.form_submit_button("Submit Review")
        if submit:
            try:
                cur2 = conn.cursor()
                cur2.execute("""
                    UPDATE Patent_Reviewers
                    SET Review_Status = 'Completed', Decision = %s, Comments = %s, Review_Date = CURDATE()
                    WHERE P_ID = %s AND R_ID = %s
                """, (decision, comments, rec['P_ID'], r_id))
                cur2.execute("UPDATE Patents SET Status=%s WHERE P_ID=%s", (decision, rec['P_ID']))
                conn.commit()
                st.success("Review submitted and patent status updated.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to submit review: {e}")
    else:
        st.info("No pending reviews assigned to you.")

def reviewer_history(conn):
    if not st.session_state.user_id:
        st.info("No reviewer session.")
        return
    r_id = st.session_state.user_id
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT PR.P_ID, P.Title, PR.Assignment_Date, PR.Review_Status, PR.Review_Date, PR.Decision, PR.Comments
        FROM Patent_Reviewers PR
        JOIN Patents P ON PR.P_ID = P.P_ID
        WHERE PR.R_ID = %s
        ORDER BY PR.Review_Date DESC
    """, (r_id,))
    rows = cur.fetchall() or []
    st.dataframe(rows, use_container_width=True)


# Logout

def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    init_state()


# App entrypoint

def main():
    st.set_page_config(page_title="Patent Lifecycle Management System", layout="wide")
    conn = get_db_connection()
    if not conn:
        st.header("Cannot connect to the database — check your DB server and credentials.")
        return

    # Render either guest or logged-in shell
    if not st.session_state.logged_in:
        render_guest_shell(conn)
    else:
        render_logged_in_shell(conn)

if __name__ == "__main__":
    main()
