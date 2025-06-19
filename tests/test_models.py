import pytest
from app import app, db
from models import Project

@pytest.fixture(scope='module')
def test_app():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def session(test_app):
    with test_app.app_context():
        yield db.session
        db.session.rollback()

def test_project_crud(session):
    project = Project(name="TestProject", encrypted_api_token=b"abc123") #type: ignore
    session.add(project)
    session.commit()

    fetched = Project.query.filter_by(name="TestProject").first()
    assert fetched is not None
    assert fetched.name == "TestProject"
    assert fetched.encrypted_api_token == b"abc123"

    fetched.name = "ChangedName"
    session.commit()
    updated = Project.query.filter_by(name="ChangedName").first()
    assert updated is not None
    assert updated.name == "ChangedName"

    session.delete(updated)
    session.commit()
    deleted = Project.query.filter_by(name="ChangedName").first()
    assert deleted is None
