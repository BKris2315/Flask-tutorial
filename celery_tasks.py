from celery import Celery
from flask import Flask
import os
from datetime import datetime

app = Flask(__name__)
app.config.from_object('celeryconfig')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task
def cleanup_task():
    uploads_folder = os.path.join(app.root_path, 'static', 'uploads')
    for subfolder in os.listdir(uploads_folder):
        subfolder_path = os.path.join(uploads_folder, subfolder)
        try:
            # Only delete subfolders created more than 30 minutes ago
            if (datetime.now() - datetime.fromtimestamp(os.path.getctime(subfolder_path))).total_seconds() > 1800:
                os.rmdir(subfolder_path)
                print(f"Subfolder {subfolder_path} deleted successfully.")
        except Exception as e:
            print(f"Error deleting subfolder {subfolder_path}: {e}")
