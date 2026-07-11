import json
import pyodbc

SERVER = "request-track.database.windows.net"
DATABASE = "db-request"
USERNAME = "deepak"
PASSWORD = "Deep@132"
PORT = 1433

connection_string = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={SERVER},{PORT};"
    f"DATABASE={DATABASE};"
    f"UID={USERNAME};"
    f"PWD={PASSWORD};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

TABLE_NAME = "request_tracker"

conn = None


def connect_db():
    """Create a fresh database connection."""
    try:
        conn = pyodbc.connect(connection_string)
        conn.autocommit = True
        return conn
    except Exception as e:
        print("❌ Database Connection Failed")
        print(e)
        raise


def ensure_request_table_exists():
    conn = None
    try:
        conn = connect_db()

        create_table_sql = f"""
        SET NOCOUNT ON;

        IF NOT EXISTS (
            SELECT 1
            FROM sys.tables
            WHERE name = '{TABLE_NAME}'
        )
        BEGIN
            CREATE TABLE {TABLE_NAME} (
                case_id NVARCHAR(50) PRIMARY KEY,
                request_id NVARCHAR(100),
                created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
                updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
                customer_name NVARCHAR(200),
                email NVARCHAR(200),
                contact NVARCHAR(100),
                support_agent_email NVARCHAR(200),
                query_text NVARCHAR(MAX),
                tool_name NVARCHAR(200),
                classification NVARCHAR(100),
                critical_level NVARCHAR(50),
                routing NVARCHAR(200),
                status NVARCHAR(100),
                draft_response NVARCHAR(MAX),
                resolution NVARCHAR(MAX),
                tracking_notes NVARCHAR(MAX)
            );
        END
        """

        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        cursor.close()

        print("✅ Table verified")
    finally:
        if conn:
            conn.close()


def insert_request_record(record):
    conn = None
    try:
        conn = connect_db()

        insert_sql = f"""
        INSERT INTO {TABLE_NAME} (
            case_id,
            request_id,
            created_at,
            updated_at,
            customer_name,
            email,
            contact,
            support_agent_email,
            query_text,
            tool_name,
            classification,
            critical_level,
            routing,
            status,
            draft_response,
            tracking_notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        values = [
            record.get("case_id"),
            record.get("request_id"),
            record.get("created_at"),
            record.get("updated_at", record.get("created_at")),
            record.get("customer_name"),
            record.get("email"),
            record.get("contact"),
            record.get("support_agent_email"),
            record.get("query"),
            record.get("tool_name"),
            record.get("classification"),
            record.get("critical_level"),
            record.get("routing"),
            record.get("status"),
            record.get("draft_response"),
            record.get("tracking_notes"),
        ]

        cursor = conn.cursor()
        cursor.execute(insert_sql, values)
        cursor.close()

        print("✅ Record inserted")
    finally:
        if conn:
            conn.close()


def get_all_requests():
    conn = None
    try:
        conn = connect_db()

        query = f"""
        SELECT *
        FROM {TABLE_NAME}
        ORDER BY created_at DESC;
        """

        cursor = conn.cursor()
        cursor.execute(query)

        columns = [column[0] for column in cursor.description]

        records = []
        for row in cursor.fetchall():
            records.append(dict(zip(columns, row)))

        cursor.close()
        return records
    finally:
        if conn:
            conn.close()


def get_requests_by_support_email(support_email: str):
    conn = None
    try:
        conn = connect_db()

        query = f"""
        SELECT *
        FROM {TABLE_NAME}
        WHERE support_agent_email = ?
        ORDER BY created_at DESC;
        """

        cursor = conn.cursor()
        cursor.execute(query, (support_email,))

        columns = [column[0] for column in cursor.description]

        records = []
        for row in cursor.fetchall():
            records.append(dict(zip(columns, row)))

        cursor.close()
        return records
    finally:
        if conn:
            conn.close()


def get_requests_by_email_and_criticality(support_email: str, criticality: str):
    conn = None
    try:
        conn = connect_db()

        query = f"""
        SELECT *
        FROM {TABLE_NAME}
        WHERE support_agent_email = ? AND critical_level = ?
        ORDER BY created_at DESC;
        """

        cursor = conn.cursor()
        cursor.execute(query, (support_email, criticality))

        columns = [column[0] for column in cursor.description]

        records = []
        for row in cursor.fetchall():
            records.append(dict(zip(columns, row)))

        cursor.close()
        return records
    finally:
        if conn:
            conn.close()


def update_resolution_for_case(case_id: str, resolution: str, status: str = "Resolved"):
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            f"""
            UPDATE {TABLE_NAME}
            SET resolution = ?, status = ?, updated_at = SYSUTCDATETIME()
            WHERE case_id = ?
            """,
            (resolution, status, case_id),
        )
        cursor.close()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":

    print(get_all_requests())

    