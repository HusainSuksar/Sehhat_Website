"""
WSGI config for PythonAnywhere deployment of Umoor Sehhat
This file contains the WSGI callable as a module-level variable named ``application``.
"""

import os
import sys
import logging

# Configure logging for WSGI errors
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Add your project directory to the sys.path
    # IMPORTANT: Replace 'yourusername' with your actual PythonAnywhere username
    username = 'yourusername'  # CHANGE THIS!
    path = f'/home/{username}/umoor_sehhat'
    
    if path not in sys.path:
        sys.path.insert(0, path)
        logger.info(f"Added {path} to Python path")

    # Set environment variable for Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings_pythonanywhere')
    logger.info("Set Django settings module")

    # Import Django WSGI application
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    
    logger.info("Django WSGI application loaded successfully")

except Exception as e:
    logger.error(f"Error loading Django application: {e}")
    
    # Fallback WSGI application for debugging
    def application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)
        
        error_message = f"""
        <html>
        <head><title>Umoor Sehhat - Configuration Error</title></head>
        <body>
            <h1>Configuration Error</h1>
            <p>There was an error loading the Django application.</p>
            <p><strong>Error:</strong> {str(e)}</p>
            <h2>Common Solutions:</h2>
            <ol>
                <li>Check that you've replaced 'yourusername' with your actual username in this file</li>
                <li>Verify your database settings in .env file</li>
                <li>Ensure all dependencies are installed: pip3.10 install --user -r requirements_pythonanywhere.txt</li>
                <li>Run migrations: python3.10 manage.py migrate --settings=umoor_sehhat.settings_pythonanywhere</li>
                <li>Check the error logs in your PythonAnywhere dashboard</li>
            </ol>
            <p>For more help, check the PYTHONANYWHERE_SETUP.md file in your project.</p>
        </body>
        </html>
        """.encode('utf-8')
        
        return [error_message]