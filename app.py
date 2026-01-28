import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
from datetime import datetime, timezone, timedelta

# ---------------- FUNCTIONS ----------------
def today_date():
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).strftime("%d-%m-%Y")

def parse_number(val):
    try:
        return float(str(val).replace(",", "").strip())
    except:
        return None

def format_indian(num):
    if not num:
        return ""
    n = int(num)
    s = str(n)[::-1]
    out = s[:3]
    s = s[3:]
    while s:
        out += "," + s[:2]
        s = s[2:]
    return "₹" + out[::-1]

def generate_image(data):
    df = pd.DataFrame(data)
    fig, ax = plt.subplots(figsize=(20, 8))  # Increased height for better wrapping
    ax.axis("off")
    
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
        bbox=[0.02, 0.02, 0.96, 0.95]  # Adjusted bbox for more space
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(14)  # Slightly smaller for better fit
    table.scale(1.2, 3.0)  # Increased row scaling height
    
    header_color = "#1E3A8A"
    border_color = "#D1D5DB"
    name_col_index = df.columns.get_loc("NAME")
    
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(border_color)
        cell.PAD = 0.05  # Add padding to prevent tight text
        
        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(color="white", weight="bold")
        else:
            cell.set_facecolor("#F9FAFB")
            cell.set_text_props(weight="bold")
        
        # FIXED: Set explicit widths for ALL columns to prevent expansion
        if col == name_col_index:
            cell.set_width(0.25)  # Wider for name with wrapping
            text_obj = cell.get_text()
            text_obj.set_wrap(True)
            text_obj.set_ha("center")
            text_obj.set_va("center")
            text_obj.set_multialignment('center')  # Better multi-line centering
        else:
            cell.set_width(0.12)  # Fixed narrow width for all other columns
    
    plt.suptitle(
        "JOS ALUKKAS INDIA PRIVATE LIMITED - BELAGAVI BRANCH",
        fontsize=22,
        fontweight="bold",
        y=0.99
    )
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

# ---------------- STREAMLIT SESSION HELPERS ----------------
def apply_today_to_all(num_customers):
    for i in range(num_customers):
        st.session_state[f"date{i}"] = today_date()

def apply_rate_to_all(num_customers, rate_value):
    for i in range(num_customers):
        st.session_state[f"rate{i}"] = rate_value

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="JOS ALUKKAS CUS ADV", layout="wide")
st.title("💎 JOS ALUKKAS CUS ADV")

num_customers = st.number_input(
    "How many customers?", min_value=1, max_value=10, value=1, step=1
)

if "shared_rate" not in st.session_state:
    st.session_state["shared_rate"] = ""
shared_rate = st.text_input(
    "Rate per gram (applies to all customers)",
    value=st.session_state["shared_rate"]
)
st.session_state["shared_rate"] = shared_rate
apply_rate_to_all(num_customers, shared_rate)

if st.button("📅 APPLY TODAY'S DATE"):
    apply_today_to_all(num_customers)

customers = []
for i in range(num_customers):
    st.subheader(f"Customer {i+1}")
    name = st.text_input("Customer Name", key=f"name{i}")
    date = st.text_input("Date (DD-MM-YYYY)", key=f"date{i}")
    amount = st.text_input("Amount (INR)", key=f"amount{i}")
    wt = st.text_input("Weight (grams)", key=f"wt{i}")
    due = st.text_input("Due Date", key=f"due{i}")
    rate = st.text_input(
        "Rate per gram", value=st.session_state.get(f"rate{i}", ""), key=f"rate{i}"
    )
    adv = st.text_input("Advance %", key=f"adv{i}")
    
    if name.strip():
        customers.append({
            "DATE": date,
            "NAME": name.upper(),
            "AMOUNT": format_indian(parse_number(amount)),
            "WT (g)": wt,
            "DUE DATE": due,
            "RATE": format_indian(parse_number(rate)),
            "ADV %": adv
        })

st.markdown("---")

if st.button("📊 GENERATE IMAGE"):
    if not customers:
        st.warning("Please enter at least one customer")
    else:
        img = generate_image(customers)
        st.image(img)
        st.download_button(
            "⬇️ DOWNLOAD IMAGE",
            data=img,
            file_name="payment_table.png",
            mime="image/png"
        )
