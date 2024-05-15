from flask import Flask, request, send_file, jsonify, Response
from firebase_admin import storage, initialize_app, credentials
from merged import merge_and_delete
from orderFile import orderFile
import os

app = Flask(__name__)

# Inicialización de Firebase
cred = credentials.Certificate("./erp-mtrtest-18f0f398893a.json")
initialize_app(cred, {'storageBucket': 'erp-mtrtest.appspot.com'})

def validate_and_create_folders():
    folders = ['temp_download', 'merged']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

@app.route("/api/")
def index():
    return "API ON"

@app.route("/api/merged/<string:uid>-<string:id_con>-<string:id_info>", methods=["GET"])
def download_file(uid, id_con, id_info):
    if not uid:
        return jsonify({"detail": "UID no válido"}), 400

    validate_and_create_folders()
    destination_folder = f"temp_download/{uid}/"
    os.makedirs(destination_folder, exist_ok=True)

    # Accede a Firebase Storage
    bucket = storage.bucket()

    try:
        blobs = bucket.list_blobs(prefix=f"documentos/{uid}/")
        for blob in blobs:
            file_name = os.path.basename(blob.name)
            blob.download_to_filename(os.path.join(destination_folder, file_name))

        blob = bucket.blob(f"documentos/2024/{id_con}/RP.pdf")
        blob.download_to_filename(os.path.join(destination_folder, "RP.pdf"))

        blobs = bucket.list_blobs(prefix=f"documentos/2024/{id_con}/informes/{id_info}/anexos/")
        for blob in blobs:
            file_name = os.path.basename(blob.name)
            blob.download_to_filename(os.path.join(destination_folder, file_name))
        
        orderFile(destination_folder)
        
        if merge_and_delete(uid, id_info):
            pdf_file_path = f"merged/merged-{id_info}.pdf"
            with open(pdf_file_path, 'rb') as pdf_file:
                pdf_content = pdf_file.read()
            return Response(pdf_content, mimetype='application/pdf', headers={"Content-Disposition": "inline"})
        else:
            return jsonify({"error": f"There was an error with the UID identification: {uid}"}), 500
    
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

@app.route("/api/merged/deleted/<int:action>", methods=["GET"])
def deleting_folder(action):
    if action == 1:
        directory = "merged/"
        pdf_files = [file for file in os.listdir(directory) if file.endswith('.pdf')]
        if len(pdf_files) < 1:
            print("There are not enough PDF files in the directory to merge.")
            return "There are not enough PDF files in the directory to merge."
        else:
            for file in pdf_files:
                full_path = os.path.join(directory, file)
                try:
                    os.remove(full_path)
                    print(f"Deleted file: {file}")
                except PermissionError as e:
                    print("Could not delete the file:", full_path, "Error:", e)
            if len(pdf_files) == 0:
                return "All PDFs in the merged/ folder have been deleted."
    elif action == 0:
        return "The real one, 0, doesn't do anything :)"
    else:
        return "ERROR: You can only enter 0 or 1."

if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host="127.0.0.1", port=8080, debug=True)
