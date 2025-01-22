import requests
import pandas as pd
from O365 import Account, FileSystemTokenBackend
from io import StringIO
import os

# JIRA credentials and URL
jira_url = 'https://eaton-corp.atlassian.net'
email = 'sandhyaraniratlavath@eaton.com'
api_token = 'ATATT3xFfGF04ZGUwa4R0SSKT-syuvEYmWdSIGWpsfcnGNGQNTBKTOZYDZX_DAtQTnLKIZ'

# SharePoint credentials
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
SHAREPOINT_SITE_URL = 'your_sharepoint_site_url'
SHAREPOINT_FOLDER_PATH = '/sites/your_site/Shared Documents/your_folder'  # Adjust this path

def initialize_sharepoint():
    # Set up token backend
    token_backend = FileSystemTokenBackend(token_path='./office365_token.txt')
    
    # Create account object
    account = Account((CLIENT_ID, CLIENT_SECRET), token_backend=token_backend)
    
    # If not authenticated, authenticate
    if not account.is_authenticated:
        account.authenticate()
    
    return account

def read_file_from_sharepoint(account, file_path):
    """Read a file from SharePoint and return its contents as a pandas DataFrame"""
    try:
        # Get SharePoint drive
        storage = account.storage()
        site = storage.get_site(SHAREPOINT_SITE_URL)
        drive = site.get_default_document_library()
        
        # Get file
        file = drive.get_item_by_path(f"{SHAREPOINT_FOLDER_PATH}/{file_path}")
        
        # Download and read content
        content = file.get_content()
        
        # Convert content to DataFrame
        df = pd.read_csv(StringIO(content.decode('utf-8')))
        return df
    
    except Exception as e:
        print(f"Error reading file {file_path} from SharePoint: {str(e)}")
        return None

def save_file_to_sharepoint(account, df, file_path):
    """Save DataFrame to SharePoint as CSV"""
    try:
        # Convert DataFrame to CSV string
        csv_content = df.to_csv(index=False)
        
        # Get SharePoint drive
        storage = account.storage()
        site = storage.get_site(SHAREPOINT_SITE_URL)
        drive = site.get_default_document_library()
        
        # Create or update file
        folder = drive.get_item_by_path(SHAREPOINT_FOLDER_PATH)
        folder.upload_file(content=csv_content.encode('utf-8'), item_name=file_path)
        
        print(f"Successfully saved {file_path} to SharePoint")
        
    except Exception as e:
        print(f"Error saving file {file_path} to SharePoint: {str(e)}")

def fetch_jira_data(jql_query):
    url = f'{jira_url}/rest/api/2/search'
    auth = (email, api_token)
    headers = {'Accept': 'application/json', 'Authorization': f'Basic {auth}', 'User-Agent': 'Mozilla/5.0 (Windows NT'}
    params = {'startAt': 0, 'maxResults': 100, 'jql': jql_query}
    response = requests.get(url, headers=headers, auth=auth, params=params, verify=False)
    response.raise_for_status()
    return response.json().get('issues')

def extract_field_value(fields, field_id):
    field = fields.get(field_id)
    if field and isinstance(field, dict):
        return field.get('value', 'Not Found')
    return 'Not Found'

def extract_issue_details(issue, business, project, metrics):
    fields = issue.get('fields', {})
    planned_business_value = extract_field_value(fields, 'customfield_16502')
    completed_business_value = extract_field_value(fields, 'customfield_16503')
    objective_type = extract_field_value(fields, 'customfield_16506')
    program_increment = extract_field_value(fields, 'customfield_18800')
    story_points = fields.get('customfield_10003', 0)
    labels = fields.get('labels', [])
    
    return {
        'Issue ID': issue.get('id'),
        'Issue Key': issue.get('key'),
        'Status': fields.get('status', {}).get('name', 'Not Found'),
        'Issue Type': fields.get('issuetype', {}).get('name', 'Not Found'),
        'Project Name': project,
        'StoryPoints': story_points,
        'Objective Type': objective_type,
        'Planned Business Value': planned_business_value,
        'Completed Business Value': completed_business_value,
        'Program Increment': program_increment,
        'Business': business,
        'Metrice': metrics
    }

def get_all_issue_data(jql_query, business, project, metrics):
    issues = fetch_jira_data(jql_query)
    issue_details = [extract_issue_details(issue, business, project, metrics) for issue in issues]
    return issue_details

def main():
    # Initialize SharePoint connection
    account = initialize_sharepoint()
    
    # Define input and output file names
    input_files = [
        'Scope.csv',
        'Test_Automation.csv',
        'Customer_Defects.csv',
        'Internal_Defects.csv',
        'Schedule_Variance.csv'
    ]
    
    output_files = [
        'Output_Scope.csv',
        'Output_Test_Automation.csv',
        'Output_Customer_Defects.csv',
        'Output_Internal_Defects.csv',
        'Output_Schedule_Variance.csv'
    ]
    
    # Process each file
    for input_file, output_file in zip(input_files, output_files):
        print(f"Processing {input_file}...")
        
        # Read input file from SharePoint
        df = read_file_from_sharepoint(account, input_file)
        if df is None:
            continue
            
        # Initialize a result column
        df['result'] = ""
        all_issue_details = []
        
        # Iterate through each row to fetch results based on JQL
        for index, row in df.iterrows():
            jql_query = row['JQL']
            business = row['Business']
            project = row['Project']
            metrics = row['Metrice']
            print(f"Fetching data for JQL: {jql_query}")
            
            # Fetch data and store it in 'result'
            detail_data = get_all_issue_data(jql_query, business, project, metrics)
            all_issue_details.extend(detail_data)
        
        # Create final dataframe and save to SharePoint
        scope_delivered = pd.DataFrame(all_issue_details)
        save_file_to_sharepoint(account, scope_delivered, output_file)

if __name__ == "__main__":
    main()
