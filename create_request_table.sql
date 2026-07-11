CREATE TABLE request_tracker
(
    id INT IDENTITY(1,1) NOT NULL,

    case_id AS (
        'CASE-' +
        RIGHT('000000' + CAST(id AS VARCHAR(6)), 6)
    ) PERSISTED,

    request_id NVARCHAR(100) NULL,

    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    customer_name NVARCHAR(200) NULL,

    email NVARCHAR(200) NULL,

    contact NVARCHAR(100) NULL,

    support_agent_email NVARCHAR(200) NULL,

    query_text NVARCHAR(MAX) NULL,

    tool_name NVARCHAR(200) NULL,

    classification NVARCHAR(100) NULL,

    critical_level NVARCHAR(50) NULL,

    routing NVARCHAR(200) NULL,

    status NVARCHAR(100) NULL,

    draft_response NVARCHAR(MAX) NULL,

    resolution NVARCHAR(MAX) NULL,

    tracking_notes NVARCHAR(MAX) NULL,

    CONSTRAINT PK_request_tracker PRIMARY KEY (id)
);