# PythonAutoAttendance (Rhul Auto Attendance)

Lectures are pointless, but they annoy me if my attendance is low, so this bot goes brrr and looks like im a very good student.

## How to run this?

1. Create an environment with the following:

    ```
    EMAIL="UNI_EMAIL"
    PASS="UNI_PASS"
    PRIVKEY="YOUR_TOKEN_KEY"
    ```

2. Install Poetry, the package manager for python
3. Install the required libraries: Selenium and pyotp
4. Make sure that Firefox is installed in your system

5. Once the environment variables are set, run the script using the command "poetry run python src/PythonAuto.py"

6. Troubleshoot: If you have any issues running the script, please make sure that you have the latest version of Firefox and Selenium installed on your machine.

7. Note: Dont bother with lectures. 


To formally run this script, use a server like digital ocean and run cronejobs, per house or something. 

To run this script on a personal computer, you can set up a crontab to run the script every hour past the hour, from 9am to 6pm. An example command for this would be:

```
0 9-18 * * * poetry run python /path/to/src/PythonAuto.py
```

This command will run the script every hour from 9am to 6pm, every day.

Using a server like DigitalOcean can be useful for running the script continuously, even when your personal computer is turned off. However, if you are not familiar with setting up and managing a server, it may be best to stick to running the script on your personal computer with a crontab. It is also important to note that using this script may violate your University or college's policies, so use it at your own risk. [But I assume you dont care so meh what ever]. 
