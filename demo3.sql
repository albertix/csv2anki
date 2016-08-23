PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE col (
    id              integer primary key,
    crt             integer not null,
    mod             integer not null,
    scm             integer not null,
    ver             integer not null,
    dty             integer not null,
    usn             integer not null,
    ls              integer not null,
    conf            text not null,
    --{"nextPos": 1, "estTimes": true, "activeDecks": [1], "sortType": "noteFld", "timeLim": 0, "sortBackwards": false, "addToCur": true, "curDeck": 1, "newBury": true, "newSpread": 0, "dueCounts": true, "curModel": "1471353286236", "collapseTime": 1200}

    models          text not null,
    --{"1471346850690": 
    --  {"vers": [],
    --   "name": "\u57fa\u7840", "tags": [], "did": 1, "usn": -1, "req": [[0, "all", [0]]],
    --   "sortf": 0,
    --   "flds": [
    --     {"name": "xxxxxxxxx",
    --      "media": [],
    --      "sticky": false,
    --      "rtl": false,
    --      "ord": 0,
    --      "font": "Arial",
    --      "size": 20}, {"name": "\u80cc\u9762", "media": [], "sticky": false, "rtl": false, "ord": 1, "font": "Arial", "size": 20}],
    --   "tmpls": [
    --     {"name": "\u5361\u72471",
    --      "qfmt": "{{xxxxxxxxx}}",
    --      "did": null,
    --      "bafmt": "",
    --      "afmt": "{{FrontSide}}\n\n<hr id=answer>\n\n{{\u80cc\u9762}}",
    --      "ord": 0,
    --      "bqfmt": ""}],
    --   "mod": 1471352390,
    --   "latexPost": "\\end{document}",
    --   "type": 0,
    --   "id": "1471346850690",
    --   "css": ".card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n",
    --   "latexPre": "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\begin{document}\n"
    -- }}

    decks           text not null,
    --{"1": {"name": "\u9ed8\u8ba4", "extendRev": 50, "usn": 0, "collapsed": false, "newToday": [0, 0], "timeToday": [0, 0], "dyn": 0, "extendNew": 10, "conf": 1, "revToday": [0, 0], "lrnToday": [0, 0], "id": 1, "mod": 1471353286, "desc": ""}}

    dconf           text not null,
    --{"1": {"name": "Default", "replayq": true, "lapse": {"leechFails": 8, "minInt": 1, "delays": [10], "leechAction": 0, "mult": 0}, "rev": {"perDay": 100, "ivlFct": 1, "maxIvl": 36500, "minSpace": 1, "ease4": 1.3, "bury": true, "fuzz": 0.05}, "timer": 0, "maxTaken": 60, "usn": 0, "new": {"separate": true, "delays": [1, 10], "perDay": 20, "ints": [1, 4, 7], "initialFactor": 2500, "bury": true, "order": 1}, "autoplay": true, "id": 1, "mod": 0}}

    tags            text not null
);
<<<<<<< HEAD
INSERT INTO "col" VALUES(1,1471291200,1471353286239,1471353286235,11,0,0,0,
'{"nextPos": 1, "estTimes": true, "activeDecks": [1], "sortType": "noteFld", "timeLim": 0, "sortBackwards": false, "addToCur": true, "curDeck": 1, "newBury": true, "newSpread": 0, "dueCounts": true, "curModel": "1471353286236", "collapseTime": 1200}',
'{"1471346850690": {"vers": [], "name": "\u57fa\u7840", "tags": [], "did": 1, "usn": -1, "req": [[0, "all", [0]]], "flds": [{"name": "xxxxxxxxx", "media": [], "sticky": false, "rtl": false, "ord": 0, "font": "Arial", "size": 20}, {"name": "\u80cc\u9762", "media": [], "sticky": false, "rtl": false, "ord": 1, "font": "Arial", "size": 20}], "sortf": 0, "tmpls": [{"name": "\u5361\u72471", "qfmt": "{{xxxxxxxxx}}", "did": null, "bafmt": "", "afmt": "{{FrontSide}}\n\n<hr id=answer>\n\n{{\u80cc\u9762}}", "ord": 0, "bqfmt": ""}], "mod": 1471352390, "latexPost": "\\end{document}", "type": 0, "id": "1471346850690", "css": ".card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n", "latexPre": "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\begin{document}\n"}}',
'{"1": {"name": "\u9ed8\u8ba4", "extendRev": 50, "usn": 0, "collapsed": false, "newToday": [0, 0], "timeToday": [0, 0], "dyn": 0, "extendNew": 10, "conf": 1, "revToday": [0, 0], "lrnToday": [0, 0], "id": 1, "mod": 1471353286, "desc": ""}}',
'{"1": {"name": "Default", "replayq": true, "lapse": {"leechFails": 8, "minInt": 1, "delays": [10], "leechAction": 0, "mult": 0}, "rev": {"perDay": 100, "ivlFct": 1, "maxIvl": 36500, "minSpace": 1, "ease4": 1.3, "bury": true, "fuzz": 0.05}, "timer": 0, "maxTaken": 60, "usn": 0, "new": {"separate": true, "delays": [1, 10], "perDay": 20, "ints": [1, 4, 7], "initialFactor": 2500, "bury": true, "order": 1}, "autoplay": true, "id": 1, "mod": 0}}',
'{}');
=======
INSERT INTO "col" VALUES(1,1471291200,1471353286239,1471353286235,11,0,0,0,'','','','','{}');
>>>>>>> c92a960c30cd1560bfccfc051cec0597e10563b8
CREATE TABLE notes (
    id              integer primary key,   /* 0 */
    guid            text not null,         /* 1 */
    mid             integer not null,      /* 2 */
    mod             integer not null,      /* 3 */
    usn             integer not null,      /* 4 */
    tags            text not null,         /* 5 */
    flds            text not null,         /* 6 */
    sfld            integer not null,      /* 7 */
    csum            integer not null,      /* 8 */
    flags           integer not null,      /* 9 */
    data            text not null          /* 10 */
);
INSERT INTO "notes" VALUES(1471348041425,'fNmt(k[<z,',1471346850690,1471348049,-1,'','ab','a',2264392759,0,'');
INSERT INTO "notes" VALUES(1471352378949,'lb6TMLp7eu',1471346850690,1471352390,-1,'','tttttttttttttttttttttttttsssssssssssssss','ttttttttttttttttttttttttt',1247077238,0,'');
CREATE TABLE cards (
    id              integer primary key,   /* 0 */
    nid             integer not null,      /* 1 */
    did             integer not null,      /* 2 */
    ord             integer not null,      /* 3 */
    mod             integer not null,      /* 4 */
    usn             integer not null,      /* 5 */
    type            integer not null,      /* 6 */
    queue           integer not null,      /* 7 */
    due             integer not null,      /* 8 */
    ivl             integer not null,      /* 9 */
    factor          integer not null,      /* 10 */
    reps            integer not null,      /* 11 */
    lapses          integer not null,      /* 12 */
    left            integer not null,      /* 13 */
    odue            integer not null,      /* 14 */
    odid            integer not null,      /* 15 */
    flags           integer not null,      /* 16 */
    data            text not null          /* 17 */
);
INSERT INTO "cards" VALUES(1471348049592,1471348041425,1,0,1471348049,-1,0,0,1,0,0,0,0,0,0,0,0,'');
INSERT INTO "cards" VALUES(1471352390054,1471352378949,1,0,1471352390,-1,0,0,2,0,0,0,0,0,0,0,0,'');
CREATE TABLE revlog (
    id              integer primary key,
    cid             integer not null,
    usn             integer not null,
    ease            integer not null,
    ivl             integer not null,
    lastIvl         integer not null,
    factor          integer not null,
    time            integer not null,
    type            integer not null
);
CREATE TABLE graves (
    usn             integer not null,
    oid             integer not null,
    type            integer not null
);
ANALYZE sqlite_master;
INSERT INTO "sqlite_stat1" VALUES('col',NULL,'1');
CREATE INDEX ix_notes_usn on notes (usn);
CREATE INDEX ix_cards_usn on cards (usn);
CREATE INDEX ix_revlog_usn on revlog (usn);
CREATE INDEX ix_cards_nid on cards (nid);
CREATE INDEX ix_cards_sched on cards (did, queue, due);
CREATE INDEX ix_revlog_cid on revlog (cid);
CREATE INDEX ix_notes_csum on notes (csum);
COMMIT;
