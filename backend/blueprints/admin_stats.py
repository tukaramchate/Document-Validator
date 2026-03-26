import logging
from flask import Blueprint, request
from extensions import limiter
from middleware.auth_middleware import token_required, admin_required
from models import db
from models.user import User
from models.document import Document
from models.result import Result
from models.institution_record import InstitutionRecord
from utils.response_utils import success_response, error_response

admin_stats_bp = Blueprint('admin_stats', __name__)
logger = logging.getLogger(__name__)

@admin_stats_bp.route('/stats', methods=['GET'])
@token_required
@admin_required
def get_system_stats(current_user):
    """Get system-wide statistics for the admin dashboard."""
    try:
        total_users = User.query.filter_by(role='user').count()
        total_institutions = User.query.filter_by(role='institution').count()
        total_documents = Document.query.count()
        total_validations = Result.query.count()
        
        # Verdict distribution
        authentic = Result.query.filter_by(verdict='AUTHENTIC').count()
        suspicious = Result.query.filter_by(verdict='SUSPICIOUS').count()
        fake = Result.query.filter_by(verdict='FAKE').count()
        
        return success_response(
            data={
                'users': total_users,
                'institutions': total_institutions,
                'documents': total_documents,
                'validations': total_validations,
                'distribution': {
                    'authentic': authentic,
                    'suspicious': suspicious,
                    'fake': fake
                }
            },
            message='System stats retrieved successfully'
        )
    except Exception as e:
        logger.error(f'Admin stats error: {e}', exc_info=True)
        return error_response('Failed to retrieve system stats', 'INTERNAL_ERROR', 500)

@admin_stats_bp.route('/activity', methods=['GET'])
@token_required
@admin_required
def get_recent_activity(current_user):
    """Get recent system-wide activity."""
    try:
        from sqlalchemy.orm import joinedload
        recent_results = Result.query \
            .options(joinedload(Result.document)) \
            .order_by(Result.validated_at.desc()) \
            .limit(10) \
            .all()
            
        activity = []
        for res in recent_results:
            activity.append({
                'id': res.id,
                'document_id': res.document_id,
                'filename': res.document.filename,
                'verdict': res.verdict,
                'score': res.final_score,
                'validated_at': res.validated_at.isoformat() if res.validated_at else None,
                'user_id': res.document.user_id
            })
            
        return success_response(data={'activity': activity})
    except Exception as e:
        logger.error(f'Admin activity error: {e}', exc_info=True)
        return error_response('Failed to retrieve recent activity', 'INTERNAL_ERROR', 500)


@admin_stats_bp.route('/institutions/pending', methods=['GET'])
@token_required
@admin_required
def list_pending_institutions(current_user):
    """List all institution accounts awaiting admin approval."""
    try:
        pending = User.query.filter_by(role='institution', is_approved=False).all()
        return success_response(data={
            'institutions': [u.to_dict() for u in pending]
        })
    except Exception as e:
        logger.error(f'Pending institutions error: {e}', exc_info=True)
        return error_response('Failed to retrieve pending institutions', 'INTERNAL_ERROR', 500)


@admin_stats_bp.route('/institutions/<int:user_id>/approve', methods=['PUT'])
@token_required
@admin_required
def approve_institution(current_user, user_id):
    """Approve or reject an institution registration."""
    try:
        user = db.session.get(User, user_id)
        if not user or user.role != 'institution':
            return error_response('Institution not found', 'NOT_FOUND', 404)

        data = request.get_json() or {}
        approved = data.get('approved', True)

        user.is_approved = approved
        db.session.commit()

        action = 'approved' if approved else 'rejected'
        logger.info(f'Institution {user.email} {action} by admin {current_user.email}')
        return success_response(
            data={'user': user.to_dict()},
            message=f'Institution {action} successfully'
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f'Approve institution error: {e}', exc_info=True)
        return error_response('Failed to update institution status', 'INTERNAL_ERROR', 500)
