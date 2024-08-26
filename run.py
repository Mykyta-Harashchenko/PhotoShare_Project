import sys
import os
import uvicorn

sys.path.append(os.path.join(os.path.dirname(__file__), 'Project'))

if __name__ == "__main__":
    uvicorn.run("Project.main:app", host="0.0.0.0", port=8888, reload=True)
