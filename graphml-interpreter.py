import csv, os, re
from bs4 import BeautifulSoup

def convert_list_to_string(list, delimiter):
  list_string = ''

  for item in list[:-1]:
    list_string = list_string + item + delimiter

  list_string = list_string + list[-1]

  return list_string

def convert_sorted_list_to_dictionary_with_sequence_index(list):
  dictionary_with_sequence_index = {}

  for index, value in enumerate(list):
    dictionary_with_sequence_index[value] = index + 1

  return dictionary_with_sequence_index

def create_csv_file_from_graphml_file(filename, source_directory, target_directory):
  data_file_full_path = source_directory + filename + '.graphml'
  group_sort_order_list = [
    'Source Data', 'Extract', 'Transform / Conform', 'Deliver', 'Load'
  ]
  group_sort_order = convert_sorted_list_to_dictionary_with_sequence_index(group_sort_order_list)

  with open(data_file_full_path) as file:
    soup = BeautifulSoup(file, 'lxml')
    nodes = soup.findAll("node", {"yfiles.foldertype":""})
    groups = soup.find_all("node", {"yfiles.foldertype":"group"})
    edges = soup.findAll("edge")

  groups_dict = {}

  for group in groups:
    group_dict = {}
    group_dict['group_id'] = group['id']
    group_dict['group_name'] = group.find('y:nodelabel').text.strip()
    group_id_parts = re.findall(r'n\d{1,}', group_dict['group_id'])

    if(len(group_id_parts) > 1):
      group_dict['parent_group_id'] = convert_list_to_string(group_id_parts[:-1], '::')
      group_dict['parent_group_name'] = groups_dict[group_dict['parent_group_id']]['group_name']
      group_dict['parent_group_sort_order'] = groups_dict[group_dict['parent_group_id']]['group_sort_order']
      group_dict['group_sort_order'] = groups_dict[group_dict['parent_group_id']]['group_sort_order']
    else:
      group_dict['group_sort_order'] = group_sort_order[group_dict['group_name']]

    groups_dict[group_dict['group_id']] = group_dict

  csv_dict_data = []
  nodes_dict = {}

  for node in nodes:
    node_dict = {}
    node_dict['node_id'] = node['id']
    node_id_parts = re.findall(r'n\d{1,}', node_dict['node_id'])
    node_dict['node_group_id'] = convert_list_to_string(node_id_parts[:-1], '::')
    node_dict['node_name'] = node.find('y:nodelabel').text.strip()
    node_tree = []

    if('parent_group_name' in groups_dict[node_dict['node_group_id']]):
      node_tree.append(groups_dict[node_dict['node_group_id']]['parent_group_name'])
      node_dict['node_group_name'] = groups_dict[node_dict['node_group_id']]['parent_group_name']
      node_dict['node_group_sort_order'] = groups_dict[node_dict['node_group_id']]['parent_group_sort_order']
    else:
      node_dict['node_group_name'] = groups_dict[node_dict['node_group_id']]['group_name']
      node_dict['node_group_sort_order'] = groups_dict[node_dict['node_group_id']]['group_sort_order']

    node_tree.append(groups_dict[node_dict['node_group_id']]['group_name'])
    node_tree.append(node_dict['node_name'])
    node_tree_text = convert_list_to_string(node_tree, ' > ')
    node_tree_text = node_tree_text + ' (' + str(groups_dict[node_dict['node_group_id']]['group_sort_order']) + ')'

    nodes_dict[node_dict['node_id']] = node_dict
    csv_dict_data.append(node_dict)

  csv_columns = [
    'node_id',
    'node_name',
    'node_group_id',
    'node_group_name',
    'node_group_sort_order'
  ]

  dict_data = csv_dict_data
  csv_filename = filename + '.csv'
  csv_file = target_directory + csv_filename

  try:
    with open(csv_file, 'w', newline='') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
      writer.writeheader()
      for data in dict_data:
        writer.writerow(data)
  except IOError:
    print('I/O error')

def get_filenames_in_directory(directory):
  filenames = []
  for root, dirs, files in os.walk(directory):
    for filename in files:
      filenames.append(filename)

  return filenames

def graphml_interpreter():
  source_directory = './in/'
  target_directory = './out/'
  filenames = get_filenames_in_directory(source_directory)

  for file in filenames:
    filename = file.replace('.graphml', '')
    create_csv_file_from_graphml_file(filename, source_directory, target_directory)

graphml_interpreter()
