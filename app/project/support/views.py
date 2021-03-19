# project/items/views.py

# IMPORTS
from flask import render_template, Blueprint, request, redirect, url_for, flash, Markup
from flask_login import current_user, login_required
from project import db
from project.models import Items, User
# from .forms import ItemsForm, EditItemsForm


# CONFIG
support_blueprint = Blueprint('support', __name__, template_folder='templates')


# ROUTES
@support_blueprint.route('/list', methods=['GET', 'POST'])
@login_required
def all_items():
    """Render homepage"""
    # all_user_items = Items.query.filter_by(user_id=current_user.id)
    return render_template('support/list.html' )


# ROUTES
@support_blueprint.route('/detail/<ticket_id>', methods=['GET', 'POST'])
@login_required
def detail(ticket_id):
    """Render homepage"""
    # all_user_items = Items.query.filter_by(user_id=current_user.id)
    return render_template('support/detail.html' )


@support_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    # form = ItemsForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_item = Items(form.name.data, form.notes.data,
                                 current_user.id)
                db.session.add(new_item)
                db.session.commit()
                message = Markup(
                    "<strong>Well done!</strong> Item added successfully!")
                flash(message, 'success')
                return redirect(url_for('home'))
            except:
                db.session.rollback()
                message = Markup(
                    "<strong>Oh snap!</strong>! Unable to add item.")
                flash(message, 'danger')
    # return render_template('support/add.html', form=form)
    return render_template('support/add.html' )


@support_blueprint.route('/edit/<items_id>', methods=['GET', 'POST'])
@login_required
def edit_item(items_id):
    form = EditItemsForm(request.form)
    item_with_user = db.session.query(Items, User).join(User).filter(Items.id == items_id).first()
    if item_with_user is not None:
        if current_user.is_authenticated and item_with_user.Items.user_id == current_user.id:
            if request.method == 'POST':
                if form.validate_on_submit():
                    try:
                        item = Items.query.get(items_id)
                        item.name = form.name.data
                        item.notes = form.notes.data
                        db.session.commit()
                        message = Markup("Item edited successfully!")
                        flash(message, 'success')
                        return redirect(url_for('home'))
                    except:
                        db.session.rollback()
                        message = Markup(
                            "<strong>Error!</strong> Unable to edit item.")
                        flash(message, 'danger')
            return render_template('support/edit.html', item=item_with_user, form=form)
        else:
            message = Markup(
                "<strong>Error!</strong> Incorrect permissions to access this item.")
            flash(message, 'danger')
    else:
        message = Markup("<strong>Error!</strong> Item does not exist.")
        flash(message, 'danger')
    return redirect(url_for('home'))


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
