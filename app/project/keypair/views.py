from flask import render_template, Blueprint, request, redirect, url_for, flash, Markup
from flask_login import current_user, login_required
from project import db
from project import app
from project.models import User, Cloud, Plan, Oslist, VPC, Subnet, Keypair
import boto3
import os
from .forms import KeypairForm, EditKeypairForm
import base64

keypair_blueprint = Blueprint('keypair', __name__, template_folder='templates')
ec2 = boto3.client('ec2', config=app.config.get('AWS_CONFIG'), aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key= os.environ.get("AWS_SECRET_ACCESS_KEY")) 

def back_ec2_keypair_create(userid, keyname): # 키페어 사용자한테 다운로드 처리 필요!!!!
    response = ec2.create_key_pair(KeyName="{}_{}".format(userid, keyname))
    # response["keyMaterial"] -> private key
    # response["KeyPairId"] KeyPairId
    # response["KeyFingerprint"] KeyFingerPrint
    # ResponseMetadata': {'RequestId': '6dfe219f-e9d5-4c60-924e-5ad74a938967', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '6dfe219f-e9d5-4c60-924e-5ad74a938967', 'cache-control': 'no-cache, no-store', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'content-type': 'text/xml;charset=UTF-8', 'content-length': '2090', 'vary': 'accept-encoding', 'date': 'Sat, 30 Jan 2021 06:37:15 GMT', 'server': 'AmazonEC2'}, 'RetryAttempts': 0}}
    return response

def back_ec2_keypair_remove(userid, keyname):
    response = ec2.delete_key_pair(KeyName="{}_{}".format(userid, keyname))
    # 'ResponseMetadata': {'RequestId': '940e2759-8c0a-465a-ba75-1a287263c917', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '940e2759-8c0a-465a-ba75-1a287263c917', 'cache-control': 'no-cache, no-store', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'content-type': 'text/xml;charset=UTF-8', 'content-length': '227', 'date': 'Sat, 30 Jan 2021 06:40:17 GMT', 'server': 'AmazonEC2'}, 'RetryAttempts': 0}}
    return response 

@keypair_blueprint.route('/list', methods=['GET'])
@login_required
def all_keypairs():
    keypair_list = Keypair.query.filter_by(user_id = current_user.id)
    return render_template('all_keypairs.html', keypairs=keypair_list)

@keypair_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = KeypairForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                result = back_ec2_keypair_create(current_user.email, form.name.data) 
                new_keypair = Keypair(form.name.data, result["KeyFingerprint"], result["KeyPairId"], current_user.id)
                db.session.add(new_keypair)
                db.session.commit() 
                # 입출력 처리 / 파일다운로드 / 키파일 삭제 처리 
                formatted = base64.b64encode(result["KeyMaterial"].encode()).decode()
                message = Markup(
                    "<strong>키 파일을 다운로드 해주세요. 한번만 가능합니다. 서버엔 저장되지 않습니다. </strong><a onclick='this.remove()' download='id_rsa.pem' href='data:blob;base64,{}'>다운로드</a>".format( formatted ))
                flash(message, 'success')
                return redirect(url_for('keypair.all_keypairs'))
            except Exception as e:
                db.session.rollback()
                message = Markup(
                    "<strong>Oh snap!</strong>! Unable to add item.{} ".format(e))
                flash(message, 'danger')
    return render_template('add_keypair.html', form=form)
     

@keypair_blueprint.route('/edit', methods=['GET', 'POSST'])
@login_required
def edit():
    # form = EditItemsForm(request.form)
    # item_with_user = db.session.query(Items, User).join(User).filter(Items.id == items_id).first()
    # if item_with_user is not None:
    #     if current_user.is_authenticated and item_with_user.Items.user_id == current_user.id:
    #         if request.method == 'POST':
    #             if form.validate_on_submit():
    #                 try:
    #                     item = Items.query.get(items_id)
    #                     item.name = form.name.data
    #                     item.notes = form.notes.data
    #                     db.session.commit()
    #                     message = Markup("Item edited successfully!")
    #                     flash(message, 'success')
    #                     return redirect(url_for('home'))
    #                 except:
    #                     db.session.rollback()
    #                     message = Markup(
    #                         "<strong>Error!</strong> Unable to edit item.")
    #                     flash(message, 'danger')
    #         return render_template('edit_item.html', item=item_with_user, form=form)
    #     else:
    #         message = Markup(
    #             "<strong>Error!</strong> Incorrect permissions to access this item.")
    #         flash(message, 'danger')
    # else:
    #     message = Markup("<strong>Error!</strong> Item does not exist.")
    #     flash(message, 'danger')
    # return redirect(url_for('home'))
    pass

@keypair_blueprint.route('/delete/<keypair_id>', methods=['POST'])
@login_required
def delete():
    # item = Items.query.filter_by(id=items_id).first_or_404()

    # if not item.user_id == current_user.id:
    #     message = Markup(
    #         "<strong>Error!</strong> Incorrect permissions to delete this item.")
    #     flash(message, 'danger')
    #     return redirect(url_for('home'))

    # db.session.delete(item)
    # db.session.commit()
    # flash('{} was deleted.'.format(item.name), 'success')
    # return redirect(url_for('items.all_items'))
    pass
