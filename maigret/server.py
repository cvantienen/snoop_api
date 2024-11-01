import os
from flask import Flask, request, jsonify
import subprocess
import logging

app = Flask(__name__)

# Configure logging
LOG_DIR = '/logs'
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'maigret.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


@app.route('/maigret-basic', methods=['POST'])
def get_dossier():
    """
    Handle POST requests to generate a dossier html report for a given username.

    This endpoint expects a JSON payload with a 'username' field. It runs the
    Maigret command-line tool to generate a report for the specified username.
    The report is saved as an HTML file in the '/reports/html' directory.

    Docker Volume:
    When running the application in a Docker container, the reports are saved
    to a volume mounted at '/maigret_reports' on the host machine.

    Example Docker Run Command:
    docker run -p 5000:5000 -v /maigret_reports:/app/reports/html --name maigret-container maigret

    Example Test Command:
    curl -X POST http://localhost:5000/maigret -H "Content-Type: application/json" -d '{"username": "xxxxtesting_this_shitxxxx"}'

    Returns:
        JSON response indicating success or failure:
        - On success: {'message': 'Report generated successfully for username: <username>'}
        - On failure: {'error': 'Description of the error'}
    """
    data = request.json
    username = data.get('username')

    if not username:
        logging.warning("Username not provided in request")
        return jsonify({'error': 'Username is required'}), 400

    try:
        # Log the command being executed
        logging.debug(f"Received request for username: {username}")
        command = ['maigret', username, '--html', '--folderoutput', '/reports/html']
        logging.debug(f"Executing command: {' '.join(command)}")

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        # Log the stdout and stderr for debugging
        logging.debug(f"Maigret stdout: {result.stdout}")
        logging.debug(f"Maigret stderr: {result.stderr}")

        if result.returncode != 0:
            logging.error(f"Maigret command failed with return code {result.returncode}")
            return jsonify({'error': 'Failed to collect dossier', 'details': result.stderr}), 500

        # Ensure the report is saved with a 'report_' prefix
        html_file_path = f'/reports/html/report_{username}.html'
        logging.debug(f"HTML file path: {html_file_path}")
        
        # TODO HTML content return feature
        # try:
        #     with open(html_file_path, 'r') as file:
        #         html_content = file.read()
        # except FileNotFoundError:
        #     logging.error(f"HTML file not found: {html_file_path}")
        #     return jsonify({'error': 'HTML file not found'}), 500

        # Return a success message instead of the HTML content
        logging.info(f"Report generated successfully for username: {username}")
        return jsonify({'message': f'Report generated successfully for username: {username}'}), 200

    except Exception as e:
        logging.exception("An unexpected error occurred")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)