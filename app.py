from flask import Flask, request, render_template, redirect, url_for
from parse_entry import Entry
app = Flask(__name__)
app.config["APPLICATION_ROOT"] = "/ddo"


@app.route("/")
def lookup():
    print("hi")
    query = request.args.get("query")
    select = request.args.get("select", "")
    if query is None:
        return render_template("entry.html")
    else:
        try:
            entry = Entry(query, select)
        except ValueError:
            return render_template("entry.html")
        return render_template(
            'entry.html',
            title=entry.title,
            pronunciations=entry.pronunciations,
            definitions=entry.definitions,
            faste_udtryk=entry.faste_udtryk,
            suggestions=entry.suggestions,
            bojning=entry.inflection
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
