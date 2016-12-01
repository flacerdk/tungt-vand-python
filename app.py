from flask import Flask, request, render_template, redirect, url_for
from parse_entry import Entry
app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("entry.html")


@app.route("/ddo")
def lookup():
    query = request.args.get("query")
    select = request.args.get("select", "")
    if query is None:
        return redirect(url_for('/'))
    else:
        try:
            entry = Entry(query, select)
        except ValueError:
            return render_template("entry.html")
        return render_template(
            'entry.html',
            title=entry.title["title"]["title"],
            pronunciations=entry.pronunciations["pronunciations"],
            definitions=entry.definitions["definitions"],
            faste_udtryk=entry.faste_udtryk["definitions"],
            suggestions=entry.suggestions["suggestions"],
            bojning=entry.inflection["inflection"]
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
