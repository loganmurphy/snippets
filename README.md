copy config.py.example to config.py and fill in the correct values

make sure to set your callback to http://localhost:5000/callback/google during development

manage credentials at https://console.developers.google.com/apis/credentials

to setup:
- python create_test_data.py
- python run.py
- go to http://localhost:5000/



TODO:
Build as dumb HTML forms
DONE - view groups
DONE - view user
- subscribe to group
DONE - subscripe to user

group admin UI
- create group
- add user to group

Build a search interface
- group & user autocomplete APIs

Rebuild the initial pages as API-driven?

Clean up
- break out pages into blueprints?
- get more consistent in code & html with subscribe vs follow vs member
