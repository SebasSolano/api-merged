import os
from PyPDF2 import PdfMerger
import shutil

# Update the merge_and_delete function in combined.py to use the 'download' directory for input and output
def merge_and_delete(uid, id_info):
    directory = f"temp_download/{uid}/"
    pdf_files = [file for file in os.listdir(directory) if file.endswith('.pdf')]

    if len(pdf_files) <= 1:
        print("There are not enough PDF files in the directory to merge.")
        return False
    else:
        pdf_files.sort(key=lambda x: int(x.split('-')[-1].split('.')[0]))
        merger = PdfMerger()

        for file in pdf_files:
            full_path = os.path.join(directory, file)
            with open(full_path, 'rb') as pdf_file:
                merger.append(pdf_file)
                pdf_file.close()

        new_output_file = os.path.join("merged/", f"merged-{id_info}.pdf")

        with open(new_output_file, 'wb') as output:
            merger.write(output)


        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"The file {directory} has been deleted.")
        else:
            print(f"The file {directory} does not exist.")
        return True