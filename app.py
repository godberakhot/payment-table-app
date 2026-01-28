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
    # Increase figure height significantly to prevent vertical overlap
    fig, ax = plt.subplots(figsize=(20, 8)) 
    ax.axis("off")
    
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
        bbox=[0.02, 0.05, 0.96, 0.9]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(14)
    # The 5.0 here creates huge vertical space so words can stack
    table.scale(1.2, 5.0) 

    header_color = "#1E3A8A"
    border_color = "#D1D5DB"
    name_col_index = df.columns.get_loc("NAME")

    # Set specific widths for columns to force wrapping
    widths = {
        "DATE": 0.12,
        "NAME": 0.22,  # Narrow enough to force "Samuel Philip John" to wrap
        "AMOUNT": 0.14,
        "WT (g)": 0.10,
        "DUE DATE": 0.12,
        "RATE": 0.14,
        "ADV %": 0.10
    }

    for (row, col_idx), cell in table.get_celld().items():
        cell.set_edgecolor(border_color)
        col_name = df.columns[col_idx] if row >= 0 else None
        
        # Apply the widths defined above
        if col_idx < len(df.columns):
            cell.set_width(widths.get(df.columns[col_idx], 0.15))

        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(color="white", weight="bold")
        else:
            cell.set_facecolor("#F9FAFB")
            cell.set_text_props(weight="bold")
            
            # FORCE WRAP LOGIC
            if col_idx == name_col_index:
                txt = cell.get_text()
                txt.set_wrap(True)
                # This ensures it stays centered and doesn't bleed out
                txt.set_verticalalignment('center')
                txt.set_multialignment('center')

    plt.suptitle(
        "JOS ALUKKAS INDIA PRIVATE LIMITED - BELAGAVI BRANCH",
        fontsize=22,
        fontweight="bold",
        y=0.98
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
    "Rate per gram (applies to all customers)", value=st.session_state["shared_rate"]
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
    rate = st.text_input("Rate per gram", value=st.session_state.get(f"rate{i}", ""), key=f"rate{i}")
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
