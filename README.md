# Requirements
have python 3.6+ installed (https://www.python.org/downloads/)
(make sure python.exe is added to PATH)

1. run setup.bat
2. place jsons in the jsons folder
3. run run.bat or run_list.bat for list tours

## Note
If you want to execute a dry run of the script, the results don't get submitted to the sheet, then you can either:
1. Run the following from the command line: `DEBUG=true python3 ngm-stats.py` and add ` -l` at the end if it's for NGM watched
2. Edit the `.bat` script that you're going to use and prepend `DEBUG=true ` to the second line in much the same way. Remember to remove it after you're done.