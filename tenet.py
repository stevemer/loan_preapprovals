import os
from flask_migrate import Migrate
from app import create_app, db
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = create_app()
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(debug=True)