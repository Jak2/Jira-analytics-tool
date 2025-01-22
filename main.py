import os
import logging
from datetime import datetime
import pandas as pd
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from jira import JIRA
from tqdm import tqdm
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'jira_sharepoint_integration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
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
        try:
            self.ctx = ClientContext(sharepoint_url).with_credentials(
                UserCredential(username, password)
            )
            self.site = sharepoint_site
            logger.info("SharePoint connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SharePoint connection: {str(e)}")
            raise
        
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
            
            temp_file = f'temp_input_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            with open(temp_file, 'wb') as local_file:
                local_file.write(response.content)
            
            df = pd.read_csv(temp_file)
            os.remove(temp_file)
            
            logger.info(f"Successfully read file with {len(df)} rows")
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
            
            temp_file = f'temp_output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            df.to_csv(temp_file, index=False)
            
            with open(temp_file, 'rb') as content_file:
                file_content = content_file.read()
            
            File.save_binary(self.ctx, file_path, file_content)
            os.remove(temp_file)
            
            logger.info(f"Successfully wrote {len(df)} rows to SharePoint")
            
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
        try:
            self.jira = JIRA(
                server=jira_url,
                basic_auth=(email, api_token)
            )
            logger.info("JIRA connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize JIRA connection: {str(e)}")
            raise

    def fetch_jira_data(self, jql_query):
        """
        Fetch data from JIRA using JQL query
        
        Args:
            jql_query (str): JQL query to execute
            
        Returns:
            list: List of JIRA issues
        """
        try:
            logger.info(f"Executing JQL query: {jql_query}")
            issues = []
            start_at = 0
            max_results = 100

            # Get total number of issues for progress bar
            total = self.jira.search_issues(jql_query, maxResults=0).total
            logger.info(f"Found {total} issues to process")

            with tqdm(total=total, desc="Fetching JIRA issues") as pbar:
                while True:
                    batch = self.jira.search_issues(
                        jql_query,
                        startAt=start_at,
                        maxResults=max_results,
                        expand='changelog'
                    )
                    
                    if not batch:
                        break
                        
                    issues.extend(batch)
                    start_at += max_results
                    pbar.update(len(batch))
                    
                    if len(batch) < max_results:
                        break

            logger.info(f"Successfully fetched {len(issues)} issues")
            return issues
            
        except Exception as e:
            logger.error(f"Error fetching JIRA data: {str(e)}")
            raise

def extract_issue_details(issue, business, project, metrics):
    """
    Extract relevant fields from JIRA issue
    
    Args:
        issue: JIRA issue object
        business (str): Business unit name
        project (str): Project name
        metrics (str): Metrics information
        
    Returns:
        dict: Dictionary containing extracted issue details
    """
    try:
        fields = issue.fields
        
        # Configure these labels based on your needs
        labels_to_include = ['label1', 'label2']
        filtered_labels = [
            label for label in getattr(fields, 'labels', [])
            if label in labels_to_include
        ]
        
        return {
            'Issue ID': issue.id,
            'Issue Key': issue.key,
            'Status': str(fields.status),
            'Issue Type': str(fields.issuetype),
            'Project Name': project,
            'Story Points': getattr(fields, 'customfield_10003', 0),
            'Objective Type': getattr(fields, 'customfield_16506', 'Not Found'),
            'Planned Business Value': getattr(fields, 'customfield_16502', 'Not Found'),
            'Completed Business Value': getattr(fields, 'customfield_16503', 'Not Found'),
            'Program Increment': getattr(fields, 'customfield_18800', 'Not Found'),
            'Business': business,
            'Metrics': metrics,
            'Labels': filtered_labels
        }
    except Exception as e:
        logger.error(f"Error extracting details for issue {issue.key}: {str(e)}")
        return None

def process_jira_data(jira_manager, df):
    """
    Process JIRA data for each row in the input DataFrame
    
    Args:
        jira_manager (JiraManager): Initialized JIRA manager
        df (pd.DataFrame): Input DataFrame
        
    Returns:
        list: List of processed issue details
    """
    results = []
    
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        try:
            logger.info(f"Processing row {index + 1}/{len(df)}")
            issues = jira_manager.fetch_jira_data(row['jql_query'])
            
            for issue in issues:
                details = extract_issue_details(
                    issue,
                    row['business'],
                    row['project'],
                    row['metrics']
                )
                if details:
                    results.append(details)
                    
        except Exception as e:
            logger.error(f"Error processing row {index}: {str(e)}")
            continue
            
    return results

def main():
    try:
        # Load environment variables
        load_dotenv()
        
        # Configuration
        config = {
            'sharepoint': {
                'url': os.getenv('SHAREPOINT_URL'),
                'site': os.getenv('SHAREPOINT_SITE'),
                'username': os.getenv('SHAREPOINT_USERNAME'),
                'password': os.getenv('SHAREPOINT_PASSWORD'),
                'input_file': os.getenv('SHAREPOINT_INPUT_FILE'),
                'output_file': os.getenv('SHAREPOINT_OUTPUT_FILE')
            },
            'jira': {
                'url': os.getenv('JIRA_URL'),
                'email': os.getenv('JIRA_EMAIL'),
                'api_token': os.getenv('JIRA_API_TOKEN')
            }
        }
        
        # Validate configuration
        for section in config:
            for key, value in config[section].items():
                if not value:
                    raise ValueError(f"Missing configuration: {section}.{key}")
        
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
        input_df = sharepoint.read_file(config['sharepoint']['input_file'])
        
        # Process JIRA data
        results = process_jira_data(jira, input_df)
        
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
