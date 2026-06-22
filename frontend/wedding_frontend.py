# destination_wedding_frontend.py
import streamlit as st
import requests
import plotly.express as px
import pandas as pd
from datetime import datetime
from io import BytesIO

# Configure Streamlit Page
st.set_page_config(
    page_title="Destination Wedding Planner",
    page_icon="💍",
    layout="wide"
)

# Backend API URL
BASE_URL = "http://localhost:5000"

# Function to get available countries
@st.cache_data(ttl=3600)
def get_countries():
    try:
        response = requests.get(f"{BASE_URL}/countries")
        if response.ok:
            return response.json()['countries']
        st.error("Error fetching countries.")
        return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

# Function to get cities for a selected country
@st.cache_data(ttl=3600)
def get_cities(country):
    try:
        response = requests.get(f"{BASE_URL}/cities", params={'country': country})
        if response.ok:
            return response.json()['cities']
        st.error("Error fetching cities.")
        return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

# Function to get wedding destination recommendations
def get_recommendations(country, city):
    try:
        response = requests.post(f"{BASE_URL}/recommend", json={"country": country, "city": city})
        if response.ok:
            return response.json()
        st.error("Error fetching recommendations.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Sidebar Inputs
st.sidebar.header("💒 Plan Your Dream Wedding")
countries = get_countries()
selected_country = st.sidebar.selectbox("🌍 Select Country", options=countries)

if selected_country:
    cities = get_cities(selected_country)
    selected_city = st.sidebar.selectbox("🏙️ Select City", options=cities)
    analyze_btn = st.sidebar.button("🔍 Find Wedding Destinations")

# Main Dashboard
st.title("💍 Destination Wedding Planner")

if selected_country and selected_city and analyze_btn:
    with st.spinner("Fetching destination details..."):
        data = get_recommendations(selected_country, selected_city)

    if data:
        st.write("Backend Response:")
        st.json(data)
        st.header(f"🏆 Wedding Destination Score: **{data['selected']['Destination Wedding Score']:.2f}**")

        # Metrics Section
        st.subheader("📊 Key Metrics")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("🌍 Tourist Arrivals", f"{data['selected']['Tourist Arrivals (millions)']}M")
        with col2:
            st.metric("✈️ International Passengers", f"{data['selected']['International Air Passengers']}")
        with col3:
            st.metric("🛡️ Safety Index", f"{data['selected']['Safety Index (Low Crime Rate)']}")

        # Comparative Charts
        st.subheader("📈 Comparative Analysis")
        rec_data = pd.DataFrame(data['recommendations'])

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.bar(
                rec_data,
                x="name",
                y="Ease of Business Score",
                title="🏛️ Ease of Business (Wedding Logistics)"
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.scatter(
                rec_data,
                x="Safety Index (Low Crime Rate)",
                y="Destination Wedding Score",
                title="🔒 Safety vs Wedding Suitability",
                size="Tourist Arrivals (millions)"
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Top Wedding Destinations
        st.subheader("💐 Recommended Wedding Destinations")
        for index, rec in rec_data.head(5).iterrows():
            with st.container():
                st.markdown(f"""
                ### **{rec['name']}, {rec['countrycode']}**
                - 🏆 **Wedding Score:** {rec['Destination Wedding Score']:.2f}
                - ✈️ **International Passengers:** {rec['International Air Passengers']}
                - 🌍 **Tourist Arrivals:** {rec['Tourist Arrivals (millions)']}M
                - 🛡️ **Safety Index:** {rec['Safety Index (Low Crime Rate)']}
                """)

        # Export Options
        st.subheader("📤 Export Your Plan")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📄 Download CSV"):
                csv_data = rec_data.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    data=csv_data,
                    file_name="wedding_destinations.csv",
                    mime="text/csv"
                )

        with col2:
            if st.button("📑 Generate Wedding Report"):
                def generate_pdf():
                    """Generate a PDF with wedding recommendations"""
                    from reportlab.lib import colors
                    from reportlab.lib.pagesizes import letter
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
                    from reportlab.lib.styles import getSampleStyleSheet

                    buffer = BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=letter)
                    styles = getSampleStyleSheet()
                    story = []

                    # Title
                    story.append(Paragraph("Destination Wedding Report", styles['Title']))

                    # Selected Destination
                    selected_data = [
                        ['Metric', 'Value'],
                        ['City', data['selected']['name']],
                        ['Country', data['selected']['countrycode']],
                        ['Wedding Score', f"{data['selected']['Destination Wedding Score']:.2f}"],
                        ['Safety Index', f"{data['selected']['Safety Index (Low Crime Rate)']}"],
                        ['Tourist Arrivals', f"{data['selected']['Tourist Arrivals (millions)']}M"]
                    ]
                    table = Table(selected_data, colWidths=[200, 200])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(table)

                    # Build PDF
                    doc.build(story)
                    buffer.seek(0)
                    return buffer

                pdf_data = generate_pdf()
                st.download_button(
                    "Download Report",
                    data=pdf_data,
                    file_name="wedding_report.pdf",
                    mime="application/pdf"
                )

else:
    st.info("👈 Choose a country and city to explore wedding destinations!")
