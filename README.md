
# StashTabSynchronizer
## Usage

- Download the latest release [here](https://github.com/redhelling21/StashTabSynchronizer/releases/latest)
- Extract it where you want
- Download ([here](https://github.com/viktorgullmark/exilence-next/releases/latest)) and install Exilence Next
- Run the *patch_exilence_handle.cmd* script. **WARNING** This will break Exilence Next, as we use their handle to run our app. To restore it to its previous state, just run the *exilence_handle_bkp.reg* script that should have been created when you ran the first script.
- Run the exe file

## Development
  - Pull the project
  - `pip install -r requirements.txt`
  - Install the recommended VSCode extensions.
  - To build, run *build.py* or run the task "Build"

## TODO
 
- Notifs systray
- Config interval
- Make the sleep interval not run duration dependant
- Handle missing datas / failed calls
- Exception handling
