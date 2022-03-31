from config import TEMP_FOLDER, OUTPUT_FOLDER
from libraries.common import log_message, print_version, create_or_clean_dir, get_bitwarden_data, capture_page_screenshot
from libraries.process import Process

def main():
    """
    Main function which calls all other functions.
    """
    create_or_clean_dir(TEMP_FOLDER)
    create_or_clean_dir(OUTPUT_FOLDER)

    # Get credentials
    credentials = get_bitwarden_data()


    process = Process(credentials)
    try:
        process.start()
    except Exception as e:
        capture_page_screenshot(OUTPUT_FOLDER)
        log_message("An unexpected error was encountered during the process: {}".format(str(e)))
        raise e
    finally:
        process.finish()


if __name__ == '__main__':
    digital_worker_name = "CL3 - Secondary Billing"
    log_message("Start - {}".format(digital_worker_name))
    print_version()
    main()
    log_message("End - {}".format(digital_worker_name))
