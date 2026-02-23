"""Script to fetch QUP-637 epic and child stories from Jira."""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from atlassian_mcp_server.clients import JiraClient, AtlassianConfig

config_path = Path(__file__).parent / "config.json"
with open(config_path) as f:
    config_data = json.load(f)

config = AtlassianConfig(
    site_url=config_data["ATLASSIAN_SITE_URL"],
    client_id=config_data["ATLASSIAN_CLIENT_ID"],
    client_secret=config_data["ATLASSIAN_CLIENT_SECRET"],
)

creds_file = Path.home() / ".atlassian_mcp_credentials.json"
if creds_file.exists():
    with open(creds_file) as f:
        creds = json.load(f)
        config.access_token = creds.get("access_token")
        config.refresh_token = creds.get("refresh_token")

client = JiraClient(config)


async def fetch_epic_and_children():
    """Fetch QUP-637 epic and all child stories."""
    result = {}
    try:
        # Fetch epic
        epic = await client.jira_get_issue("QUP-637")
        result["epic"] = epic
        print("=== EPIC QUP-637 ===")
        print(json.dumps(epic, indent=2, default=str))

        # Search for child stories
        children = await client.jira_search("parent = QUP-637", max_results=50)
        result["children"] = children
        print("\n=== CHILD STORIES (parent=QUP-637) ===")
        print(json.dumps(children, indent=2, default=str))

        # Also try Epic Link in case structure differs
        epic_link = await client.jira_search('"Epic Link" = QUP-637', max_results=50)
        if epic_link and epic_link != children:
            result["epic_link_children"] = epic_link
            print("\n=== EPIC LINK CHILDREN ===")
            print(json.dumps(epic_link, indent=2, default=str))

        # Fetch full details for each child
        all_children = children or epic_link or []
        child_details = []
        for c in all_children:
            key = c.get("key") or (c.get("id") and f"QUP-{c['id']}")
            if key:
                try:
                    detail = await client.jira_get_issue(key)
                    child_details.append(detail)
                    print(f"\n=== CHILD {key} (full details) ===")
                    print(json.dumps(detail, indent=2, default=str))
                except Exception as e:
                    print(f"Could not fetch {key}: {e}", file=sys.stderr)
        result["child_details"] = child_details

        return result
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if hasattr(e, "__dict__"):
            print(json.dumps(e.__dict__, indent=2, default=str), file=sys.stderr)
        raise


if __name__ == "__main__":
    asyncio.run(fetch_epic_and_children())
