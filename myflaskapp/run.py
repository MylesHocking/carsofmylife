# start it all off = WOOHOO!
import sys
import os
print("Current Working Directory:", os.getcwd())
print("DebugPython PATH:", sys.path)

from app.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
