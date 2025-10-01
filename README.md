## GmailBuddy

a small script which logs in to your gmail, fetches x number of emails and can process them as per certain criteria defined.

## Tech Used
- Database: Postgresql
- Language: Python
- ORM: SQLAlchemy

## File Setup

├── README.md
├── __init__.py
├── credentials.json
├── download_and_store_emails.py
├── process_emails.py
├── rules.json
├── tests
│   ├── __init__.py
│   ├── test_all.py
│   └── test_rules.json
├── token.json
└── utils
    ├── __init__.py
    ├── dbutils
    │   ├── __init__.py
    │   ├── db_funcs.py
    │   └── emailbase.py
    ├── emailutils
    │   ├── __init__.py
    │   └── gmail.py
    ├── parsing_utils.py
    └── rule_parser.py

download_and_store_emails.py: The initial script. Downloads Emails from Gmail and stores them in the local database
process_emails.py: The main processing script. Uses rules (defined in rules.json) file to process emails in the database
rules.json: The JSON file which dictates the rules to be used to process.

### Format of rules.json file

The rules.json file has a JSON structure which can be described as follows.

```
{
    "operations": [
        {
            "actions": [
                {
                   "action": "<name_of_action>", //Valid actions currently include: ["move", "mark"]
                   "value": "<value>" //Value for the action. For move: a mailbox location, for mark: [read, unread]
                },
                ..
            ],
            "rules": [
                {"field_name": "<email_header_name>", "predicate": "<condition_to_pick_records_for_processing>", "value": "<value_for_filtering>"},
                ..
            ],
            "rule_predicate": "<All/Any>"
        }
    ]
}```

<b>operations</b>: The list of operations to be performed on some data.
<b>actions</b>: Each operation has an action. For example: move (mails to another mailbox) or mark (an email as read/unread)
<b>rules</b>: Each operation has a list of rules which dictates which records the action will be performed on. 
    - Each rule has 3 properties: field_name, predicate and value
    - field_name: dictates the header of the email for filtering. For example: From, To. This tells us which field will be used to filter the records to perform the action on.
    - predicate: This states the condition itself. For string specific fields - ["contains", "does not contain"], etc.

A detailed list of supported values for each has been given below


### Supported Values

<b>action</b>: `"move", "mark"`
<b>field_name</b>: `"From", "To", "Date Sent", "Date Received", "Subject"`
<b>predicate</b>: `for strings: "contains, does not contain", for dates: "less than, greater than"`
<b>value</b>: `corresponding value: string or date`

## Project Setup

In order to initially set up this project, you would need to configure the Gmail client ID locally. This can be obtained via the Google Cloud API console. The following steps need to be performed

    1. Enable the GMail API ([Google Documentation](https://developers.google.com/workspace/gmail/api/quickstart/python#enable_the_api) for this)
    2. Create the Client ID for the desktop Application ([Google Documentation](https://developers.google.com/workspace/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application) for this)

We do NOT need to configure OAUTH Consent Screen unless we are going to be interacting via a web server based project via a hosted domain.

Once the google credentials have been obtained, download them and save them in the project directory under the name `credentials.json`.

Once done, you can proceed with the following

```
1. export PYTHONPATH="<root directory of the project>"
2. pip install -r requirements.txt
3. python3 download_and_store_emails.py
    3a: You can configure the number of emails to be downloaded by an environment variable: `NUMBER_OF_RESULTS=10 python3 download_and_store_emails.py`
4. Add Rules in the rules.json file
5. python3 process_emails.py
6. Check the database table `emails` to check the status reflected
```

### Testing

The project comes with some unit tests already written. These use test mode to run and are done on a separate table to prevent interference with the main table's data. 
To run the tests, do the following

```
1. export TEST=true
2. cd tests/
3. python3 test_all.py
```

The unit tests use a different table named `email_tests`. This is truncated after the completion of the tests to prevent occupying unnecessary space. 
The tests to be run are defined in the `tests/test_rules.json` file.


## Working

The following is a basic overview on how this program and script works
```
1. Use Gmail OAUTH API to login to your gmail account
2. Download x number of emails and insert them into your local database (x = configured via env var. Default is 10)
3. Run the processing script
4. The processing script reads rules.json file
5. It establishes a connection to the Database
6. the rule_parser.py file under utils contains a simple RuleParser class which acts as a rule parsing engine. It reads the operations, actions and rules defined in the rules.json file and constructs an SQL statement.
7. The final SQL statement has some parameters in it to make sure SQL injection attacks are prevented via escaping. These are substituted via a keyword argument feature that SQLAlchemy provides
8. The query finds the records and performs the required action. This is done via an UPDATE SQL statement.
9. The script finishes running
```

A simple diagram below should give enough context. The codebase is rather simple so context can be obtained in detail just by going through it.

## Future Scope and Improvements
