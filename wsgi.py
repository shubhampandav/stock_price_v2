from app import app

if __name__ == '__main__':
    # Use Waitress as the production WSGI server
    app.run(debug=True)
