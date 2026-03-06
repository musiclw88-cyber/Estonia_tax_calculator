import streamlit as st

def calculate_tax_from_net(net_salary, pension_rate):
    """
    Reverse calculation for Estonia 2026.
    - Flat tax-free allowance: €700
    - Income Tax: 22%
    - Pension Pillar II: User defined (0%, 2%, 4%, or 6%)
    - Unemployment Insurance: 1.6% (Employee) / 0.8% (Employer)
    """
    
    # Rates and Constants
    p_rate = pension_rate / 100
    ui_ee_rate = 0.016
    allowance = 700.0
    it_rate = 0.22

    # Step 1: Reverse Calculate Gross Salary
    # If Net <= 700 * (1 - p_rate - ui_ee_rate), no income tax is paid.
    threshold_net = allowance * (1 - p_rate - ui_ee_rate)
    
    if net_salary <= threshold_net:
        gross_salary = net_salary / (1 - p_rate - ui_ee_rate)
    else:
        # Derived formula for 2026 rules:
        # Gross = (Net - (Allowance * IT_rate)) / ((1 - p_rate - ui_ee_rate) * (1 - IT_rate))
        numerator = net_salary - (allowance * it_rate)
        denominator = (1 - p_rate - ui_ee_rate) * (1 - it_rate)
        gross_salary = numerator / denominator

    # Step 2: Detailed Calculations (Employee side)
    pension_funded = gross_salary * p_rate
    unemployment_ee = gross_salary * ui_ee_rate
    
    # Taxable base = Gross - Pension - UI_EE - 700
    taxable_base = gross_salary - pension_funded - unemployment_ee - allowance
    income_tax = max(0.0, taxable_base * it_rate)

    # Step 3: Employer Contributions
    social_tax = gross_salary * 0.33
    unemployment_er = gross_salary * 0.008
    total_employer_cost = gross_salary + social_tax + unemployment_er

    # Step 4: Total Tax Burden (All taxes combined)
    total_tax_paid = (pension_funded + unemployment_ee + income_tax) + (social_tax + unemployment_er)

    return {
        "gross": gross_salary,
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

st.title("🇪🇪 Estonia Salary Reverse Calculator (2026)")
st.info("Calculated with the **€700** flat allowance and **22%** income tax rate.")

# Input Section
col1, col2 = st.columns([2, 1])
with col1:
    net_input = st.number_input("Desired Net Salary (In hand €):", min_value=0.0, value=1900.0, step=50.0)
with col2:
    pension_opt = st.selectbox("Pension Pillar II:", [0, 2, 4, 6], index=3, format_func=lambda x: f"{x}%")

if net_input > 0:
    res = calculate_tax_from_net(net_input, pension_opt)
    
    # Primary Results
    st.divider()
    res_col1, res_col2 = st.columns(2)
    res_col1.metric("Required Gross Salary", f"€{res['gross']:,.2f}")
    res_col2.metric("Total Employer Cost", f"€{res['total_cost']:,.2f}")

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
            f"€{net_input:,.2f}",
            f"€{res['pension']:,.2f}",
            f"€{res['income_tax']:,.2f}",
            f"€{res['ee_ui']:,.2f}",
            f"€{res['social']:,.2f}",
            f"€{res['er_ui']:,.2f}"
        ]
    })

    st.warning(f"Total tax burden: **€{res['burden']:,.2f}** ({res['ratio']:.2f}% of total cost).")
