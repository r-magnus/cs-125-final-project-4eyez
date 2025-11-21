# Gabriel Leung <gleung@westmont.edu>
# Ryan Magnuson <rmagnuson@westmont.edu>

from fastapi import FastAPI
import mysql.connector

app = FastAPI()

@app.get("/")
def main():
    return {"message": "CS125 Paper Youth Group DB"}