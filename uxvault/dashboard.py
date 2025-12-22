# streamlit_app.py

import streamlit as st
import importlib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from st_supabase_connection import SupabaseConnection, execute_query

import uxvault.backend.supabase_client as supa_client #import get_authenticated_client, get_user_surveys_responses    
importlib.reload(supa_client)
get_authenticated_client = supa_client.get_authenticated_client
get_user_surveys_responses = supa_client.get_user_surveys_responses

st.set_page_config(layout="wide")
# Initialize connection without authentication.
if hasattr(st, 'user') == False:
    st.error("User is not logged in. Please log in to access your dashboard.")
    st.stop()
else:
    #uses session_state to cache sign up and sign in status
    st_supabase_client_authenticated = get_authenticated_client(user=st.user, secrets=st.secrets.connections.supabase)



with st.container(horizontal=True,vertical_alignment="center"):
    st.title("Dashboard")
    refreshed = st.button("Refresh my dashboard")

if refreshed or st.session_state.get('first_run',True):
    try:
        if st_supabase_client_authenticated is None:
            st.error("Authentication failed. Please log in again.")
            st.stop()
        rows = get_user_surveys_responses(st_supabase_client_authenticated)
        st.session_state['query_with_auth'] = rows
        # Handle different response types - some have .data attribute, others are direct lists
        try:
            if hasattr(rows, 'data') and rows.data is not None:
                st.session_state['query_with_auth_rows'] = rows.data
            elif isinstance(rows, list):
                st.session_state['query_with_auth_rows'] = rows
            else:
                st.session_state['query_with_auth_rows'] = []
        except:
            st.session_state['query_with_auth_rows'] = []
        st.session_state['first_run'] = False
    except Exception as e:
        st.error(f"Error: {e}")
st.divider()

# Two-tab layout: one tab to select surveys/responses to analyze, another to view packaged results
tab_select, tab_results = st.tabs(["Select Surveys", "Results"])

with tab_select:
    st.subheader("Select Surveys to Analyze")
    if 'query_with_auth' in st.session_state and st.session_state['query_with_auth'].data != []:
        if 'query_with_auth_rows' in st.session_state:
            # Group responses by survey_id so we can render each group in its own horizontal container
            rows = st.session_state['query_with_auth_rows']
            groups = {}
            for row in rows:
                sid = row.get('survey_id') or 'unknown'
                groups.setdefault(sid, []).append(row)

            def _toggle_group(survey_id, response_ids):
                val = st.session_state.get(f"analyze_survey_{survey_id}", False)
                for rid in response_ids:
                    st.session_state[f"analyze_response_{rid}"] = val

            for survey_id, group_rows in groups.items():
                with st.container(horizontal=True, gap="medium"):
                    st.subheader(f"Survey: {survey_id}")
                    response_ids = [r.get('id') for r in group_rows]
                    survey_key = f"analyze_survey_{survey_id}"
                    if survey_key not in st.session_state:
                        st.session_state[survey_key] = False
                    st.checkbox("Toggle all responses in this survey", key=survey_key, on_change=_toggle_group, args=(survey_id, response_ids))

                with st.container(horizontal=True, gap="large"):
                    for row in group_rows:
                        # Basic metadata / small card view
                        with st.container(border=True, width=300):
                            st.caption("Response ID" + row.get('id'))

                            # Completed at and count of sorted cards
                            response_data = row.get('response_data') or {}
                            completed_at = response_data.get('completed_at') if isinstance(response_data, dict) else None
                            sorted_cards = response_data.get('sorted_cards') if isinstance(response_data, dict) else []
                            st.caption("Completed At")
                            completed_at_fmtted = completed_at.split(".")[0] if completed_at else "N/A"
                            st.write(completed_at_fmtted)

                            st.caption("Sorted Cards")
                            st.write(len(sorted_cards) if sorted_cards is not None else 0)

                            # Checkbox to mark this response for further analysis
                            analyze_key = f"analyze_response_{row.get('id')}"
                            if analyze_key not in st.session_state:
                                st.session_state[analyze_key] = False
                            st.checkbox("Analyze this response", key=analyze_key)

            # removed packaging button: Results tab will show surveys with survey-level toggle enabled
    else:
        st.info("No results yet. Click button above to refresh.")

with tab_results: # complex data processing should be cached AND be done on a button
    # this is because this will always run 
    # TODO if session state of deleted widgets is fixed go back to conditional rendering
    # see https://discuss.streamlit.io/t/keyed-widget-state-persistence-discussion-possible-fixes/37359/12
    st.subheader("Results")
    # Collect all selected responses with their data
    selected_responses = []
    if 'query_with_auth_rows' in st.session_state:
        for row in st.session_state['query_with_auth_rows']:
            response_id = row.get('id')
            if st.session_state.get(f"analyze_response_{response_id}", False):
                selected_responses.append(row)

    if selected_responses:
        # Import analysis functions
        from uxvault.utils.card_sorting_analysis import (
            build_analysis_dataframe,
            build_comprehensive_category_analysis
        )

        # Create tabs for different types of analysis
        analysis_tabs = st.tabs(["Card Co-occurrence", "Category Analysis"])

        with analysis_tabs[0]:  # Card Co-occurrence Analysis
            st.subheader("Card Co-occurrence Analysis")
            analysis_data = build_analysis_dataframe(selected_responses)

            if analysis_data['cooccurrence'] is not None:
                total_responses = len(selected_responses)

                # Create interactive co-occurrence heatmap
                st.write("### Co-occurrence Heatmap")
                st.write("Interactive visualization showing how often cards appear together:")

                # Convert to percentage for better visualization
                cooccurrence_percent = analysis_data['cooccurrence'].copy()
                if total_responses > 0:
                    cooccurrence_percent = (cooccurrence_percent / total_responses * 100).round(1)

                # Create a mask for upper diagonal to show only lower triangle
                mask = np.triu(np.ones_like(cooccurrence_percent, dtype=bool), k=1)

                # Apply mask to set upper diagonal to NaN
                masked_values = cooccurrence_percent.values.copy()
                masked_values[mask] = np.nan

                # Create interactive heatmap using Plotly
                # TODO consider moving to a dataframe or something else

                fig = go.Figure(data=go.Heatmap(
                    z=masked_values,
                    x=cooccurrence_percent.columns,
                    y=cooccurrence_percent.index,
                    colorscale='Viridis',
                    text=masked_values,
                    texttemplate='%{text:.1f}%',
                    textfont={"size": 10},
                    hovertemplate='%{y} + %{x}: %{z:.1f}%<extra></extra>'
                ))

                fig.update_layout(
                    title='Card Co-occurrence Percentages (Lower Triangle)',
                    xaxis_title='Cards',
                    yaxis_title='Cards',
                    height=600,
                    width=800
                )

                st.plotly_chart(fig, use_container_width=True)

                # Add summary statistics using horizontal containers
                with st.container(horizontal=True):
                    st.metric("Total Responses", len(selected_responses))
                    st.metric("Unique Cards", len(analysis_data['unique_cards']))
                    st.metric("Card Pairs", f"{len(analysis_data['unique_cards']) * (len(analysis_data['unique_cards']) - 1) // 2}")

                # Make similarity matrix less prominent (used for dendrograms)
                with st.expander("📊 Advanced: Similarity Matrix (for dendrograms)"):
                    st.write("This matrix is used for hierarchical clustering and dendrogram visualization:")
                    st.dataframe(analysis_data['similarity'])

                with st.expander("📊 Advanced: Distance Matrix (for dendrograms)"):
                    st.write("This matrix is used for hierarchical clustering and dendrogram visualization:")
                    st.dataframe(analysis_data['distance'])

            if analysis_data['unique_cards']:
                st.write(f"### Cards in Analysis")
                st.write(", ".join(analysis_data['unique_cards']))

        with analysis_tabs[1]:  # Category Analysis
            st.subheader("Category Analysis")
            category_analysis = build_comprehensive_category_analysis(selected_responses)

            if category_analysis['category_matrix'] is not None:
                st.write("### Category Assignment Matrix")
                st.write("Shows how many times each card was assigned to each category:")
                st.dataframe(category_analysis['category_matrix'])

                st.write("### Category Consistency Matrix")
                st.write("Shows the proportion (0-1) of times each card was assigned to each category:")
                st.dataframe(category_analysis['consistency_matrix'])

            if category_analysis['category_popularity'] is not None:
                st.write("### Category Popularity Analysis")

                col1, col2 = st.columns(2)

                with col1:
                    st.write("#### Category Usage")
                    popularity = category_analysis['category_popularity']
                    usage_df = pd.DataFrame({
                        'Category': list(popularity['category_usage'].keys()),
                        'Responses Using': list(popularity['category_usage'].values()),
                        'Total Cards': list(popularity['category_counts'].values()),
                        'Avg Cards/Response': [f"{val:.1f}" for val in popularity['average_cards_per_category'].values()]
                    })
                    st.dataframe(usage_df)

                with col2:
                    st.write("#### Category Statistics")
                    st.write(f"**Total Responses Analyzed:** {popularity['total_responses']}")
                    st.write(f"**Total Categories Found:** {popularity['total_categories']}")

                    # Find most and least used categories
                    if popularity['category_usage']:
                        most_used = max(popularity['category_usage'].items(), key=lambda x: x[1])
                        least_used = min(popularity['category_usage'].items(), key=lambda x: x[1])
                        st.write(f"**Most Used Category:** {most_used[0]} ({most_used[1]} responses)")
                        st.write(f"**Least Used Category:** {least_used[0]} ({least_used[1]} responses)")

            if category_analysis['unique_categories']:
                st.write(f"### Categories Found ({len(category_analysis['unique_categories'])})")
                st.write(", ".join(category_analysis['unique_categories']))

                st.write(f"### Cards Found ({len(category_analysis['unique_cards'])})")
                st.write(", ".join(category_analysis['unique_cards']))

            # Show raw data in expanders for advanced users
            with st.expander("📊 Advanced: Raw Analysis Data"):
                for key, value in category_analysis.items():
                    if key not in ['category_matrix', 'consistency_matrix', 'unique_cards', 'unique_categories']:
                        st.write(f"**{key}:**")
                        st.write(value)

    else:
        st.info("No responses selected for analysis. Please select responses in the 'Select Surveys' tab.")


# display the user info
