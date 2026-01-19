import pandas as pd
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/prioritize")
def prioritize():
    files = pd.read_csv("data/file_events.csv")
    net = pd.read_csv("data/network_edges.csv")

    files["score"] = files["encrypt_ops"]*3 + files["rename_ops"]*2
    risk = files.groupby("asset")["score"].sum().reset_index()

    risk["priority"] = pd.cut(
        risk["score"],
        bins=[-1,5,20,1000],
        labels=["P4","P3","P1"]
    )
    return jsonify(risk.to_dict(orient="records"))

if __name__ == "__main__":
    app.run()
