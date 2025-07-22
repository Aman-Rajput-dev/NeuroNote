import streamlit as st
from db_utils import fetch_filtered_notes

st.subheader("📚 Your Study Notes")

# Sidebar Filters
with st.sidebar:
    st.markdown("### 🔍 Filter Your Notes")
    keyword = st.text_input("Search by keyword")
    start_date = st.date_input("Start date")
    end_date = st.date_input("End date")

    # Convert to datetime
    from datetime import datetime
    start_dt = datetime.combine(start_date, datetime.min.time()) if start_date else None
    end_dt = datetime.combine(end_date, datetime.max.time()) if end_date else None

# Fetch filtered notes
notes = fetch_filtered_notes(start_dt, end_dt, keyword)

if not notes:
    st.info("No notes found for the selected filters.")
else:
    for idx, (prompt, response, source, img_list, timestamp) in enumerate(notes):
        with st.expander(f"📝 Note {idx+1} — {timestamp.strftime('%Y-%m-%d')} — {prompt}"):
            st.markdown(f"**🧠 Question:** {prompt}")
            st.markdown(f"**✅ Answer:** {response}")
            st.markdown(f"**📄 Sources:**\n\n{source}")
            if img_list:
                st.markdown("**🖼️ Related Images:**")
                img_cols = st.columns(len(img_list))
                for col, img_path in zip(img_cols, img_list):
                    with col:
                        st.image(img_path, use_container_width=True)
                        
    