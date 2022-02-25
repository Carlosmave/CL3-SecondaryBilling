import os


class RunMode:
    """
    Here you need to specify all the flags that make any changes to the site or interact with the customer.

    The main goal is that any developer can run DV when all flags = False and be sure that this will not affect anything

    Here you can add:
    - sending a report
    - all data changes to the site
    - uploading files to Google disk, etc.
    """

    send_email = False
    # ...


TEMP_FOLDER = os.path.join(os.environ.get("ROBOT_ROOT", os.getcwd()), "temp")
OUTPUT_FOLDER = os.path.join(os.environ.get("ROBOT_ROOT", os.getcwd()), "output")
