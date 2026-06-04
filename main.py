import streamlit as st
import langchain_helper

st.set_page_config(
    page_title="AI Restaurant Planner", 
    page_icon="🍽",
    initial_sidebar_state="expanded"
)
st.title("🍽️ The Menu Architect")

# Map of countries to their respective currency formats
CURRENCY_MAP = {
    "India (INR - ₹)": "₹",
    "United States (USD - $)": "$",
    "United Kingdom (GBP - £)": "£",
    "Europe (EUR - €)": "€",
    "Japan (JPY - ¥)": "¥",
    "Australia (AUD - A$)": "A$"
}

# Sidebar - Location/Currency selection
country_selection = st.sidebar.selectbox(
    "Choose Location",
    tuple(CURRENCY_MAP.keys()),
    index=None, # Starts completely blank so you can choose whatever you want
    placeholder="Select target country..."
)

# Extract the raw symbol only if a country has been selected
currency_symbol = CURRENCY_MAP[country_selection] if country_selection else ""

# Sidebar - Cuisine selection
cuisine = st.sidebar.selectbox(
    "Pick a Cuisine",
    ("Indian", "Italian", "Mexican", "Arabic", "American", "Chinese"),
    index=None,
    placeholder="Select a cuisine..."
)

# Sidebar - Vibe/Theme selection
vibe = st.sidebar.selectbox(
    "Select a Vibe",
    ("Fine Dining", "Fast Food", "Street Food", "Cafeteria", "Trendy Cafe", "Family Buffet"),
    index=None,
    placeholder="Select a vibe..."
)

# Trigger logic ONLY when all three configurations are selected
if country_selection and cuisine and vibe:
    with st.spinner(f"Designing your {vibe} {cuisine} restaurant for {country_selection}..."):
        try:
            @st.cache_data(show_spinner=False)
            def get_cached_restaurant_data(c, v, curr):
                return langchain_helper.generate_restaurant_name_and_items(c, v, curr)
                
            response = get_cached_restaurant_data(cuisine, vibe, currency_symbol)
            
            # Display Restaurant Name
            st.header(response["restaurant_name"])
            st.write(f"*A unique {vibe.lower()} concept serving exceptional {cuisine.lower()} cuisine custom-priced for {country_selection}.*")
            st.markdown("---")
            
            st.subheader("Suggested Menu")
            
            download_text = f"Restaurant Name: {response['restaurant_name']}\nConcept: {vibe} {cuisine}\nLocation Context: {country_selection}\n\nMENU ITEMS:\n"
            
            # Use a dynamic container key based on selections to clear old state layouts instantly
            container_key = f"menu_block_{cuisine}_{vibe}_{currency_symbol}"
            
            with st.container(key=container_key):
                for item in response["menu_items"]:
                    name = item["name"]
                    price = item["price"]
                    
                    download_text += f"- {name} ({price})\n"
                    
                    # Render item title and price
                    st.markdown(f"### {name} —  `{price}`")
                    
                    # Create a unique key inside session state for the data fetching
                    state_key = f"ing_{name.replace(' ', '_')}"
                    
                    with st.expander("🛒 View Required Ingredients", expanded=False):
                        if state_key not in st.session_state:
                            with st.spinner("Analyzing recipe requirements..."):
                                st.session_state[state_key] = langchain_helper.get_ingredients(name, cuisine)
                        
                        st.write(st.session_state[state_key])
                    
                    st.write("") # Tiny spacer between items
            
            st.markdown("---")
            
            # Download Menu Button
            st.download_button(
                label="📥 Download Menu",
                data=download_text,
                file_name=f"{response['restaurant_name'].replace(' ', '_')}_menu.txt",
                mime="text/plain"
            )
                
        except Exception as e:
            st.error(f"An error occurred: {e}")