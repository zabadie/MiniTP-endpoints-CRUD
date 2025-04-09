from flask import Flask
from config import Config
from models import db  # Importation correcte de db depuis models
from route.students import students_bp  # Importation du blueprint des étudiants
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

# Créer les tables
with app.app_context():
    db.create_all()

# Enregistrer les blueprints
app.register_blueprint(students_bp)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
