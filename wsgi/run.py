from app import app
from flask import Flask

if __name__ == "__main__":
    app.run(debug = True,host='0.0.0.0') #We will set debug false in production 
