import zipfile
import sys
import signal
from zipfile import ZipFile, BadZipFile, LargeZipFile
from argparse import ArgumentParser
from colorama import Fore, Style
import math

banner = (
    Fore.GREEN
    + """
·▄▄▄ ▄· ▄▌ ▐ ▄     ·▄▄▄▄•▪   ▄▄▄·     ▄▄· ▄▄▄   ▄▄▄·  ▄▄· ▄ •▄ ▄▄▄ .▄▄▄  
▐▄▄·▐█▪██▌•█▌▐█    ▪▀·.█▌██ ▐█ ▄█    ▐█ ▌▪▀▄ █·▐█ ▀█ ▐█ ▌▪█▌▄▌▪▀▄.▀·▀▄ █·
██▪ ▐█▌▐█▪▐█▐▐▌    ▄█▀▀▀•▐█· ██▀·    ██ ▄▄▐▀▀▄ ▄█▀▀█ ██ ▄▄▐▀▀▄·▐▀▀▪▄▐▀▀▄ 
██▌. ▐█▀·.██▐█▌    █▌▪▄█▀▐█▌▐█▪·•    ▐███▌▐█•█▌▐█ ▪▐▌▐███▌▐█.█▌▐█▄▄▌▐█•█▌
▀▀▀   ▀ • ▀▀ █▪    ·▀▀▀ •▀▀▀.▀       ·▀▀▀ .▀  ▀ ▀  ▀ ·▀▀▀ ·▀  ▀ ▀▀▀ .▀  ▀
"""
    + Style.RESET_ALL
)


def signal_handler(sig, frame):
    print("Process canceled by user (Ctrl+C). Exiting...")
    sys.exit(0)


# handler untuk SIGINT
signal.signal(signal.SIGINT, signal_handler)


def wordlist_parser(path: str) -> list:
    try:
        with open(path, encoding="latin-1", mode="r") as words:
            wordlist = words.readlines()
            print("Preparing wordlist...")
            return [word.strip() for word in wordlist]
    except FileNotFoundError:
        print("Wordlist file not found!")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while reading the wordlist: {e}")
        sys.exit(1)


def check_zip(path: str) -> bool:
    try:
        with ZipFile(file=path, allowZip64=True) as zf:
            zf.extractall()
    except RuntimeError as err:
        if "password required" in str(err).lower():
            print(
                Fore.GREEN
                + "✓ ZIP file is valid and protected, running brute force"
                + Style.RESET_ALL
            )
            return True
        else:
            print(f"Runtime error occurred: {err}")
            sys.exit(1)
    except BadZipFile:
        print("ZIP file is invalid")
        sys.exit(1)
    except FileNotFoundError:
        print("ZIP file not found")
        sys.exit(1)
    except LargeZipFile:
        print("ZIP file is too large to be processed")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

    print("ZIP file is not protected")
    sys.exit(0)


def brute_force(passlist: list, zip_path: str) -> bool:
    print("Cracking...")
    with ZipFile(zip_path, allowZip64=True) as zf:
        password_counter = 0
        for pw in passlist:
            try:
                password_counter += 1
                password_in_percent = math.floor(password_counter / len(passlist) * 100)

                sys.stdout.write(
                    f"Trying {password_counter} password from {len(passlist)} passwords -> {password_in_percent}% \r"
                )
                sys.stdout.flush()

                zf.setpassword(pwd=pw.encode("utf-8"))
                if zf.testzip() is None:
                    print(
                        f"\n\n\n✓ Cracked with password: [  {Fore.GREEN+pw+Fore.RESET}  ]\n\n\n"
                    )
                    return True
            except RuntimeError:
                continue
            except Exception as e:
                continue
    print("Failed to crack the ZIP file with provided passwords.")
    return False


def main():
    print("\n\n\n")
    print(banner)
    print("Press CTRL+C to cancel")
    print("\n\n\n")

    parser = ArgumentParser()
    parser.add_argument(
        "-i", "--input", type=str, help="Input: path/to/zipfile.zip", required=True
    )
    parser.add_argument(
        "-l",
        "--passlist",
        type=str,
        help="Password list: path/to/passwordlist",
        required=True,
    )
    args = parser.parse_args()

    input_zip_path = args.input
    password_list_path = args.passlist

    if check_zip(input_zip_path):
        password_list = wordlist_parser(password_list_path)
        if brute_force(passlist=password_list, zip_path=input_zip_path):
            print("Brute force attack succeeded.")
        else:
            print("Brute force attack failed.")
            sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
