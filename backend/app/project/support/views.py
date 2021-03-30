# project/items/views.py

# IMPORTS
from flask import render_template, Blueprint, request, redirect, url_for, flash, Markup
from flask_login import current_user, login_required
from project import db
from project.models import Items, User,Support, ReplyTicket
# from .forms import ItemsForm, EditItemsForm


# CONFIG
support_blueprint = Blueprint('support', __name__, template_folder='templates')


# ROUTES
@support_blueprint.route('/list', methods=['GET', 'POST'])
@login_required
def all_items():
    """Render homepage"""
    all_user_support = Support.query.filter_by(author_id=current_user.id)
    # title, support_type

    return render_template('support/list.html' )


# ROUTES
@support_blueprint.route('/detail/<ticket_id>', methods=['GET', 'POST'])
@login_required
def detail(ticket_id):
    # support_detail_post = Support.query.filter_by(author_id=current_user.id, id = ticket_id)
    
    # reply_list = ReplyTicket.query.filter_by(reply_to = ticket_id) # 얘는 html에서 for 로 뿌려줘야겠지??
    # detail = support_detail_post.content # Support.content
    
    return render_template('support/detail.html' )


@support_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    # form = ItemsForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_item = Support(form.support_type.data, form.title.data, form.content.data,
                                 current_user.id)
                db.session.add(new_item)
                db.session.commit()
                message = Markup(
                    "<strong>Well done!</strong> Item added successfully!")
                flash(message, 'success')
                return redirect(url_for('support.all_items'))
            except:
                db.session.rollback()
                message = Markup(
                    "<strong>Oh snap!</strong>! db error.")
                flash(message, 'danger')
    # return render_template('support/add.html', form=form)
    return render_template('support/add.html' )


@support_blueprint.route('/delete/<items_id>')
@login_required
def delete_item(items_id):
    item = Items.query.filter_by(id=items_id).first_or_404()

    if not item.user_id == current_user.id:
        message = Markup(
            "<strong>Error!</strong> Incorrect permissions to delete this item.")
        flash(message, 'danger')
        return redirect(url_for('home'))

    db.session.delete(item)
    db.session.commit()
    flash('{} was deleted.'.format(item.name), 'success')
    return redirect(url_for('items.all_items'))
