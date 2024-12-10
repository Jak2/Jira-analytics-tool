#!/usr/bin/env python3

import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.jira_analytics import JiraAnalyticsTool

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