# start it all off = WOOHOO!
import sys
print("DebugPython PATH:", sys.path)

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
