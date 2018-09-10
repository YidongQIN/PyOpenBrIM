#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Yidong QIN'

"""
PyELMT gets all interfaces' methods.
Each PyELMT has 3 kinds of attributes:
1. distinguished naming: type and _id.
2. characteristic attr: depends on element typy.
    For example, Material will have E=elastic modulel, d=density, etc.
    Whie Parameter will only have a value.
3. Interfaces, including a OpenBrIM interface, a MongoDB interface so far.
    Each Interface will be a combination of setter() and getter().
"""
import json

from Interfaces import *


class PyELMT(object):

    def __init__(self, elmt_type, elmt_id, elmt_name=None):
        """Basic mandatory attributes of PyELMT are type, id;
        the optional attribute is name."""
        self._id = elmt_id
        self.type = elmt_type
        if elmt_name:
            self.name = elmt_name
        else:
            self.name = elmt_type + '_' + str(elmt_id)
        # two interfaces: Database and OpenBrIM
        self.db_config = dict()  # dict(database=, table=, user=,...)
        self.openBrIM: dict or PyOpenBrIMElmt  # dict of eET.elements



    def set_openbrim(self, ob_class: (OBPrmElmt, OBObjElmt), **attrib_dict: dict):
        """attrib_dict is used to add other redundancy info,
        so don't update the element.__dict__ with it."""
        # get attributes required by the OpenBrIM type
        _required_attr: dict = _attr_pick(self, *ob_class._REQUIRE)
        # _openbrim_attrib = {**_required_attr, **attrib_dict}
        try:
            _ob_model: PyOpenBrIMElmt = ob_class(**_required_attr, **attrib_dict)
            return _ob_model
        except TypeError as e:
            print("TypeError: <{}>.set_openbrim()".format(self.name), e)
            return

    def get_openbrim(self, model_class: str = None):
        if not model_class:
            return self.openBrIM
        else:
            try:
                return self.openBrIM[model_class]
            except KeyError:
                print("{} has no OpenBrIM model of {}".format(self.name, model_class))
                return

    def set_sap2k(self):
        pass

    def get_sap2k(self):
        pass

    def update_attr(self, **attributes_dict: dict):
        for _k, _v in attributes_dict.items():
            try:
                if not _v == self.__dict__[_k]:
                    print('<{}> changed by update_attr()'.format(self.name))
                    print('* {} -> {}'.format(_k, _v))
            except KeyError:
                print("<{}> new attribute by update_attr()".format(self.name))
                print('* {} -> {}'.format(_k, _v))
            self.__dict__[_k] = _v



    def _set_mysql_config(self, database, user, password, host='localhost', port=3306, **kwargs):
        """get db config and connect to MySQL"""
        self.db_config = {'user': user, 'password': password, 'database': database,
                          'host': host, 'port': port}
        if 'table' not in kwargs.keys():
            print('The table/collection name is needed')
        self.db_config['table'] = kwargs['table']

    def link_elmt(self, attrib, elmt):
        """link the PyELMT to another PyELMT."""
        self.__dict__[attrib] = elmt
        self.__dict__["{}_ob".format(attrib)] = elmt.openBrIM
        self.__dict__["{}_id".format(attrib)] = elmt._id
        """
        option #1, only one attribute is linked, the PyELMT. Then in the set_openbrim() method, use a try...block to find corresponding ob node.
        #2, in the interfaces.__init__, create a new class, much like the PyOpenBrIM, to accept the OB type and variables together.
        """


class Document(object):
    """Document only store in MongoDB or file, no OpenBrIm eET.
    The class name is not sure yet."""

    def __init__(self, name, id=None, des=None):
        self.name = name
        self._id = id
        if des:
            self.des = des

    def set_mongo_doc(self):
        """write info into the mongo.collection.document"""
        with ConnMongoDB(**self.db_config) as _db:
            _col = self.db_config['table']
            if not self._id:
                self._id = _db.insert_data(_col, **_attr_to_mongo_dict(self))
            elif not _db.find_by_kv(_col, 'name', self.name):
                _ = _db.update_data(_col, self._id, **_attr_to_mongo_dict(self))
            else:
                _db.update_data(_col, self._id, **_attr_to_mongo_dict(self))
                print("<{}> is in <{}>, ObjectID={}".format(self.name, _col, self._id))

    def get_mongo_doc(self, if_print=False):
        with ConnMongoDB(**self.db_config) as _db:
            _result = _db.find_by_kv(self.db_config['table'], '_id', self._id, if_print)
            self.update_attr(_result)
            return _result

    def set_file(self, file_path=None):
        """write the attributes into JSON"""
        _j = json.dumps(self.__dict__, indent=2)
        if not file_path:
            file_path = "{}.json".format(self.name)
        with open(file_path, 'w') as _f:
            _f.write(_j)
        print("<{}> data stored in {}".format(self.name, file_path))

    def update_attr(self, **attributes_dict):
        for _k, _v in attributes_dict.items():
            try:
                if not _v == self.__dict__[_k]:
                    print('<{}> changed by update_attr()'.format(self.name))
                    print(' .{} -> {}'.format(_k, _v))
            except KeyError:
                print("<{}> new attribute by update_attr()".format(self.name))
                print(' .{} -> {}'.format(_k, _v))
            self.__dict__[_k] = _v

    def set_dbconfig(self, database, table, host='localhost', port=27017):
        self.db_config = {'host': host, 'port': port,
                          'database': database, 'table': table}




# def parameter_format(k):
#     if isinstance(k, int):
#         return k
#     elif isinstance(k, float):
#         try:
#             return int(k)
#         except ValueError:
#             return k
#     elif isinstance(k, str):
#         try:
#             return float(k)
#         except ValueError:
#             return k
#     else:
#         from BMS_BrIM.Py_Abstract import Parameter
#         if isinstance(k, Parameter):
#             return k.value
#         else:
#             print("Error formatting parameter")
#             print(type(k))
#             return

# class XY(object):
#     def __init__(self, x=0, y=0):
#         if x is not None:
#             self.x = parameter_format(x)
#         if y is not None:
#             self.y = parameter_format(y)
#
#
# class XYZ(object):
#
#     def __init__(self, x=0, y=0, z=0):
#         if x is not None:
#             self.x = parameter_format(x)
#         if y is not None:
#             self.y = parameter_format(y)
#         if z is not None:
#             self.z = parameter_format(z)
#
#
# class RXYZ(object):
#
#     def __init__(self, rx=0, ry=0, rz=0):
#         self.rx = rx
#         self.ry = ry
#         self.rz = rz
