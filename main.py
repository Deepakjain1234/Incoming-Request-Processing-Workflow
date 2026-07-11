import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from openai import AzureOpenAI

try:
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.tools import tool
    from langchain_openai import AzureChatOpenAI

    LANGCHAIN_READY = True

except Exception as e:
    LANGCHAIN_READY = False

    import traceback

    st.error("❌ LangChain Import Failed")
    st.code(traceback.format_exc())

    def tool(*args, **kwargs):
        def decorator(func):
            func.langchain_tool = True
            return func

        return decorator

    AgentExecutor = None
    create_tool_calling_agent = None
    ChatPromptTemplate = None
    AzureChatOpenAI = None

st.set_page_config(
    page_title="LangChain Request Orchestrator", page_icon="🤖", layout="wide"
)

if "requests" not in st.session_state:
    st.session_state.requests = []

st.sidebar.markdown("### Navigation")
st.sidebar.markdown(
    "- Use the Streamlit page selector to open **Support Dashboard** and view all stored database records."
)

st.info(
    "Navigate to the Support Dashboard page via Streamlit pages to review persisted records."
)


def get_config(key, default=""):
    """
    Priority:
    1. Streamlit Cloud Secrets
    2. Local .env
    3. Default value
    """
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass

    return os.getenv(key, default)


# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = get_config(
    "AZURE_OPENAI_ENDPOINT",
    "https://knowlageking-3505-resource.cognitiveservices.azure.com/",
)

AZURE_OPENAI_DEPLOYMENT = get_config(
    "AZURE_OPENAI_DEPLOYMENT",
    "gpt-5-mini",
)

AZURE_OPENAI_API_VERSION = get_config(
    "AZURE_OPENAI_API_VERSION",
    "2024-12-01-preview",
)

AZURE_OPENAI_API_KEY = get_config("AZURE_OPENAI_API_KEY")
# Timeout for Logic App HTTP requests (seconds). Default 1 hour.
LOGIC_APP_TIMEOUT = int(os.getenv("LOGIC_APP_TIMEOUT", str(60 * 60)))
COMPLAINT_LOGIC_APP_URL = os.getenv(
    "COMPLAINT_LOGIC_APP_URL",
    "https://prod-14.eastus2.logic.azure.com:443/workflows/3af39504f8f54f66a4c775ec7940e500/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=fiWhCeyMY2woFp97o6YXSMFDUBviTvc-9bcgKSsS3y0",
)
SERVICE_LOGIC_APP_URL = os.getenv(
    "SERVICE_LOGIC_APP_URL",
    "https://prod-21.eastus2.logic.azure.com:443/workflows/dac8ffcc2329470aaaa2a4f7670bc3f0/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=Xp6_tcWaGlwhH9dIzvYqxUB5EA6k8DS_88j3NW_54yc",
)

ESCALATION_LOGIC_APP_URL = os.getenv(
    "ESCALATION_LOGIC_APP_URL",
    "https://prod-10.eastus2.logic.azure.com:443/workflows/ff71f0b8b79e47ddba2451596c8d4b5f/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=yWK3IqdpugzOinzfdo0xxbTV0IlyJxswHxmzfsl0N_s",
)
GENERAL_ENQUIRY_LOGIC_APP_URL = os.getenv(
    "GENERAL_ENQUIRY_LOGIC_APP_URL",
    "https://prod-54.eastus2.logic.azure.com:443/workflows/4d747caabbc54b4e81de24eba183cac4/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=bKj1oEFpQpWz_iIpdnPtqd0fjBOYVlN25pQBls5i-TM",
)
RESOLUTION_LOGIC_APP_URL = os.getenv(
    "RESOLUTION_LOGIC_APP_URL",
    "https://prod-29.eastus2.logic.azure.com:443/workflows/c278c23391e644888ad80b7bb9fe488a/triggers/When_an_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun&sv=1.0&sig=qU07P0ol64ydL64rQu3JRDPeukHtWU9Tbkyu44xVqJI",
)

client = None

try:
    if AZURE_OPENAI_API_KEY:
        client = AzureOpenAI(
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
        )
except Exception as e:
    st.error(f"Failed to initialize Azure OpenAI: {e}")

missing_config = []

required = {
    "AZURE_OPENAI_ENDPOINT": AZURE_OPENAI_ENDPOINT,
    "AZURE_OPENAI_DEPLOYMENT": AZURE_OPENAI_DEPLOYMENT,
    "AZURE_OPENAI_API_VERSION": AZURE_OPENAI_API_VERSION,
    "AZURE_OPENAI_API_KEY": AZURE_OPENAI_API_KEY,
}

for key, value in required.items():
    if not value:
        missing_config.append(key)


def build_logic_app_payload(
    name: str,
    email: str,
    contact: str,
    query: str,
    support_agent_email: str = "",
    request_id: Optional[str] = None,
    case_id: Optional[str] = None,
    resolution: Optional[str] = None,
) -> Dict[str, Any]:
    now_utc = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "request_id": request_id or f"req-{now_utc.strftime('%Y%m%d%H%M%S')}",
        "timestamp": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "channel": "streamlit",
        "customer": {
            "name": name,
            "email": email,
            "contact": contact,
        },
        "query": query,
        "support_agent_email": support_agent_email or "deepak.passrid@gmail.com",
    }
    if case_id:
        payload["case_id"] = case_id
    if resolution:
        payload["resolution"] = resolution
    return payload


def invoke_logic_app(logic_app_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not logic_app_url or logic_app_url.startswith("https://example.logic"):
        return {
            "status": "skipped",
            "message": "No real Logic App endpoint configured.",
            "body": {},
        }
    request = Request(
        logic_app_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    try:
        # Use configured timeout to accommodate long-running Logic Apps
        with urlopen(request, timeout=LOGIC_APP_TIMEOUT) as response:
            raw_body = response.read().decode("utf-8", errors="ignore")
            body_is_json = False
            body_is_html = False
            parsed_body: Any = raw_body
            # capture response headers when available
            try:
                response_headers = dict(response.getheaders())
            except Exception:
                response_headers = {}
            if raw_body and raw_body.strip():
                s = raw_body.strip()
                if s.startswith("<"):
                    # Likely HTML/plain text response
                    body_is_html = True
                    parsed_body = raw_body
                else:
                    try:
                        parsed_body = json.loads(raw_body)
                        body_is_json = True
                    except Exception:
                        parsed_body = raw_body

            return {
                "status": "success",
                "http_status": response.status,
                "body": parsed_body,
                "body_is_json": body_is_json,
                "body_is_html": body_is_html,
                "headers": response_headers,
            }
    except HTTPError as exc:
        raw_body = exc.read().decode("utf-8", errors="ignore")
        body_is_json = False
        body_is_html = False
        try:
            parsed_body = json.loads(raw_body)
            body_is_json = True
        except Exception:
            parsed_body = raw_body or ""
            if isinstance(parsed_body, str) and parsed_body.strip().startswith("<"):
                body_is_html = True
        # try to capture headers from HTTPError if present
        try:
            err_headers = dict(exc.headers) if getattr(exc, "headers", None) else {}
        except Exception:
            err_headers = {}

        return {
            "status": "error http",
            "http_status": exc.code,
            "body": parsed_body,
            "body_is_json": body_is_json,
            "body_is_html": body_is_html,
            "headers": err_headers,
        }
    except URLError as exc:
        return {
            "status": "error",
            "http_status": None,
            "body": str(exc.reason),
        }
    except TimeoutError as exc:
        return {
            "status": "error",
            "http_status": None,
            "body": f"Request to Logic App timed out: {exc}",
        }
    except Exception as exc:  # pragma: no cover - defensive fallback
        return {
            "status": "error",
            "http_status": None,
            "body": f"Unexpected Logic App error: {exc}",
        }


@tool
def complaint_request_tool(
    query: str,
    name: str = "",
    email: str = "",
    contact: str = "",
    support_agent_email: str = "deepak.passrid@gmail.com",
) -> Dict[str, object]:
    """Use this tool for complaints, billing disputes, refund issues, or dissatisfied customer feedback. It sends the request to the Complaint Logic App workflow and assigns a high-priority response path."""
    payload = build_logic_app_payload(
        name=name,
        email=email,
        contact=contact,
        query=query,
        support_agent_email=support_agent_email,
    )
    logic_app_response = invoke_logic_app(COMPLAINT_LOGIC_APP_URL, payload)
    print(logic_app_response)
    return {
        "tool_name": "Complaint Handler",
        "critical_level": "High",
        "logic_app_url": COMPLAINT_LOGIC_APP_URL,
        "classification": "Complaint",
        "steps": [
            "Acknowledge receipt with empathy",
            "Escalate to a senior handler",
            "Log the complaint with a priority flag",
            "Set a 2-hour follow-up reminder",
        ],
        "draft_response": f"Hi {name}, we have received your complaint and escalated it for priority review. You will receive a confirmation email shortly.",
        "status": logic_app_response.get("status", "Received"),
        "routing": "Customer Care Escalations Team",
        "logic_app_payload": payload,
        "logic_app_response": logic_app_response,
    }


@tool
def service_request_tool(
    query: str,
    name: str = "",
    email: str = "",
    contact: str = "",
    support_agent_email: str = "deepak.passrid@gmail.com",
) -> Dict[str, object]:
    """Use this tool for service requests, change requests, orders, upgrades, or activation requests. It routes the request to the relevant department through the Service Request Logic App workflow."""
    payload = build_logic_app_payload(
        name=name,
        email=email,
        contact=contact,
        query=query,
        support_agent_email=support_agent_email,
    )
    logic_app_response = invoke_logic_app(SERVICE_LOGIC_APP_URL, payload)
    return {
        "tool_name": "Service Request Handler",
        "critical_level": "Medium",
        "logic_app_url": SERVICE_LOGIC_APP_URL,
        "classification": "Service Request",
        "steps": [
            "Capture request details",
            "Route to Customer Account Management",
            "Send acknowledgement email",
            "Track SLA and dashboard notification",
        ],
        "draft_response": f"Hi {name}, your service request has been received and routed to the Customer Account Management team. You will receive a confirmation email shortly.",
        "status": logic_app_response.get("status", "Received"),
        "routing": "Customer Account Management",
        "logic_app_payload": payload,
        "logic_app_response": logic_app_response,
    }


@tool
def escalation_request_tool(
    query: str,
    name: str = "",
    email: str = "",
    contact: str = "",
    support_agent_email: str = "deepak.passrid@gmail.com",
) -> Dict[str, object]:
    """Use this tool for urgent incidents, critical escalations, outages, or requests that need immediate human review. It routes the request to the urgent escalation workflow with a critical priority."""
    payload = build_logic_app_payload(
        name=name,
        email=email,
        contact=contact,
        query=query,
        support_agent_email=support_agent_email,
    )
    logic_app_response = invoke_logic_app(ESCALATION_LOGIC_APP_URL, payload)
    return {
        "tool_name": "Escalation Handler",
        "critical_level": "Critical",
        "logic_app_url": ESCALATION_LOGIC_APP_URL,
        "classification": "Escalation",
        "steps": [
            "Immediately flag for human review",
            "Draft an urgent acknowledgement",
            "Notify the supervisor team",
            "Pause automatic resolution",
        ],
        "draft_response": f"Hi {name}, your request has been flagged as urgent and escalated for immediate review.",
        "status": logic_app_response.get("status", "Needs human review"),
        "routing": "Supervisor Review Queue",
        "logic_app_payload": payload,
        "logic_app_response": logic_app_response,
    }


@tool
def general_enquiry_tool(
    query: str,
    name: str = "",
    email: str = "",
    contact: str = "",
    support_agent_email: str = "deepak.passrid@gmail.com",
) -> Dict[str, object]:
    """Use this tool for general questions, informational requests, or low-risk support enquiries. It routes the request to the General Enquiry Logic App workflow."""
    payload = build_logic_app_payload(
        name=name,
        email=email,
        contact=contact,
        query=query,
        support_agent_email=support_agent_email,
    )
    logic_app_response = invoke_logic_app(GENERAL_ENQUIRY_LOGIC_APP_URL, payload)
    return {
        "tool_name": "General Enquiry Handler",
        "critical_level": "Low",
        "logic_app_url": GENERAL_ENQUIRY_LOGIC_APP_URL,
        "classification": "General Enquiry",
        "steps": [
            "Classify the sub-topic",
            "Generate a response from the knowledge base",
            "Send the response to the requester",
            "Log the case as resolved",
        ],
        "draft_response": f"Hi {name}, thank you for your enquiry. We have prepared a helpful response for you.",
        "status": logic_app_response.get("status", "Resolved"),
        "routing": "Support Desk",
        "logic_app_payload": payload,
        "logic_app_response": logic_app_response,
    }


class RequestAgent:
    def __init__(self) -> None:
        self.tools = [
            complaint_request_tool,
            service_request_tool,
            escalation_request_tool,
            general_enquiry_tool,
        ]
        self.client = client
        self.deployment = AZURE_OPENAI_DEPLOYMENT
        self.executor = None
        self.tool_lookup = {
            "Complaint Handler": complaint_request_tool,
            "Service Request Handler": service_request_tool,
            "Escalation Handler": escalation_request_tool,
            "General Enquiry Handler": general_enquiry_tool,
        }
        st.write("## Azure / LangChain Debug")

        st.json(
    {
        "LANGCHAIN_READY": LANGCHAIN_READY,
        "AzureChatOpenAI": AzureChatOpenAI is not None,
        "AgentExecutor": AgentExecutor is not None,
        "create_tool_calling_agent": create_tool_calling_agent is not None,
        "ChatPromptTemplate": ChatPromptTemplate is not None,
        "Azure Client": self.client is not None,
        "Endpoint": AZURE_OPENAI_ENDPOINT,
        "Deployment": AZURE_OPENAI_DEPLOYMENT,
        "API Version": AZURE_OPENAI_API_VERSION,
        "API Key Present": bool(AZURE_OPENAI_API_KEY),
    }
)
        if (
    LANGCHAIN_READY
    and AzureChatOpenAI
    and AgentExecutor
    and create_tool_calling_agent
    and ChatPromptTemplate
    and self.client
):






    try:
        llm = AzureChatOpenAI(
            azure_deployment=AZURE_OPENAI_DEPLOYMENT,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            temperature=1,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful request-routing agent. Always use exactly one tool.",
                ),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        agent = create_tool_calling_agent(
            llm,
            self.tools,
            prompt,
        )

        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
        )

        st.success("✅ LangChain Agent Initialized Successfully")

    except Exception as e:
        import traceback

        st.error("❌ Failed to create LangChain Agent")
        st.code(traceback.format_exc())

        self.executor = None

else:
    st.error("❌ LangChain prerequisites not satisfied.")

    def process_request(
        self,
        query: str,
        name: str,
        email: str,
        contact: str,
        support_agent_email: str = "deepak.passrid@gmail.com",
    ) -> Dict[str, Any]:
        if self.executor is None:
            st.error("Executor is None")
            st.json(
                {
                    "LANGCHAIN_READY": LANGCHAIN_READY,
                    "AzureChatOpenAI": AzureChatOpenAI is not None,
                    "AgentExecutor": AgentExecutor is not None,
                    "create_tool_calling_agent": create_tool_calling_agent is not None,
                    "ChatPromptTemplate": ChatPromptTemplate is not None,
                    "Client": self.client is not None,
                    "Endpoint": bool(AZURE_OPENAI_ENDPOINT),
                    "Deployment": bool(AZURE_OPENAI_DEPLOYMENT),
                    "API Version": bool(AZURE_OPENAI_API_VERSION),
                    "API Key": bool(AZURE_OPENAI_API_KEY),
                }
            )
            raise RuntimeError("Agent initialization failed.")

        response = self.executor.invoke(
            {
                "input": f"Customer Name: {name}\nEmail: {email}\nContact: {contact}\nQuery: {query}",
            }
        )

        # --- Primary path: read the tool's real output straight from the agent's
        # intermediate steps. This is the actual dict the tool function returned
        # (including logic_app_response with the true Logic App body/headers),
        # not the LLM's re-typed summary of it, so nothing gets dropped or
        # truncated no matter how long the Logic App took to respond.
        intermediate_steps = response.get("intermediate_steps") or []
        if intermediate_steps:
            _, raw_tool_output = intermediate_steps[-1]
            tool_result: Any = raw_tool_output
            if isinstance(tool_result, str):
                try:
                    tool_result = json.loads(tool_result)
                except json.JSONDecodeError:
                    tool_result = None
            if isinstance(tool_result, dict):
                return {
                    "selected_tool": tool_result.get("tool_name", "unknown"),
                    **tool_result,
                }

        # --- Fallback path: older langchain versions, or an executor that didn't
        # return intermediate steps for some reason. Falls back to parsing the
        # LLM's final text output, same as before.
        tool_output = response.get("output")
        parsed_output: Any = None

        if isinstance(tool_output, dict):
            parsed_output = tool_output
        elif isinstance(tool_output, str):
            try:
                parsed_output = json.loads(tool_output)
            except json.JSONDecodeError:
                parsed_output = None

        if isinstance(parsed_output, dict):
            selected_tool = (
                parsed_output.get("tool_name")
                or parsed_output.get("selected_tool")
                or "unknown"
            )
            if selected_tool in self.tool_lookup:
                full_result = self.tool_lookup[selected_tool].invoke(
                    {
                        "query": query,
                        "name": name,
                        "email": email,
                        "contact": contact,
                        "support_agent_email": support_agent_email,
                    }
                )
            else:
                full_result = parsed_output

            if isinstance(full_result, dict):
                return {
                    "selected_tool": full_result.get("tool_name", selected_tool),
                    **full_result,
                }

        return {
            "selected_tool": "unknown",
            "tool_output": str(tool_output),
            "critical_level": "Medium",
        }


agent = RequestAgent()

st.title("LangChain AI Request Processing System")
st.caption(
    "One agent routes the request to the correct Logic App-backed workflow tool."
)

if missing_config:
    st.warning(
        "Azure OpenAI orchestration is disabled until the required settings are provided. "
        f"Missing: {', '.join(missing_config)}"
    )

with st.form("request_form"):
    st.markdown("### Request Details")
    name = st.text_input("Name")
    email = st.text_input("Email")
    contact = st.text_input("Contact")
    query = st.text_area(
        "Query", placeholder="Describe your request, complaint, or service need here..."
    )
    support_agent_email = st.text_input(
        "Customer Support Agent Email", value="deepak.passrid@gmail.com"
    )
    st.caption(
        "Please change the support email to test the complete flow; otherwise the default value will be used."
    )
    submitted = st.form_submit_button("Process request")

if submitted:
    if not name or not email or not query:
        st.error(
            "Please provide a name, email address, and request details before processing."
        )
        st.stop()

    case_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    st.info(
        "Please wait — processing your request. The Logic App can take a few minutes to respond."
    )
    with st.spinner(
        "Agent is choosing the workflow tool and invoking the Logic App — this may take a few minutes..."
    ):
        try:
            result = agent.process_request(
                query, name, email, contact, support_agent_email
            )
        except Exception as exc:
            st.error(str(exc))
            st.stop()

    # Normalize result keys so the UI can safely read them
    # Ensure tool_name exists (some agent outputs only `selected_tool`)
    if isinstance(result, dict):
        result.setdefault("tool_name", result.get("selected_tool", "unknown"))
        result.setdefault("critical_level", result.get("critical_level", "Medium"))
        result.setdefault("routing", result.get("routing", "Unknown"))
        result.setdefault(
            "classification", result.get("classification", "Unclassified")
        )
        result.setdefault("steps", result.get("steps", []))
        result.setdefault("logic_app_url", result.get("logic_app_url", ""))
        result.setdefault("status", result.get("status", "Pending"))

    result.update(
        {
            "case_id": case_id,
            "request_id": result.get("logic_app_payload", {}).get("request_id", ""),
            "customer_name": name,
            "email": email,
            "contact": contact,
            "request": query,
            "support_agent_email": support_agent_email or "deepak.passrid@gmail.com",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )

    st.session_state.requests.append(result)

    st.success(f"Request processed successfully. Case ID: {case_id}")

    st.markdown("### Agent outcome")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(
            "Selected tool",
            result.get("tool_name", result.get("selected_tool", "unknown")),
        )
    with col_b:
        st.metric("Critical level", result.get("critical_level", "Medium"))

    st.markdown("### Confirmation")
    st.info(
        "Your request has been submitted successfully. You will receive a confirmation email soon."
    )

    logic_app_response = result.get("logic_app_response", {})
    if isinstance(logic_app_response, dict) and logic_app_response:
        st.markdown("### Logic App response")
        payload_body = logic_app_response.get("body", {})
        body_is_json = logic_app_response.get("body_is_json", False)
        body_is_html = logic_app_response.get("body_is_html", False)
        response_headers = logic_app_response.get("headers", {})
        http_status = logic_app_response.get("http_status")

        # Always show status and headers for debugging
        st.write(f"HTTP status: {http_status}")
        if response_headers:
            st.markdown("**Response headers**")
            st.json(response_headers)
        if logic_app_response.get("status") == "success":
            if body_is_json and isinstance(payload_body, dict):
                # Special-case Logic App complaint response schema: { "response": "..." }
                if "response" in payload_body:
                    st.success(payload_body.get("response"))
                else:
                    st.json(payload_body)
            elif body_is_json and isinstance(payload_body, list):
                st.json(payload_body)
            elif isinstance(payload_body, str) and payload_body.strip():
                if body_is_html or payload_body.strip().startswith("<"):
                    st.text_area("Raw HTML/Text response", payload_body, height=220)
                else:
                    st.text_area("Returned response", payload_body, height=220)
            else:
                st.info(
                    "Logic App returned an empty body. The workflow may be processing asynchronously and will complete shortly."
                )
                # Offer a retry to fetch any eventual response
                if st.button("Retry fetching Logic App response"):
                    retry_url = result.get("logic_app_url") or ""
                    if retry_url:
                        with st.spinner("Re-invoking Logic App to fetch response..."):
                            retry_payload = build_logic_app_payload(
                                name, email, contact, query, support_agent_email
                            )
                            retry_resp = invoke_logic_app(retry_url, retry_payload)
                            st.write(
                                "Retry HTTP status:", retry_resp.get("http_status")
                            )
                            if (
                                retry_resp.get("body_is_json")
                                and isinstance(retry_resp.get("body"), dict)
                                and "response" in retry_resp.get("body")
                            ):
                                st.success(retry_resp.get("body").get("response"))
                            else:
                                st.write(retry_resp.get("body") or retry_resp)
        else:
            if logic_app_response.get("http_status") == 401:
                st.error(
                    "The Logic App endpoint rejected the request because the invoke URL or SAS signature is invalid. Please update the service Logic App URL and try again."
                )
            else:
                # Show the raw body if available
                if isinstance(payload_body, str):
                    if logic_app_response.get("body_is_html"):
                        st.text_area("Logic App error (raw)", payload_body, height=220)
                    else:
                        st.warning(payload_body)
                else:
                    st.warning(json.dumps(logic_app_response, indent=2))
    elif "logic_app_response" not in result:
        # This tool run had no Logic App call at all (e.g. General Enquiry), so
        # don't render a misleading empty "Logic App response" section for it.
        pass

    if isinstance(result.get("logic_app_payload"), dict):
        with st.expander("Logic App request payload"):
            st.json(result["logic_app_payload"])

    with st.expander("Execution details"):
        sanitized = {
            k: v
            for k, v in result.items()
            if k
            not in {"logic_app_url", "steps", "draft_response", "status", "routing"}
        }
        st.json(sanitized)

st.markdown("---")
st.subheader("Recent processed requests (session)")
st.info(
    "For full request tracking with filtering and resolution management, go to **Request History** page."
)

if st.session_state.requests:
    for item in reversed(st.session_state.requests):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**{item['case_id']}**")
        with col2:
            st.write(f"Customer: {item['customer_name']}")
        with col3:
            st.write(f"{item['tool_name']} ({item['critical_level']})")
else:
    st.info("No requests have been processed in this session yet.")
