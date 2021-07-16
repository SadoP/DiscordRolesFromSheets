# DiscordRolesFromSheets

## Installation:
- Clone / download the repo:
```bash
git clone git@github.com:SadoP/DiscordRolesFromSheets.git
```
- Create a Conda environment for the bot and activate it
```bash
conda conda env create -f environment.yml
conda activte DRFS
```
- Follow this guideline to obtain Credentials for a Desktop Application for your Bot:
https://developers.google.com/workspace/guides/create-credentials
Once you have done this, place the `credentials.json` in the same folder as the bot.
- Copy or move `config.json.default` to `config.json` and fill in all the information in the `config.json`. The bot does not have any default values, if a field is left blank, it will break.
    - sheetId: The id of the spreadsheet
    - discordToken: The token used to login to your discord Bot
    - clientID: The client ID of your google Application
    - clientSecret: The accompanying secret
    - sheetName: Name of the sheet within the spreadsheet
    - InformationRowStart: The first row that is not a header.
      This counts the same way as the sheet, ie the first row is 1 not 0
    - userIDsColumn:
      Column in the sheet that contains the Discord users' IDs
    - roles: List of roles.
      I added 3 in the template, this can be increased or decreased.
      Needs the following two parameters per role:
        - roleColumn: The column in the sheet that contains a marker whether the role is assigned
        - roleID: The id of the role this column belongs to
    - roleConfirmationPhrase: Phrase that is used to assign the role. Could for example be "X" or "true".
      Case sensitive.
    - guildID: ID of the guild the bot is on.
    - loggingChannel: Channel used for logging. Has to be filled.
- Invite the bot to your Discord. 
- Start the bot:
 ```bash
 python start.py
 ```
- Copy the link to your browser and follow the instructions to authorize access to your spreadsheet.
  This has to be done only the first time you start the bot, but the bot has to be restarted the first time after authorization has been granted.

## Example Sheet and config
| Access | A        | B   | C         | D     | E     | F     |
|--------|----------|-----|-----------|-------|-------|-------|
| 1      | Name     | Dpt | DiscordID | Role1 | Role2 | Role3 |
| 2      | Person A | Z   | 12        | X     | O     | X     |
| 3      | Person B | Y   | 34        | X     | O     | O     |
| 4      | Person C | X   | 56        | X     | X     | O     |
| 5      | Person D | W   | 78        | X     | X     | O     |
| 6      | Person E | V   | 90        | X     | X     | X     |

The above is an example sheet.
The following sheet-specific config would be necessary:
```
    "sheetName": "Access",
    "InformationRowStart": "2",
    "userIDsColumn": "C",
    "roles": [
    {
        "roleColumn": "D",
        "roleID": "0987"
    },
    {
        "roleColumn": "E",
        "roleID": "6543"
    },
    {
        "roleColumn": "F",
        "roleID": "2100"
    }
    ],
    "roleConfirmationPhrase": "X",
```
This would assign any DiscordID the roles marked with an "X" in their specific row.
Filling out the "O" is not strictly necessary, but I encourage it to avoid user-based mistakes.
