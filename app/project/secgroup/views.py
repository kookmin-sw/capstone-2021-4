from flask import render_template, Blueprint, request, redirect, url_for, flash, Markup
from flask_login import current_user, login_required
from project import db
from project import app
from project.models import User, Cloud, Plan, Oslist, VPC, Subnet, Keypair, SecurityGroup, SecurityRule
import boto3
import os
from .forms import SecurityInputForm,SecurityEditForm, SecurityRuleEditForm, SecurityRuleAddForm
import base64

secgroup_blueprint = Blueprint('secgroup', __name__, template_folder='templates')
ec2 = boto3.client('ec2', config=app.config.get('AWS_CONFIG'), aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key= os.environ.get("AWS_SECRET_ACCESS_KEY")) 

 
@secgroup_blueprint.route('/list', methods=['GET'])
@login_required
def all_secgroup():
    secgroup_list = SecurityGroup.query.filter_by(user_id = current_user.id)
    return render_template('secgroup/list.html', secgroups=secgroup_list)

@secgroup_blueprint.route('/add', methods=['GET', 'POST']) # 보안 그룹을 생성하는것
@login_required
def add():
    form = SecGroupForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                vpc_id = form.vpcid.data
                result = back_ec2_create_security_group(vpc_id)
                new_secgroup = SecurityGroup(form.name.data,  result["GroupId"],current_user.id, None ) 
                db.session.add(new_secgroup)
                db.session.commit() 
                # 입출력 처리 / 파일다운로드 / 키파일 삭제 처리 
                message = Markup(
                    "<strong>보안 그룹 {} 이 생성되었습니다.</strong>".format(result["GroupId"]))
                flash(message, 'success')
                return redirect(url_for('securitygroup.all_secgroup'))
            except Exception as e:
                db.session.rollback()
                message = Markup(
                    "<strong>Oh snap!</strong>! Unable to add item.{} ".format(e))
                flash(message, 'danger')
    return render_template('add_secgroup.html', form=form)
     
@secgroup_blueprint.route('/delete/<secgroup_id>', methods=['POST']) # 보안 그룹을 삭제 ( cloud에 할당이 되어있으면 삭제할 수 없음)
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

@secgroup_blueprint.route('/<secgroup_id>/detail', methods=["GET"]) # all security group of rules
@login_required
def detail(secgroup_id):
    check = db.session.query(User, SecurityGroup).join(User).filter(SecurityGroup.id == secgroup_id).first()
    if check is not None:
        if current_user.is_authenticated and check.SecurityGroup.user_id == current_user.id:
            # response = ec2.describe_security_groups(
            #     GroupIds=[
            #         check.SecurityGroup.sec_group_id,
            #     ]
            # )
            rulelist = db.session.query(SecurityRule).filter(SecurityRule.group_id == secgroup_id)
            
            # print(response["SecurityGroups"][0])
            # return response["SecurityGroups"][0]
            return render_template('secgroup/detail.html', detail=rulelist, groupid =secgroup_id) 
        else:
            message = Markup("Access Denied 1")
            flash(message, 'danger')
    else:
        message = Markup("Access Denied 2 ")
        flash(message, 'danger')
    
    return redirect(url_for('home'))

@secgroup_blueprint.route('/attach/<secgroup_id>', methods=["POST"]) # 인스턴스에 보안 그룹 할당
@login_required
def attach():
    pass

@secgroup_blueprint.route('/detach/<secgroup_id>', methods=["POST"]) # 인스턴스에 보안그룹 빼기
@login_required
def detach():
    pass


@secgroup_blueprint.route('/<secgroup_id>/delete', methods=["GET", "POST"])
@login_required
def sec_delete():
    # get security rules()
    # delete_security_group() 
    #revoke
    pass 

@secgroup_blueprint.route('/<secgroup_id>/edit/<ruleid>', methods=["GET", "POST"])
@login_required
def edit(secgroup_id, ruleid):
    # 기존에 어떤 Rule을 수정하려 헀는지 Cidr, FromPort, Protocol, ToPort 를 가져와야함.
    # 룰 하나만 삭제
    check = db.session.query(User, SecurityGroup).join(User).filter(SecurityGroup.id == secgroup_id).first()
    form = SecurityRuleEditForm(request.form)
    if check is not None:
        rule = db.session.query(SecurityRule).filter(SecurityRule.id == ruleid).first()
        # print(rule.cidr.)
        if request.method == "POST":
            fromport = form.fromport.data
            toport = form.toport.data
            protocol = form.protocol.data
            cidr = form.cidr.data 
            ec2 = boto3.resource('ec2')
            print(protocol)
            security_group = ec2.SecurityGroup(check.SecurityGroup.sec_group_id)
            
            security_group.revoke_ingress( 
                IpProtocol=rule.protocol, CidrIp=rule.cidr, FromPort=rule.fromport, ToPort=rule.toport
            )
            security_group.authorize_ingress(
                IpProtocol=protocol,CidrIp=cidr,FromPort=fromport,ToPort=toport
            )
            rule.fromport = fromport
            rule.toport = toport
            rule.protocol = protocol
            rule.cidr = cidr
            db.session.add(rule)
            db.session.commit()

            return redirect(url_for('secgroup.detail', secgroup_id=secgroup_id))
             
    return render_template('secgroup_edit.html',detail=rule, form=form, ruleid=ruleid, groupid=secgroup_id)
  


@secgroup_blueprint.route('/<secgroup_id>/sec_add', methods=["GET", "POST"])
@login_required
def sec_add(secgroup_id):
    form = SecurityRuleAddForm(request.form)
    check = db.session.query(User, SecurityGroup).join(User).filter(SecurityGroup.id == secgroup_id).first()
    if check is not None:
        if request.method == "POST":
            fromport = form.fromport.data
            toport = form.toport.data
            protocol = form.protocol.data
            cidr = form.cidr.data
            response = ec2.authorize_security_group_ingress( 
                GroupId=check.SecurityGroup.sec_group_id, 
                IpPermissions=[
                    {
                        'FromPort': fromport,
                        'IpProtocol': protocol,
                        'IpRanges': [
                            {
                                'CidrIp': cidr,
                                'Description': 'add from testapi'
                            },
                        ],
                        'ToPort': toport, 
                    },
                ], 
            )
            new_rule = SecurityRule(protocol, fromport, toport, cidr, "", secgroup_id)
            db.session.add(new_rule)
            db.session.commit()
            message = Markup(
                "<strong>Well done!</strong> Rule add success")
            flash(message, 'success')                   
            return redirect(url_for('secgroup.detail', secgroup_id=secgroup_id))
            # return response
    else:
        return "denied"
    # authorize_security_group_ingress
    # 추가
    # ec2.authorize_security_group_ingress( 
    #     GroupId='sg-0aa5b53c90c76a2ac', 
    #     IpPermissions=[
    #         {
    #             'FromPort': 80,
    #             'IpProtocol': 'tcp',
    #             'IpRanges': [
    #                 {
    #                     'CidrIp': '0.0.0.0/0',
    #                     'Description': 'http'
    #                 },
    #             ],
    #             'ToPort': 81, 
    #         },
    #     ], 
    # )

    return render_template('secgroup_rule_add.html', form=form, groupid=secgroup_id)


