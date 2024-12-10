import os
import sys
from jira import JIRA
from typing import List, Dict, Any, Optional
import pandas as pd

class JiraAnalyticsTool:
    def __init__(self, 
                 jira_server: Optional[str] = None, 
                 username: Optional[str] = None, 
                 api_token: Optional[str] = None):
        """
        Initialize Jira connection 
        
        Args:
            jira_server (Optional[str]): Jira server URL
            username (Optional[str]): Jira username
            api_token (Optional[str]): Jira API token
        """
        # Use provided credentials or fall back to environment variables
        self.jira_server = jira_server or os.getenv('JIRA_SERVER', 'https://your-jira-instance.atlassian.net')
        self.username = username or os.getenv('JIRA_USERNAME')
        self.api_token = api_token or os.getenv('JIRA_API_TOKEN')
        
        # Validate credentials
        self._validate_credentials()
        
        # Initialize Jira client
        self.jira_client = self._connect_to_jira()

    def _validate_credentials(self):
        """
        Validate Jira connection credentials
        """
        if not self.jira_server:
            raise ValueError("Jira server URL is required")
        if not self.username:
            raise ValueError("Jira username is required")
        if not self.api_token:
            raise ValueError("Jira API token is required")

    def _connect_to_jira(self) -> JIRA:
        """
        Establish connection to Jira instance
        
        Returns:
            JIRA: Authenticated Jira client
        """
        try:
            jira = JIRA(
                server=self.jira_server,
                basic_auth=(self.username, self.api_token)
            )
            print("Successfully connected to Jira!")
            return jira
        except Exception as e:
            print(f"Error connecting to Jira: {e}")
            raise

    def fetch_issues(self, jql_query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch Jira issues directly using a JQL query
        
        Args:
            jql_query (str): Jira Query Language (JQL) query
            max_results (Optional[int]): Maximum number of issues to fetch
        
        Returns:
            List[Dict[str, Any]]: List of issue dictionaries
        """
        # Determine max results
        if max_results is None or max_results <= 0:
            max_results = None
        
        try:
            print(f"Executing JQL Query: {jql_query}")
            
            # Fetch issues with all relevant fields
            issues = self.jira_client.search_issues(
                jql_query, 
                maxResults=max_results,
                fields=[
                    'summary', 'status', 'priority', 'issuetype', 'created', 
                    'updated', 'resolved', 'assignee', 'reporter', 
                    'project', 'fixVersion', 'components', 'labels', 
                    'environment', 'resolution', 'timeSpent', 'description'
                ]
            )
            
            # Format and return issues
            formatted_issues = [self._format_issue(issue) for issue in issues]
            print(f"Found {len(formatted_issues)} issues")
            return formatted_issues
        
        except Exception as e:
            print(f"Error fetching issues: {e}")
            return []

    def _format_issue(self, issue) -> Dict[str, Any]:
        """
        Format Jira issue for easier consumption
        
        Args:
            issue: Jira issue object
        
        Returns:
            Dict[str, Any]: Formatted issue dictionary
        """
        return {
            'Issue Key': issue.key,
            'Summary': issue.fields.summary,
            'Description': getattr(issue.fields, 'description', ''),
            'Status': str(issue.fields.status),
            'Priority': str(issue.fields.priority),
            'Issue Type': str(issue.fields.issuetype),
            'Created Date': str(issue.fields.created),
            'Updated Date': str(issue.fields.updated),
            'Resolved Date': str(getattr(issue.fields, 'resolutiondate', None) or ''),
            'Assignee': str(issue.fields.assignee) if issue.fields.assignee else 'Unassigned',
            'Reporter': str(issue.fields.reporter),
            'Project': str(issue.fields.project),
            'Fix Versions': ', '.join([str(v) for v in issue.fields.fixVersions]) if issue.fields.fixVersions else '',
            'Components': ', '.join([str(c) for c in issue.fields.components]) if issue.fields.components else '',
            'Labels': ', '.join(issue.fields.labels) if issue.fields.labels else '',
            'Environment': getattr(issue.fields, 'environment', ''),
            'Resolution': str(issue.fields.resolution) if issue.fields.resolution else '',
            'Time Spent': getattr(issue.fields, 'timeSpent', '')
        }

    def export_to_excel(self, issues: List[Dict[str, Any]], filename: str = 'jira_issues.xlsx'):
        """
        Export issues to Excel
        
        Args:
            issues (List[Dict[str, Any]]): List of issue dictionaries
            filename (str): Output Excel filename
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
            
            # Create DataFrame and export
            df = pd.DataFrame(issues)
            df.to_excel(filename, index=False)
            print(f"Issues exported to {filename}")
        
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            raise

    def get_project_issues(self, project_key: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch all issues for a specific project
        
        Args:
            project_key (str): Jira project key
            max_results (Optional[int]): Maximum number of issues to fetch
        
        Returns:
            List[Dict[str, Any]]: List of project issues
        """
        jql_query = f"project = {project_key}"
        return self.fetch_issues(jql_query, max_results)

    def get_issues_by_status(self, status: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch issues by their status
        
        Args:
            status (str): Issue status (e.g., 'Open', 'In Progress', 'Closed')
            max_results (Optional[int]): Maximum number of issues to fetch
        
        Returns:
            List[Dict[str, Any]]: List of issues with specified status
        """
        jql_query = f"status = '{status}'"
        return self.fetch_issues(jql_query, max_results)

    def get_issues_by_assignee(self, assignee: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch issues assigned to a specific user
        
        Args:
            assignee (str): Assignee username
            max_results (Optional[int]): Maximum number of issues to fetch
        
        Returns:
            List[Dict[str, Any]]: List of issues assigned to the user
        """
        jql_query = f"assignee = '{assignee}'"
        return self.fetch_issues(jql_query, max_results)