from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from firebase_admin import storage
from merged import merge_and_delete
from orderFile import orderFile
import os
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("./erp-mtrtest-18f0f398893a.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'erp-mtrtest.appspot.com'
})



app = FastAPI()

def validate_and_create_folders():
    folders = ['temp_download', 'merged']
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)


@app.get("/api/")
def index():
    return "API ON"


'''
    Con este link @/api/merged/{uid}-{id_con}-{id_info}
    Se pasa uid(ID del usuario), id_con(ID del contrato),
    id_info(ID de informes)
'''
@app.get("/api/merged/{uid}-{id_con}-{id_info}")
async def download_file(uid: str,id_con: str,id_info: str ):
    if not uid:
        raise HTTPException(status_code=400, detail="UID no válido")

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
        
        if(merge_and_delete(uid, id_info)):
            pdf_file_path = f"merged/merged-{id_info}.pdf"
            pdf_content = open(pdf_file_path, 'rb').read()
            response = Response(content=pdf_content, media_type='application/pdf')
            response.headers["Content-Disposition"] = f'inline; filename="merged-{id_info}.pdf"'
            return response
        else:
            return {"error": f"There was an error with the UID identification: {uid}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



'''
    Con este link @/api/merged/deleted/{action}
    Se pasa action(0 or 1) que se identifican como
    False or True
'''
@app.get("/api/merged/deleted/{action}")
def deleting_folder(action: int):
    if action == 1:
        directory = f"merged/"
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

    
