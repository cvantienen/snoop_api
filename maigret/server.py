import os
from flask import Flask, request, jsonify
import subprocess
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logging.DEBUG({os.getcwd()})

@app.route('/maigret', methods=['POST'])
def get_dossier():
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    try:
        # Run Maigret with the provided username
            # Log the command being executed
        (logging.debug(f"Maigret username: {username}"  ))
        (logging.debug(f"Maigret command: {os.getcwd}"  ))
        command = ['maigret', username, '--html', '--folderoutput', 'app/maigret/reports/html']
        logging.debug(f"Executing command: {' '.join(command)}")
        result = subprocess.run(
            ['maigret', username, '--html', '--folderoutput', 'app/maigret/reports/html'],
            capture_output=True,
            text=True
        )

        # Log the stdout and stderr for debugging
        logging.debug(f"Maigret stdout: {result.stdout}")
        logging.debug(f"Maigret stderr: {result.stderr}")

        if result.returncode != 0:
            logging.error(f"Maigret command failed with return code {result.returncode}")
            return jsonify({'error': 'Failed to collect dossier', 'details': result.stderr}), 500

        # Read the generated HTML file
        html_file_path = f'app/maigret/reports/html/{username}.html'
        logging.debug(f"HTML file path: {html_file_path}")
        try:
            with open(html_file_path, 'r') as file:
                html_content = file.read()
        except FileNotFoundError:
            logging.error(f"HTML file not found: {html_file_path}")
            return jsonify({'error': 'HTML file not found'}), 500

        return html_content, 200, {'Content-Type': 'text/html'}

    except Exception as e:
        logging.exception("An unexpected error occurred")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)