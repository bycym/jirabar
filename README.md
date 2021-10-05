# Jirabar

## Features

* get assigned tickets
* search in the result
* dropdow and always on top
* dark theme
* get top 10 most recent ticket
* hit enter open in browser
* always update

![jirabar demo](doc/screenshot2.png?raw=true)

![jirabar search](doc/screenshot1.png?raw=true)


## Deploy

### Windows

Install missing modules
```
pip install -r Requirements.txt
```

Build Jirabar

## Install missing modules
```
pip install -r Requirements.txt
```

## Build Jirabar

run powershell az administrator
```
 C:\Python39\Scripts\pyinstaller.exe --name="Jirabar" --windowed --onefile .\main.py
```

## Config file update

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