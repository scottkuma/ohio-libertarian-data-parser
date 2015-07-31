# STOP!  DON'T DELETE THIS FILE!  IT IS REFERENCED IN THESE SCRIPTS!

import sys
import sqlite3


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def first_startswith(stringtofind, fields):
    first = -1
    for i, j in enumerate(fields):
        if j.startswith(stringtofind) and first == -1:
            first = i
    return first


def last_startswith(stringtofind, fields):
    fields.reverse()
    first = len(fields) - (first_startswith(stringtofind, fields) + 1)
    fields.reverse()  # change this back to avoid problems
    return first


def open_db(nam):
    conn = sqlite3.connect(nam)
    # Let rows returned be of dict/tuple type
    conn.row_factory = sqlite3.Row
    print "Opened database %s as %r" % (nam, conn)
    return conn


def copy_table(table, src, dest):
    print "Copying %s %s => %s" % (table, src, dest)
    sc = src.execute('SELECT * FROM %s' % table)
    ins = None
    dc = dest.cursor()
    for row in sc.fetchall():
        if not ins:
            cols = tuple([k for k in row.keys() if k != 'id'])
            ins = 'INSERT OR REPLACE INTO %s %s VALUES (%s)' % (table, cols,
                                                     ','.join(['?'] * len(cols)))
            print 'INSERT stmt = ' + ins
        c = [row[c] for c in cols]
        print c
        dc.execute(ins, c)

    dest.commit()

def get_lean(row, FIRST_PRIMARY_FIELD, LAST_PRIMARY_FIELD):
    leaning = {}
    for x in xrange(FIRST_PRIMARY_FIELD, LAST_PRIMARY_FIELD):
        if row[x] not in ['', 'X']:
            if row[x] in leaning:
                leaning[row[x]] += 1
            else:
                leaning[row[x]] = 1
    leaningParty = ""
    maxLean = 0
    for l, num in leaning.iteritems():
        #print maxLean, l, num
        if num > maxLean:
            leaningParty = l
            maxLean = num
        elif num == maxLean:
            leaningParty = ""
    return leaningParty