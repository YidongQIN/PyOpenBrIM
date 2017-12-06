import xml.etree.ElementTree as ET

# ParamML XML file
## read XML
def read_xml(in_path):
	tree = ET.parse(in_path)
	return tree
## write XML
def write_xml(tree, out_path):
	tree.write(out_path, encoding="utf-8",xml_declaration=True)
# search
##
def if_match(node, kv_map):
    '''''判断某个节点是否包含所有传入参数属性
       node: 节点
       kv_map: 属性及属性值组成的map'''
    for key in kv_map:
        if node.get(key) != kv_map.get(key):
            return False
    return True

def get_node_by_keyvalue(nodelist, kv_map):
    '''根据属性及属性值定位符合的节点，返回节点
       nodelist: 节点列表
       kv_map: 匹配属性及属性值map'''
    result_nodes = []
    for node in nodelist:
        if if_match(node, kv_map):
            result_nodes.append(node)
    return result_nodes

# ----main----
tree = read_xml('0 MARC.xml')
root = tree.getroot()


