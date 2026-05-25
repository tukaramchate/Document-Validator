#!/usr/bin/env python3
"""Script to check validation job statuses and related information."""

from app import create_app
from models import db
from models.validation_job import ValidationJob
from models.document import Document
from models.user import User

def check_validation_status():
    """Display validation job statuses with document and user info."""
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 100)
        print("📋 VALIDATION JOBS STATUS REPORT")
        print("=" * 100 + "\n")
        
        jobs = ValidationJob.query.all()
        
        if not jobs:
            print("No validation jobs found in database.")
            return
        
        # Group by status
        status_counts = {}
        for job in jobs:
            status = job.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("📊 STATUS SUMMARY:")
        for status, count in sorted(status_counts.items()):
            print(f"   {status}: {count}")
        print()
        
        # Display detailed info
        print("📄 DETAILED VALIDATION JOBS:")
        print("-" * 100)
        
        for i, job in enumerate(jobs, 1):
            document = Document.query.get(job.document_id)
            user = User.query.get(job.user_id)
            
            print(f"\n[Job {i}]")
            print(f"  ID:            {job.id}")
            print(f"  Status:        {job.status}")
            print(f"  Document:      {document.filename} (ID: {document.id})")
            print(f"  User:          {user.email} (ID: {user.id})")
            print(f"  File Type:     {document.file_type}")
            print(f"  File Size:     {document.file_size} bytes")
            print(f"  Created:       {job.created_at}")
            if job.started_at:
                print(f"  Started:       {job.started_at}")
            if job.finished_at:
                print(f"  Finished:      {job.finished_at}")
            if job.error_message:
                print(f"  Error:         {job.error_message}")
        
        print("\n" + "=" * 100)
        print(f"✓ Total validation jobs: {len(jobs)}")
        print("=" * 100 + "\n")

if __name__ == '__main__':
    check_validation_status()
