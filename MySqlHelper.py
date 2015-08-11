# !/usr/bin/env python
# coding=utf-8
import MySQLdb


def execute(db_info_list, sql_cmd):
    """

    :rtype : None
    """
    password = db_info_list[1]
    db = db_info_list[2]
    conn = MySQLdb.connect(host='localhost', user='root', passwd=password, db=db)
    cursor = conn.cursor()
    cursor.execute(sql_cmd)
    conn.commit()
    cursor.close()
    conn.close()


def insert(db_info_list, values, sql_cmd):  # list contains [user ,password, db_name]
    """
    :type values: list of tuples
    """
    password = db_info_list[1]
    db = db_info_list[2]
    conn = MySQLdb.connect(host='localhost', user='root', passwd=password, db=db)
    # conn.select_db('python');
    cursor = conn.cursor()
    # cursor.executemany("""insert into test values(%s,%s) """ , values);
    cursor.executemany(sql_cmd, values)
    conn.commit()
    cursor.close()
    conn.close()


def select(db_info_list, sql_cmd):
    """

    :rtype : list of tuples
    """
    password = db_info_list[1]
    db = db_info_list[2]
    conn = MySQLdb.connect(host='localhost', user='root', passwd=password, db=db)
    cursor = conn.cursor()
    count = cursor.execute(sql_cmd)
    print 'in all %d records' % count
    # print "fetch one:"
    # result = cursor.fetchone();
    # print result
    # print 'ID: %s   info: %s' % (result[0], result[1])
    # print 'ID: %s   info: %s' % result

    # print "get only 5 recodes:"
    # results = cursor.fetchmany(5)
    # for r in results:
    #     print r
    # print "get all records:"
    # cursor.scroll(0, mode='absolute')

    results = cursor.fetchall()
    for r in results:
        print r
    cursor.close()
    conn.close()
    return results

