import logging
import os
def setup_logger(logpath):
    if not os.path.exists(logpath):
        os.makedirs(os.path.dirname(logpath), exist_ok=True)

        with open(logpath,'a') as elogs:
            elogs.write('_____________Logs______________')
            elogs.close()

        
    logger = logging.getLogger(logpath)  
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(logpath)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%m-%y %H:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

