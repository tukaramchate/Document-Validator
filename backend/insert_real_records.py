import os
import requests
import mimetypes
from app import create_app
from models import db
from models.institution_record import InstitutionRecord
from models.user import User

app = create_app()

REAL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "AI Model", "data", "real"))
API_URL = "http://localhost:8001/api/ocr/extract/"

def process_and_insert():
    with app.app_context():
        # Find the first institution user or create a default one
        institution = User.query.filter_by(role='institution').first()
        if not institution:
            institution = User(
                email='demo_institution@example.com',
                name='Demo Institution',
                role='institution',
                is_approved=True
            )
            institution.set_password('password123')
            db.session.add(institution)
            db.session.commit()
            print("Created demo institution profile.")

        count = 0
        limit = 10 # Process only 10 files to avoid Gemini API free-tier rate limits (15 RPM)
        
        for filename in os.listdir(REAL_DIR):
            if count >= limit:
                break
                
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                file_path = os.path.join(REAL_DIR, filename)
                print(f"Processing {filename}...")
                
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'
                
                try:
                    with open(file_path, 'rb') as f:
                        resp = requests.post(API_URL, files={'file': (filename, f, mime_type)})
                    
                    if resp.status_code == 200:
                        data = resp.json().get('fields', {})
                        name = data.get('name')
                        id_number = data.get('id_number') or data.get('certificate_id')
                        
                        if name and id_number and str(id_number).lower() != 'not found':
                            if not InstitutionRecord.query.filter_by(id_number=id_number).first():
                                record = InstitutionRecord(
                                    institution_id=institution.id,
                                    name=name,
                                    id_number=id_number,
                                    metadata_fields={
                                        'course': data.get('course'),
                                        'branch': data.get('branch'),
                                        'year': data.get('year'),
                                        'cgpa': data.get('cgpa'),
                                        'institution': data.get('institution'),
                                        'source_file': filename
                                    }
                                )
                                db.session.add(record)
                                db.session.commit()
                                count += 1
                                print(f"  [+] Inserted record for '{name}' with ID '{id_number}'")
                            else:
                                print(f"  [-] Record {id_number} already exists.")
                        else:
                            print(f"  [!] Skipping {filename}: OCR could not find a valid name or id_number.")
                    else:
                        print(f"  [x] AI API failed for {filename}: {resp.text}")
                except Exception as e:
                    print(f"  [ERROR] Processing {filename}: {e}")
                    
        print(f"\nSuccessfully inserted {count} ground-truth records into the database.")

if __name__ == '__main__':
    process_and_insert()
