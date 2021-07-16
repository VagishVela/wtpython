# Manually Test the Features of WTPython

* Check if it can run with `wtpython example/runs_with_error.py`
    - Check if pressing `q` and `ctrl + c` exits the app
    - Check if pressing `left`, `right`, `k`, and `j` change the question
    - Check if pressing `s` toggles the sidebar
    - Check if pressing `t` toggles the traceback
    - Check if pressing `d` opens the current question in the browser
    - Check if pressing `f` opens google
    - Check if pressing `i` opens the issue tracker
* Check if no display mode works with `wtpython -n example/runs_with_error.py`
* Check if copy mode works with `wtpython -c example/runs_with_error.py`
* Check if copy and no display mode works with`wtpython -c -n example/runs_with_error.py`
