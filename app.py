import streamlit as st

def calculate_payroll(amount, input_type, pension_rate):
    # --- Standard Parameters ---
    tax_free_threshold = 700
    income_tax_rate = 0.22
    unemployment_ee_rate = 0.016
    social_tax_er_rate = 0.33
    unemployment_er_rate = 0.008
    standard_pension_rate = 0.06
    
    # Total Employee Deduction rate (excluding Income Tax)
    # 6% Standard + 1.6% Unemployment + Selected Funded Pension (0-6%)
    ee_deduction_rate = standard_pension_rate + unemployment_ee_rate + (pension_rate / 100)

    # --- Core Logic: Calculate Gross Salary ---
    if input_type == "Gross Salary":
        gross = amount
    else:
        # Reverse Calculation (Net -> Gross)
        tax_credit = tax_free_threshold * income_tax_rate
        # Coefficient representing the ratio of Net after deductions and tax
        coefficient = (1 - ee_deduction_rate) * (1 - income_tax_rate)
        
        # Check if the amount is below the tax-free threshold logic
        threshold_net = tax_free_threshold * (1 - ee_deduction_rate)
        if amount <= threshold_net:
            gross = amount / (1 - ee_deduction_rate)
        else:
            gross =(amount - 154)/0.72072

    # --- Detailed Calculations ---
    pension_std = gross * standard_pension_rate
    pension_funded = gross * (pension_rate / 100)
    unemployment_ee = gross * unemployment_ee_rate
    
    # Taxable Base for Income Tax
    taxable_base = gross - pension_std - pension_funded - unemployment_ee - tax_free_threshold
    income_tax = max(0.0, taxable_base * income_tax_rate)
    
    # Final Net Salary
    if input_type == "Gross Salary":
        net_salary = gross - (pension_std + pension_funded + unemployment_ee) - income_tax
    else: net_salary = amount 
        
    # Employer Contributions
    social_tax_er = gross * social_tax_er_rate
    unemployment_er = gross * unemployment_er_rate
    total_employer_cost = gross + social_tax_er + unemployment_er
    
    # --- TOTAL TAX BURDEN ---
    # Formula: Total Employer Cost - Net Salary = Everything paid to the state
    total_tax_burden = total_employer_cost - net_salary
    
    return {
        "Total Employer Cost": total_employer_cost,
        "Total Tax Burden": total_tax_burden,
        "Gross Salary": gross,
        "Net Salary": net_salary,
        "Income Tax (22%)": income_tax,
        "Standard Pension (6%)": pension_std,
        "Funded Pension (Selected)": pension_funded,
        "Unemployment (Employee)": unemployment_ee,
        "Social Security (Employer)": social_tax_er,
        "Unemployment (Employer)": unemployment_er
    }

# --- Web Interface Layout ---
st.set_page_config(page_title="Global Payroll Calculator", page_icon="🏦")
st.title("🏦 Advanced Payroll & Tax Simulator")

st.markdown("""
This tool calculates the full cost of employment and tax breakdowns based on either **Net** or **Gross** salary.
""")

# Input Section
col_in1, col_in2 = st.columns(2)
with col_in1:
    salary_type = st.radio("1. Select Input Type", ["Net Salary", "Gross Salary"])
    input_amount = st.number_input(f"2. Enter {salary_type} Amount", min_value=0.0, value=3000.0, step=100.0)
with col_in2:
    pension_choice = st.selectbox("3. Funded Pension Subscriber (%)", [0, 2, 4, 6], index=0)

if input_amount:
    res = calculate_payroll(input_amount, salary_type, pension_choice)
    
    st.divider()
    
    # Metrics Row: The three most important numbers
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Employer Cost", f"${res['Total Employer Cost']:,.2f}")
    m2.metric("Total Tax Burden", f"${res['Total Tax Burden']:,.2f}", delta="-Government Take", delta_color="inverse")
    m3.metric("Employee Take-home", f"${res['Net Salary']:,.2f}")

    # Detailed Table
    st.subheader("📊 Full Financial Breakdown")
    # Formatting numbers for the table
    formatted_res = {k: f"${v:,.2f}" for k, v in res.items()}
    st.table(formatted_res)

    # Efficiency Insights
    efficiency = (res['Net Salary'] / res['Total Employer Cost']) * 100
    st.info(f"💡 **Salary Efficiency:** The employee receives **{efficiency:.2f}%** of the company's total expenditure.")

st.caption("Calculation based on standard 22% Income Tax after a 700 threshold and combined employer/employee social contributions.")
