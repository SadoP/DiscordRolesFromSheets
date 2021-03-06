from __future__ import print_function

import json
import os.path
import traceback

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from logger import logger

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


class SheetReader:
    scopes = ['https://www.googleapis.com/auth/spreadsheets',
              'https://www.googleapis.com/auth/drive']

    service_account_file = "service_account.json"
    config_path = "config.json"
    creds = None
    sheet = None
    config = {}

    def __init__(self):
        self.config = self.get_config()
        self.creds = self.get_creds()
        self.sheet = self.get_service().spreadsheets()

    def get_creds(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file, scopes=self.scopes)
        return credentials

    def get_service(self):
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
        cols = [userIDColumn] + roleColumns
        pdCols = ["userID"] + roleIDs
        try:
            result = self.sheet.values().get(spreadsheetId=sheetId, range=sheet).execute()
            data = pd.DataFrame(result.get("values")[1:], columns=result.get("values")[0])
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("error upon requesting data", e)
            return
        columns = [excel_style(i + 1) for i in range(len(data.columns))]
        data.columns = columns
        data = data.iloc[informationRow - 2:].loc[:, cols]
        data.columns = pdCols
        data.loc[:, roleIDs] = data.loc[:, roleIDs] == self.config.get("roleConfirmationPhrase")
        data.index = data.loc[:, "userID"]
        data = data.drop("userID", axis=1)
        return data
