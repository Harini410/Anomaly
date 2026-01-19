import pandas as pd
from flask import Flask, jsonify, render_template
import os

app = Flask(__name__)

def compute_risk():
    files = pd.read_csv("data/file_events.csv")
    net = pd.read_csv("data/network_edges.csv")

    files["score"] = files["encrypt_ops"]*3 + files["rename_ops"]*2
    risk = files.groupby("asset")["score"].sum().reset_index()

    high_risk = risk[risk["score"] > 25]["asset"].tolist()
    for _, row in net.iterrows():
        if row["src"] in high_risk:
            risk.loc[risk["asset"] == row["dst"], "score"] += 6

    risk["priority"] = pd.cut(
        risk["score"],
        bins=[-1,8,25,1000],
        labels=["P4","P3","P1"]
    )
    return risk.sort_values("score", ascending=False)

@app.route("/")
def dashboard():
    return render_template("dashboard.html", data=compute_risk().to_dict(orient="records"))

@app.route("/prioritize")
def prioritize():
    return jsonify(compute_risk().to_dict(orient="records"))

@app.route("/scan")
def scan():
    risk = compute_risk()
    return jsonify({"scan_targets": risk[risk["priority"].isin(["P1","P3"])]["asset"].tolist()})

@app.route("/recover")
def recover():
    risk = compute_risk()
    return jsonify({"recovery_order": risk["asset"].tolist()})

@app.route("/dashboard")
def full_dashboard():
    risk = compute_risk()
    files = pd.read_csv("data/file_events.csv")
    net = pd.read_csv("data/network_edges.csv")

    p1 = risk[risk["priority"] == "P1"]

    resources = [
        "File activity logs",
        "Network telemetry",
        "Compute resources for scan",
        "Backup repositories"
    ]

    return render_template(
        "full_dashboard.html",
        resources=resources,
        assets=risk.to_dict(orient="records"),
        file_data=files.to_dict(orient="records"),
        net_data=net.to_dict(orient="records"),
        p1_assets=p1.to_dict(orient="records")
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
