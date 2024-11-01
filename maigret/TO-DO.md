**File: //wsl$/Ubuntu/home/gsacs/git-downloads/snoop_api/maigret/README.md**
```markdown
# Streaming Live Results from Maigret to Django Web Application

To stream live results from the Maigret command running in the Flask container to your Django web application, you can use server-sent events (SSE) or WebSockets. Here's a basic approach using SSE, which is simpler to implement than WebSockets for this use case:

## 1. Modify the Flask API to Stream Results

You need to modify the Flask API to execute the Maigret command and stream the output line by line to the client.

**File: //wsl$/Ubuntu/home/gsacs/git-downloads/snoop_api/maigret/server.py**
```python
import os
from flask import Flask, request, jsonify, Response
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

@app.route('/maigret', methods=['POST'])
def get_dossier():
    data = request.json
    username = data.get('username')

    if not username:
        logging.warning("Username not provided in request")
        return jsonify({'error': 'Username is required'}), 400

    def generate():
        command = ['maigret', username, '--html', '--folderoutput', '/reports/html']
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        for line in process.stdout:
            yield f"data: {line}\n\n"

        process.stdout.close()
        process.wait()

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 2. Consume SSE in Django Web Application

In your Django web application, you can use JavaScript to listen to the SSE and update the UI with the live results.

**File: /path/to/your/django/app/templates/your_template.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Maigret Results</title>
</head>
<body>
    <h1>Live Maigret Results</h1>
    <pre id="results"></pre>

    <script>
        const eventSource = new EventSource('http://localhost:5000/maigret');

        eventSource.onmessage = function(event) {
            const resultsElement = document.getElementById('results');
            resultsElement.textContent += event.data + '\n';
        };

        eventSource.onerror = function() {
            console.error('Error receiving SSE');
            eventSource.close();
        };
    </script>
</body>
</html>
```

## 3. Ensure Network Connectivity

Make sure your Django application can access the Flask API endpoint. If they are running on the same server, using `localhost` should work. If they are in separate containers, ensure they are on the same Docker network or can communicate with each other.

By following these steps, you can stream live results from the Maigret command to your Django web application using server-sent events.
```