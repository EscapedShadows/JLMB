import logging
import argparse
from ftplib import FTP, FTP_TLS, error_perm

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

parser = argparse.ArgumentParser(description="JLMB Command Line Parser")
parser.add_argument(
    "--log-level",
    default="info",
    choices=LOG_LEVELS.keys(),
    help="Set the logging level (default: info)"
)

args = parser.parse_args()

class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.relativeCreatedSec = f"{record.relativeCreated / 1000:.3f}s"
        return super().format(record)

handler = logging.StreamHandler()
formatter = CustomFormatter("[%(relativeCreatedSec)s] %(levelname)s: %(message)s")
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(LOG_LEVELS[args.log_level])
logger.addHandler(handler)
logger.propagate = False

def upload_progress(block):
    logger.debug(f"Uploaded block size: {len(block)} bytes")

def download_progress(block):
    logger.debug(f"Downloaded block size: {len(block)} bytes")

def upload_to_ftp(addr: str, src: str, dst: str, dstp: str = "", usr: str = None, pwd: str = None, port=21, dir_create=False):
    addr = addr.split("://")[-1]
    ftp = FTP()

    try:
        ftp.connect(addr, port)
        if usr and pwd:
            ftp.login(usr, pwd)
        else:
            ftp.login()

        logger.info(f"Connected to {addr}, initial dir: {ftp.pwd()}")

        if dstp:
            try:
                ftp.cwd(dstp)
            except error_perm as e:
                logger.error(f"Error navigating to directory {dstp}: {e}")
                if dir_create:
                    logger.info(f"Directory {dstp} does not exist. Creating it.")
                    ftp.mkd(dstp)
                    ftp.cwd(dstp)

        with open(src, "rb") as f:
            ftp.storbinary(f"STOR {dst}", f, callback=upload_progress)

        logger.info(f"File uploaded to {dst}")

    except error_perm as e:
        logger.error(f"Permission error: {e}")
    except FileNotFoundError as e:
        logger.error(f"Source file not found: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        try:
            ftp.quit()
        except Exception as e:
            logger.error(f"Error during FTP quit: {e}")

def download_from_ftp(addr: str, src: str, dst: str, usr: str = None, pwd: str = None, port=21):
    addr = addr.split("://")[-1]
    ftp = FTP()

    try:
        ftp.connect(addr, port)
        if usr and pwd:
            ftp.login(usr, pwd)
        else:
            ftp.login()

        logger.info(f"Connected to {addr}, initial dir: {ftp.pwd()}")

        with open(dst, "wb") as f:
            ftp.retrbinary(f"RETR {src}", f.write, callback=download_progress)

        logger.info(f"File downloaded to {dst}")

    except error_perm as e:
        logger.error(f"Permission error: {e}")
    except FileNotFoundError as e:
        logger.error(f"Source file not found: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        try:
            ftp.quit()
        except Exception as e:
            logger.error(f"Error during FTP quit: {e}")

def upload_to_ftps(addr: str, src: str, dst: str, dstp: str = "", usr: str = None, pwd: str = None, port=21, dir_create=False):
    if "://" in addr:
        addr = addr.split("://")[-1]

    ftps = FTP_TLS()

    try:
        ftps.connect(addr, port)
        ftps.auth()
        ftps.prot_p()

        if usr and pwd:
            ftps.login(usr, pwd)
        elif not usr and not pwd:
            ftps.login()
        else:
            raise ValueError("User and password cannot be partially provided")

        logger.info(f"Connected to {addr}, initial dir: {ftps.pwd()}")

        if dstp:
            try:
                ftps.cwd(dstp)
            except error_perm as e:
                logger.error(f"Error navigating to directory {dstp}: {e}")
                if dir_create:
                    logger.info(f"Directory {dstp} does not exist. Creating it.")
                    ftps.mkd(dstp)
                    ftps.cwd(dstp)

        with open(src, "rb") as f:
            ftps.storbinary(f"STOR {dst}", f, callback=upload_progress)

        logger.info(f"File uploaded to {dst}")

    except error_perm as e:
        logger.error(f"Permission error: {e}")
    except FileNotFoundError as e:
        logger.error(f"Source file not found: {e}")
    except ValueError as e:
        logger.error(f"Invalid value error: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        try:
            ftps.quit()
        except Exception as e:
            logger.error(f"Error during FTPS quit: {e}")

def download_from_ftps(addr: str, src: str, dst: str, usr: str = None, pwd: str = None, port=21):
    if "://" in addr:
        addr = addr.split("://")[-1]

    ftps = FTP_TLS()

    try:
        ftps.connect(addr, port)
        ftps.auth()
        ftps.prot_p()

        if usr and pwd:
            ftps.login(usr, pwd)
        elif not usr and not pwd:
            ftps.login()
        else:
            raise ValueError("User and password cannot be partially provided")

        logger.info(f"Connected to {addr}, initial dir: {ftps.pwd()}")

        with open(dst, "wb") as f:
            ftps.retrbinary(f"RETR {src}", f.write, callback=download_progress)

        logger.info(f"File downloaded to {dst}")

    except error_perm as e:
        logger.error(f"Permission error: {e}")
    except FileNotFoundError as e:
        logger.error(f"Source file not found: {e}")
    except ValueError as e:
        logger.error(f"Invalid value error: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        try:
            ftps.quit()
        except Exception as e:
            logger.error(f"Error during FTPS quit: {e}")