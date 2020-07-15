import os
import secrets
import sys

from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from flask import Flask, redirect, request, session, url_for
from minisaml.request import get_request_redirect_url
from minisaml.response import validate_response

app = Flask(__name__)
app.secret_key = secrets.token_bytes()


@app.route("/")
def hello():
    if "user" in session:
        return f"Hello, {session['user']}"
    else:
        acs_url = url_for("acs", _external=True)
        return redirect(
            get_request_redirect_url(
                saml_endpoint=endpoint, expected_audience=AUDIENCE, acs_url=acs_url
            )
        )


@app.route("/acs/", methods=["POST"])
def acs():
    raw_response = request.form["SAMLResponse"].encode("ascii")
    try:
        response = validate_response(
            data=raw_response, certificate=certificate, expected_audience=AUDIENCE
        )
    except Exception as e:
        return f"Invalid SAML Response {e!r}"
    session["user"] = response.name_id
    return redirect("/")


try:
    with open(os.environ["MINISAML_CERT_PEM_PATH"], "rb") as fobj:
        certificate = load_pem_x509_certificate(fobj.read(), default_backend())
except KeyError:
    print(
        "You must set the MINISAML_CERT_PEM_PATH environment variable to point to the IdP certificate to use"
    )
    sys.exit(1)

try:
    endpoint = os.environ["MINISAML_ENDPOINT"]
except KeyError:
    print(
        "You must set the MINISAML_ENDPOINT environment variable to point to the URL of the IdP SAML endpoint"
    )
    sys.exit(1)

try:
    AUDIENCE = os.environ["MINISAML_AUDIENCE"]
except KeyError:
    print(
        "You must set the MINISAML_AUDIENCE environment variable to point to Issuer value for your IdP"
    )
    sys.exit(1)


if __name__ == "__main__":
    app.run(port=os.environ.get("PORT", 5000))
