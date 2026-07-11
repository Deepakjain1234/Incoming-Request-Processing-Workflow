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


def connect_db():
    conn = pyodbc.connect(connection_string)
    conn.autocommit = True
    return conn


def recreate_request_tracker_table():
    conn = None

    try:
        conn = connect_db()
        cursor = conn.cursor()

        sql = """
        IF OBJECT_ID('dbo.request_tracker', 'U') IS NOT NULL
        BEGIN
            DROP TABLE dbo.request_tracker;
        END;

        CREATE TABLE dbo.request_tracker
        (
            id INT IDENTITY(1,1) NOT NULL,

            case_id AS (
                'CASE-' +
                RIGHT('000000' + CAST(id AS VARCHAR(6)),6)
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
        """

        cursor.execute(sql)
        cursor.close()

        print("✅ request_tracker table recreated successfully.")

    except Exception as e:
        print("❌ Error")
        print(e)

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    recreate_request_tracker_table()