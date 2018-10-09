import json
import os,sys

def find_index_by_service_code_id(dict, service_code_id):
    for i in range(0,len(dict['services'])):
        if (dict['services'][i]['code'] == service_code_id):
            break
    return i

def getCategoryNameList(dict, service_code_id, index):
    categoriesForServiceCode_list = dict['services'][index]['categories']
    categoryNameListByServiceCode = []
    for i in range(0,len(categoriesForServiceCode_list)):
        categoryNameListByServiceCode.append(categoriesForServiceCode_list[i]['name'])
    return categoryNameListByServiceCode

def getCategoryListByServiceCode(service_code_id):
    serviceCodeResponseJSONFile = "categoryMap.json"
    f = open(serviceCodeResponseJSONFile)
    serviceCodeResponse_dict = json.load(f)
    index = find_index_by_service_code_id(serviceCodeResponse_dict,service_code_id)
    categoryNameListByServiceCode = getCategoryNameList(serviceCodeResponse_dict,service_code_id,index)
    return categoryNameListByServiceCode
