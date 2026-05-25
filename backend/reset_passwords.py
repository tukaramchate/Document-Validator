#!/usr/bin/env python3
"""Script to reset and set proper passwords for all accounts."""

from app import create_app
from models import db
from models.user import User

def reset_all_passwords():
    """Reset passwords for all admins, institutions, and users."""
    app = create_app()
    
    with app.app_context():
        print("🔐 Resetting passwords for all accounts...\n")
        
        # Reset admin passwords
        admins = User.query.filter_by(role='admin').all()
        print("👨‍💼 ADMINS:")
        for i, admin in enumerate(admins, 1):
            password = f'admin{i}@123456'
            admin.set_password(password)
            db.session.add(admin)
            print(f"  ✓ {admin.email} → Password: {password}")
        
        db.session.commit()
        print()
        
        # Reset institution passwords
        institutions = User.query.filter_by(role='institution').all()
        print("🏢 INSTITUTIONS:")
        for i, inst in enumerate(institutions, 1):
            # Extract number from email if possible
            if 'institution' in inst.email.lower():
                num = str(i)
            else:
                num = '1'
            password = f'institution{num}@123456'
            inst.set_password(password)
            db.session.add(inst)
            print(f"  ✓ {inst.email} → Password: {password}")
        
        db.session.commit()
        print()
        
        # Reset user passwords
        users = User.query.filter_by(role='user').all()
        print("👥 USERS:")
        for i, user in enumerate(users, 1):
            password = f'user{i}@123456'
            user.set_password(password)
            db.session.add(user)
            print(f"  ✓ {user.email} → Password: {password}")
        
        db.session.commit()
        print()
        
        # Generate new credentials file
        content = []
        content.append("=" * 100)
        content.append("📋 DOCUMENT VALIDATOR - UPDATED CREDENTIALS REFERENCE")
        content.append("=" * 100)
        content.append("")
        content.append(f"Generated: 2026-04-08")
        content.append(f"Total Accounts: {len(admins) + len(institutions) + len(users)}")
        content.append("")
        
        # ADMINS SECTION
        content.append("=" * 100)
        content.append("👨‍💼 ADMINS ({})".format(len(admins)))
        content.append("=" * 100)
        content.append("")
        
        for i, admin in enumerate(admins, 1):
            content.append(f"Admin #{i}")
            content.append(f"  ID:       {admin.id}")
            content.append(f"  Email:    {admin.email}")
            content.append(f"  Password: admin{i}@123456")
            content.append(f"  Name:     {admin.name}")
            content.append("")
        
        # INSTITUTIONS SECTION
        content.append("=" * 100)
        content.append("🏢 INSTITUTIONS ({})".format(len(institutions)))
        content.append("=" * 100)
        content.append("")
        
        for i, inst in enumerate(institutions, 1):
            content.append(f"Institution #{i}")
            content.append(f"  ID:       {inst.id}")
            content.append(f"  Email:    {inst.email}")
            content.append(f"  Password: institution{i}@123456")
            content.append(f"  Name:     {inst.name}")
            content.append(f"  Records:  {len(inst.records)}")
            content.append("")
        
        # USERS SECTION
        content.append("=" * 100)
        content.append("👥 USERS ({})".format(len(users)))
        content.append("=" * 100)
        content.append("")
        
        for i, user in enumerate(users, 1):
            content.append(f"User #{i}")
            content.append(f"  ID:       {user.id}")
            content.append(f"  Email:    {user.email}")
            content.append(f"  Password: user{i}@123456")
            content.append(f"  Name:     {user.name}")
            content.append(f"  Paid:     {'Yes' if user.is_paid else 'No'}")
            content.append("")
        
        # API LOGIN INFO
        content.append("=" * 100)
        content.append("🔐 API LOGIN INFORMATION")
        content.append("=" * 100)
        content.append("")
        content.append("ENDPOINT: POST http://localhost:5000/api/auth/login")
        content.append("CONTENT-TYPE: application/json")
        content.append("")
        content.append("REQUEST FORMAT:")
        content.append('{')
        content.append('  "email": "your-email@example.com",')
        content.append('  "password": "your-password"')
        content.append('}')
        content.append("")
        
        # CURL EXAMPLES
        content.append("=" * 100)
        content.append("📝 CURL EXAMPLES")
        content.append("=" * 100)
        content.append("")
        
        if admins:
            admin = admins[0]
            content.append(f"1. Login as Admin ({admin.email}):")
            content.append("")
            content.append(f'  curl -X POST http://localhost:5000/api/auth/login \\')
            content.append(f'    -H "Content-Type: application/json" \\')
            content.append(f'    -d \'{{"email": "{admin.email}", "password": "admin1@123456"}}\'')
            content.append("")
        
        if institutions:
            inst = institutions[0]
            content.append(f"2. Login as Institution ({inst.email}):")
            content.append("")
            content.append(f'  curl -X POST http://localhost:5000/api/auth/login \\')
            content.append(f'    -H "Content-Type: application/json" \\')
            content.append(f'    -d \'{{"email": "{inst.email}", "password": "institution1@123456"}}\'')
            content.append("")
        
        if users:
            user = users[0]
            content.append(f"3. Login as User ({user.email}):")
            content.append("")
            content.append(f'  curl -X POST http://localhost:5000/api/auth/login \\')
            content.append(f'    -H "Content-Type: application/json" \\')
            content.append(f'    -d \'{{"email": "{user.email}", "password": "user1@123456"}}\'')
            content.append("")
        
        content.append("=" * 100)
        
        # Write updated credentials file
        with open('CREDENTIALS.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        print("=" * 100)
        print("✅ ALL PASSWORDS RESET SUCCESSFULLY")
        print("=" * 100)
        print("\nUpdated credentials saved to: CREDENTIALS.txt")

if __name__ == '__main__':
    reset_all_passwords()
