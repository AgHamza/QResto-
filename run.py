from app import create_app, db
import os

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    # For local development, you might run this directly
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))