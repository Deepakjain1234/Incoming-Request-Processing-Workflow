# 🚀 Incoming Request Processing Workflow

> **AI-Powered Multi-Step Customer Request Processing System**
>
> Built using **Azure OpenAI GPT-5.3-mini, LangChain, Azure Logic Apps, Azure SQL Database, Azure AI Search, Azure Blob Storage, Microsoft Outlook, and Streamlit**.

---

# 📖 Project Overview

Incoming Request Processing Workflow is an AI-powered customer support automation platform that intelligently classifies incoming customer requests and executes branch-specific remediation workflows.

The solution leverages **Azure OpenAI**, **LangChain Agents**, **Azure Logic Apps**, **Azure SQL Database**, **Azure AI Search (RAG)**, and **Microsoft Outlook** to automate customer communication while maintaining **Human-in-the-Loop (HITL)** support for critical scenarios.

---

# ✨ Features

- 🤖 AI-powered Request Classification
- 📨 Automatic Customer Acknowledgement Emails
- 🏢 Intelligent Department Routing
- 📋 Request Tracking in Azure SQL Database
- 🚨 Critical Escalation Workflow
- 📚 Retrieval-Augmented Generation (RAG)
- 👨‍💼 Human-in-the-Loop Resolution Dashboard
- 📧 Outlook Email Automation
- 📊 Streamlit Dashboard
- ☁ Azure Cloud Native Architecture

---

# 🏗 Solution Architecture

The application consists of four major layers.

## 1. User Interface

- Streamlit Web Application
- Customer Request Form

---

## 2. AI Orchestration Layer

- LangChain Agent
- Azure OpenAI GPT-5.3-mini
- Intent Classification
- Tool Selection

---

## 3. Workflow Execution Layer

Azure Logic Apps execute branch-specific workflows.

- Complaint Workflow
- Service Request Workflow
- Escalation Workflow
- General Enquiry (RAG)
- Resolution Workflow

---

## 4. Shared Azure Services

- Azure SQL Database
- Azure AI Search
- Azure Blob Storage
- Azure OpenAI
- Microsoft Outlook

---

# 🔄 Supported Request Types

## 🔴 Complaint (High Priority)

Workflow

- AI Classification
- Generate Customer Acknowledgement
- Notify Department
- Store Request
- Return Response

---

## 🔵 Service Request (Medium Priority)

Workflow

- Extract Customer Details
- Route to Department
- Generate Confirmation
- Set SLA
- Store Request

---

## 🟢 General Enquiry (Low Priority)

Workflow

- Azure AI Search
- Retrieve Knowledge
- Generate AI Resolution
- Send Customer Response
- Log Request

---

## 🟣 Escalation / Urgent (Critical)

Workflow

- Immediate Human Review
- Notify Supervisor
- Assign Senior Support Agent
- Pause Auto Resolution
- Human Resolution
- Notify Customer

---

# 🛠 Technologies Used

## Frontend

- Streamlit

## Programming Language

- Python

## AI

- Azure OpenAI GPT-5.3-mini
- LangChain
- LangGraph

## Azure Services

- Azure Logic Apps
- Azure AI Search
- Azure SQL Database
- Azure Blob Storage
- Azure OpenAI Service

## Database

- Azure SQL Database

## Email

- Microsoft Outlook Connector

## Vector Search

- Azure AI Search
- Azure OpenAI Embeddings

---

# 📁 Project Structure

```text
Incoming-Request-Processing-Workflow/

│
├── main.py
├── requirements.txt
├── README.md
├── .env.example
│
├── knowledge_base/
│   ├── FAQ.pdf
│   ├── BillingPolicy.pdf
│   ├── RefundPolicy.pdf
│   ├── CancellationPolicy.pdf
│   ├── SubscriptionGuide.pdf
│   └── TechnicalSupport.pdf
│
├── screenshots/
│
├── assets/
│
└── logicapps/
```

---

# ⚙ Installation Guide

## Clone Repository

```bash
git clone https://github.com/Deepakjain1234/Incoming-Request-Processing-Workflow.git

cd Incoming-Request-Processing-Workflow
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file.

```env
AZURE_OPENAI_ENDPOINT=

AZURE_OPENAI_API_KEY=

AZURE_OPENAI_DEPLOYMENT=

AZURE_OPENAI_API_VERSION=

COMPLAINT_LOGIC_APP_URL=

SERVICE_LOGIC_APP_URL=

ESCALATION_LOGIC_APP_URL=

GENERAL_ENQUIRY_LOGIC_APP_URL=

RESOLUTION_LOGIC_APP_URL=
```

---

# ▶ Run the Application

```bash
streamlit run main.py
```

---

# ☁ Streamlit Cloud Deployment

Store the following values securely in **Streamlit Secrets**.

```toml
AZURE_OPENAI_ENDPOINT=""
AZURE_OPENAI_API_KEY=""
AZURE_OPENAI_DEPLOYMENT=""
AZURE_OPENAI_API_VERSION=""

COMPLAINT_LOGIC_APP_URL=""
SERVICE_LOGIC_APP_URL=""
ESCALATION_LOGIC_APP_URL=""
GENERAL_ENQUIRY_LOGIC_APP_URL=""
RESOLUTION_LOGIC_APP_URL=""
```

---

# 🔗 Azure Logic Apps

The application uses multiple Azure Logic Apps to orchestrate different workflows.

| Logic App | Purpose |
|------------|----------|
| Complaint Workflow | Generates acknowledgement email, routes complaint, and logs request. |
| Service Request Workflow | Extracts request details, routes to department, generates confirmation, and tracks SLA. |
| Escalation Workflow | Assigns senior support, enables Human-in-the-Loop review, and pauses auto-resolution. |
| General Enquiry Workflow | Uses Azure AI Search (RAG) to retrieve knowledge and generate contextual responses. |
| Resolution Workflow | Sends the final resolution email after the support agent completes the request. |

> **Note:** Logic App endpoint URLs are stored securely using environment variables and are intentionally excluded from this repository.

---

# 📚 Knowledge Base

The RAG pipeline uses the following documents stored in Azure Blob Storage and indexed in Azure AI Search.

- FAQ.pdf
- BillingPolicy.pdf
- RefundPolicy.pdf
- CancellationPolicy.pdf
- SubscriptionGuide.pdf
- TechnicalSupport.pdf

---

# 📊 Azure Services Used

| Azure Service | Purpose |
|----------------|---------|
| Azure OpenAI | Request classification, email generation, AI responses |
| Azure Logic Apps | Workflow orchestration |
| Azure SQL Database | Request tracking & audit logs |
| Azure AI Search | Hybrid Search & RAG |
| Azure Blob Storage | Knowledge Base |
| Microsoft Outlook | Email delivery |

---

# 🌐 Live Demo

https://incoming-request-processing-workflow-cn8caajnd8madhdxfpraf7.streamlit.app/

---

# 💻 GitHub Repository

https://github.com/Deepakjain1234/Incoming-Request-Processing-Workflow

---

# 📷 Screenshots

You can add screenshots of:

- Streamlit Dashboard
- AI Classification
- Logic Apps
- Azure AI Search
- Azure SQL Database
- Human-in-the-Loop Dashboard

---

# 🚀 Future Enhancements

- 🌍 Multi-language request support
- 😊 Sentiment Analysis
- 📈 Confidence Score for AI classification
- 🤖 Automatic Resolution for repetitive issues
- 📊 Power BI Dashboard
- 💬 Microsoft Teams Integration
- 📨 Azure Communication Services Email
- 📂 File Attachment Processing
- 🖼 OCR & Document Intelligence
- 🎤 Voice-based Request Processing
- 🔔 SLA Breach Notifications
- 🔐 Microsoft Entra ID Authentication
- 👥 Role-Based Access Control (RBAC)
- 📱 Mobile-friendly Dashboard
- ⚡ Azure Service Bus for asynchronous workflows
- 📉 Cost optimization through model selection and caching

---

# 📈 Key Highlights

- AI-powered request classification
- Multi-step Azure Logic App orchestration
- Retrieval-Augmented Generation (RAG)
- Human-in-the-Loop support workflow
- Azure SQL request tracking
- Automated Outlook email notifications
- Cloud-native Azure architecture
- Modular and extensible workflow design

---

# 👨‍💻 Author

**Deepak Jain**

GitHub

https://github.com/Deepakjain1234

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.

Feedback, suggestions, and contributions are always welcome!
