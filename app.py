import streamlit as st
import pandas as pd
import scraper
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize Scheduler to run nightly
@st.cache_resource
def init_scheduler():
    scheduler = BackgroundScheduler()
    # Run every day at 6 PM (18:00) server time
    # Note: Railway servers are usually in UTC. 
    # If you want 6 PM PST (UTC-8), set this to 2:00 AM UTC (hour=2)
    scheduler.add_job(scraper.monitor_deals, 'cron', hour=18, minute=0)
    scheduler.start()
    print("Scheduler started! Will run scraper daily at 18:00.")
    return scheduler

# Start the scheduler
if not os.environ.get("IS_BUILD_PROCESS"): # Avoid running during build
    scheduler = init_scheduler()

st.set_page_config(page_title="BuyWander Hunter", page_icon="🛒", layout="wide")

# --- Simple Password Protection ---
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == os.environ.get("APP_PASSWORD", "admin"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Please enter the password to access BuyWander Hunter", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error.
        st.text_input(
            "Please enter the password to access BuyWander Hunter", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
    st.title("🛒 BuyWander Deal Hunter")

    # Sidebar for controls
    with st.sidebar:
        st.header("Controls")
        if st.button("🔄 Run Scraper Now", type="primary"):
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            status_text.text("Starting scraper...")
            
            # We can't easily hook into the print statements of the imported module 
            # without complex redirection, so we'll just run it and show a spinner.
            with st.spinner("Scraping BuyWander... (This takes about 30-60 seconds)"):
                try:
                    # Run the scraper
                    scraper.monitor_deals()
                    st.success("Scraping complete! Data updated.")
                    time.sleep(1) # Give a moment to see the success message
                    st.rerun()
                except Exception as e:
                    st.error(f"Error running scraper: {e}")

        st.divider()
        st.markdown("### About")
        st.markdown("Scrapes BuyWander for specific interests: Networking, Benz parts, Tools, etc.")

    # Main content
    csv_file = 'buywander_interests.csv'

    if os.path.exists(csv_file):
        # Load data
        try:
            df = pd.read_csv(csv_file)
            
            # Basic stats
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Items Found", len(df))
            col2.metric("Last Updated", time.ctime(os.path.getmtime(csv_file)))
            
            # Filters
            st.subheader("Filter Deals")
            
            # Category Filter
            all_categories = sorted(df['Interest Category'].unique().tolist())
            selected_categories = st.multiselect("Filter by Category", options=all_categories, default=all_categories)
            
            # Search Filter
            search_term = st.text_input("Search Title", "")
            
            # Apply filters
            filtered_df = df.copy()
            if selected_categories:
                filtered_df = filtered_df[filtered_df['Interest Category'].isin(selected_categories)]
            
            if search_term:
                filtered_df = filtered_df[filtered_df['Title'].str.contains(search_term, case=False, na=False)]

            st.caption(f"Showing {len(filtered_df)} items")

            # Display Dataframe with formatting
            st.dataframe(
                filtered_df,
                column_config={
                    "Image URL": st.column_config.ImageColumn("Image", width="small"),
                    "URL": st.column_config.LinkColumn("Link", display_text="View Auction"),
                    "Retail": st.column_config.NumberColumn("Retail", format="$%.2f"),
                    "Current Bid": st.column_config.NumberColumn("Bid", format="$%.2f"),
                    "Bids": st.column_config.NumberColumn("Bids"),
                    "End Date": st.column_config.DatetimeColumn("Ends At", format="D MMM, h:mm a"),
                },
                use_container_width=True,
                hide_index=True,
                height=800
            )
            
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            st.warning("Try running the scraper again to regenerate the file.")
    else:
        st.info("No data found yet. Click 'Run Scraper Now' in the sidebar to fetch deals.")
