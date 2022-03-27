import os
import sys

class RunMode:
    """
    Here you need to specify all the flags that make any changes to the site or interact with the customer.

    The main goal is that any developer can run DV when all flags = False and be sure that this will not affect anything.

    Here you can add:
    - sending a report
    - all data changes to the site
    - uploading files to Google disk, etc.
    """
    #Add flags to enable/disable/simulate steps of the process.
    RUN_MODE = "development" if (len(sys.argv) > 1 and sys.argv[1].lower() == "local") or (os.environ.get("RUN_MODE", None) == "development") else "production"
    if RUN_MODE != "development":
        send_email = True
        upload_files = True
        close_tasks = True
    else:
        send_email = False
        upload_files = False
        close_tasks = False

TEMP_FOLDER = os.path.join(os.environ.get("ROBOT_ROOT", os.getcwd()), 'temp')
OUTPUT_FOLDER = os.path.join(os.environ.get("ROBOT_ROOT", os.getcwd()), 'output')

tabs_dict = {}
