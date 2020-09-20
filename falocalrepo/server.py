from copy import deepcopy
from json import loads as json_loads
from os.path import abspath
from os.path import dirname
from os.path import isfile
from os.path import join
from os.path import split
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from flask import Flask
from flask import abort
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file

from .__version__ import __version__
from .commands import journals_search
from .commands import submissions_search
from .database import Connection
from .database import connect_database
from .database import keys_journals
from .database import keys_submissions
from .database import select
from .database import tiered_path
from .settings import setting_read

app: Flask = Flask(
    "FurAffinity Local Repo",
    template_folder=join(abspath(dirname(__file__)), "server_templates")
)
last_search: dict = {
    "table": "",
    "order": [],
    "params": {},
    "results": []
}


@app.route("/favicon.ico")
def favicon():
    return redirect("https://www.furaffinity.net/favicon.ico")


@app.route("/")
def root():
    db_temp: Connection = connect_database("FA.db")
    sub_n: int = int(setting_read(db_temp, "SUBN"))
    usr_n: int = int(setting_read(db_temp, "USRN"))
    last_update: float = float(setting_read(db_temp, "LASTUPDATE"))
    version: str = setting_read(db_temp, "VERSION")
    db_temp.close()

    return render_template(
        "root.html",
        title=app.name,
        submissions_total=sub_n,
        users_total=usr_n,
        last_update=last_update,
        version=__version__,
        version_db=version,
    )


@app.route("/search/")
def search_default():
    return redirect("/search/submissions/")


@app.route("/search/submissions/")
def search_submissions():
    return search("submissions")


@app.route("/search/journals/")
def search_journals():
    return search("journals")


def search(table: str):
    global last_search

    if request.args:
        params: Dict[str, List[str]] = dict(map(
            lambda kv: (kv[0], json_loads(kv[1])),
            request.args.items()
        ))
        order: List[str] = params.get("order", ["AUTHOR", "ID"])
        limit: int = 50
        offset: int = params.get("offset", 0)
        offset = 0 if offset < 0 else offset

        if "order" in params:
            del params["order"]
        if "limit" in params:
            del params["limit"]
        if "offset" in params:
            del params["offset"]

        if last_search["table"] != table or last_search["order"] != table or last_search["params"] != params:
            last_search["table"] = table
            last_search["order"] = deepcopy(order)
            last_search["params"] = deepcopy(params)
            db_temp: Connection = connect_database("FA.db")
            if table == "submissions":
                last_search["results"] = submissions_search(db_temp, order=order, **params)
            elif table == "journals":
                last_search["results"] = journals_search(db_temp, order=order, **params)
            db_temp.close()

        return render_template(
            "search_results.html",
            title=f"{app.name} · {table.title()} Search Results",
            table=table,
            params=params,
            limit=limit,
            offset=offset,
            results=last_search["results"][offset:offset + limit],
            results_total=len(last_search["results"]),
            keys=keys_submissions
        )
    else:
        return render_template(
            "search.html",
            title=f"{app.name} · Search {table.title()}",
            table=table
        )


@app.route("/user/<username>/")
def user(username: str):
    return redirect(f'/search/submissions/?author=["{username}"]')


@app.route("/submission/<int:id_>/file/")
def submission_file(id_: int):
    db_temp: Connection = connect_database("FA.db")
    sub_dir: str = join(setting_read(db_temp, "FILESFOLDER"), *split(tiered_path(id_)))
    sub_ext: Optional[Tuple[str]] = select(db_temp, "SUBMISSIONS", ["FILEEXT"], "ID", id_).fetchone()
    db_temp.close()

    if isfile(path := join(sub_dir, f"submission.{sub_ext[0]}")):
        return send_file(path)
    else:
        return abort(404)


@app.route("/journal/<int:id_>/")
def journal(id_: int):
    db_temp: Connection = connect_database("FA.db")
    jrnl: Optional[tuple] = select(db_temp, "JOURNALS", ["*"], "ID", id_).fetchone()
    db_temp.close()

    if jrnl is None:
        return abort(404)

    return render_template(
        "journal.html",
        title=f"{app.name} · {jrnl[keys_journals.index('TITLE')]} by {jrnl[keys_journals.index('AUTHOR')]}",
        journal=jrnl,
        keys=keys_journals
    )


@app.route("/submission/<int:id_>/")
def submission(id_: int):
    db_temp: Connection = connect_database("FA.db")
    sub: Optional[tuple] = select(db_temp, "SUBMISSIONS", ["*"], "ID", id_).fetchone()
    db_temp.close()

    if sub is None:
        return abort(404)

    file_type: Optional[str] = ""
    if (ext := sub[keys_submissions.index('FILEEXT')]) in ("jpg", "jpeg", "png", "gif"):
        file_type = "image"
    elif not ext:
        file_type = None

    return render_template(
        "submission.html",
        title=f"{app.name} · {sub[keys_submissions.index('TITLE')]} by {sub[keys_submissions.index('AUTHOR')]}",
        sub_id=id_,
        submission=sub,
        file_type=file_type,
        keys=keys_submissions
    )


def server(host: str = "0.0.0.0", port: int = 8080):
    app.run(host=host, port=port)
