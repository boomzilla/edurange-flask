# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from .models import User, StudentGroups


class RegisterForm(FlaskForm):
    """Register form."""
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=25)]
    )
    email = StringField(
        "Email", validators=[DataRequired(), Email(), Length(min=6, max=40)]
    )
    code = StringField(
        "Registration Code (Optional)", validators=[Length(min=0, max=8)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=40)]
    )
    confirm = PasswordField(
        "Verify password",
        [DataRequired(), EqualTo("password", message="Passwords must match")],
    )

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("Username already registered")
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        if self.code.data:
            group = StudentGroups.query.filter_by(code=self.code.data).first()
            if not group:
                self.code.errors.append("Invalid registration code")
                return False
        return True


# ---------------------------------- (unused?)
class EmailForm(FlaskForm):
    """Email Form."""
    subject = StringField(
        "Subject", validators=[DataRequired()]
    )
    to = StringField(
        "Recipient", validators=[DataRequired()]
    )
    body = StringField(
        "Body", validators=[DataRequired()]
    )

    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(EmailForm, self).validate()
        if not initial_validation:
            return False
        return True
# -----------------------------------------------------


class GroupForm(FlaskForm):
    """Create New Group Form"""
    name = StringField(
        "Group Name", validators=[DataRequired()]
    )

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(GroupForm, self).validate()
        if not initial_validation:
            return False
        group = StudentGroups.query.filter_by(name=self.name.data).first()
        if group:
            self.name.errors.append("Group with this name already exists")
            return False
        return True


# ----------------------------------------(unused?)
class GroupFinderForm(FlaskForm):
    """Finds Existing Group"""
    group = StringField(
        "Group Name", validators=[DataRequired()]
    )

    def __init__(self, *args, **kwargs):
        super(GroupFinderForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(GroupFinderForm, self).validate()
        if not initial_validation:
            return False
        return True
# -------------------------------------------


class addUsersForm(FlaskForm):
    """Adds selected users to a group"""
    uids = StringField(
        'User IDs', validators=[DataRequired()]
    )
    groups = StringField(
        'Group Name', validators=[DataRequired()]
    )

    # user id list

    def __init__(self, *args, **kwargs):
        super(addUsersForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(addUsersForm, self).validate()
        if not initial_validation:
            return False
        return True


class manageInstructorForm(FlaskForm):
    """Elevates user to an instructor"""
    uName = StringField(
        "Username", validators=[DataRequired()]
    )

    def __init__(self, *args, **kwargs):
        super(manageInstructorForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(manageInstructorForm, self).validate()
        if not initial_validation:
            return False
        return True

class makeScenarioForm(FlaskForm):
    """Creates a Scenario"""
    scenario_name = StringField(
        "Scenario", validators=[DataRequired()]
    )

    scenario_group = StringField(
        "Group", validators=[DataRequired()]
    )

    def __init__(self, *args, **kwargs):
        super(makeScenarioForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(makeScenarioForm, self).validate()
        if not initial_validation:
            return False
        return True

class modScenarioForm(FlaskForm):
    """Creates a Scenario"""
    sid = StringField(
        "Scenario ID", validators=[DataRequired()]
    )

    mod_scenario = StringField(
        "Action", validators=[DataRequired()]
    )
    def __init__(self, *args, **kwargs):
        super(modScenarioForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(modScenarioForm, self).validate()
        if not initial_validation:
            return False
        return True


class deleteStudentForm(FlaskForm):
    """Deletes a student from the database"""
    stuName = StringField(
        "Username", validators=[DataRequired()]
    )

    def __init__(self, *args, **kwargs):
        super(deleteStudentForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(deleteStudentForm, self).validate()
        if not initial_validation:
            return False
        return True
