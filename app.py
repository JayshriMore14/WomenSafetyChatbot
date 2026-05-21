"""Women Safety Chatbot Streamlit application.

This is a fully local, beginner-friendly safety assistant. Twilio support is
optional and uses environment variables only when configured.
"""

from __future__ import annotations

import time
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from chatbot import detect_danger_keywords, get_chatbot_response
from database import add_contact, delete_contact, get_contacts, init_db, update_contact
from emergency import EMERGENCY_INSTRUCTIONS, simulate_emergency_notification
from location_services import (
    build_help_map,
    get_current_location,
    get_location_message,
    get_nearby_help_centers,
)
from self_defense import QUICK_ACTIONS, SELF_DEFENSE_GUIDE
from voice_support import speak_text, speech_to_text


st.set_page_config(page_title="Women Safety Chatbot", page_icon="SOS", layout="wide")


CUSTOM_CSS = """
<style>
    .main { background: #f8fafc; }
    .hero {
        background: linear-gradient(135deg, #881337, #be123c 48%, #4c1d95);
        color: white;
        padding: 1.25rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .hero h1 { margin: 0; font-size: 2rem; letter-spacing: 0; }
    .hero p { margin: .35rem 0 0; color: #ffe4e6; }
    .card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 1px 8px rgba(15, 23, 42, 0.08);
    }
    .metric-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-left: 5px solid #be123c;
        border-radius: 8px;
        padding: 1rem;
        min-height: 110px;
    }
    .metric-card span { color: #64748b; font-size: .9rem; }
    .metric-card strong { display: block; color: #0f172a; font-size: 1.7rem; margin-top: .35rem; }
    .sos-box {
        background: #fff1f2;
        border: 2px solid #be123c;
        border-radius: 8px;
        padding: 1rem;
    }
    .fake-call {
        background: linear-gradient(160deg, #111827, #374151);
        color: white;
        border-radius: 8px;
        padding: 2rem 1rem;
        text-align: center;
    }
    .fake-call h2 { margin-bottom: .25rem; }
</style>
"""


def init_state() -> None:
    """Initialize app session state."""
    defaults = {
        "emergency_mode": False,
        "chat_history": [],
        "last_location_message": "",
        "fake_call_active": False,
        "fake_caller": "Mom",
        "voice_text": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def render_hero() -> None:
    """Render the app header."""
    st.markdown(
        """
        <div class="hero">
            <h1>Women Safety Chatbot</h1>
            <p>Emergency SOS, safety guidance, contacts, maps, fake call support, and voice interaction in one local app.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(title: str, value: str) -> None:
    """Render a dashboard metric card."""
    st.markdown(
        f"""
        <div class="metric-card">
            <span>{title}</span>
            <strong>{value}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )


def activate_emergency(reason: str = "SOS button clicked") -> None:
    """Activate emergency mode and store the reason in chat history."""
    st.session_state.emergency_mode = True
    st.session_state.chat_history.append(
        {
            "role": "system",
            "message": f"Emergency mode activated: {reason}",
            "time": datetime.now().strftime("%H:%M:%S"),
        }
    )


def render_alert_banner() -> None:
    """Show an emergency alert banner if needed."""
    if st.session_state.emergency_mode:
        st.error("Emergency mode is active. Share location, contact trusted people, and call local emergency services if you are in immediate danger.")


def render_dashboard() -> None:
    """Dashboard overview with cards and charts."""
    contacts = get_contacts()
    latitude, longitude = get_current_location()
    help_centers = get_nearby_help_centers(latitude, longitude)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Emergency Mode", "Active" if st.session_state.emergency_mode else "Ready")
    with col2:
        render_metric_card("Saved Contacts", str(len(contacts)))
    with col3:
        render_metric_card("Nearby Help Centers", str(len(help_centers)))
    with col4:
        render_metric_card("Quick Actions", str(len(QUICK_ACTIONS)))

    st.subheader("Safety Feature Overview")
    chart_data = pd.DataFrame(
        {
            "Feature": ["SOS", "Tips", "Contacts", "Maps", "Fake Call", "Voice", "Self Defense"],
            "Readiness": [100, 95, 90 if contacts else 45, 90, 85, 75, 95],
        }
    )
    st.bar_chart(chart_data.set_index("Feature"))

    st.subheader("Nearby Help Map")
    st_folium(build_help_map(latitude, longitude), width=900, height=430)


def render_sos() -> None:
    """Render emergency SOS controls."""
    st.subheader("Emergency SOS")
    st.markdown('<div class="sos-box">', unsafe_allow_html=True)
    st.write("Use this button when you need immediate help. The app will activate emergency mode and prepare alerts.")

    if st.button("SOS - Activate Emergency", type="primary", use_container_width=True):
        latitude, longitude = get_current_location()
        st.session_state.last_location_message = get_location_message(latitude, longitude)
        activate_emergency("SOS button clicked")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.emergency_mode:
        st.subheader("Emergency Instructions")
        for instruction in EMERGENCY_INSTRUCTIONS:
            st.write(f"- {instruction}")

        st.subheader("Emergency Notification Simulation")
        contacts = get_contacts()
        notifications = simulate_emergency_notification(contacts, st.session_state.last_location_message)
        for notification in notifications:
            st.info(notification)

        if st.button("Deactivate Emergency Mode"):
            st.session_state.emergency_mode = False
            st.success("Emergency mode deactivated.")
            st.rerun()


def render_chatbot() -> None:
    """Render chatbot and danger keyword detection."""
    st.subheader("Safety Chatbot")
    st.write("Ask about night travel, cyber safety, public transport, self-defense, harassment help, or emotional support.")

    user_message = st.chat_input("Type your safety question or emergency message")
    if user_message:
        response, emergency_detected, danger_words = get_chatbot_response(user_message)
        st.session_state.chat_history.append(
            {"role": "user", "message": user_message, "time": datetime.now().strftime("%H:%M:%S")}
        )
        st.session_state.chat_history.append(
            {"role": "assistant", "message": response, "time": datetime.now().strftime("%H:%M:%S")}
        )

        if emergency_detected:
            activate_emergency(f"Danger keyword detected: {', '.join(danger_words)}")
            st.warning(f"Danger keywords detected: {', '.join(danger_words)}")

    for item in st.session_state.chat_history[-12:]:
        with st.chat_message("assistant" if item["role"] == "system" else item["role"]):
            st.write(item["message"])

    st.subheader("Try Quick Questions")
    examples = [
        "How can I stay safe during night travel?",
        "What should I do about online harassment?",
        "I feel unsafe and need help",
        "Give me public transport safety tips",
    ]
    cols = st.columns(2)
    for index, example in enumerate(examples):
        with cols[index % 2]:
            if st.button(example, use_container_width=True):
                response, emergency_detected, danger_words = get_chatbot_response(example)
                st.session_state.chat_history.append({"role": "user", "message": example, "time": datetime.now().strftime("%H:%M:%S")})
                st.session_state.chat_history.append({"role": "assistant", "message": response, "time": datetime.now().strftime("%H:%M:%S")})
                if emergency_detected:
                    activate_emergency(f"Danger keyword detected: {', '.join(danger_words)}")
                st.rerun()


def render_contacts() -> None:
    """Render emergency contact CRUD system."""
    st.subheader("Emergency Contacts")
    contacts = get_contacts()

    with st.form("add_contact_form", clear_on_submit=True):
        st.markdown("#### Add Contact")
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        relation = st.text_input("Relation", value="Family")
        priority = st.number_input("Priority", min_value=1, max_value=10, value=1)
        submitted = st.form_submit_button("Add Contact")
        if submitted:
            if name.strip() and phone.strip() and relation.strip():
                add_contact(name, phone, relation, int(priority))
                st.success("Contact added.")
                st.rerun()
            else:
                st.error("Name, phone, and relation are required.")

    if not contacts:
        st.info("No emergency contacts saved yet.")
        return

    st.markdown("#### Saved Contacts")
    st.dataframe(pd.DataFrame(contacts), use_container_width=True, hide_index=True)

    selected_id = st.selectbox("Select contact to edit or delete", [contact["id"] for contact in contacts])
    selected = next(contact for contact in contacts if contact["id"] == selected_id)

    with st.form("edit_contact_form"):
        edit_name = st.text_input("Edit Name", value=selected["name"])
        edit_phone = st.text_input("Edit Phone", value=selected["phone"])
        edit_relation = st.text_input("Edit Relation", value=selected["relation"])
        edit_priority = st.number_input("Edit Priority", min_value=1, max_value=10, value=int(selected["priority"]))
        update_col, delete_col = st.columns(2)
        with update_col:
            update_submitted = st.form_submit_button("Update Contact")
        with delete_col:
            delete_submitted = st.form_submit_button("Delete Contact")

        if update_submitted:
            update_contact(selected_id, edit_name, edit_phone, edit_relation, int(edit_priority))
            st.success("Contact updated.")
            st.rerun()

        if delete_submitted:
            delete_contact(selected_id)
            st.warning("Contact deleted.")
            st.rerun()

    st.markdown("#### One-Click Emergency Contact Display")
    for contact in contacts:
        st.info(f"{contact['name']} - {contact['relation']} - {contact['phone']}")


def render_help_centers() -> None:
    """Render map and help centers."""
    st.subheader("Nearby Help Centers")
    latitude, longitude = get_current_location()
    centers = get_nearby_help_centers(latitude, longitude)
    st_folium(build_help_map(latitude, longitude), width=900, height=500)
    st.dataframe(pd.DataFrame(centers), use_container_width=True, hide_index=True)


def render_fake_call() -> None:
    """Render fake incoming call simulation."""
    st.subheader("Fake Call")
    caller = st.selectbox("Caller Name", ["Mom", "Dad", "Best Friend", "Office", "Police Help Desk", "Custom"])
    if caller == "Custom":
        caller = st.text_input("Custom Caller Name", value="Trusted Contact")

    ringtone = st.selectbox("Ringtone Simulation", ["Classic Ring", "Soft Tone", "Vibration Only"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Fake Call", type="primary", use_container_width=True):
            st.session_state.fake_call_active = True
            st.session_state.fake_caller = caller
    with col2:
        if st.button("End Fake Call", use_container_width=True):
            st.session_state.fake_call_active = False

    if st.session_state.fake_call_active:
        st.markdown(
            f"""
            <div class="fake-call">
                <p>{ringtone}</p>
                <h2>Incoming Call</h2>
                <h1>{st.session_state.fake_caller}</h1>
                <p>Emergency escape mode active</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_voice_support() -> None:
    """Render voice interaction controls."""
    st.subheader("Voice Support")
    st.write("Voice input requires a working microphone. Text-to-speech uses pyttsx3 locally.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Record Voice Question", use_container_width=True):
            text, error = speech_to_text()
            if error:
                st.error(error)
            else:
                st.session_state.voice_text = text
                st.success(f"Recognized: {text}")

    voice_text = st.text_area("Voice or typed message", value=st.session_state.voice_text, height=120)
    if st.button("Get Voice Chatbot Response", type="primary"):
        response, emergency_detected, danger_words = get_chatbot_response(voice_text)
        st.write(response)
        if emergency_detected:
            activate_emergency(f"Voice danger keyword detected: {', '.join(danger_words)}")
            st.warning(f"Danger keywords detected: {', '.join(danger_words)}")
        status = speak_text(response)
        st.info(status)


def render_self_defense() -> None:
    """Render self-defense guidance."""
    st.subheader("Self-Defense Guidance")
    st.markdown("#### Quick Actions")
    st.write(" | ".join(QUICK_ACTIONS))

    for category, steps in SELF_DEFENSE_GUIDE.items():
        with st.expander(category, expanded=True):
            for step in steps:
                st.write(f"- {step}")


def render_mental_support() -> None:
    """Render mental support chat shortcuts."""
    st.subheader("Mental Support Chat")
    prompts = [
        "I am feeling anxious and scared",
        "I am alone and worried",
        "Help me calm down",
        "I feel unsafe",
    ]
    for prompt in prompts:
        if st.button(prompt, use_container_width=True):
            response, emergency_detected, danger_words = get_chatbot_response(prompt)
            st.session_state.chat_history.append({"role": "user", "message": prompt, "time": datetime.now().strftime("%H:%M:%S")})
            st.session_state.chat_history.append({"role": "assistant", "message": response, "time": datetime.now().strftime("%H:%M:%S")})
            if emergency_detected:
                activate_emergency(f"Mental support danger keyword detected: {', '.join(danger_words)}")
            st.rerun()

    st.markdown("#### Recent Support Responses")
    for item in st.session_state.chat_history[-8:]:
        st.write(f"**{item['role'].title()}**: {item['message']}")


def render_location_sharing() -> None:
    """Render live location simulation and sharing."""
    st.subheader("Live Location Sharing")
    latitude, longitude = get_current_location()
    st.write(f"Simulated GPS location: {latitude:.5f}, {longitude:.5f}")
    st_folium(build_help_map(latitude, longitude), width=900, height=460)

    if st.button("Share My Location", type="primary"):
        st.session_state.last_location_message = get_location_message(latitude, longitude)
        st.success("Emergency location message generated.")

    if st.session_state.last_location_message:
        st.code(st.session_state.last_location_message)


def render_keyword_tester() -> None:
    """Render danger keyword detection demo."""
    st.subheader("Danger Keyword Detection")
    test_message = st.text_area("Type a message to scan", placeholder="Example: I feel unsafe and need help")
    if st.button("Scan Message"):
        found = detect_danger_keywords(test_message)
        if found:
            activate_emergency(f"Manual scan detected: {', '.join(found)}")
            st.error(f"Danger keywords found: {', '.join(found)}")
        else:
            st.success("No danger keywords detected.")


def main() -> None:
    """Run the app."""
    init_db()
    init_state()
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    render_hero()
    render_alert_banner()

    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Choose feature",
            [
                "Dashboard",
                "Emergency SOS",
                "Safety Chatbot",
                "Nearby Help Centers",
                "Emergency Contacts",
                "Fake Call",
                "Voice Support",
                "Self-Defense",
                "Mental Support",
                "Danger Detection",
                "Live Location",
            ],
        )
        st.divider()
        st.write("Emergency shortcuts")
        if st.button("Activate SOS Now", type="primary", use_container_width=True):
            latitude, longitude = get_current_location()
            st.session_state.last_location_message = get_location_message(latitude, longitude)
            activate_emergency("Sidebar SOS shortcut")
            time.sleep(0.2)
            st.rerun()

    pages = {
        "Dashboard": render_dashboard,
        "Emergency SOS": render_sos,
        "Safety Chatbot": render_chatbot,
        "Nearby Help Centers": render_help_centers,
        "Emergency Contacts": render_contacts,
        "Fake Call": render_fake_call,
        "Voice Support": render_voice_support,
        "Self-Defense": render_self_defense,
        "Mental Support": render_mental_support,
        "Danger Detection": render_keyword_tester,
        "Live Location": render_location_sharing,
    }
    pages[page]()


if __name__ == "__main__":
    main()
