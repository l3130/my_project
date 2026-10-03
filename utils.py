# utils.
from datetime import datetime
import csv
import base64
import os
import sys
from pathlib import Path
import matplotlib
matplotlib.use('TkAgg')

APP_NAME = "FinanceTracker"
PLOT_MODE = "save" if "--save-plots" in sys.argv else "show"

TK_ICON_PNG = (
	"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAJUlEQVR4nGOUL9/"
	"yn4ECwESJ5lEDIICJgULANGoAw2gYMFAeBgCHAgJprYo/ugAAAABJRU5ErkJggg=="
)



def ensure_matplotlib_tk_icons():
	"""Provide Tk window icons missing from recent matplotlib distributions."""
	image_dir = Path(matplotlib.get_data_path()) / "images"
	filenames = (
		"matplotlib.png",
		"matplotlib_large.png",
		"home.png",
		"back.png",
		"forward.png",
		"move.png",
		"zoom_to_rect.png",
		"subplots.png",
		"filesave.png",
	)
	for filename in filenames:
		icon_path = image_dir / filename
		if icon_path.exists():
			continue
		try:
			image_dir.mkdir(parents=True, exist_ok=True)
			icon_path.write_bytes(base64.b64decode(TK_ICON_PNG))
		except OSError:
			pass


def get_project_root():
	cwd = Path(os.getcwd())
	if (cwd / "data").exists() or (cwd / "main.py").exists():
		return cwd

	if getattr(sys, "frozen", False):
		executable = getattr(sys, "executable", None)
		if executable:
			exe_path = Path(executable)
			for base in [exe_path.parent, exe_path.parent.parent]:
				if (base / "data").exists() or (base / "main.py").exists():
					return base

	module_file = getattr(sys.modules[__name__], "__file__", None)
	if module_file:
		module_path = Path(module_file)
		for base in [module_path.parent, module_path.parent.parent]:
			if (base / "data").exists() or (base / "main.py").exists():
				return base

	executable = getattr(sys, "executable", None)
	if executable:
		exe_dir = Path(executable).parent
		if (exe_dir / "data").exists() or (exe_dir / "main.py").exists():
			return exe_dir

	return cwd


def get_writable_data_dir():
	"""Return the project data root for CSV and plot files."""
	return get_project_root()


def resolve_data_path(relative_path, writable=False):
	"""Resolve a data file path for source runs and packaged executables."""
	relative_path = Path(relative_path)
	project_root = get_project_root()

	if writable:
		return project_root / relative_path

	if getattr(sys, "frozen", False):
		meipass = getattr(sys, "_MEIPASS", None)
		if meipass:
			candidate = Path(meipass) / relative_path
			if candidate.exists():
				return candidate

	candidate = project_root / relative_path
	if candidate.exists():
		return candidate

	cwd_candidate = Path.cwd() / relative_path
	if cwd_candidate.exists():
		return cwd_candidate

	return candidate


def show_or_save_plot(plt, filename):
	"""Display a plot in a popup window, saving a PNG only when GUI display is unavailable."""
	out_path = resolve_data_path(f"data/{filename}", writable=True)
	out_path.parent.mkdir(parents=True, exist_ok=True)

	if PLOT_MODE != "save":
		try:
			ensure_matplotlib_tk_icons()
			print("✅ Chart window opened. Close it to return to the menu.")
			plt.show()
			return
		except Exception as error:
			print(f"Could not open chart window: {error}")

	try:
		plt.savefig(out_path, dpi=100, bbox_inches='tight')
		print(f"✅ Plot saved to: {out_path}")
	except Exception as e:
		print(f"❌ Failed to save plot: {e}")



def normalize_date(date_input: str) -> str:
    """
    Convert various date formats to YYYY-MM-DD.
    
    Accepts:
    - 2026-09-29 (already correct)
    - 20260929 (no hyphens)
    - 2026/09/29 (slashes)
    - 09-29-2026 (US format)
    - 09/29/2026 (US format)
    
    Returns:
    - 2026-09-29 (normalized)
    
    Raises ValueError if date cannot be parsed.
    """
    date_input = date_input.strip()
    
    # List of common date formats to try
    formats = [
        "%Y-%m-%d",      # 2026-09-29
        "%Y%m%d",        # 20260929
        "%Y/%m/%d",      # 2026/09/29
        "%m-%d-%Y",      # 09-29-2026
        "%m/%d/%Y",      # 09/29/2026
        "%d-%m-%Y",      # 29-09-2026
        "%d/%m/%Y",      # 29/09/2026
    ]
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_input, fmt)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # If no format matched, raise an error
    raise ValueError(
        f"Could not parse date: {date_input}\n"
        f"Supported formats: YYYY-MM-DD, YYYYMMDD, YYYY/MM/DD, MM-DD-YYYY, MM/DD/YYYY, DD-MM-YYYY, DD/MM/YYYY"
    )