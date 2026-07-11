#!/usr/bin/env python
"""
Temporary script to fetch and display all request records from the database.
"""

import json
from db import get_all_requests

if __name__ == "__main__":
    try:
        print("Fetching all requests from the database...\n")
        records = get_all_requests()

        if records:
            print(f"Total records found: {len(records)}\n")
            print("=" * 100)

            for idx, record in enumerate(records, 1):
                print(f"\n[Record {idx}]")
                print(f"Case ID: {record.get('case_id', 'N/A')}")
                print(f"Request ID: {record.get('request_id', 'N/A')}")
                print(f"Customer: {record.get('customer_name', 'N/A')} ({record.get('email', 'N/A')})")
                print(f"Contact: {record.get('contact', 'N/A')}")
                print(f"Query: {record.get('query_text', 'N/A')}")
                print(f"Tool: {record.get('tool_name', 'N/A')}")
                print(f"Classification: {record.get('classification', 'N/A')}")
                print(f"Criticality: {record.get('critical_level', 'N/A')}")
                print(f"Status: {record.get('status', 'N/A')}")
                print(f"Routing: {record.get('routing', 'N/A')}")
                print(f"Support Agent Email: {record.get('support_agent_email', 'N/A')}")
                print(f"Created At: {record.get('created_at', 'N/A')}")
                print(f"Updated At: {record.get('updated_at', 'N/A')}")
                print("-" * 100)

            print("\n" + "=" * 100)
            print("Full JSON output:")
            print(json.dumps(records, indent=2, default=str))
        else:
            print("No records found in the database.")

    except Exception as exc:
        print(f"Error fetching records: {exc}")
        import traceback
        traceback.print_exc()
