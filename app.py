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
    # 1. Height is increased to prevent rows from crashing into each other
    fig, ax = plt.subplots(figsize=(18, 10)) 
    ax.axis("off")
    
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center",
        bbox=[0, 0, 1, 1] # Uses full space
    )

    table.auto_set_font_size(False)
    table.set_fontsize(14)
    # 2. Huge vertical scale (6.0) to give multi-line names space to exist
    table.scale(1, 6.0) 

    header_color = "#1E3A8A"
    border_color = "#D1D5DB"
    
    # 3. Explicitly define column widths (NAME is narrowed to FORCE wrapping)
    col_widths = {
        "DATE": 0.12,
        "NAME": 0.18,  # Narrow width = mandatory wrapping for long names
        "AMOUNT": 0.15,
        "WT (g)": 0.10,
        "DUE DATE": 0.12,
        "RATE": 0.15,
        "ADV %": 0.10
    }

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(border_color)
        
        # Apply the width
        col_name = df.columns[col]
        cell.set_width(col_widths.get(col_name, 0.15))

        # Header Styling
        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(color="white", weight="bold")
        else:
            # Data Styling
            cell.set_facecolor("#F9FAFB")
            cell.set_text_props(weight="bold")
            
            # 4. WRAP LOGIC FOR NAME COLUMN
            if col == df.columns.get_loc("NAME"):
                txt = cell.get_text()
                txt.set_wrap(True)
                # Centers the stacked words vertically and horizontally
                txt.set_verticalalignment('center')
                txt.set_multialignment('center')

    plt.suptitle(
        "JOS ALUKKAS INDIA PRIVATE LIMITED - BELAGAVI BRANCH",
        fontsize=20,
        fontweight="bold",
        y=1.05
    )

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="JOS ALUKKAS CUS ADV", layout="wide")
st.title("💎 JOS ALUKKAS CUS ADV")

num_customers = st.number_input("How many customers?", min_value=1, max_value=10, value=1)

if "shared_rate" not in st.session_state:
    st.session_state["shared_rate"] = ""

shared_rate = st.text_input("Rate per gram (applies to all)", value=st.session_state["shared_rate"])
st.session_state["shared_rate"] = shared_rate

if st.button("📅 APPLY TODAY'S DATE"):
    for i in range(num_customers):
        st.session_state[f"date{i}"] = today_date()

customers = []
for i in range(num_customers):
    st.subheader(f"Customer {i+1}")
    name = st.text_input("Customer Name", key=f"name{i}")
    date = st.text_input("Date", key=f"date{i}")
    amount = st.text_input("Amount", key=f"amount{i}")
    wt = st.text_input("Weight", key=f"wt{i}")
    due = st.text_input("Due Date", key=f"due{i}")
    rate = st.text_input("Rate", value=st.session_state.get("shared_rate", ""), key=f"rate{i}")
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

if st.button("📊 GENERATE IMAGE"):
    if not customers:
        st.warning("No data entered")
    else:
        img = generate_image(customers)
        st.image(img)
        st.download_button("⬇️ DOWNLOAD", data=img, file_name="payment_table.png", mime="image/png")
