"""Update QUP-671 with revised scope: link-based invoice notification instead of PDF attachment."""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from atlassian_mcp_server.clients import JiraClient, AtlassianConfig

# Load config from config.json
config_path = Path(__file__).parent / "config.json"
with open(config_path) as f:
    config_data = json.load(f)

config = AtlassianConfig(
    site_url=config_data["ATLASSIAN_SITE_URL"],
    client_id=config_data["ATLASSIAN_CLIENT_ID"],
    client_secret=config_data["ATLASSIAN_CLIENT_SECRET"],
)

# Try to load saved credentials
creds_file = Path.home() / ".atlassian_mcp_credentials.json"
if creds_file.exists():
    with open(creds_file) as f:
        creds = json.load(f)
        config.access_token = creds.get("access_token")
        config.refresh_token = creds.get("refresh_token")

client = JiraClient(config)

NEW_SUMMARY = "E7.5: Invoice notification email (link to billing page, no PDF attachment)"

NEW_DESCRIPTION = """**As a** system
**I want to** notify the account holder when an invoice is created by sending an email with a link to view it
**So that** they can access their invoice promptly without storing or attaching PDFs

**Scope (revised):**
- Do NOT generate or store PDF invoices
- Do NOT attach PDFs to emails
- On creation of an invoice record, send an email to the account holder with a link to the billing invoice page
- The link opens the billing invoice page; if the user has an active session, the invoice modal opens on load (or is triggered to open after load)
- If the user has no active session, show the login page; after successful login, redirect to the billing invoice page with the same behavior (invoice modal opens)
- Email template: professional wording, table showing invoice contents (line items, amounts, total), and a clear link where they can view and download the PDF version

**Acceptance Criteria:**
1. Given an invoice record is created, When creation completes, Then the system sends an email to the account holder with a link to the billing invoice page (no PDF attachment)
2. Given the account holder opens the link with an active session, When the page loads, Then the billing invoice page is shown with the invoice modal open (or triggered to open after load)
3. Given the account holder opens the link without an active session, When they do, Then they see the login page; after successful login they are redirected to the billing invoice page with the invoice modal open
4. Given the invoice notification email is sent, When delivered, Then it uses a professional template with company branding, a table showing invoice contents (description, quantity, amount, total), and a prominent link to view and download the PDF
5. Given invoice notification emails fail to send, When errors occur, Then the system logs the error and can retry sending

**Effort:** 2 hours (qobi-backend, qobi-portal)"""


async def update_qup671():
    """Update QUP-671 with new summary and description."""
    try:
        result = await client.jira_update_issue(
            "QUP-671",
            summary=NEW_SUMMARY,
            description=NEW_DESCRIPTION,
        )
        print(json.dumps(result, indent=2))
        print("\nQUP-671 updated successfully.")
        return result
    except Exception as e:
        print(f"Error updating QUP-671: {e}", file=sys.stderr)
        if hasattr(e, "__dict__"):
            print(
                f"Error details: {json.dumps(e.__dict__, indent=2, default=str)}",
                file=sys.stderr,
            )
        raise


if __name__ == "__main__":
    asyncio.run(update_qup671())
