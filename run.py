# start it all off = WOOHOO!
import sys
import os
#print("Current Working Directory:", os.getcwd())
#print("DebugPython PATH:", sys.path)

from app import create_app
from app import db

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
