from flask import render_template, Blueprint, request, redirect, url_for, flash, Markup
from flask_login import current_user, login_required
from project import db
from project import app
from project.models import User, Cloud
import boto3
import os
from .forms import CloudForm, EditCloudForm


# # CONFIG
cloud_blueprint = Blueprint('cloud', __name__, template_folder='templates')
# ec2 = boto3.client('ec2', config=app.config.get('AWS_CONFIG'), aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key= os.environ.get("AWS_SECRET_ACCESS_KEY")) 


@cloud_blueprint.route('/list', methods=['GET'])
@login_required
def all_clouds():
    cloud_lists = Cloud.query.filter_by(user_id = current_user.id)
    return render_template('all_clouds.html', items=cloud_lists)

@cloud_blueprint.route('/reboot', methods=['POST'])
@login_required
def reboot_instance():
    try:
        response = ec2.reboot_instances(InstanceIds=['INSTANCE_ID'], DryRun=False)
        print('Success', response)
        return "Success"
    except ClientError as e:
        print('Error', e)

@cloud_blueprint.route('/delete', methods=['POST'])
@login_required
def delete_cloud():
    return "Constructing"

@cloud_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_cloud():
    form = CloudForm(request.form)
    return render_template('add_cloud.html', form=form)
    # if request.method == 'POST':
    #     if form.validate_on_submit():
    #         try:
    #             # 1. AWS EC2 API 호출 - SDK

    #             # 2. DB 에 기록..
    #             # new_cloud = Cloud(form.name.data, form.
    #             message = Markup(
    #                 "<strong>Well done!</strong> Cloud deployed successfully!")
    #             flash(message, 'success')                   
    #             return redirect(url_for('home'))
    #         except:
    #             db.session.rollback()
    #             # SDK rollback implement need
    #             message = Markup(
    #                 "<strong>내부 API 에러")
    #             # flash(message, )
                
    #     else:
    #         print("Error")

