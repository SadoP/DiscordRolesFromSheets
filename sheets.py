from __future__ import print_function

import json
import os.path
import traceback

import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from logger import logger
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class SheetReader:
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    token_path = "token.json"
    credentials_path = "credentials.json"
    config_path = "config.json"
    creds = None
    sheet = None
    config = {}

    def __init__(self):
        self.config = self.get_config()
        self.get_creds()
        self.sheet = self.get_service().spreadsheets()

    # Adapted from google's documentations:
    # https://developers.google.com/sheets/api/quickstart/python
    def get_creds(self):
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
                self.creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())

    def get_service(self):
        if self.creds:
            return build('sheets', 'v4', credentials=self.creds)

    def get_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as config:
                return json.loads(config.read())

    def read_spreadsheet(self):
        def excel_style(col):
            # https://stackoverflow.com/a/19169180
            result = []
            while col:
                col, rem = divmod(col - 1, 26)
                result[:0] = LETTERS[rem]
            return ''.join(result)
        self.get_creds()
        sheetId = self.config.get("sheetId")
        sheet = self.config.get("sheetName")
        userIDColumn = self.config.get("userIDsColumn")
        roleColumns = [role.get("roleColumn") for role in self.config.get("roles")]
        roleIDs = [role.get("roleID") for role in self.config.get("roles")]
        informationRow = int(self.config.get("InformationRowStart"))
        cols = [userIDColumn]+roleColumns
        pdCols = ["userID"]+roleIDs
        try:
            result = self.sheet.values().get(spreadsheetId=sheetId, range=sheet).execute()
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("error upon requesting data", e)
            return
        data = pd.DataFrame(result.get("values")[1:], columns=result.get("values")[0])
        columns = [excel_style(i+1) for i in range(len(data.columns))]
        data.columns = columns
        data = data.iloc[informationRow-2:].loc[:, cols]
        data.columns = pdCols
        data.loc[:, roleIDs] = data.loc[:, roleIDs] == self.config.get("roleConfirmationPhrase")
        data.index = data.loc[:, "userID"]
        data = data.drop("userID", axis=1)
        return data
