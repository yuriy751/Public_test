from program.GUI import gui
from program.state import STATE
from program.project_io.save_project import cleanup_project_folders

gui()
if STATE.project.fs.root is not None:
    try:
        cleanup_project_folders(STATE.project.fs)
    except Exception as e:
        print(e)
        pass

