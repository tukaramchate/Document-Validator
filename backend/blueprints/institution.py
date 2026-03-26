import logging
from flask import Blueprint, request
from middleware.auth_middleware import token_required, institution_required
from models import db
from models.institution_record import InstitutionRecord
from utils.response_utils import success_response, error_response, paginated_response

institution_bp = Blueprint('institution', __name__)
logger = logging.getLogger(__name__)


@institution_bp.route('/records', methods=['POST'])
@token_required
@institution_required
def add_record(current_user):
    """Add a new verification record (e.g. Student/Employee)."""
    data = request.get_json()
    if not data:
        return error_response('Request body is required', 'BAD_REQUEST', 400)

    name = data.get('name')
    id_number = data.get('id_number')
    metadata_fields = data.get('metadata', {})

    if not name or not id_number:
        return error_response('Name and ID number are required', 'VALIDATION_ERROR', 400)

    try:
        record = InstitutionRecord(
            institution_id=current_user.id,
            name=name,
            id_number=id_number,
            metadata_fields=metadata_fields
        )
        db.session.add(record)
        db.session.commit()
        return success_response(message='Record added successfully', data={'record': record.to_dict()}, status_code=201)
    except Exception as e:
        db.session.rollback()
        logger.error(f'Add record error: {e}', exc_info=True)
        return error_response('Failed to add record', 'INTERNAL_ERROR', 500)


@institution_bp.route('/records/bulk', methods=['POST'])
@token_required
@institution_required
def bulk_add_records(current_user):
    """Bulk add verification records."""
    data = request.get_json()
    if not data:
        return error_response('Request body is required', 'BAD_REQUEST', 400)

    records_data = data.get('records', [])

    if not records_data:
        return error_response('No records provided', 'VALIDATION_ERROR', 400)

    MAX_BULK_RECORDS = 500
    if len(records_data) > MAX_BULK_RECORDS:
        return error_response(
            f'Too many records. Maximum {MAX_BULK_RECORDS} per request.',
            'VALIDATION_ERROR', 400
        )

    # Validate all records before inserting
    for i, item in enumerate(records_data):
        if not item.get('name') or not item.get('id_number'):
            return error_response(
                f'Record at index {i} is missing name or id_number',
                'VALIDATION_ERROR', 400
            )

    try:
        new_records = []
        for item in records_data:
            record = InstitutionRecord(
                institution_id=current_user.id,
                name=item.get('name'),
                id_number=item.get('id_number'),
                metadata_fields=item.get('metadata', {})
            )
            db.session.add(record)
            new_records.append(record)

        db.session.commit()
        return success_response(message=f'{len(new_records)} records added successfully', status_code=201)
    except Exception as e:
        db.session.rollback()
        logger.error(f'Bulk add records error: {e}', exc_info=True)
        return error_response('Failed to bulk add records', 'INTERNAL_ERROR', 500)


@institution_bp.route('/records', methods=['GET'])
@token_required
@institution_required
def list_records(current_user):
    """List records for the current institution."""
    page = max(1, request.args.get('page', 1, type=int))
    per_page = max(1, min(request.args.get('per_page', 10, type=int), 100))

    query = InstitutionRecord.query.filter_by(institution_id=current_user.id)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return paginated_response(
        [r.to_dict() for r in pagination.items],
        pagination.total,
        page,
        per_page,
        'records'
    )


@institution_bp.route('/records/<int:record_id>', methods=['DELETE'])
@token_required
@institution_required
def delete_record(current_user, record_id):
    """Delete a verification record owned by the current institution."""
    try:
        record = db.session.get(InstitutionRecord, record_id)
        if not record:
            return error_response('Record not found', 'NOT_FOUND', 404)
        if current_user.role != 'admin' and record.institution_id != current_user.id:
            return error_response('Access denied', 'FORBIDDEN', 403)

        db.session.delete(record)
        db.session.commit()
        return success_response(message='Record deleted successfully')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Delete record error: {e}', exc_info=True)
        return error_response('Failed to delete record', 'INTERNAL_ERROR', 500)


@institution_bp.route('/stats', methods=['GET'])
@token_required
@institution_required
def get_institution_stats(current_user):
    """Get statistics for the current institution dashboard."""
    try:
        from models.result import Result

        total_records = InstitutionRecord.query.filter_by(institution_id=current_user.id).count()
        
        # Count validations that matched this institution's data
        # In validation_service.py, we store match_details. 
        # We can look for results where match_details['institution'] is True.
        # This is a bit complex with JSON fields, but for now we'll do a simple count 
        # of records owned by them.
        
        return success_response(
            data={
                'total_records': total_records,
                'institution_name': current_user.name
            },
            message='Institution stats retrieved successfully'
        )
    except Exception as e:
        logger.error(f'Institution stats error: {e}', exc_info=True)
        return error_response('Failed to retrieve institution stats', 'INTERNAL_ERROR', 500)

