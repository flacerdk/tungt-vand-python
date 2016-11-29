from flask import Flask, request, render_template
from parse_entry import Entry
app = Flask(__name__)


@app.route("/")
def hello():
    query = request.args.get("query")
    if query is None:
        return "Hello"
    else:
        entry = Entry(query)
        return render_template(
            'entry.html',
            title=entry.title["title"],
            pronunciations=entry.pronunciations["json"],
            definitions=entry.definitions["json"],
            faste_udtryk=entry.faste_udtryk["json"]
        )


if __name__ == "__main__":
    app.run()
