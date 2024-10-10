import os
import requests
from flask import Flask, request, jsonify
from google.cloud import storage
from io import BytesIO
from werkzeug.datastructures import FileStorage
import mysql.connector
import logging
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

db_config = {
    'user': 'admin',               # Your MySQL username
    'password': 'nimda',           # Your MySQL password                  
    'host': '127.0.0.1',             # Your Cloud SQL instance IP or 'localhost' for local MySQL
    'database': 'inclass_database',     # Your MySQL database name
    'port':'1234'
}

# Function to get a database connection
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn
# Configure logging
# logging.basicConfig(level=logging.INFO)




# Google Cloud Storage configuration
# Hardcoded Google Cloud service account credentials
SERVICE_ACCOUNT_INFO= {
  "type": "service_account",
  "project_id": "ds-assignment-1-438201",
  "private_key_id": "08a6a00726ec15abf139535fc84f766e1fafe526",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCslYGW74t48MCO\nnI4n1YamFaEAJKVdCZnB+v+JA0RehW1YCJHs7Roaudr4SPU00K4+vgvn+Fc2wZmp\n3WJIbVxLdQFQkh2Pw8mIBZUTaRk9IE8vmVjNFCO1UQa4vmGRzWRKoYTe2FSLGtUy\nkc7UnzOIsqUXEMfH2cF9epa6oMocbBc2EQ/k1T3S0WStwzKaAwfm428/myI4Oa/D\nH61BgD1u9MldRs+Bw36qZpDtf7G/4aXzMcwzkNO9R/BMOtqtjbmJXfhIuJfiDspo\nUyhcmZrlBsDZBKF4Jjh+nySrELwN0Gm7UtXli28TJQ15pJgII/CAP73L/eSd0xtI\nKhqXs4HtAgMBAAECggEAFjnKzp1a4OBga/1NcWPWS11Ntq8BfNHXs1uXvRVmoKWe\nR1ATOufuDLMSuBbtPTgCuKHQ9rbMxIh6OZ4BIkKzOCSBXtbyZ6lXMuVFJZLLZUvb\n5s1g2khVsOwWaYRbHGPPHq1eZzSE7sUt361XbZpzEI+xIx9OGza37Gj1MGO0o6Qx\nmokhfbNFxNA9rRM4yHtQFKpuPdzfE4LxF0Ou1AFPNBCuDwnDh7aGzjP1KfdMYxaV\nxNUGFc+/HFCBKd+K51vOoiF3QPK8s4VmHt2QynGDtPZFft+Rot/ED7HSbecQY1OC\neCgfKSsgMDDrQK2v5/N51kq0a/p9hptVkmTecO7oAQKBgQC/siSu5Y+W8uuvs3WQ\nlSafrAB14K0gQIC+NmLK6RMEJnLhM3kOFmnzwMCJKmQA4hL4mF99/Dr/HzAh8Lb5\n4xOifIDxwnsQ3svifz+wY8IVdSXcVOfFzcybW/GgvuTfMLrFSp3i6UW38RKrRvof\nCwLd5R3bqSt8uRG/y9ZYZsbqQQKBgQDmeiJeXQjiFF71XMsmZVAi1OVP/UnS4ZRn\n5ePERAofpDv1RnE5+T1wkAaBJvI/O2GzEydje9RYvaZSC+c4qj43JKP1tUE9DlwX\nlX3C860c5jvQOEBFJVVHQJakNDG9AOENpBImJXRDh3e1YTobJz+XxPlHHrrSoMk8\n+usmOzI0rQKBgCpIqT7K9DlfrA09kJkrzTE7R3646HdMwxkx9ei8MK2hrYVvTSyG\nVSinQ9D9wMFRHM4pDidEE99iicNyzWmhZRtaSzcIpwy5mE+Fsg6+cnk5Nfi74cQH\n+THrvgivEt0IaqpKIzmCKxa/3lZZeaKPUzqO518kmasRR5D+7XDies4BAoGBAMfd\nIfCyvQFQqQgdcA3bzaJm/HRhMaOt+wQeV2XbmuvVgCky7P1ZJe529y0ImQo8dHzW\nH1ImD/7kd1au+9QnzcwD+isZA3nu+e15tZVZusVU4omuPg24Ujt3xyqeGIPOP1uU\n7CgoUqo8z5J6vejOIFd8eK8z9s6wn9JBxalhrCgBAoGAAYeDCyyKD2G4iI7l+Cba\nKXaZQ97X30vCk7DrcKXqdYZJT3l/ieFh+z1m8RhxkRq4YctnLl8uxlUw1xLq0Iza\nb0wovNGBhkapuN58lSbudTN3+IOS2iVYRN1ios0bvTAiZIOnISX4vKkLe1pUV5xj\noMgWjJv3PSeYsAcqFl4ExlU=\n-----END PRIVATE KEY-----\n",
  "client_email": "ds-assignment-1-438201@appspot.gserviceaccount.com",
  "client_id": "106716704080843210577",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/ds-assignment-1-438201%40appspot.gserviceaccount.com",
  "universe_domain": "googleapis.com"}




# Bucket name
BUCKET_NAME = 'class-activity_9942'

# Create a Google Cloud Storage client using hardcoded service account credentials
def get_storage_client():
    return storage.Client.from_service_account_info(SERVICE_ACCOUNT_INFO)

def upload_to_gcs(file, bucket_name, destination_blob_name):
    """Uploads a file to the Google Cloud Storage bucket."""
    storage_client = get_storage_client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file, content_type=file.mimetype)
    return blob.public_url

@app.route('/upload-url', methods=['POST'])
def upload_from_url():
    data = request.get_json()
    if not data or 'image_url' not in data:
        return jsonify({"error": "Missing 'image_url' in request body"}), 400

    image_url = data['image_url']

    try:
        # Download the image from the provided URL
        response = requests.get(image_url)
        response.raise_for_status()  # Ensure the request was successful
        file = BytesIO(response.content)

        # Convert to a FileStorage object (Flask uses this for file handling)
        filename = image_url.split("/")[-1]
        file_storage = FileStorage(file, filename=filename, content_type=response.headers['Content-Type'])

        # Upload to Google Cloud Storage
        public_url = upload_to_gcs(file_storage, BUCKET_NAME, filename)
        
        # Insert the image details into the Cloud SQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_image_query = (
            "INSERT INTO images (image_name, image_url) "
            "VALUES (%s, %s)"
        )

        cursor.execute(insert_image_query, (filename, public_url))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "File uploaded successfully", "public_url": public_url}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 400
    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)