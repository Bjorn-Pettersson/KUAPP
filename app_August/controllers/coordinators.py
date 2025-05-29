from flask import Blueprint, render_template, request
from models.coordinators import *

bp = Blueprint('coordinators', __name__, url_prefix='/')

@bp.route('/coordinators', methods=['GET', 'POST'])
def coordinators():
    sort = request.args.get('sort')
    desc = request.args.get('desc', '1') == '1'
    if sort == 'rating':
        coordinators = list_coordinators(sort_by_rating=True, descending=desc)
    else:
        coordinators = list_coordinators()

    return render_template('coordinators.html', coordinators=coordinators)
