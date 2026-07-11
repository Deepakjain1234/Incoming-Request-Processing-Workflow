import json
import os
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st

from db import (
    get_requests_by_email_and_criticality,
    get_requests_by_support_email,
    update_resolution_for_case,
)

RESOLUTION_LOGIC_APP_URL = os.getenv(
    "RESOLUTION_LOGIC_APP_URL",
    "https://prod-29.eastus2.logic.azure.com:443/workflows/c278c23391e644888ad80b7bb9fe488a/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=qU07P0ol64ydL64rQu3JRDPeukHtWU9Tbkyu44xVqJI",
)

st.set_page_config(page_title="Support Dashboard", page_icon="🛠️", layout="wide")

st.title("Support Dashboard")
st.markdown("View and manage requests assigned to your support team.")

# Initialize session state for selected case
if "selected_case_id" not in st.session_state:
    st.session_state.selected_case_id = None

# Filter section
st.markdown("### Filter Requests")
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    support_email = st.text_input("Support Team Email", value="deepak.passrid@gmail.com")

with col2:
    criticality_filter = st.selectbox(
        "Filter by Criticality",
        ["All", "Low", "Medium", "High", "Critical"],
    )

with col3:
    fetch_clicked = st.button("Fetch Requests", use_container_width=True)

# Fetch requests based on filters
records = []
if fetch_clicked or support_email:
    try:
        if criticality_filter == "All":
            records = get_requests_by_support_email(support_email)
        else:
            records = get_requests_by_email_and_criticality(support_email, criticality_filter)

        if not records:
            st.info(f"No requests found for {support_email}" + (f" with criticality {criticality_filter}" if criticality_filter != "All" else ""))
        else:
            st.success(f"Found {len(records)} request(s)")
    except Exception as exc:
        st.error(f"Error fetching requests: {exc}")


# Color coding for criticality/status
def get_criticality_color(criticality):
    """Return a color badge for criticality level."""
    colors = {
        "Low": "🟢 Low",
        "Medium": "🟡 Medium",
        "High": "🟠 High",
        "Critical": "🔴 Critical",
    }
    return colors.get(criticality, f"⚪ {criticality}")


def normalize_case_id(case_id_value) -> str:
    if case_id_value is None:
        return ""

    text = str(case_id_value).strip()
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return ""

    return digits.zfill(6)


def build_resolution_submission_payload(selected_record, resolution_text: str) -> dict:
    now_utc = datetime.now(timezone.utc)
    request_id = selected_record.get("request_id") or f"req-{now_utc.strftime('%Y%m%d%H%M%S')}"
    case_reference = selected_record.get("id") or selected_record.get("case_id")
    return {
        "request_id": request_id,
        "timestamp": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "channel": "streamlit",
        "customer": {
            "name": selected_record.get("customer_name", ""),
            "email": selected_record.get("email", ""),
            "contact": selected_record.get("contact", ""),
        },
        "query": selected_record.get("query_text", selected_record.get("query", "")),
        "resolution": resolution_text,
        "case_id": normalize_case_id(case_reference),
        "support_agent_email": selected_record.get("support_agent_email", "deepak.passrid@gmail.com"),
    }


def submit_resolution_to_logic_app(payload: dict) -> dict:
    if not RESOLUTION_LOGIC_APP_URL or RESOLUTION_LOGIC_APP_URL.startswith("https://example.logic"):
        return {
            "status": "skipped",
            "message": "No real resolution Logic App endpoint configured.",
            "body": {},
        }

    request = Request(
        RESOLUTION_LOGIC_APP_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            raw_body = response.read().decode("utf-8", errors="ignore")
            try:
                parsed_body = json.loads(raw_body) if raw_body.strip() else {}
            except Exception:
                parsed_body = raw_body
            return {
                "status": "success",
                "http_status": response.status,
                "body": parsed_body,
            }
    except HTTPError as exc:
        raw_body = exc.read().decode("utf-8", errors="ignore")
        try:
            parsed_body = json.loads(raw_body) if raw_body.strip() else {}
        except Exception:
            parsed_body = raw_body
        return {
            "status": "error",
            "http_status": exc.code,
            "body": parsed_body,
        }
    except URLError as exc:
        return {
            "status": "error",
            "http_status": None,
            "body": str(exc.reason),
        }
    except Exception as exc:
        return {
            "status": "error",
            "http_status": None,
            "body": f"Unexpected resolution submission error: {exc}",
        }


if records:
    st.markdown("### Requests Summary")

    # Render each row with a Dialog button on the right
    for idx, record in enumerate(records):
        cols = st.columns([1, 3, 3, 2, 2, 1, 1, 1])
        with cols[0]:
            st.write(f"**#{idx+1}**")
        with cols[1]:
            st.write(record.get("case_id", "N/A"))
            st.write(record.get("customer_name", "N/A"))
        with cols[2]:
            st.write(record.get("email", "N/A"))
            st.write(record.get("contact", "N/A"))
        with cols[3]:
            st.write(record.get("classification", "N/A"))
        with cols[4]:
            st.write(get_criticality_color(record.get("critical_level", "N/A")))
        with cols[5]:
            st.write(record.get("status", "N/A"))
        with cols[6]:
            st.write(str(record.get("created_at", "N/A"))[:19])
        with cols[7]:
            if st.button("Dialog", key=f"dialog_{idx}"):
                st.session_state.selected_case_id = record.get("case_id")
                st.rerun()

    st.markdown("---")

    if st.session_state.selected_case_id:
        selected_record = next((r for r in records if r["case_id"] == st.session_state.selected_case_id), None)
        if selected_record:
            st.markdown("### 📋 Request Details Dialog")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Case ID", selected_record.get("case_id", "N/A"))
            with col2:
                criticality = selected_record.get("critical_level", "N/A")
                st.metric("Criticality", get_criticality_color(criticality))
            with col3:
                st.metric("Status", selected_record.get("status", "N/A"))
            with col4:
                st.metric("Tool", selected_record.get("tool_name", "N/A"))

            st.markdown("**Customer Information**")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"**Name**: {selected_record.get('customer_name', 'N/A')}")
            with c2:
                st.write(f"**Email**: {selected_record.get('email', 'N/A')}")
            with c3:
                st.write(f"**Contact**: {selected_record.get('contact', 'N/A')}")

            st.markdown("**Request Details**")
            st.write(f"**Query**: {selected_record.get('query_text', 'N/A')}")
            r1, r2, r3 = st.columns(3)
            with r1:
                st.write(f"**Classification**: {selected_record.get('classification', 'N/A')}")
            with r2:
                st.write(f"**Routing**: {selected_record.get('routing', 'N/A')}")
            with r3:
                st.write(f"**Support Agent**: {selected_record.get('support_agent_email', 'N/A')}")

            st.markdown("---")
            status_value = str(selected_record.get("status", "")).strip().lower()
            if status_value in {"closed", "close", "resolved", "resolve", "completed", "complete"}:
                resolution_text = selected_record.get("resolution")
                if resolution_text and str(resolution_text).strip():
                    st.markdown("### 📝 Resolution")
                    st.text_area("Resolution", value=str(resolution_text), height=150, disabled=True)
                else:
                    st.info("This ticket is already closed. No resolution details are available.")
            else:
                st.markdown("### ✅ Submit Resolution")
                resolution_text = st.text_area("Resolution Notes", height=150)
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    if st.button("Submit Resolution", key="submit_resolution"):
                        if not resolution_text.strip():
                            st.error("Please enter resolution details before submitting.")
                        else:
                            with st.status("Your request is submitted. Waiting for the endpoint response...", expanded=True):
                                st.write("Submitting the resolution payload to the configured Logic App endpoint...")
                                payload = build_resolution_submission_payload(selected_record, resolution_text)
                                submit_result = submit_resolution_to_logic_app(payload)

                                if submit_result.get("status") == "success":
                                    try:
                                        update_resolution_for_case(
                                            case_id=selected_record.get("case_id"),
                                            resolution=resolution_text,
                                            status="Resolved",
                                            record_id=selected_record.get("id"),
                                        )
                                    except Exception as db_exc:
                                        st.warning(f"Resolution endpoint accepted the payload, but database update failed: {db_exc}")

                                    st.success("✅ Resolution submitted successfully. Refreshing the dialog with the latest response.")
                                    st.rerun()
                                else:
                                    st.error("Resolution submission failed. Please verify the endpoint configuration and try again.")
                                    st.json(submit_result)
                with col_b:
                    if st.button("Close Dialog", key="close_dialog"):
                        st.session_state.selected_case_id = None
                        st.rerun()

            if st.button("Close Dialog", key="close_dialog_footer"):
                st.session_state.selected_case_id = None
                st.rerun()

else:
    st.info("No requests found. Use the filters above to fetch requests for your support team.")
