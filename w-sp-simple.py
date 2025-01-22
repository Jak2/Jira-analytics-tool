import requests
import pandas as pd
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
import io

# JIRA credentials and URL
jira_url = 'https://eaton-corp.atlassian.net'
email = 'sandhyaraniratlavath@eaton.com'
api_token = 'ATATT3xFfGF04ZGUwa4R0SSKT-syuvEYmWdSIGWpsfcnGNGQNTBKTOZYDZX_DAtQTnLKIZ'

# SharePoint configuration
sharepoint_base_url = 'https://eaton.sharepoint.com'
sharepoint_site = '/sites/Vision2025forDigitalofficeEIIC'
sharepoint_user = 'your_username'
sharepoint_password = 'your_password'

# SharePoint paths
input_folder_path = '/sites/Vision2025forDigitalofficeEIIC/Shared Documents/General/Raise the Bar/2024/Input file_JQL'
output_folder_path = '/sites/Vision2025forDigitalofficeEIIC/Shared Documents/General/Raise the Bar/2024/Output'

def initialize_sharepoint():
    """Initialize SharePoint connection"""
    auth = AuthenticationContext(sharepoint_base_url)
    auth.acquire_token_for_user(sharepoint_user, sharepoint_password)
    ctx = ClientContext(sharepoint_base_url + sharepoint_site, auth)
    web = ctx.web
    ctx.load(web)
    ctx.execute_query()
    print('Connected to SharePoint:', web.properties['Title'])
    return ctx

def read_file_from_sharepoint(ctx, file_path):
    """Read a file from SharePoint and return as DataFrame"""
    try:
        # Get file content
        file_response = File.open_binary(ctx, file_path)
        
        # Convert to DataFrame
        content = file_response.content
        df = pd.read_csv(io.BytesIO(content))
        print(f"Successfully read file: {file_path}")
        return df
    
    except Exception as e:
        print(f"Error reading file {file_path} from SharePoint: {str(e)}")
        return None

def save_file_to_sharepoint(ctx, df, file_path):
    """Save DataFrame to SharePoint as CSV"""
    try:
        # Convert DataFrame to CSV bytes
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_content = csv_buffer.getvalue()
        
        # Upload to SharePoint
        folder = ctx.web.get_folder_by_server_relative_url(output_folder_path)
        target_file = folder.upload_file(file_path, csv_content)
        ctx.execute_query()
        print(f"Successfully saved file: {file_path}")
        
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
    ctx = initialize_sharepoint()
    
    # Define input and output files
    input_files = [
        'Working in Progress Automation.csv',
        'Test_Automation.csv',
        'Customer_Defects.csv',
        'Internal_Defects.csv',
        'Schedule_Variance.csv'
    ]
    
    output_files = [
        'Output_WIP_Automation.csv',
        'Output_Test_Automation.csv',
        'Output_Customer_Defects.csv',
        'Output_Internal_Defects.csv',
        'Output_Schedule_Variance.csv'
    ]
    
    # Process each file
    for input_file, output_file in zip(input_files, output_files):
        print(f"\nProcessing {input_file}...")
        
        # Construct full SharePoint path
        input_file_path = f"{input_folder_path}/{input_file}"
        
        # Read input file from SharePoint
        df = read_file_from_sharepoint(ctx, input_file_path)
        if df is None:
            continue
        
        # Initialize a result column
        df['result'] = ""
        all_issue_details = []
        
        # Process each row
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
        save_file_to_sharepoint(ctx, scope_delivered, output_file)

if __name__ == "__main__":
    main()
