from loguru import logger

mdrive = r'M:\CPP-Data\Sutherland RPA\Northwell Process Automation ETM Files\Monthly Reports\Charge Correction\New vs Established\Logs'

logger.add(f"{mdrive}/{time:YYYY-MM-DD}.log",
           format="{time:YYYY-MM-DD at HH:mm:ss} | {level} - {message}",
           colorize=True, backtrace=True, diagnose=True, level='INFO', retention='90 days')
