from flask import abort, Blueprint, flash, g, redirect, render_template, request, url_for
import random
from . import lslga_utils
from .db import get_db
from . import subsets

bp = Blueprint('inspect', __name__)

@bp.route('/')
def index():
    return render_template('catalog-list.html', pretty_strings=subsets.pretty_string_dict)

@bp.route('/inspect')
def inspect_index():
    return redirect(url_for('.inspect_catalog', catalog_raw='all'))

@bp.route('/inspect/<string:catalog_raw>')
def inspect_catalog(catalog_raw):

    # galaxy_list = subsets.galaxy_list_dict[catalog_raw]
    galaxy_list = subsets.galaxy_list_dict.get(catalog_raw, None)

    if galaxy_list is None:
        return abort(500, 'Catalog name not found.')

    if g.user is not None:

        galaxy_list = set(galaxy_list)
        user_inspected = set(subsets.get_inspected(g.user['id']))
        to_inspect = galaxy_list - user_inspected
        to_inspect = list(to_inspect)

        if len(to_inspect) == 0:
            return render_template(
                'message.html',
                title='Set completed',
                header='Set completed',
                message='Set {} completed.'.format(subsets.pretty_string_dict[catalog_raw])
            )

        # rand_id = random.choice(to_inspect)
        rand_id = to_inspect[0]
        return redirect(url_for('.inspect_galaxy', catalog_raw=catalog_raw, galaxy_id=rand_id))

    else:
        rand_id = random.choice(galaxy_list)
        return redirect(url_for('.inspect_galaxy', catalog_raw=catalog_raw, galaxy_id=rand_id))

@bp.route('/inspect/<string:catalog_raw>/<int:galaxy_id>', methods=('GET', 'POST'))
def inspect_galaxy(catalog_raw, galaxy_id):

    if request.method == 'POST':

        if g.user is None:
            flash("User must be logged in to submit information!")
        else:

            db = get_db()

            existing_inspection = db.execute(
                'SELECT * FROM inspection WHERE user_id = ? AND lslga_id = ?',
                (g.user['id'], galaxy_id)
            ).fetchone()

            if existing_inspection is not None:
                db.execute(
                    "UPDATE inspection SET quality = ?, feedback = ? WHERE user_id = ? AND lslga_id = ?",
                    (request.form['quality'], None if request.form['feedback'] == '' else request.form['feedback'], g.user['id'], galaxy_id)
                )
            else:
                db.execute(
                    "INSERT INTO inspection (user_id, lslga_id, quality, feedback, subset) VALUES (?, ?, ?, ?, ?)",
                    (g.user['id'], galaxy_id, request.form['quality'], None if request.form['feedback'] == '' else request.form['feedback'], catalog_raw)
                )

            db.commit()

            return redirect(url_for('.inspect_catalog', catalog_raw=catalog_raw))

    if catalog_raw not in subsets.pretty_string_dict:
        return abort(500, 'Catalog name not found.')
        
    galaxy_info = lslga_utils.get_lslga_tablerow(galaxy_id)

    viewer_link = (
        "http://legacysurvey.org/viewer"
        "?ra={:.7f}"
        "&dec={:.7f}"
        "&zoom=14"
        "&lslga"
    ).format(galaxy_info['RA'], galaxy_info['DEC'])

    # TODO: Iterate over all questions
    # TODO: Will need to figure out how to migrate old DB into this one...
    inspection_questions = [
        {
            'good': 'Good',
            'bad-ellipse': 'Ellipse wrong size/shape/position',
            'spurious-src': 'Spurious source (star/smaller galaxy)',
            'lsb-resolved': 'Resolved, low surface brightness galaxy',
            'bad-mask': 'Galaxy masked too aggressively by pipeline'
        },
        {
            'tmp': 'tmp',
        }
    ]

    db = get_db()

    success = False

    if g.user is not None:

        existing_inspection = db.execute(
            'SELECT * FROM inspection WHERE user_id = ? AND lslga_id = ?',
            (g.user['id'], galaxy_id)
        ).fetchone()

        if existing_inspection is not None:

            checked_option = existing_inspection['quality']
            load_text = '' if existing_inspection['feedback'] == None else existing_inspection['feedback']
            submit_button = 'Update'

            success = True

        prev_inspections = subsets.get_inspected(g.user['id'])
        catalog_galaxies = subsets.galaxy_list_dict[catalog_raw]
        prev_inspections_set = set(prev_inspections)
        catalog_galaxies_set = set(catalog_galaxies)
        intersecting_inspections = prev_inspections_set & catalog_galaxies_set
        sorted_inspections = sorted(list(intersecting_inspections), key=prev_inspections.index)

        index = None
        for i, test_id in enumerate(sorted_inspections):
            if test_id == galaxy_id:
                index = i
                break
        if index is None:
            if len(sorted_inspections) > 0:
                prev_id = sorted_inspections[-1]
            else:
                prev_id = None
            next_id = None
        else:
            if index > 0:
                prev_id = sorted_inspections[index - 1]
            else:
                prev_id = None

            if index == len(sorted_inspections) - 1:
                next_id = 'new'
            elif index < len(sorted_inspections) - 1:
                next_id = sorted_inspections[index + 1]
            else:
                next_id = None
    else:
        prev_id = None
        next_id = None

    if not success:

        checked_option = 'good'
        load_text = ''
        submit_button = 'Submit'
    
    return render_template(
        "inspect.html",
        catalog_raw=catalog_raw,
        catalog_pretty=subsets.pretty_string_dict[catalog_raw],
        id=galaxy_id,
        info=galaxy_info,
        viewer_link = viewer_link,
        inspection_options=inspection_options,
        checked_option=checked_option,
        load_text=load_text,
        submit_button=submit_button,
        prev_id=prev_id,
        next_id=next_id
    )
