def file_exists_in_sharepoint(ctx, file_path):
    """
    Check if a file exists in the SharePoint path.

    Args:
        ctx (ClientContext): Initialized SharePoint client context.
        file_path (str): Path to the file in SharePoint.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    try:
        print(f"Checking if file exists: {file_path}")
        file = ctx.web.get_file_by_server_relative_url(file_path)
        ctx.load(file)
        ctx.execute_query()
        print(f"File exists: {file_path}")
        return True
    except Exception as e:
        print(f"File does not exist or error occurred: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    sharepoint_url = 'https://eaton.sharepoint.com'
    sharepoint_site = 'Vision2025forDigitalofficeEIIC'
    sharepoint_username = 'your_username'
    sharepoint_password = 'your_password'
    sharepoint_input_file = '/sites/Vision2025forDigitalofficeEIIC/Shared Documents/General/Raise the Bar/2024/Input file_JQL/Working in Progress Automation.csv'

    ctx = ClientContext(sharepoint_url).with_credentials(
        UserCredential(sharepoint_username, sharepoint_password)
    )

    if file_exists_in_sharepoint(ctx, sharepoint_input_file):
        print("File exists in SharePoint.")
    else:
        print("File does not exist in SharePoint.")
