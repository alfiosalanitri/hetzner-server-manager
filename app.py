import os
import secrets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from flask import Flask, render_template, redirect, url_for, flash, abort
from hcloud import Client, APIException
from typing import cast, List
from models import Server
from models import db, Project
from forms import AddProjectForm
from utils import encrypt_token, decrypt_token
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

# App Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

# Initialize Extensions
db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# Helper Functions
def get_hcloud_client(project_id: int):
    """Initializes and returns a Hetzner Cloud Client for a given project."""
    project = db.session.get(Project, project_id)
    if not project:
        return None
    try:
        decrypted_token = decrypt_token(project.encrypted_api_token)
        return Client(token=decrypted_token)
    except Exception:
        # Handle cases where decryption might fail (e.g., bad key)
        return None

# This makes the list of projects available to all templates
@app.context_processor
def inject_projects():
    # Only try to query the DB if the tables exist
    try:
        projects = Project.query.order_by(Project.name).all()
        return dict(all_projects=projects)
    except Exception:
        return dict(all_projects=[])


# Routes
@app.route('/')
def index():
    """Redirect to the projects management page."""
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """Page to list, add, and delete projects."""
    form = AddProjectForm()
    if form.validate_on_submit():
        project_name = form.name.data
        api_token = form.api_token.data

        if not project_name:
            flash('Project name is required.', 'error')
        elif not api_token:
            flash('Api Toke is required.', 'error')
        elif Project.query.filter_by(name=project_name).first():
            flash('A project with this name already exists.', 'error')
        else:
            encrypted = encrypt_token(api_token)
            new_project = Project(name=project_name, encrypted_api_token=encrypted) # type: ignore
            db.session.add(new_project)
            db.session.commit()
            flash(f'Project "{project_name}" added successfully!', 'success')
            return redirect(url_for('dashboard'))

    projects = Project.query.order_by(Project.name).all()
    return render_template('dashboard.html', projects=projects, form=form)

@app.route('/project/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    project = db.session.get(Project, project_id) or abort(404)
    db.session.delete(project)
    db.session.commit()
    flash(f'Project "{project.name}" has been deleted.', 'warning')
    return redirect(url_for('dashboard'))

@app.route('/project/<int:project_id>')
def project(project_id):
    """Main project page to list all servers for a specific project."""
    project = db.session.get(Project, project_id) or abort(404)
    client = get_hcloud_client(project_id)
    
    servers = []
    error_message = None

    if not client:
        error_message = "Could not initialize Hetzner client. The API token might be invalid or the encryption key is wrong."
    else:
        try:
            servers = sorted(cast(List[Server], client.servers.get_all()), key=lambda s: s.name)
        except APIException as e:
            error_message = f"Hetzner API Error: {e}. Please verify the API token for this project."
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            
    return render_template('project.html', servers=servers, project=project, error_message=error_message)


@app.route('/project/<int:project_id>/server/<int:server_id>/<string:action>', methods=['POST'])
def server_action(project_id, server_id, action):
    """Handle actions like poweron, shutdown, and reboot for a server in a project."""
    client = get_hcloud_client(project_id)
    if not client:
        flash("Could not perform action. Invalid project or API token.", "error")
        return redirect(url_for('project', project_id=project_id))
    
    try:
        server = client.servers.get_by_id(server_id)
        if not server:
            flash(f"Server with ID {server_id} not found in this project.", "error")
            return redirect(url_for('project', project_id=project_id))

        if action == 'poweron':
            server.power_on()
            flash(f"Server '{server.name}' is starting.", "success")
        elif action == 'shutdown':
            server.shutdown()
            flash(f"Server '{server.name}' is shutting down.", "warning")
        elif action == 'reboot':
            server.reboot()
            flash(f"Server '{server.name}' is rebooting.", "info")
        else:
            flash(f"Unknown action: {action}", "error")
            
    except APIException as e:
        flash(f"Hetzner API Error: {e}", "error")
    except Exception as e:
        flash(f"An error occurred: {e}", "error")

    return redirect(url_for('project', project_id=project_id))

if __name__ == '__main__':
    app.run(debug=debug_mode)