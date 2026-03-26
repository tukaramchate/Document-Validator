"""Shared Flask extensions — imported by blueprints and app.py.

Defining extensions here avoids circular imports when blueprints
need to reference extension objects like `limiter`.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Shared limiter instance — initialized with app in create_app()
limiter = Limiter(key_func=get_remote_address, default_limits=[])
