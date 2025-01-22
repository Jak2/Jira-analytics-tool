import os
import logging
from datetime import datetime
import pandas as pd
import requests
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jira_sharepoint_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SharePointManager:
    """Handles SharePoint operations"""
    
    def __init__(self, sharepoint_url, sharepoint_site, username, password):
        """
        Initialize SharePoint connection
        
        Args:
            sharepoint_url (str): SharePoint site URL
            sharepoint_site (str): SharePoint site name
            username (str): SharePoint username
            password (str): SharePoint password
        """
        self.ctx = ClientContext(sharepoint_url).with_credentials(
            UserCredential(username, password)
        )
        self.site = sharepoint_site
        
    def read_file(self, file_path):
        """
        Read file from SharePoint
        
        Args:
            file_path (str): Path to file in SharePoint
            
        Returns:
            pd.DataFrame: DataFrame containing file contents
        """
        try:
            logger.info(f"Reading file from SharePoint: {file_path}")
            response = File.open_binary(self.ctx, file_path)
            
            with open('temp_file.csv', 'wb') as local_file:
                local_file.write(response.content)
            
            df = pd.read_csv('temp_file.csv')
            os.remove('temp_file.csv')
            
            return df
            
        except Exception as e:
            logger.error(f"Error reading file from SharePoint: {str(e)}")
            raise

    def write_file(self, df, file_path):
        """
        Write DataFrame to SharePoint
        
        Args:
            df (pd.DataFrame): DataFrame to write
            file_path (str): Path where to save file in SharePoint
        """
        try:
            logger.info(f"Writing file to SharePoint: {file_path}")
            
            # Save DataFrame to temporary file
            temp_file = 'temp_output.csv'
            df.to_csv(temp_file, index=False)
            
            # Upload to SharePoint
            with open(temp_file, 'rb') as content_file:
                file_content = content_file.read()
            
            File.save_binary(self.ctx, file_path, file_content)
            
            # Clean up temporary file
            os.remove(temp_file)
            
            logger.info("File successfully written to SharePoint")
            
        except Exception as e:
            logger.error(f"Error writing file to SharePoint: {str(e)}")
            raise

class JiraManager:
    """Handles JIRA operations"""
    
    def __init__(self, jira_url, email, api_token):
        """
        Initialize JIRA connection
        
        Args:
            jira_url (str): JIRA base URL
            email (str): JIRA email
            api_token (str): JIRA API token
        """
        self.jira_url = jira_url
        self.auth = (email, api_token)
        self.headers = {'Accept': 'application/json'}

    def fetch_jira_data(self, jql_query):
        """
        Fetch data from JIRA using JQL query
        
        Args:
            jql_query (str): JQL query to execute
            
        Returns:
            list: List of JIRA issues
        """
        try:
            url = f'{self.jira_url}/rest/api/2/search'
            params = {'startAt': 0, 'maxResults': 100, 'jql': jql_query}
            
            response = requests.get(
                url, 
                headers=self.headers, 
                auth=self.auth, 
                params=params, 
                verify=False
            )
            response.raise_for_status()
            
            return response.json().get('issues', [])
            
        except Exception as e:
            logger.error(f"Error fetching JIRA data: {str(e)}")
            raise

def extract_issue_details(issue, business, project, metrics):
    """Extract relevant fields from JIRA issue"""
    fields = issue.get('fields', {})
    labels_to_include = ['label1', 'label2']  # Configure as needed
    filtered_labels = [
        label for label in fields.get('labels', []) 
        if label in labels_to_include
    ]
    
    return {
        'Issue ID': issue.get('id'),
        'Issue Key': issue.get('key'),
        'Status': fields.get('status', {}).get('name', 'Not Found'),
        'Issue Type': fields.get('issuetype', {}).get('name', 'Not Found'),
        'Project Name': project,
        'Story Points': fields.get('customfield_10003', 0),
        'Objective Type': fields.get('customfield_16506', 'Not Found'),
        'Planned Business Value': fields.get('customfield_16502', 'Not Found'),
        'Completed Business Value': fields.get('customfield_16503', 'Not Found'),
        'Program Increment': fields.get('customfield_18800', 'Not Found'),
        'Business': business,
        'Metrics': metrics,
        'Labels': filtered_labels
    }

def main():
    # Configuration
    config = {
        'sharepoint': {
            'url': 'your_sharepoint_url',
            'site': 'your_site_name',
            'username': 'your_username',
            'password': 'your_password',
            'input_file': '/sites/your_site/Shared Documents/input.csv',
            'output_file': '/sites/your_site/Shared Documents/output.csv'
        },
        'jira': {
            'url': 'https://eaton-corp.atlassian.net',
            'email': 'sandhyaranirathlavath@eaton.com',
            'api_token': 'your_api_token_here'
        }
    }
    
    try:
        # Initialize managers
        sharepoint = SharePointManager(
            config['sharepoint']['url'],
            config['sharepoint']['site'],
            config['sharepoint']['username'],
            config['sharepoint']['password']
        )
        
        jira = JiraManager(
            config['jira']['url'],
            config['jira']['email'],
            config['jira']['api_token']
        )
        
        # Read input file from SharePoint
        logger.info("Starting data processing")
        df = sharepoint.read_file(config['sharepoint']['input_file'])
        
        # Process each row
        results = []
        for index, row in df.iterrows():
            logger.info(f"Processing row {index + 1}/{len(df)}")
            
            issues = jira.fetch_jira_data(row['jql_query'])
            detail_data = [
                extract_issue_details(
                    issue, 
                    row['business'], 
                    row['project'], 
                    row['metrics']
                ) for issue in issues
            ]
            results.extend(detail_data)
        
        # Create output DataFrame
        output_df = pd.DataFrame(results)
        
        # Write to SharePoint
        sharepoint.write_file(output_df, config['sharepoint']['output_file'])
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
