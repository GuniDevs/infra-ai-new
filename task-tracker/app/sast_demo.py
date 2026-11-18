"""Deliberately vulnerable code for testing the Infra AI SAST check. Do not use."""
import hashlib
import pickle
import subprocess

import requests
import yaml
from flask import Flask, request

app = Flask(__name__)


@app.route("/ping")
def ping():
  host = request.args.get("host")
  return subprocess.check_output("ping -c 1 " + host, shell=True)


@app.route("/load", methods=["POST"])
def load():
  return str(pickle.loads(request.data))


@app.route("/config", methods=["POST"])
def config():
  return str(yaml.load(request.data))


def fingerprint(data: bytes) -> str:
  return hashlib.md5(data).hexdigest()


def partner_status() -> str:
  return requests.get("https://partner.example.com/status", verify=False, timeout=5).text


if __name__ == "__main__":
  app.run(debug=True)
