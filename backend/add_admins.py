#!/usr/bin/env python3
"""Script to add admin users to the database."""

import os
from app import create_app
from models import db
from models.user import User

def add_admins():
    """Add two admin users to the database."""
    app = create_app()
    
    with app.app_context():
        # Admin 1
        admin1_email = 'admin1@example.com'
        admin1_name = 'Admin One'
        admin1_password = 'admin123456'
        
        # Admin 2
        admin2_email = 'admin2@example.com'
        admin2_name = 'Admin Two'
        admin2_password = 'admin123456'
        
        # Check if admins already exist
        admin1_exists = User.query.filter_by(email=admin1_email).first()
        admin2_exists = User.query.filter_by(email=admin2_email).first()
        
        if admin1_exists:
            print(f"✓ Admin1 already exists: {admin1_email}")
        else:
            admin1 = User(
                email=admin1_email,
                name=admin1_name,
                role='admin',
                is_approved=True
            )
            admin1.set_password(admin1_password)
            db.session.add(admin1)
            print(f"✓ Created Admin1: {admin1_email} (password: {admin1_password})")
        
        if admin2_exists:
            print(f"✓ Admin2 already exists: {admin2_email}")
        else:
            admin2 = User(
                email=admin2_email,
                name=admin2_name,
                role='admin',
                is_approved=True
            )
            admin2.set_password(admin2_password)
            db.session.add(admin2)
            print(f"✓ Created Admin2: {admin2_email} (password: {admin2_password})")
        
        db.session.commit()
        
        # Verify admins were created
        all_admins = User.query.filter_by(role='admin').all()
        print(f"\n✓ Total admins in database: {len(all_admins)}")
        for admin in all_admins:
            print(f"  - {admin.email} ({admin.name})")

if __name__ == '__main__':
    add_admins()
