# AI Request Intake & Remediation Prototype

This prototype provides a Streamlit-based UI for capturing incoming customer requests and routing them through a branch-specific remediation workflow.

## What it does
- Accepts customer details such as name, email, phone number, request topic, and request text.
- Classifies each request into one of four branches:
  - Complaint
  - Service Request
  - Escalation
  - General Enquiry
- Generates a branch-specific action plan, draft response, routing target, and follow-up instructions.
- Keeps a simple audit trail of processed requests in the session.

## How to run
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   streamlit run main.py
   ```

## Example workflow
- Complaint requests trigger empathy acknowledgement, escalation, priority logging, and a 2-hour follow-up.
- Service requests trigger detail extraction, department routing, confirmation drafting, and SLA tracking.
- Escalations trigger human review, urgent acknowledgement, supervisor notification, and pause of auto-resolution.
- General enquiries trigger knowledge-base style replies and a resolved status log.
