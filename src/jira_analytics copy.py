import os
from jira import JIRA
from typing import List, Dict, Any, Optional
import pandas as pd

class JiraAnalyticsTool:
    def __init__(self, jira_server=None, username=None, api_token=None, 
                 client_id=None, client_secret=None, access_token=None):
        """
        Initialize Jira connection with multiple authentication methods
        
        Authentication Methods:
        1. Basic Authentication (username + API token)
        2. OAuth 2.0 (client_id, client_secret, access_token)
        
        Args:
            jira_server (str): Jira instance URL
            username (str): Jira username for basic auth
            api_token (str): API token for basic auth
            client_id (str): OAuth 2.0 client ID
            client_secret (str): OAuth 2.0 client secret
            access_token (str): OAuth 2.0 access token
        """
        # Jira connection parameters
        self.jira_server = jira_server or os.getenv('JIRA_SERVER', 'https://your-jira-instance.atlassian.net')
        self.username = username or os.getenv('JIRA_USERNAME')
        self.api_token = api_token or os.getenv('JIRA_API_TOKEN')
        
        # OAuth parameters
        self.client_id = client_id or os.getenv('JIRA_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('JIRA_CLIENT_SECRET')
        self.access_token = access_token or os.getenv('JIRA_ACCESS_TOKEN')
        
        # Initialize Jira client
        self.jira_client = self._connect_to_jira()

    def _connect_to_jira(self) -> JIRA:
        """
        Establish connection to Jira instance with multiple auth methods
        
        Returns:
            JIRA: Authenticated Jira client
        """
        try:
            # Basic Authentication
            if self.username and self.api_token:
                jira = JIRA(
                    server=self.jira_server,
                    basic_auth=(self.username, self.api_token)
                )
                print("Successfully connected to Jira using Basic Authentication!")
                return jira
            
            # OAuth 2.0 Authentication
            elif self.client_id and self.client_secret and self.access_token:
                oauth_dict = {
                    'access_token': self.access_token,
                    'access_token_secret': '',
                    'consumer_key': self.client_id,
                    'key_cert': self.client_secret
                }
                jira = JIRA(
                    server=self.jira_server,
                    oauth=oauth_dict
                )
                print("Successfully connected to Jira using OAuth 2.0!")
                return jira
            
            else:
                raise ValueError("No valid authentication method provided")
        
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
            # Fetch all issues if no limit specified
            max_results = None
        
        try:
            issues = self.jira_client.search_issues(
                jql_query, 
                maxResults=max_results,
                fields=[
                    'summary', 'status', 'priority', 'issuetype', 'created', 
                    'updated', 'resolved', 'assignee', 'reporter', 
                    'project', 'fixVersion', 'components', 'labels', 
                    'environment', 'resolution', 'timeSpent'
                ]
            )
            return [self._format_issue(issue) for issue in issues]
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
            'issueKey': issue.key,
            'summary': issue.fields.summary,
            'status': str(issue.fields.status),
            'priority': str(issue.fields.priority),
            'issuetype': str(issue.fields.issuetype),
            'created': str(issue.fields.created),
            'updated': str(issue.fields.updated),
            'resolved': str(getattr(issue.fields, 'resolutiondate', None)),
            'assignee': str(issue.fields.assignee) if issue.fields.assignee else None,
            'reporter': str(issue.fields.reporter),
            'project': str(issue.fields.project),
            'fixVersion': ', '.join([str(v) for v in issue.fields.fixVersions]) if issue.fields.fixVersions else None,
            'component': ', '.join([str(c) for c in issue.fields.components]) if issue.fields.components else None,
            'labels': issue.fields.labels,
            'environment': getattr(issue.fields, 'environment', None),
            'resolution': str(issue.fields.resolution) if issue.fields.resolution else None,
            'timeSpent': getattr(issue.fields, 'timeSpent', None)
        }

    def export_to_excel(self, issues: List[Dict[str, Any]], filename: str = 'jira_issues.xlsx'):
        """
        Export issues to Excel
        
        Args:
            issues (List[Dict[str, Any]]): List of issue dictionaries
            filename (str): Output Excel filename
        """
        try:
            df = pd.DataFrame(issues)
            df.to_excel(filename, index=False)
            print(f"Issues exported to {filename}")
        except Exception as e:
            print(f"Error exporting to Excel: {e}")

def main():
    # Create Jira Analytics Tool instance
    jira_tool = JiraAnalyticsTool()
    
    # Prompt for JQL query
    jql_query = input("Enter your JQL query: ").strip()
    
    # Prompt for number of issues
    try:
        max_issues = input("Enter number of issues to fetch (press Enter to fetch all): ").strip()
        max_issues = int(max_issues) if max_issues else None
    except ValueError:
        print("Invalid input. Fetching all issues.")
        max_issues = None
    
    # Fetch issues
    issues = jira_tool.fetch_issues(jql_query, max_issues)
    
    # Print issues
    if issues:
        print(f"\nFetched {len(issues)} issues:")
        for issue in issues:
            print(f"Issue Key: {issue['issueKey']} - Summary: {issue['summary']}")
        
        # Export to Excel option
        export_choice = input("\nDo you want to export issues to Excel? (y/n): ").strip().lower()
        if export_choice == 'y':
            jira_tool.export_to_excel(issues)
    else:
        print("No issues found matching the JQL query.")

if __name__ == "__main__":
    main()