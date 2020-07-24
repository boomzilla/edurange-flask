# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, redirect, render_template, request, url_for, session, flash, abort
from flask_login import login_required
from edurange_refactored.user.forms import GroupForm, addUsersForm, manageInstructorForm, modScenarioForm, \
    deleteStudentForm, makeScenarioForm
from .models import User, StudentGroups, GroupUsers, Scenarios, ScenarioGroups
from ..tasks import CreateScenarioTask
from ..utils import UserInfoTable, check_admin, check_instructor, flash_errors, checkEx, \
    tempMaker, checkAuth, checkEnr, check_role_view
from ..form_utils import process_request
from ..scenario_utils import populate_catalog, identify_type, identify_state
from edurange_refactored.extensions import db

blueprint = Blueprint("dashboard", __name__, url_prefix="/dashboard", static_folder="../static")


@blueprint.route("/set_view", methods=['GET'])
@login_required
def set_view():
    if check_role_view(request.args['mode']):
        session['viewMode'] = request.args['mode']
        return redirect(url_for('public.home'))
    else:
        session.pop('viewMode', None)
        return redirect(url_for('public.home'))

@blueprint.route("/")
@login_required
def student():
    """List members."""
    # Queries for the user dashboard
    db_ses = db.session
    curId = session.get('_user_id')

    userInfo = db_ses.query(User.id, User.username, User.email).filter(User.id == curId)
    infoTable = UserInfoTable(userInfo)

    groups = db_ses.query(StudentGroups.id, StudentGroups.name, GroupUsers).filter(GroupUsers.user_id == curId)\
        .filter(GroupUsers.group_id == StudentGroups.id)

    scenarioTable = db_ses.query(Scenarios.id, Scenarios.name.label('sname'),
                                 Scenarios.description.label('type'), StudentGroups.name.label('gname'),
                                 User.username.label('iname')).filter(GroupUsers.user_id == curId)\
        .filter(StudentGroups.id == GroupUsers.group_id).filter(User.id == StudentGroups.owner_id)\
        .filter(ScenarioGroups.group_id == StudentGroups.id).filter(Scenarios.id == ScenarioGroups.scenario_id)

    return render_template("dashboard/student.html", infoTable=infoTable, groups=groups, scenarioTable=scenarioTable)


@blueprint.route("/student_scenario/<i>")
@login_required
def student_scenario(i):
    if checkEnr(i):
        if checkEx(i):
            s, o, d, t, n = tempMaker(i, "s")
            p = "00000"
            address = identify_state(n, s)
            pw = "_"
            return render_template("dashboard/student_scenario.html", s=s, o=o, de=d, t=t, n=n, p=p, pw=pw, add=address)
        else:
            return abort(404)
    else:
        return abort(403)


# ---- scenario routes


@blueprint.route("/catalog", methods=['GET'])
@login_required
def catalog():
    check_admin()
    scenarios = populate_catalog()
    groups = StudentGroups.query.all()
    form = modScenarioForm(request.form)

    return render_template("dashboard/catalog.html", scenarios=scenarios, groups=groups, form=form)


@blueprint.route("/make_scenario", methods=['POST'])
@login_required
def make_scenario():
    check_admin()
    form = makeScenarioForm(request.form)
    if form.validate_on_submit():
        db_ses = db.session
        name = request.form.get('scenario_name')
        s_type = identify_type(request.form)
        own_id = session.get('_user_id')
        group = request.form.get('scenario_group')

        students = db_ses.query(User.username).filter(StudentGroups.name == group)\
            .filter(StudentGroups.id == GroupUsers.group_id).filter(GroupUsers.user_id == User.id).all()

        Scenarios.create(name=name, description=s_type, owner_id=own_id)
        s_id = db_ses.query(Scenarios.id).filter(Scenarios.name == name).first()
        g_id = db_ses.query(StudentGroups.id).filter(StudentGroups.name == group).first()

        # JUSTIFICATION:
        # Above queries return sqlalchemy collections.result objects
        # _asdict() method is needed in case celery serializer fails
        # Unknown exactly when this may occur, maybe version differences between Mac/Linux

        for i, s, in enumerate(students):
            students[i] = s._asdict()
        s_id = s_id._asdict()
        g_id = g_id._asdict()

        CreateScenarioTask.delay(name, s_type, own_id, students, g_id, s_id)
        flash("Success, your scenario will appear shortly. This page will automatically update. Students Found: {}".format(students), "success")
    else:
        flash_errors(form)

    return redirect(url_for('dashboard.scenarios'))


@blueprint.route("/scenarios", methods=['GET', 'POST'])
@login_required
def scenarios():
    """List of scenarios and scenario controls"""
    check_admin()
    scenarioModder = modScenarioForm()
    scenarios = Scenarios.query.all()
    groups = StudentGroups.query.all()

    if request.method == 'GET':
        return render_template("dashboard/scenarios.html", scenarios=scenarios, scenarioModder=scenarioModder,
                               groups=groups)

    elif request.method == 'POST':
        process_request(request.form)
        return render_template("dashboard/scenarios.html", scenarios=scenarios, scenarioModder=scenarioModder,
                               groups=groups)


@blueprint.route("/scenarios/<i>")
def scenariosInfo(i):
    if checkAuth(i):
        if checkEx(i):
            s, o, b, d, t, n = tempMaker(i, "i")
            address = identify_state(n, s)
            pw = "_"
            return render_template("dashboard/scenarios_info.html", i=i, t=t, de=d, s=s, o=o, dt=b, n=n, pw=pw, add=address)
        else:
            return abort(404)
    else:
        return abort(403)


# -----


@blueprint.route("/instructor", methods=['GET', 'POST'])
@login_required
def instructor():
    """List of an instructors groups"""
    check_instructor()
    # Queries for the owned groups table
    curId = session.get('_user_id')
    db_ses = db.session

    groups = db_ses.query(StudentGroups.id, StudentGroups.name, StudentGroups.code)\
        .filter(StudentGroups.owner_id == curId)

    userInfo = db_ses.query(User.id, User.username, User.email).filter(User.id == curId)
    infoTable = UserInfoTable(userInfo)
    if request.method == 'GET':
        groupMaker = GroupForm()
        return render_template('dashboard/instructor.html', groupMaker=groupMaker, groups=groups, infoTable=infoTable)

    elif request.method == 'POST':
        process_request(request.form)
        return redirect(url_for('dashboard.admin'))


@blueprint.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    """List of all students and groups. Group, student, and instructor management forms"""
    check_admin()
    db_ses = db.session
    # Queries for the tables of students and groups
    students = db_ses.query(User.id, User.username, User.email).filter(User.is_instructor == False)
    instructors = db_ses.query(User.id, User.username, User.email).filter(User.is_instructor == True)
    groups = StudentGroups.query.all()
    groupNames = []
    users_per_group = {}

    for g in groups:
        groupNames.append(g.name)

    for name in groupNames:
        users_per_group[name] = db_ses.query(User.id, User.username, User.email).filter(StudentGroups.name == name, StudentGroups.id == GroupUsers.group_id, GroupUsers.user_id == User.id)

    if request.method == 'GET':
        groupMaker = GroupForm()
        userAdder = addUsersForm()
        instructorManager = manageInstructorForm()
        userDropper = deleteStudentForm()

        return render_template('dashboard/admin.html', groupMaker=groupMaker, userAdder=userAdder,
                               instructorManager=instructorManager, userDropper=userDropper, groups=groups,
                               students=students, instructors=instructors, usersPGroup=users_per_group)

    elif request.method == 'POST':
        ajax = process_request(request.form)
        if ajax:
            groupMaker = GroupForm()
            userAdder = addUsersForm()
            instructorManager = manageInstructorForm()
            userDropper = deleteStudentForm()
            return render_template('dashboard/admin.html', groupMaker=groupMaker, userAdder=userAdder, instructorManager=instructorManager, userDropper=userDropper, groups=groups, students=students, instructors=instructors, usersPGroup=users_per_group)
        else:
            return redirect(url_for('dashboard.admin'))
