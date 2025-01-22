import requests
import pandas as pd

# JIRA credentials and URL
jira_url = 'https://eaton-corp.atlassian.net'
email = 'sandhyaraniratlavath@eaton.com'
api_token = 'ATATT3xFfGF04ZGUwa4R0SSKT-syuvEYmWdSIGWpsfcnGNGQNTBKTOZYDZX_DAtQTnLKIZ'

def fetch_jira_data(jql_query):
    url = f'{jira_url}/rest/api/2/search'
    auth = (email, api_token)
    headers = {'Accept': 'application/json', 'Authorization': f'Basic {auth}', 'User-Agent': 'Mozilla/5.0 (Windows NT'}
    params = {'startAt': 0, 'maxResults': 100, 'jql': jql_query}
    response = requests.get(url, headers=headers, auth=auth, params=params, verify=False)
    response.raise_for_status()  # Raise an error for bad status codes
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

def main(input_files, output_files):
    for input_file, output_file in zip(input_files, output_files):
        # Read input file
        df = pd.read_csv(input_file)
        
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
        
        # Save the final dataframe to a CSV
        scope_delivered = pd.DataFrame(all_issue_details)
        scope_delivered.to_csv(output_file, index=False)
        print(f"Output saved to {output_file}")

# Replace 'input1.csv', 'input2.csv', etc. and 'output1.csv', 'output2.csv', etc. with your file names
input_files = ['Scope.csv', 'Test_Automation.csv', 'Customer_Defects.csv', 'Internal_Defects.csv', 'Schedule_Variance.csv']
output_files = ['Output_Scope.csv', 'Output_Test_Automation.csv', 'Output_Customer_Defects.csv', 'Output_Internal_Defects.csv', 'Output_Schedule_Variance.csv']

main(input_files, output_files)
