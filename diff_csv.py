# -*- coding: utf-8 -*-
import sys
import csv

def _sort_by_list_column(csv_content, col=[], reverse=False):
    """
    对csv内容排序，按列名（col类型是str）
                 按列索引（col类型是int）
    """
    header = csv_content[0]
    body = csv_content[1:]
    if [True for i in col if isinstance(i, str)]:
        col_index_list = [header.index(c) for c in col]
    else:
        col_index_list = col
    body = sorted(body, key=lambda x: tuple(x[i] for i in col_index_list), reverse=reverse)
    body.insert(0, header)
    return body


def _sort_by_dict_key(csv_content, col=[], reverse=False):
    header = csv_content[0].keys()
    keys = []
    for i in col:
        if i in header:
            keys.append(i)
    if keys:
        csv_content = sorted(csv_content, key=lambda x: tuple(x[i] for i in keys), reverse=reverse)
    return csv_content


def _csv_to_list(filename, delimiter=','):
    try:
        with open(filename, 'r') as fileHandle:
            data = csv.reader(fileHandle, delimiter=delimiter)
            return list(data)
    except IOError as e:
        print("Read file Error:", e)
        sys.exit()


def _csv_to_dict(filename, delimiter=','):
    try:
        with open(filename, 'r') as fileHandle:
            data = csv.DictReader(fileHandle, delimiter=delimiter)
            return list(data)
    except IOError as e:
        print("Read file Error:", e)
        sys.exit()


def _list_file_handle(filename, sort_field=[], delimiter=','):
    data = _csv_to_list(filename, delimiter=delimiter)
    if sort_field:
        data = _sort_by_list_column(data, col=sort_field)
    return data


def _dict_file_handle(filename, sort_field=[], delimiter=','):
    data = _csv_to_dict(filename, delimiter=delimiter)
    if sort_field:
        data = _sort_by_dict_key(data, col=sort_field)
    return data


def _convert_result_to_dict(content, index=1):
    result = {}
    for i in content:
        result[','.join(i[:index])] = i[index:]
    return result


def _convert_diff_list_to_html(filename1, filename2, diff_list, len_field=2):
    table_header = """
                    <table class="table table-hover table-bordered table-striped table-condensed table" cellpadding="3px" style="margin-top:6px" border="1">
                        <thead>
                            <tr>
                                <th colspan="{len_files}" class="diff_header">{filename1}</th>
                                <th colspan="{len_files}" class="diff_header">{filename2}</th>
                            </tr>
                        </thead>
                        <tbody style="cursor:pointer">
                            %s
                        </tbody>
                    </table>
                """.format(len_files=len_field+2, filename1=filename1, filename2=filename2)
    trs = []
    for index, differ in enumerate(diff_list):
        tr_header = "<tr>%s</tr>"
        td_header = '<td nowrap="nowrap">%s</td>'
        td_style_header = '<td nowrap="nowrap" style="background-color: red">%s</td>'
        td_split_header = '<td nowrap="nowrap" style="background-color: yellow">%s</td>'
        tds = []
        tds.append(td_header % str(index))
        if not differ.get('diff_row_1', []):
            tds.append('<th colspan="{len_files}" class="diff_header"></th>'.format(len_files=len_field))
        for i, v in enumerate(differ.get('diff_row_1', [])):
            if i in differ.get('diff_indexs_1', []):
                td = td_style_header % v
            else:
                td = td_header % v
            tds.append(td)

        tds.append(td_split_header % 'vs')
        tds.append(td_header % str(index))
        if not differ.get('diff_row_2', []):
            tds.append('<th colspan="{len_files}" class="diff_header"></th>'.format(len_files=len_field))
        for i, v in enumerate(differ.get('diff_row_2', [])):
            if i in differ.get('diff_indexs_2', []):
                td = td_style_header % v
            else:
                td = td_header % v
            tds.append(td)
        trs.append(tr_header % ''.join(tds))
    tables = table_header % ''.join(trs)
    return tables


def compare_result_to_html(filename1, filename2, sort_field=[], unique_index=1, unique_index_field=[]):
    """
    对比两个csv文件
    :param filename1: 文件1
    :param filename2: 文件2
    :param sort_field:
    :param unique_index: 根据索引选取作为唯一key的字段, 默认 24列之前的
    :param unique_index_field: TODO 根据字段名选取唯一key
    :return: html table
    """
    try:
        if filename1.split('.')[-1] not in ['csv'] or filename2.split('.')[-1] not in ['csv']:
            print(u'计算失败：数据文件格式不正确：%s, %s' % filename1, filename2)
            return []
    except Exception as e:
        print e

    content1 = _list_file_handle(filename1, sort_field=sort_field)
    print '_file_handle read file 1 success '
    content2 = _list_file_handle(filename2, sort_field=sort_field)
    print '_file_handle read file 2 success '
    if not content1 or not content2:
        print(u'计算失败：找不到方案数据：%s, %s' % filename1, filename2)
        return []

    len_field = len(content1[0])

    # TODO 目前只写了根据前几位字段作为唯一key, 之后要做根据字段名/字段索引列表作为唯一key
    if unique_index_field:
        pass

    result_1 = _convert_result_to_dict(content1[1:], index=unique_index)
    print '_convert_result_to_diff_format result 1 success'
    result_2 = _convert_result_to_dict(content2[1:], index=unique_index)
    print '_convert_result_to_diff_format result 2 success'

    diff_list = []
    diff_list.append({
                    'diff_row_1': content1[0],
                    'diff_row_2': content2[0],
                    'diff_indexs_1': [],
                    'diff_indexs_2': []
                })
    for k, v in result_1.iteritems():
        if k in result_2.keys():
            if v == result_2.get(k, []):
                pass
            else:
                diff_indexs_1 = []
                diff_indexs_2 = []
                for diff_index, diff_field in enumerate(v):
                    r2_field_index = content2[0].index(content1[0][len(k.split(',')) + diff_index]) - len(k.split(','))
                    if diff_field != result_2[k][r2_field_index]:
                        if diff_field == 'N/A':
                            diff_field = 0
                        if result_2[k][r2_field_index] == 'N/A':
                            result_2[k][r2_field_index] = 0
                        try:
                            if float(diff_field) - float(result_2[k][r2_field_index]) > 0.1 or \
                                float(diff_field) - float(result_2[k][r2_field_index]) < -0.1:
                                diff_indexs_1.append(len(k.split(',')) + diff_index)
                                diff_indexs_2.append(len(k.split(',')) + r2_field_index)
                            else:
                                pass
                        except:
                            diff_indexs_1.append(len(k.split(',')) + diff_index)
                            diff_indexs_2.append(len(k.split(',')) + r2_field_index)
                if diff_indexs_1 or diff_indexs_2:
                    d = {
                        'diff_row_1': k.split(',') + v,
                        'diff_row_2': k.split(',') + result_2[k],
                        'diff_indexs_1': diff_indexs_1,
                        'diff_indexs_2': diff_indexs_2
                    }
                    diff_list.append(d)
        else:
            d = {
                'diff_row_1': k.split(',') + v,
                'diff_row_2': [],
                'diff_indexs_1': [],
                'diff_indexs_2': []
            }
            diff_list.append(d)
    print 'diff result 1 of result 2 success %s' % str(len(diff_list))

    for k, v in result_2.iteritems():
        if k not in result_1.keys():
            d = {
                'diff_row_1': [],
                'diff_row_2': k.split(',') + v,
                'diff_indexs_1': [],
                'diff_indexs_2': []
            }
            diff_list.append(d)
    print 'diff result 2 of result 1 success %s' % str(len(diff_list))

    diff_html = _convert_diff_list_to_html(filename1, filename2, diff_list, len_field=len_field)
    print "_convert_diff_list_to_html success"
    # # 内容保存到result.html文件中
    with open('result.html', 'w') as resultfile:
        resultfile.write(diff_html)
    return diff_html

def compare_result_to_dict(filename1, filename2, sort_field=[], unique_index=24, unique_index_field=[]):
    """
    对比两个csv文件
    :param filename1: 文件1
    :param filename2: 文件2
    :param sort_field:
    :param unique_index: 根据索引选取作为唯一key的字段, 默认 24列之前的
    :param unique_index_field: TODO 根据字段名选取唯一key
    :return: [
                {
                    'key': [
                        {'name': '', 'v1': '', 'v2': ''},
                    ]
                }
            ]
    """
    try:
        if filename1.split('.')[-1] not in ['csv'] or filename2.split('.')[-1] not in ['csv']:
            print(u'计算失败：数据文件格式不正确：%s, %s' % filename1, filename2)
            return []
    except Exception as e:
        print e

    content1 = _list_file_handle(filename1, sort_field=sort_field)
    print '_file_handle read file 1 success '
    content2 = _list_file_handle(filename2, sort_field=sort_field)
    print '_file_handle read file 2 success '
    if not content1 or not content2:
        print(u'计算失败：找不到方案数据：%s, %s' % filename1, filename2)
        return []

    # TODO 目前只写了根据前几位字段作为唯一key, 之后要做根据字段名/字段索引列表作为唯一key
    if unique_index_field:
        pass

    result_1 = _convert_result_to_dict(content1[1:], index=unique_index)
    print '_convert_result_to_diff_format result 1 success'
    result_2 = _convert_result_to_dict(content2[1:], index=unique_index)
    print '_convert_result_to_diff_format result 2 success'

    diff_list = []
    for k, v in result_1.iteritems():
        diff_dict = {k: []}
        if k in result_2.keys():
            if v == result_2.get(k, []):
                pass
            else:
                for diff_index, diff_field in enumerate(v):
                    r2_field_index = content2[0].index(content1[0][len(k.split(',')) + diff_index]) - len(k.split(','))
                    if diff_field != result_2[k][r2_field_index]:
                        if diff_field == 'N/A':
                            diff_field = 0
                        if result_2[k][r2_field_index] == 'N/A':
                            result_2[k][r2_field_index] = 0
                        try:
                            if float(diff_field) - float(result_2[k][r2_field_index]) > 0.1 or \
                                float(diff_field) - float(result_2[k][r2_field_index]) < -0.1:
                                diff_field_struct = {}
                                diff_field_struct['name'] = content1[0][len(k.split(',')) + diff_index]
                                diff_field_struct['v1'] = diff_field
                                diff_field_struct['v2'] = result_2[k][r2_field_index]
                                diff_dict[k].append(diff_field_struct)
                            else:
                                pass
                        except:
                            diff_field_struct = {}
                            diff_field_struct['name'] = content1[0][len(k.split(',')) + diff_index]
                            diff_field_struct['v1'] = diff_field
                            diff_field_struct['v2'] = result_2[k][r2_field_index]
                            diff_dict[k].append(diff_field_struct)
                if diff_dict[k]:
                    diff_list.append(diff_dict)
        else:
            for diff_index, diff_field in enumerate(v):
                diff_field_struct = {}
                diff_field_struct['name'] = content1[0][len(k.split(',')) + diff_index]
                diff_field_struct['v1'] = diff_field
                diff_field_struct['v2'] = ''
                diff_dict[k].append(diff_field_struct)
            diff_list.append(diff_dict)
    print 'diff result 1 of result 2 success %s' % str(len(diff_list))

    for k, v in result_2.iteritems():
        diff_dict = {k: []}
        if k not in result_1.keys():
            for diff_index, diff_field in enumerate(v):
                diff_field_struct = {}
                diff_field_struct['name'] = content2[0][len(k.split(',')) + diff_index]
                diff_field_struct['v1'] = ''
                diff_field_struct['v2'] = diff_field
                diff_dict[k].append(diff_field_struct)
            diff_list.append(diff_dict)
    print 'diff result 2 of result 1 success %s' % str(len(diff_list))
    return diff_list

if __name__ == '__main__':
    # need_diff = {'filename1': '1.csv', 'filename2': '2.csv', 'unique_index': 4}
    # need_diff = {'filename1': 'bhp_sci_rotated_2017q2v1_test.csv', 'filename2': 'bhp_sci_rotated_2017q2v2_test.csv',
    #              'unique_index': 24}
    need_diff = {'filename1': 'bhp_sci_rotated_2017q2v1.csv', 'filename2': 'bhp_sci_rotated_2017q2v2.csv',
                 'unique_index': 24}
    # _test_diff_file(filename1, filename2)
    # diff_html = compare_result_to_html(need_diff['filename1'], need_diff['filename2'],
    #                                     unique_index=need_diff['unique_index'])
    diff_dict = compare_result_to_dict(need_diff['filename1'], need_diff['filename2'],
                                        unique_index=need_diff['unique_index'])
    c = 0
    for i in diff_dict:
        c += 1
        print c, '---'*50
        print i
