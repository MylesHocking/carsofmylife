from flask import Flask, render_template
from api import api  # Import the Blueprint

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')  # Register the Blueprint

@app.route('/')
def index():
    print("Index function triggered.")  # Debugging print statement
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
