# Integrations and connections

Source: https://www.notion.so/help/integrations

---

Connect Notion to external tools and services through integrations (also called connections) to sync data, receive notifications, or automate workflows.

## Types of integrations

- **Pre-built integrations** — official connectors (Slack, Google Drive, GitHub, Figma, etc.).
- **Internal integrations** — custom bots built with the Notion API for your workspace.
- **Link previews** — when you paste a URL from a supported service, Notion renders a rich preview.

## Connect a pre-built integration

1. Go to **Settings & Members** > **Connections**.
2. Browse the available integrations.
3. Click **Connect** next to the desired service.
4. Authorize Notion to access the external service (OAuth flow).
5. Configure settings specific to that integration.

## Common integrations

### Slack
- Get Notion notifications in Slack channels.
- Preview Notion links shared in Slack.
- Search Notion content from Slack.

### Google Drive
- Embed Google Docs, Sheets, and Slides directly in Notion pages.
- Search and insert files from within Notion.

### GitHub
- Paste GitHub links to see rich previews (issues, PRs, repos).
- Sync GitHub issues into a Notion database.

### Figma
- Paste Figma links to see live design previews.
- Previews update as the design changes.

## Add a connection to a page

1. Open a page.
2. Click **•••** > **Connections** > **Add connections**.
3. Select the integration from the list.
4. The integration now has access to this page and its sub-pages.
5. This is required for internal/API integrations to read page content.

## Internal integrations (API bots)

1. Visit notion.so/my-integrations.
2. Click **+ New integration**.
3. Name it and select the workspace.
4. Set capabilities (Read content, Update content, Insert content).
5. Copy the **Internal Integration Token**.
6. Add the integration to specific pages (it only sees pages where it's connected).

## Remove a connection

1. Go to **Settings & Members** > **Connections**.
2. Find the integration.
3. Click **•••** > **Disconnect**.
4. The integration loses access immediately.
