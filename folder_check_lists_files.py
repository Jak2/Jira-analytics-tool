from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File
from office365.sharepoint.folders.folder import Folder


def folder_exists_and_list_files(ctx, folder_path):
    """
    Check if a folder exists in the SharePoint path and list files within it.

    Args:
        ctx (ClientContext): Initialized SharePoint client context.
        folder_path (str): Path to the folder in SharePoint.

    Returns:
        tuple: 
            - bool: True if the folder exists, False otherwise.
            - list: List of file names within the folder if it exists.
    """
    try:
        print(f"Checking if folder exists: {folder_path}")
        web = ctx.web
        folders = web.get_sub_folders(folder_path=folder_path)
        ctx.load(folders)
        ctx.execute_query()

        if len(folders) > 0:
            folder = folders[0]  # Assuming only one folder with the given path

            # Get files within the folder
            files = folder.files
            ctx.load(files)
            ctx.execute_query()

            file_names = [file.name for file in files]
            print(f"Files in the folder: {file_names}")

            return True, file_names
        else:
            print(f"Folder does not exist: {folder_path}")
            return False, []

    except ClientRequestException as e:
        if e.error_code == '-2147024894':  # Folder not found
            print(f"Folder does not exist: {folder_path}")
            return False, []
        else:
            print(f"An error occurred: {str(e)}")
            raise
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False, []


# Example usage
if __name__ == "__main__":
    sharepoint_url = 'https://eaton.sharepoint.com'
    sharepoint_site = 'Vision2025forDigitalofficeEIIC'
    sharepoint_username = 'your_username'
    sharepoint_password = 'your_password'
    folder_path = '/sites/Vision2025forDigitalofficeEIIC/Shared Documents/General/Raise the Bar/2024/Input file_JQL/'

    ctx = ClientContext(sharepoint_url).with_credentials(
        UserCredential(sharepoint_username, sharepoint_password)
    )

    folder_exists, files_in_folder = folder_exists_and_list_files(ctx, folder_path)

    if folder_exists:
        print("Folder exists in SharePoint.")
        if files_in_folder:
            print("Files found in the folder:")
            for file in files_in_folder:
                print(f" - {file}")
        else:
            print("No files found in the folder.")
    else:
        print("Folder does not exist in SharePoint.")
