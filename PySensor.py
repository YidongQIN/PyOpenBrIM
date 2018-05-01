__author__ = 'Yidong QIN'

'''
Sensors definition in OpenBrIM
'''

import matplotlib.pyplot as plt
import numpy as np

from PyOBobjects import *


class Sensor(ObjElmt):
    base_node: FENode

    def __init__(self, sensor_id, sensor_type, des: str, database_config: dict):
        super(Sensor, self).__init__('Sensor', sensor_id, D=des)
        self.id = sensor_id
        self.type = sensor_type
        self.name = '{}_{}'.format(sensor_type[0:4], sensor_id)
        dbconfig = dict(database_config)
        # db = database_config.copy()
        try:
            self.datpath = dbconfig.pop('path')
            # fileName is from the Server Setting JSON
        except KeyError:
            print('For the sensor <{}>,a "path" item is required in the config dictionary'.format(self.name))
        self.dbconfig = dbconfig  # user, passwd, host, database, port
        # self.x, self.y, self.z, self.dx, self.dy, self.dz
        self.get_install()
        self.get_dimension()
        self.get_backup_filename()

    def read_table(self, tbname, *col_names):
        db = ConnMySQL(**self.dbconfig)
        sql = 'select {} from bridge_test.{} where sensorID ={}'.format(", ".join(col_names), tbname, self.id)
        db.query(sql)
        info = db.fetch_row()
        db.close()
        return info

    def print_dbinfo(self, tbname, *col_names ):
        info = self.read_table(tbname, *col_names)
        for i in range(len(info)):
            print('{}: {}'.format(col_names[i], info[i]))


    def read_dat(self):
        DatProc(self.datpath)

    def get_install(self):
        self.x, self.y, self.z, self.dx, self.dy, self.dz = self.read_table('sensorchannelinstallation', 'PositionX', 'PositionY', 'PositionZ', 'DirectionX', 'DirectionY', 'DirectionZ')
        return self.x, self.y, self.z, self.dx, self.dy, self.dz


    def get_dimension(self, dimension1=10, dimension2=10, dimension3=10):
        self.fac, self.model = self.read_table('sensor', 'manufacturerName', 'modelNumber')
        self.width, self.length, self.thick =self.read_table('sensorchannelinstallation', 'dimension1', 'dimension2', 'dimension3')
        if not self.width:
            self.width = dimension1
        if not self.length:
            self.width = dimension2
        if not self.thick:
            self.width = dimension3
        return self.fac, self.width, self.width, self.length, self.thick

    def get_backup_filename(self):
        """fileName is U{unitID}_{ChannelID}.dat"""
        self.unitid, self.channel = self.read_table('sensorchannelinstallation','wirelessUnitId','channelID')
        self.datpath = '{}\\{}_{}.dat'.format(self.datpath, self.unitid, self.channel)
        # return self.datpath

    def geom(self):
        """ OpenBrIM geometry model"""
        if not (self.x, self.y, self.z):
            print('Sensor {} position information is required'.format(self.name))
        if not (self.dx, self.dy, self.dz):
            print('Sensor {} direction information is required'.format(self.name))

    def set_base_node(self, fenode):
        if isinstance(fenode, FENode):
            self.base_node = fenode
        else:
            print('{}.base_node is not a FENode'.format(self.name))

    def fem(self):
        """FEM model. For sensor, it's just a node."""
        node = FENode(self.x, self.y, self.z, self.name)
        # not sure if realizable?
        # when create a FEM, cannot insert the node into this position
        # because it will change the node number and element
        return node


class Temperature(Sensor):
    def __init__(self, tp_id, des, database_config):
        super(Temperature, self).__init__(tp_id, 'Temperature', des, database_config)

    def geom(self):
        pass

    def fem(self):
        pass


class StrainGauge(Sensor):
    def __init__(self, sg_id, des, database_config):
        super(StrainGauge, self).__init__(sg_id, 'strainGauge', des, database_config)
        # self.name = 'SG{}'.format(sg_id)
        # self.id = sg_id

    def geom(self):
        ss = Surface(Point(-self.length / 2, -self.width / 2),
                     Point(self.length / 2, -self.width / 2),
                     Point(self.length / 2, self.width / 2),
                     Point(-self.length / 2, self.width / 2),
                     thick_par=1,
                     material_obj='Sensor_StrainGauge',
                     surface_name=self.name)
        ss.add_attr(Color='#DC143C')
        ss.move_to(self.x, self.y, self.z)
        ss.rotate(self.dx, self.dy, self.dz)
        return ss


class Accelerometer(Sensor):
    def __init__(self, ac_id, des, database_config):
        super(Accelerometer, self).__init__(ac_id, 'accelerometer', des, database_config)
        # self.name = 'AC{}'.format(ac_id)
        # self.id = ac_id

    def geom(self):
        ac = Cuboid(self.width, self.length, self.thick)
        ac.add_attr(Color='#DC143C')
        ac.move_to(self.x, self.y, self.z)
        ac.rotate(self.dx, self.dy, self.dz)
        return ac


class Displacement(Sensor):
    def __init__(self, ds_id, des, database_config):
        super(Displacement, self).__init__(ds_id, 'Displacement', des, database_config)
        self.name = 'DS{}'.format(ds_id)
        self.id = ds_id

    def geom(self):
        line = Line(Point(0, 0, 0), Point(self.length, 0, 0), section=Section('','',Circle('',1)))
        box = Cuboid(self.width, self.width, self.thick)
        box.move_to(self.length / 2, 0, -self.thick/2)
        ds = Group(self.name, line, box)
        ds.add_attr(Color='#DC143C')
        ds.move_to(self.x, self.y, self.z)
        ds.rotate(self.dx, self.dy, self.dz)
        return ds


class DatProc(object):

    def __init__(self, file_path='Server//backup//.dat'):
        self.data = np.loadtxt(file_path)
        self.plot()

    def plot(self):
        plt.plot(self.data)
        plt.show()
