import streamlit as st

def calculate_taxes(amount, mode, pension_rate):
    """
    Handles both Gross-to-Net and Net-to-Gross for Estonia 2026.
    """
    p_rate = pension_rate / 100
    ui_ee_rate = 0.016
    allowance = 700.0
    it_rate = 0.22
    
    if mode == "Net to Gross (Reverse)":
        net_salary = amount
        threshold_net = allowance * (1 - p_rate - ui_ee_rate)
        if net_salary <= threshold_net:
            gross_salary = net_salary / (1 - p_rate - ui_ee_rate)
        else:
            numerator = net_salary - (allowance * it_rate)
            denominator = (1 - p_rate - ui_ee_rate) * (1 - it_rate)
            gross_salary = numerator / denominator
    else:
        # Gross to Net
        gross_salary = amount

    # Detailed Breakdown
    pension_funded = gross_salary * p_rate
    unemployment_ee = gross_salary * ui_ee_rate
    
    # Taxable base calculation
    taxable_base = gross_salary - pension_funded - unemployment_ee - allowance
    income_tax = max(0.0, taxable_base * it_rate)
    
    # Final Net
    net_final = gross_salary - pension_funded - unemployment_ee - income_tax
    
    # Employer Costs
    social_tax = gross_salary * 0.33
    unemployment_er = gross_salary * 0.008
    total_employer_cost = gross_salary + social_tax + unemployment_er
    
    # Total Burden
    total_tax_paid = (pension_funded + unemployment_ee + income_tax) + (social_tax + unemployment_er)

    return {
        "gross": gross_salary,
        "net": net_final,
        "total_cost": total_employer_cost,
        "income_tax": income_tax,
        "pension": pension_funded,
        "ee_ui": unemployment_ee,
        "social": social_tax,
        "er_ui": unemployment_er,
        "burden": total_tax_paid,
        "ratio": (total_tax_paid / total_employer_cost) * 100 if total_employer_cost > 0 else 0
    }

# --- Streamlit UI ---
st.set_page_config(page_title="Estonia Tax Calc 2026", page_icon="🇪🇪")

st.title("🇪🇪 Estonia Salary Calculator (2026)")
st.info("Updated for 2026: **€700** flat allowance and **22%** income tax rate.")

# Mode Selection
calc_mode = st.radio("Choose Calculation Mode:", ["Gross to Net", "Net to Gross (Reverse)"], horizontal=True)

# Input Row
col1, col2 = st.columns([2, 1])
with col1:
    label = "Enter Gross Salary (€):" if calc_mode == "Gross to Net" else "Enter Net Salary (In hand €):"
    input_val = st.number_input(label, min_value=0.0, value=2500.0 if calc_mode == "Gross to Net" else 1900.0, step=50.0)
with col2:
    pension_opt = st.selectbox("Pension Pillar II:", [0, 2, 4, 6], index=3, format_func=lambda x: f"{x}%")

if input_val > 0:
    res = calculate_taxes(input_val, calc_mode, pension_opt)
    
    # Primary Results
    st.divider()
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("Net (In hand)", f"€{res['net']:,.2f}")
    res_col2.metric("Gross Salary", f"€{res['gross']:,.2f}")
    res_col3.metric("Total Employer Cost", f"€{res['total_cost']:,.2f}")

    # Detailed Breakdown Table
    st.subheader("Monthly Breakdown")
    st.table({
        "Category": [
            "Net Salary (In hand)", 
            f"Pension Pillar II ({pension_opt}%)", 
            "Income Tax (22%)", 
            "Unemployment Insurance (Employee 1.6%)", 
            "Social Tax (Employer 33%)", 
            "Unemployment Insurance (Employer 0.8%)"
        ],
        "Amount": [
            f"€{res['net']:,.2f}",
            f"€{res['pension']:,.2f}",
            f"€{res['income_tax']:,.2f}",
            f"€{res['ee_ui']:,.2f}",
            f"€{res['social']:,.2f}",
            f"€{res['er_ui']:,.2f}"
        ]
    })

    st.warning(f"Total tax burden: **€{res['burden']:,.2f}** ({res['ratio']:.2f}% of total cost).")
