from __future__ import print_function

import json
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class SheetReader():
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    token_path = "token.json"
    credentials_path = "credentials.json"
    config_path = "config.json"
    creds = None
    sheet = None
    config = {}

    def __init__(self):
        self.creds = self.get_creds()
        self.sheet = self.get_service().spreadsheets()
        self.config = self.get_config()

    # Adapted from google's documentations:
    # https://developers.google.com/sheets/api/quickstart/python
    def get_creds(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
            return creds
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
                creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

    def get_service(self):
        if self.creds:
            return build('sheets', 'v4', credentials=self.creds)

    def get_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as config:
                return json.loads(config.read())

    def read_spreadsheet(self):
        sheetId = self.config.get("sheetId")
        range = "Access"
        result = self.sheet.values().get(spreadsheetId=sheetId, range=range).execute()
        values = result.get('values', [])
        return values

sr = SheetReader()
r = sr.read_spreadsheet()


