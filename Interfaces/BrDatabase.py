# usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Yidong QIN'

"""
BrIM use database to store the information of elements.
structural members, like beams, columns, are stored in NoSQL
and non-structural members, such as sensor, etc.

"""

import mysql.connector as mc
import pymongo as mg


class ConnMySQL(object):

    def __init__(self, database, user, password, host, port, **kwargs):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.othersetting = kwargs
        self.conn = mc.connect(host=self.host, port=self.port,
                               user=self.user, password=self.password)
        self.conn.autocommit = True
        self.cur = self.conn.cursor(buffered=True)
        # charset = "utf8mb4"
        # self.charset = charset

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb:
            print('\nSQL Error Type : {}\n'
                  '--- Error Value: {}\n'
                  '--- Error is at: {}'.format(exc_type, exc_val, exc_tb))
        self.close()

    def select_db(self, db):
        try:
            self.conn.select_db(db)
        except mc.Error as e:
            print("Mysql Error {:d}: {}".format(e.args[0], e.args[1]))

    def query(self, sql):
        print("Executing SQL script:\n  '{}'".format(sql))
        try:
            n = self.cur.execute(sql)
            return n
        except mc.Error as e:
            print("MySQL Error: {}\n  with SQL: '{}'".format(e, sql))

    def fetch(self, fetch_type, with_description=False):
        if fetch_type is 'ALL':
            return self.fetch_all(with_description)  # return a list of tuples: [(),(),...]
        else:
            return self.fetch_row(with_description)  # return a tuple

    def fetch_row(self, with_description=False):
        result = self.cur.fetchone()
        if with_description:
            col_name = [i[0] for i in self.cur.describe]
            return dict((col, res) for col, res in zip(col_name, result))
        else:
            return result

    def fetch_all(self, with_description=False):
        result = self.cur.fetchall()  # a list of tuples
        col_name = [i[0] for i in self.cur.describe]  # cur.describe[0] = column name
        if with_description:
            d = []
            for oneline in result:
                d.append(dict((col, res) for col, res in zip(col_name, oneline)))
            return d
        else:
            return result

    def have_a_look(self, db_name, table_name):
        _sql = 'select * from {}.{} '.format(db_name, table_name)
        self.query(_sql)
        _result = self.fetch_all()
        for row in _result:
            print(row)

    def select(self, id_name, key_id, db_name, table_name, *col_name):
        _sql = 'select {} from {}.{} where {}={}' \
            .format(', '.join(col_name), db_name, table_name, id_name, key_id)
        print("Executing SQL script:\n  '{}'".format(_sql))
        self.query(_sql)

    def insert(self, table_name, data):
        columns = data.keys()
        _prefix = "".join(['INSERT INTO `', table_name, '`'])
        _fields = ",".join(["".join(['`', column, '`']) for column in columns])
        _values = ",".join(["%s"] * len(columns))
        # _values = ",".join(["%s" for i in range(len(columns))])
        _sql = "".join([_prefix, "(", _fields, ") VALUES (", _values, ")"])
        _params = [data[key] for key in columns]
        return self.cur.execute(_sql, tuple(_params))

    def update(self, tbname, data, condition):
        _fields = []
        _prefix = "".join(['UPDATE `', tbname, '`', 'SET'])
        for key in data.keys():
            _fields.append("%s = %s" % (key, data[key]))
        _sql = "".join([_prefix, _fields, "WHERE", condition])

        return self.cur.execute(_sql)

    def delete(self, tbname, condition):
        _prefix = "".join(['DELETE FROM  `', tbname, '`', 'WHERE'])
        _sql = "".join([_prefix, condition])
        return self.cur.execute(_sql)

    def get_last_insert_id(self):
        return self.cur.lastrowid

    def rowcount(self):
        return self.cur.rowcount

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.cur.close()
        self.conn.close()

    @property
    def backup_path(self):
        if 'path' in self.othersetting.keys():
            return self.othersetting['path']
        else:
            return 'No backup file path is provided for {}'.format(self)


class ConnMongoDB(object):

    def __init__(self, database, host='localhost', port=27017, **kwargs):
        self.host = host
        self.port = port
        self.db_name = database
        if 'table' in kwargs.keys():
            self.collection = kwargs['table']
        self.client = mg.MongoClient(self.host, self.port)
        self.db = self.client[self.db_name]
        # print("MongoDB connected.\n -  <{}> has collections of:\n\t{}".format(self.db_name, self.db.collection_names(False)))

    def __enter__(self, new_db_name=None):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # print('MongoDB connection finished')
        if exc_tb:
            print("Mongo Error Type : {}".format(exc_type))
            print("----- Error Value: {}".format(exc_val))
            print("----- Error is at: {}".format(exc_tb))

    def new_db(self,new_db_name):
        self.db_name = new_db_name
        self.db = self.client[self.db_name]

    def col_find_one(self, collection, condition):
        """ if the condition is not just one field"""
        _result = self.db[collection].find_one(condition)
        # _d={**_result}
        print("Searched in <{}> where {}".format(collection, condition))
        if _result:
            for _k,_v in _result.items():
                print(' -  ',_k, '=', _v)
        else:
            print(" -  NO document")
        return _result

    def col_find_all(self, collection, condition):
        """ if the condition is not just one field"""
        cursor = self.db[collection].find(condition)
        _l = [doc for doc in cursor]
        print("Searched in <{}> where {}".format(collection, condition))
        print(
            "Found {} document(s)".format(len(_l)))
        if _l:
            for a in _l:
                print("  - {}".format(a))
        return _l

    def find_by_kv(self, collection, key_field, value):
        """find one document and return a BSON"""
        _condition = {key_field: value}
        # print('find by kv',self.col_find_one(collection, _condition))
        return self.col_find_one(collection, _condition)

    def findall_by_kv(self, collection, key_field, value):
        """find all documents matched the condition, return a list"""
        _condition = {key_field: value}
        return self.col_find_all(collection, _condition)

    def have_a_look(self, collection):
        print("All documents in <{}> are:".format(collection))
        cursor = self.db[collection].find()
        for i in cursor:
            print('  - ' + str(i))

    def insert_data(self, collection, **data):
        try:
            return self.db[collection].insert({**data})
        except mg.errors.DuplicateKeyError as e:
            print("This document already exists")
            print(e)

    def update_data(self, collection, id, **data):
        try:
            self.db[collection].update({'_id': id}, data, True)
            # if self.find_by_kv(collection, '_id', data['id']):
        except KeyError as e:
            print(e)
            raise

    # below are methods for element, should not be use.
    # Mongo focus on the methods of CURD, not info process of element
    '''''''''
    def update_elmt(self, collection, elmt):
        """first find, then update or insert"""
        try:
            if self.find_by_kv(collection, '_id', elmt.id):
                print("Document <'_id'> = {} already exits".format(elmt.id))
            else:
                print('New document will be inserted.')
            self.update_data(collection, elmt.id, **self.modify_field_value(elmt))
            # self.db[collection].update({'_id': elmt.__dict__['id']}, self.modify_field_value(elmt), True)
        except AttributeError as e:
            print("The elmt <{}> does not have a <'id'> attribute".format(elmt.name or elmt))
            print(e)

    def insert_elmt(self, collection, elmt):
        """elmt has __dict__"""
        self.insert_data(collection, **self.modify_field_value(elmt))

    def delete_elmt(self, collection, elmt):
        try:
            if self.find_by_kv(collection, '_id', elmt.id):
                self.db[collection].delete_one({'_id': elmt.id})
                print('Successfully Delete the element whose id={}'.format(elmt.id))
            else:
                print('Cannot find such a document in Collection <{}> with id={}'.format(collection, elmt.id))
        except:
            print('Deleting element <{}> error'.format(elmt))
            raise

    @staticmethod
    def modify_field_value(elmt, *pop_list):
        """transfer the element to dict of attributes.
                        no empty attribute and change 'id' to '_id'. """
        from BMS_BrIM import ABrIMELMT
        assert isinstance(elmt, ABrIMELMT.PyElmt)
        field_value = dict()
        for _key, _value in elmt.__dict__.items():
            if _value:
                field_value[_key] = _value
        try:
            field_value['_id'] = field_value['id']
            print("Document's '_id' is {}".format(field_value['_id']))
            field_value.pop('id')
        except KeyError:
            print("No '_id' field contained, will be assigned automatically")
        for _pop in pop_list:
            field_value.pop(_pop)
        field_value.pop('openbrim')
        field_value.pop('db_config')
        return field_value
    '''''''''