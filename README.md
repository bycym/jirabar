# Deploy exe

## Install missing modules
```
pip install -r Requirements.txt
```

## Build Jirabar

run powershell az administrator
```
 C:\Python39\Scripts\pyinstaller.exe --name="Jirabar" --windowed --onefile .\main.py
```

# Config file update

Create an API token here for password: 
https://id.atlassian.com/manage/api-tokens

Update these informations

```json
{
    ...
    "jiraApiKey": "dummypassword",
    "jiraUser": "example@example.com",
    "server": "https://example.atlassian.net",
    ...
}
```