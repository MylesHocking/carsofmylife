from flask import Blueprint, render_template, request, jsonify
import db_ops

main = Blueprint('main', __name__)

@main.route('/')
def index():
    print("Index function triggered.")  # Debugging print statement
    return render_template('index.html')

@main.route('/debug_static_folder')
def debug_static_folder():
    return f"Static folder is located at: {main.static_folder}"



