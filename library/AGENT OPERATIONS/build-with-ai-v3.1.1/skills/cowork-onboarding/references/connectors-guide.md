# Connectors Guide

Available connectors, setup patterns, and test prompts. Read this before running the Connect Your Tools capability.

---

## What Connectors Do

Connectors link Claude to external platforms via the Model Context Protocol (MCP). Once connected, Claude can read and search data from those platforms directly — no copy-pasting, no screenshots, no file uploads needed.

Connectors are set up in Settings → Connectors in the Claude desktop app. Users authenticate once and the connection persists across sessions.

In the onboarding workflow, use `search_mcp_registry` to find available connectors and `suggest_connectors` to present them to the user with a connect button.

## Common Tools → Connector Search Keywords

When the user mentions a tool, use these keywords with `search_mcp_registry`:

| Tool the User Mentions | Search Keywords |
|------------------------|----------------|
| Google Drive | `["google", "drive", "docs"]` |
| Gmail | `["google", "gmail", "email"]` |
| Google Calendar | `["google", "calendar", "schedule"]` |
| Slack | `["slack", "messaging", "chat"]` |
| Notion | `["notion", "wiki", "docs"]` |
| Asana | `["asana", "tasks", "project"]` |
| Linear | `["linear", "issues", "project"]` |
| Jira | `["jira", "issues", "project"]` |
| Monday.com | `["monday", "project", "tasks"]` |
| Figma | `["figma", "design"]` |
| GitHub | `["github", "code", "repository"]` |
| Salesforce | `["salesforce", "crm", "sales"]` |
| HubSpot | `["hubspot", "crm", "marketing"]` |
| Dropbox | `["dropbox", "files", "storage"]` |
| Box | `["box", "files", "storage"]` |
| Confluence | `["confluence", "wiki", "docs"]` |
| SharePoint | `["sharepoint", "docs", "microsoft"]` |
| Microsoft Teams | `["teams", "microsoft", "chat"]` |
| Trello | `["trello", "boards", "tasks"]` |
| Airtable | `["airtable", "database", "tables"]` |
| Zapier | `["zapier", "automation"]` |
| Make (Integromat) | `["make", "automation", "integromat"]` |
| Discord | `["discord", "chat", "community"]` |
| WordPress | `["wordpress", "website", "blog"]` |
| Shopify | `["shopify", "ecommerce", "store"]` |
| Stripe | `["stripe", "payments", "billing"]` |
| QuickBooks | `["quickbooks", "accounting", "finance"]` |
| Calendly | `["calendly", "scheduling", "booking"]` |

## Verification Test Prompts

After a connector is set up, suggest one of these to verify it works:

| Connector | Test Prompt |
|-----------|------------|
| Google Drive | "Search my Google Drive for the most recently modified document and tell me its title." |
| Gmail | "Show me the subjects of my 5 most recent emails." |
| Google Calendar | "What's on my calendar for the rest of today?" |
| Slack | "Find the most recent messages in my Slack and summarize what's being discussed." |
| Notion | "Search my Notion workspace for any pages modified this week." |
| Asana | "List my assigned tasks in Asana that are due this week." |
| GitHub | "Show me the most recent pull requests in my repositories." |
| Salesforce | "List my most recent Salesforce opportunities." |

## Handling Missing Connectors

When a tool has no connector available, be transparent and suggest alternatives:

**Calendar tools (Calendly, Cal.com, Acuity):**
"There's no direct connector for [tool] right now. If you sync it to Google Calendar, I can access your schedule through the Google Calendar connector."

**Accounting tools (QuickBooks, Xero, FreshBooks):**
"Financial platform connectors are limited. You can export reports as spreadsheets and share them via Google Drive, which I can then access."

**Social media (Instagram, TikTok, Facebook):**
"Social media platforms generally don't have direct connectors. For content creation workflows, I can help you draft content and you can post it manually or through your scheduling tool."

**Email marketing (Mailchimp, Kit, ConvertKit):**
"No direct connector available. You can share campaign data via Google Drive or describe your needs and I'll help create the content."

**Automation platforms (n8n, Make, Zapier):**
"These platforms don't need direct connectors since they operate independently. I can help you design workflows or debug configurations if you share screenshots or descriptions."

## Tips for the Onboarding Flow

- **Start with Google Drive.** It's the most universally useful connector — almost everyone has documents that would help build context files.
- **Don't push too many at once.** Recommend 2-3 connectors that match their stated tools. They can always add more later.
- **Explain the value, not the tech.** Instead of "this uses MCP to create a bidirectional connection," say "this lets me search your Drive and pull documents into our conversation without you needing to copy-paste anything."
- **Respect privacy concerns.** If a user hesitates about connecting a platform, reassure them: connections are read-only for most connectors, and they can disconnect anytime in Settings.
