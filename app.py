from flask import Flask, request, render_template
from parse_entry import Entry
app = Flask(__name__)
app.config["APPLICATION_ROOT"] = "/ddo"


@app.route("/")
def lookup():
    query = request.args.get("query")
    select = request.args.get("select", "")
    if query is None:
        return render_template("default.html")
    else:
        try:
            entry = Entry(query, select)
        except ValueError:
            return render_template("default.html")
        return render_template("definition.html", entry=entry)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
