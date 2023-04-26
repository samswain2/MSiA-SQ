
import logging

#log levels
logging.debug('1.This is a debug message')
logging.info('2.This is an info message')
logging.warning('3.This is a warning message')
logging.error('4.This is an error message')
logging.critical('5.This is a critical message')

#basicConfig() function can be only called once to configure the root logger
logging.basicConfig(level=logging.DEBUG)
logging.debug('6.This will get logged')

#write to a log file
logging.basicConfig(filename='example.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('7.This will get logged to a file')

#removes all logs from previous runs
logging.basicConfig(filemode='w')

#log formatting
logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s')
logging.warning('8.This is a Warning')

#log formatting
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logging.info('9.Admin logged in')

# Create a custom logger
logger = logging.getLogger(__name__) 

# Log messages
logger.warning('10. This is a warning')
logger.error('11. This is an error')

logger = logging.getLogger('example_logger')
logger.setLevel(logging.DEBUG)

#Log Handler - File Handler
exampleHandler = logging.FileHandler('example.log')
exampleHandler.setLevel(logging.DEBUG)
exampleFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
exampleHandler.setFormatter(exampleFormatter)

logger.addHandler(exampleHandler)

logger.warning('12. This is a warning')
logger.error('13. This is an error')