# Template for simple robot task/main file?
from ta_bitwarden_cli.ta_bitwarden_cli import Bitwarden

from config import TEMP_FOLDER, OUTPUT_FOLDER, CREDENTIALS_NAME
from libraries.common import log_message, print_version, create_or_clean_dir, get_bitwarden_credentials, get_input
from libraries.process import Process


def main():
    create_or_clean_dir(TEMP_FOLDER)
    create_or_clean_dir(OUTPUT_FOLDER)

    # Get credentials
    bitwarden_credentials = get_bitwarden_credentials()
    bw = Bitwarden(bitwarden_credentials)
    credentials = bw.get_credentials(CREDENTIALS_NAME)

    # Get inputs
    input_date, input_text, executor_email = get_input()
    log_message(f"Executed by: {executor_email}")
    log_message(f'Received input data: "{input_date}"; "{input_text}"')

    process = Process(credentials)
    try:
        process.start()
    except Exception as ex:
        log_message(f"An unexpected error was encountered during the process. {str(ex)}")
        raise ex
    finally:
        process.finish()


if __name__ == "__main__":
    digital_worker_name = "Digital-Worker-Template"
    log_message(f'Start "{digital_worker_name}"')
    print_version()

    main()

    log_message(f'End "{digital_worker_name}"')
