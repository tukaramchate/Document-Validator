#!/usr/bin/env python3
"""Script to add test data: 10 institutions, 10 users, and 10 document validations."""

import os
from datetime import datetime, timedelta, timezone
from app import create_app
from models import db
from models.user import User
from models.document import Document
from models.institution_record import InstitutionRecord
from models.validation_job import ValidationJob

def add_test_data():
    """Add 10 institutions, 10 users, and 10 document validations."""
    app = create_app()
    
    with app.app_context():
        print("🔄 Adding test data...\n")
        
        # Add 10 institutions
        print("📦 Creating 10 institutions...")
        institutions = []
        for i in range(1, 11):
            inst_email = f'institution{i}@example.com'
            existing = User.query.filter_by(email=inst_email).first()
            
            if existing:
                print(f"   ⊘ Institution {i} already exists: {inst_email}")
                institutions.append(existing)
            else:
                institution = User(
                    email=inst_email,
                    name=f'Institution {i}',
                    role='institution',
                    is_approved=True
                )
                institution.set_password(f'inst_password_{i}')
                db.session.add(institution)
                institutions.append(institution)
                print(f"   ✓ Created Institution {i}: {inst_email}")
        
        db.session.commit()
        print(f"✓ Total institutions: {len(institutions)}\n")
        
        # Add 10 regular users
        print("👥 Creating 10 users...")
        users = []
        for i in range(1, 11):
            user_email = f'user{i}@example.com'
            existing = User.query.filter_by(email=user_email).first()
            
            if existing:
                print(f"   ⊘ User {i} already exists: {user_email}")
                users.append(existing)
            else:
                user = User(
                    email=user_email,
                    name=f'User {i}',
                    role='user',
                    is_approved=True,
                    is_paid=(i % 2 == 0)  # Every other user is paid
                )
                user.set_password(f'user_password_{i}')
                db.session.add(user)
                users.append(user)
                print(f"   ✓ Created User {i}: {user_email}")
        
        db.session.commit()
        print(f"✓ Total users: {len(users)}\n")
        
        # Add institution records
        print("📊 Creating institution records...")
        for i, institution in enumerate(institutions):
            record_exists = InstitutionRecord.query.filter_by(
                institution_id=institution.id,
                id_number=f'REC_{institution.id}_001'
            ).first()
            
            if not record_exists:
                for j in range(1, 6):  # 5 records per institution
                    record = InstitutionRecord(
                        institution_id=institution.id,
                        name=f'Record {j} for {institution.name}',
                        id_number=f'REC_{institution.id}_{j:03d}',
                        metadata_fields={
                            'status': 'active',
                            'batch': j,
                            'category': 'general'
                        }
                    )
                    db.session.add(record)
                print(f"   ✓ Created 5 records for Institution {i+1}")
        
        db.session.commit()
        print("✓ Institution records created\n")
        
        # Add 10 documents for various users
        print("📄 Creating 10 documents...")
        documents = []
        file_types = ['pdf', 'jpg', 'png', 'jpeg']
        
        for i in range(1, 11):
            user = users[i % len(users)]  # Cycle through users
            doc_exists = Document.query.filter_by(
                filename=f'test_document_{i}.{file_types[i % len(file_types)]}'
            ).first()
            
            if not doc_exists:
                doc = Document(
                    filename=f'test_document_{i}.{file_types[i % len(file_types)]}',
                    stored_name=f'stored_doc_{i}_{user.id}.bin',
                    file_type=file_types[i % len(file_types)],
                    file_size=1024 * (i + 1),  # Variable sizes
                    user_id=user.id
                )
                db.session.add(doc)
                documents.append(doc)
                print(f"   ✓ Created Document {i} for {user.email}")
        
        db.session.commit()
        print(f"✓ Total documents: {len(documents)}\n")
        
        # Add 10 validation jobs
        print("⚙️  Creating 10 validation jobs...")
        validation_statuses = ['QUEUED', 'PROCESSING', 'COMPLETED', 'FAILED']
        validation_jobs = []
        
        for i, doc in enumerate(documents):
            user = users[i % len(users)]
            status = validation_statuses[i % len(validation_statuses)]
            
            job_exists = ValidationJob.query.filter_by(
                document_id=doc.id,
                user_id=user.id
            ).first()
            
            if not job_exists:
                now = datetime.now(timezone.utc).replace(tzinfo=None)
                job = ValidationJob(
                    document_id=doc.id,
                    user_id=user.id,
                    status=status,
                    created_at=now - timedelta(hours=i),
                    started_at=now - timedelta(hours=i-1) if status != 'QUEUED' else None,
                    finished_at=now if status in ['COMPLETED', 'FAILED'] else None,
                    error_message='Test error message' if status == 'FAILED' else None
                )
                db.session.add(job)
                validation_jobs.append(job)
                print(f"   ✓ Created Validation Job {i+1} (Status: {status}) for Document {i+1}")
        
        db.session.commit()
        print(f"✓ Total validation jobs: {len(validation_jobs)}\n")
        
        # Summary
        print("=" * 50)
        print("📊 DATABASE SUMMARY")
        print("=" * 50)
        total_institutions = User.query.filter_by(role='institution').count()
        total_users = User.query.filter_by(role='user').count()
        total_admins = User.query.filter_by(role='admin').count()
        total_documents = Document.query.count()
        total_validations = ValidationJob.query.count()
        total_records = InstitutionRecord.query.count()
        
        print(f"Admins:               {total_admins}")
        print(f"Institutions:         {total_institutions}")
        print(f"Users:                {total_users}")
        print(f"Institution Records:  {total_records}")
        print(f"Documents:            {total_documents}")
        print(f"Validation Jobs:      {total_validations}")
        print("=" * 50)

if __name__ == '__main__':
    add_test_data()
