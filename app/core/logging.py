import sys, logging 
from datetime import date, datetime 
from pathlib import Path

LOG_DIR = Path("logs")
RETENTION_MONTHS = 6 

FORMATTER = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S", 
)

def _clear_old_logs(folder: Path, prefix: str) -> None:
    "Auto clear old log files (older than 6 months)"
    today = date.today()
    cutoff = today.year * 12 + today.month - RETENTION_MONTHS 
    for f in folder.glob(f"{prefix}.*.log"):
        try: 
            ym = f.stem.split(".")[-1]
            year, month = ym.split("-")
            file_month = int(year) *12 + int(month)
            if file_month < cutoff:
                f.unlink()
        except (ValueError, IndexError):
            continue
        
def _make_handler(folder: Path, prefix:str, level: int) -> logging.FileHandler:
    folder.mkdir(parents=True, exist_ok=True)
    _clear_old_logs(folder, prefix)
    current_month = datetime.now().strftime("%Y-%m")
    path = folder / f"{prefix}.{current_month}.log"
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(FORMATTER)
    return handler 

def get_logger(name: str, category: str = "app") -> logging.Logger: 
    logger = logging.getLogger(f"{category}.{name}")
    logger.setLevel(logging.INFO)
    
    if logger.handlers:
        return logger 
    
    base = LOG_DIR / category 
    logger.addHandler(_make_handler(base, "info", logging.INFO))
    logger.addHandler(_make_handler(base, "error", logging.ERROR))
    logger.propagate = False 
    
    return logger 