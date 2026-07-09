import faulthandler, os
faulthandler.dump_traceback_later(50, exit=False)
os.environ["PYTHONIOENCODING"] = "utf-8"
import get_ful_report as g
g.analyze_stock("000100", parallel=True)
