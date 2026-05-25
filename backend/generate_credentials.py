#!/usr/bin/env python3
"""Script to generate a credentials reference file for all users, institutions, and admins."""

from app import create_app
from models import db
from models.user import User

def generate_credentials_file():
    """Generate a comprehensive credentials reference file."""
    app = create_app()
    
    with app.app_context():
        # Get all users by role
        admins = User.query.filter_by(role='admin').all()
        institutions = User.query.filter_by(role='institution').all()
        users = User.query.filter_by(role='user').all()
        
        # Create credentials content
        content = []
        content.append("=" * 100)
        content.append("📋 DOCUMENT VALIDATOR - CREDENTIALS REFERENCE")
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
        
        for admin in admins:
            content.append(f"Admin ID: {admin.id}")
            content.append(f"  Email:    {admin.email}")
            content.append(f"  Name:     {admin.name}")
            content.append(f"  Role:     {admin.role}")
            content.append(f"  Status:   {'Approved' if admin.is_approved else 'Pending'}")
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
            content.append(f"  Password: inst_password_{i}")
            content.append(f"  Name:     {inst.name}")
            content.append(f"  Role:     {inst.role}")
            content.append(f"  Status:   {'Approved' if inst.is_approved else 'Pending'}")
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
            content.append(f"  Password: user_password_{i}")
            content.append(f"  Name:     {user.name}")
            content.append(f"  Role:     {user.role}")
            content.append(f"  Status:   {'Approved' if user.is_approved else 'Pending'}")
            content.append(f"  Paid:     {'Yes' if user.is_paid else 'No'}")
            content.append(f"  Documents: {len(user.documents)}")
            content.append("")
        
        # QUICK LOGIN COMMANDS SECTION
        content.append("=" * 100)
        content.append("🔐 QUICK REFERENCE - LOGIN CREDENTIALS")
        content.append("=" * 100)
        content.append("")
        
        # API endpoint info
        content.append("API ENDPOINT:")
        content.append("  POST http://localhost:5000/api/auth/login")
        content.append("  Content-Type: application/json")
        content.append("")
        content.append("REQUEST FORMAT:")
        content.append('  { "email": "user@example.com", "password": "password" }')
        content.append("")
        
        # Example curl commands
        content.append("EXAMPLE CURL COMMANDS:")
        content.append("")
        
        if admins:
            admin = admins[0]
            content.append("Login as Admin:")
            content.append(f'  curl -X POST http://localhost:5000/api/auth/login \\')
            content.append(f'    -H "Content-Type: application/json" \\')
            content.append(f'    -d \'{{"email": "{admin.email}", "password": "dev-secret-key-change-in-production"}}\'')
            content.append("")
        
        if institutions:
            inst = institutions[0]
            idx = 1
            content.append("Login as Institution:")
            content.append(f'  curl -X POST http://localhost:5000/api/auth/login \\')
            content.append(f'    -H "Content-Type: application/json" \\')
            content.append(f'    -d \'{{"email": "{inst.email}", "password": "inst_password_{idx}"}}\'')
            content.append("")
        
        if users:
            user = users[0]
            idx = 1
            content.append("Login as User:")
            content.append(f'  curl -X POST http://localhost:5000/api/auth/login \\')
            content.append(f'    -H "Content-Type: application/json" \\')
            content.append(f'    -d \'{{"email": "{user.email}", "password": "user_password_{idx}"}}\'')
            content.append("")
        
        # Save to file
        content.append("=" * 100)
        content.append("✓ Credentials file generated successfully")
        content.append("=" * 100)
        
        # Write to credentials file
        credentials_path = 'CREDENTIALS.txt'
        with open(credentials_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        print('\n'.join(content))
        print(f"\n✓ Credentials saved to: {credentials_path}")

if __name__ == '__main__':
    generate_credentials_file()
