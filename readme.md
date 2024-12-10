# Jira Analytics Tool

## Project Structure
```
jira-analytics-tool/
│
├── src/
│   ├── __init__.py
│   └── jira_analytics.py
│
├── scripts/
│   └── run_jira_analytics.py
│
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

## Prerequisites

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jira-analytics-tool.git
cd jira-analytics-tool
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Authentication Setup

#### Method 1: Environment Variables (Recommended)
1. Copy the `.env.example` file to `.env`
```bash
cp .env.example .env
```

2. Edit the `.env` file with your Jira credentials:
```
# Basic Authentication
JIRA_SERVER=https://your-jira-instance.atlassian.net
JIRA_USERNAME=your_username
JIRA_API_TOKEN=your_api_token

# Optional OAuth 2.0 Credentials
JIRA_CLIENT_ID=your_client_id
JIRA_CLIENT_SECRET=your_client_secret
JIRA_ACCESS_TOKEN=your_access_token
```

#### Method 2: Direct Instantiation
You can also pass credentials directly when creating the JiraAnalyticsTool instance:
```python
jira_tool = JiraAnalyticsTool(
    jira_server='https://your-jira-instance.atlassian.net',
    username='your_username', 
    api_token='your_api_token'
)
```

## Usage

### Running the Script
```bash
python scripts/run_jira_analytics.py
```

### Example JQL Queries
1. Fetch all open issues:
```
status = Open
```

2. Fetch issues assigned to a specific user:
```
assignee = "john.doe"
```

3. Fetch issues created in the last week:
```
created >= -1w
```

4. Fetch issues by project and priority:
```
project = "PROJECT_KEY" AND priority = High
```

## Configuration Options

### Fetching Issues
- You can specify the maximum number of issues to fetch
- Leave blank to fetch all matching issues

### Export Options
- Export fetched issues to Excel 
- Choose filename and location during runtime

## Troubleshooting

### Common Issues
1. **Authentication Failure**
   - Double-check your Jira server URL
   - Verify username and API token
   - Ensure proper network access

2. **No Issues Found**
   - Verify your JQL query syntax
   - Check issue visibility and permissions

### Obtaining Jira API Token
1. Log in to Atlassian Account
2. Go to API Tokens section
3. Create a new API token
4. Copy and use in `.env` file

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License
[Specify your license, e.g., MIT]

## Contact
[Your contact information or support email]