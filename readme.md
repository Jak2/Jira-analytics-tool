# SharePoint-JIRA Integration Tool Documentation

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Code Structure](#code-structure)
6. [Usage Guide](#usage-guide)
7. [Troubleshooting](#troubleshooting)

## Overview

This tool automates the process of:
1. Reading data from a SharePoint CSV file
2. Querying JIRA based on the input data
3. Processing JIRA responses
4. Saving results back to SharePoint

## Prerequisites

- Python 3.8 or higher
- SharePoint Online account with appropriate permissions
- JIRA account with API access
- Network access to both SharePoint and JIRA servers

## Installation

1. Clone the repository or download the script
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Required Configuration Parameters

1. SharePoint Configuration:
   ```python
   'sharepoint': {
       'url': 'https://your-company.sharepoint.com',
       'site': 'your-site-name',
       'username': 'your.email@company.com',
       'password': 'your-password',
       'input_file': '/sites/your_site/Shared Documents/input.csv',
       'output_file': '/sites/your_site/Shared Documents/output.csv'
   }
   ```

2. JIRA Configuration:
   ```python
   'jira': {
       'url': 'https://your-company.atlassian.net',
       'email': 'your.email@company.com',
       'api_token': 'your-jira-api-token'
   }
   ```

### Input File Format
The input CSV file should contain the following columns:
- jql_query: JIRA query string
- business: Business unit name
- project: Project name
- metrics: Metrics information

## Code Structure

### Main Components

1. **SharePointManager Class**
   - Handles all SharePoint operations
   - Methods:
     - `read_file()`: Reads CSV from SharePoint
     - `write_file()`: Writes DataFrame to SharePoint

2. **JiraManager Class**
   - Manages JIRA API interactions
   - Methods:
     - `fetch_jira_data()`: Executes JQL queries
     - Handles authentication and response processing

3. **Helper Functions**
   - `extract_issue_details()`: Processes JIRA issue data
   - Logging utilities for operation tracking

### Data Flow

```
SharePoint Input File
       ↓
Read CSV Data
       ↓
Process Each Row
       ↓
Query JIRA API
       ↓
Extract Issue Details
       ↓
Compile Results
       ↓
Write to SharePoint
```

## Usage Guide

### Basic Usage

1. Update configuration in the script:
   ```python
   config = {
       'sharepoint': {
           # Your SharePoint configuration
       },
       'jira': {
           # Your JIRA configuration
       }
   }
   ```

2. Run the script:
   ```bash
   python script_name.py
   ```

### Logging

- Logs are written to 'jira_sharepoint_integration.log'
- Console output shows real-time progress
- Log levels: INFO, ERROR, DEBUG

### Example Input CSV

```csv
jql_query,business,project,metrics
"project = PROJ AND issuetype = Bug",Business Unit 1,Project A,Metric 1
"project = PROJ AND issuetype = Task",Business Unit 2,Project B,Metric 2
```

### Example Output CSV

The output file will contain columns including:
- Issue ID
- Issue Key
- Status
- Issue Type
- Project Name
- Story Points
- Business
- Metrics
- Labels

## Troubleshooting

### Common Issues and Solutions

1. **SharePoint Connection Failed**
   - Check credentials
   - Verify SharePoint URL format
   - Ensure network access

2. **JIRA API Errors**
   - Verify API token
   - Check JQL query syntax
   - Confirm API access permissions

3. **File Access Issues**
   - Verify file paths
   - Check SharePoint permissions
   - Ensure file format is correct

### Error Messages

- "Error reading file from SharePoint": Check file path and permissions
- "Error fetching JIRA data": Verify JIRA configuration and query
- "Error in main execution": Check overall configuration and logs

### Best Practices

1. **Performance Optimization**
   - Process data in smaller batches for large datasets
   - Use appropriate JQL queries to limit results
   - Monitor memory usage for large operations

2. **Security**
   - Store credentials securely (use environment variables)
   - Regular API token rotation
   - Minimum required permissions

3. **Maintenance**
   - Regular log file cleanup
   - Monitor SharePoint storage usage
   - Update dependencies regularly

For additional support or questions, please contact your system administrator or refer to the internal documentation.
