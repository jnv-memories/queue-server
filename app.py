from flask import Flask, request, jsonify
import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore

import os
import json
import time

app = Flask(__name__)

if not firebase_admin._apps:

    cred = credentials.Certificate(
        json.loads(
            os.environ["FIREBASE_JSON"]
        )
    )

    firebase_admin.initialize_app(
        cred
    )

db = firestore.client()
def get_pending_jobs():
    docs = (
        db.collection(DOWNLOAD_QUEUE)
        .where(
            "status",
            "==",
            "pending"
        ).stream()
    )
    jobs = []
    for doc in docs:
        data = doc.to_dict()
        data["jobId"] = doc.id
        jobs.append(data)
    return len(jobs)
@app.get("/")
def home():
    number=get_pending_jobs()
    return {
        "status": "running",
        "no_of_jobs": number
    }


@app.post("/add")
def add():

    data = request.get_json(
        force=True
    )

    url = data.get(
        "url",
        ""
    ).strip()

    folder_id = data.get(
        "folderId",
        ""
    ).strip()

    if not url:

        return (
            jsonify(
                {
                    "success": False,
                    "message": "url required"
                }
            ),
            400
        )

    doc = db.collection(
        "downloadQueue"
    ).document()

    doc.set(

        {
            "url": url,
            "folderId": folder_id,
            "status": "pending",
            "createdAt": int(time.time())
        }

    )

    return {

        "success": True,
        "jobId": doc.id

    }


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
