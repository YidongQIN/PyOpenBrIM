# import ClassPyOpenBrIM
from ClassPyOpenBrIM import *

newproj = PyOpenBrIMElmt('new proj')
newproj.read_xmlfile('xml file/new proj.xml')
# newproj.findall_by_xpath('.//','Y')
# print('---find all sub by key&value test----')
# results=newproj.findall_by_attribute(N='test param')
# print(results)
# print(newproj.verify_attributes(T='Project'))
# ResultsTable(results)
# newproj.save_project()
newproj.show_info('','Y')
print('---add sub nodes test---')
new_node = ObjElmt('Line', 'object name', D='description of object', UC='test')
# newproj.add_sub(new_node)
new_node2 = ObjElmt('Not Line', 'object2', D='des')
# new_par = PrmElmt('test param', '666', 'de', par_type='p_tag')
# new_node2.add_sub(new_par)
#@TODO
newproj.add_sub([new_node2,new_node])
newproj.show_info('','Y')

# print('--- change attribute test ---')
# newproj.show_sub()
# new_node2.update(D='this has been changed!')
# point1 = Point(1,2,0.2,'point1 has no name')
# print(point1.elmt.attrib)
# newproj.add_sub(point1)
# point1.show_self()
# newproj.del_sub('P',N='Fc28')
# newproj.show_sub()
# newproj.save_project()