from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os


def get_creds(creds_file_name: str) -> Credentials:
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive']

    creds = None
    if os.path.exists('../secrets/token.json'):
        creds = Credentials.from_authorized_user_file('../secrets/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file_name, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('../secrets/token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def get_rowData(spreadsheet_id: str, ranges: str) -> list:
    creds = get_creds('../secrets/credentials.json')

    service = build('sheets', 'v4', credentials=creds, cache_discovery=False)

    include_grid_data = True

    request = service.spreadsheets().get(spreadsheetId=spreadsheet_id, ranges=ranges, includeGridData=include_grid_data)
    response = request.execute()

    rowData = response['sheets'][0]['data'][0]['rowData']
    for i, row in enumerate(rowData):
        if 'values' in row.keys():
            for j, value in enumerate(row['values']):
                if value and 'formattedValue' in value.keys():
                    row['values'][j] = value['formattedValue']
                else:
                    row['values'][j] = None
            rowData[i] = row['values']
        else:
            rowData[i] = None

    return rowData
