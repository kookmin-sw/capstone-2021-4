# project/items/views.py

# IMPORTS
from flask import render_template, Blueprint, request, redirect, url_for, flash, Markup
from flask_login import current_user, login_required
from project import db
from project.models import Items, User, Invoice, Credit, Balance
from .forms import AddCredictForm

from sqlalchemy.sql import func



# CONFIG
billing_blueprint = Blueprint('billing', __name__, template_folder='templates')


# ROUTES
@billing_blueprint.route('/me', methods=['GET', 'POST'])
@login_required
def all_items():
    """Render homepage"""
    form = AddCredictForm(request.form)
    all_user_items = Credit.query.filter_by(user_id=current_user.id)
    credit_sum = db.session.query(Balance.balance).filter_by(user_id=current_user.id).scalar() 
    return render_template('billing/me.html', items=all_user_items, form=form, credit_sum = credit_sum)


@billing_blueprint.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role == 'admin':
        all_user_items = Credit.query.all()
        print(all_user_items)
        return render_template('billing/admin.html', items=all_user_items)
    else:
        return render_template('404.html'), 404
        # return render_template('billing/me.html') 


@billing_blueprint.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = AddCredictForm(request.form)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_item = Credit(form.data["deposit_name"], form.data["bank"],
                                 form.data["amount"], current_user.id)
                
                print(new_item)
                print(form.data["deposit_name"])
                print(form.data["amount"])
                print(form.data["bank"])
                
                db.session.add(new_item)
                db.session.commit()
                message = Markup(
                    "<strong>Well done!</strong> Item added successfully!")
                flash(message, 'success')
                return redirect(url_for('billing.all_items'))
            except Exception as e:
                print(e)
                db.session.rollback()
                message = Markup(
                    "<strong>Oh snap!</strong>! Unable to add item.")
                flash(message, 'danger')
        else:
            return 403
    return redirect(url_for('billing.all_items'))


@billing_blueprint.route('/edit_item/<items_id>', methods=['GET', 'POST'])
@login_required
def edit_item(items_id):
    form = AddCredictForm(request.form)
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
            return render_template('edit_item.html', item=item_with_user, form=form)
        else:
            message = Markup(
                "<strong>Error!</strong> Incorrect permissions to access this item.")
            flash(message, 'danger')
    else:
        message = Markup("<strong>Error!</strong> Item does not exist.")
        flash(message, 'danger')
    return redirect(url_for('home'))



@billing_blueprint.route('/delete_item/<items_id>')
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


@billing_blueprint.route('/transaction/<transaction_id>/<status>')
@login_required
def start_transaction(transaction_id, status):
    
    if current_user.role == "admin": #관리자만
        try:
            item = Credit.query.filter_by(id = transaction_id).first()
            print("param")
            print(status)
            print("current")
            item_user_id = item.user_id 
         
            if status == "accept":
                item.status = True
            elif status == "reject":
                print("Rejected")
                item.status = False
            
            
            credit_sum = db.session.query(func.sum(Credit.charge_amount).label("amount") ).filter_by(user_id=item_user_id, status=True).scalar() 
            
            if credit_sum == None:
                credit_sum = 0
                 
            update_balance = db.session.query(Balance).filter_by(user_id = item_user_id).first()
            update_balance.balance = credit_sum
            
            db.session.commit()
            
            
            message = Markup(
                "<strong>Good!</strong> Transaction Success")
            flash(message, 'success')
        except Exception as e:
            print(e)
            db.session.rollback()
            
        return redirect(url_for('billing.admin'))
        
    else:
        abort(404) 
    pass
