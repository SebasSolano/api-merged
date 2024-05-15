import os
import shutil

list_docs= [
    'Orden de Giro',
    'Orden de Pago',
    'Cuenta de Cobro',
    'Factura',
    'Planilla SS',
    'RP',
    'Certificación Bancaria',
    'RUT',
    'Cedula de Ciudadania',
    'Soporte Dependientes',
    'Credito de Vivienda',
    'Medicina Prepagada'
    
]

docs_dict = {doc: index + 1 for index, doc in enumerate(list_docs)}

def orderFile(uid_file):
    for file_name in os.listdir(uid_file):
        for doc in list_docs:
            if doc in file_name:
                index = docs_dict.get(doc, 0)
                new_file = f"{index}.pdf"
                os.rename(os.path.join(uid_file, file_name), os.path.join(uid_file, new_file))
                break
