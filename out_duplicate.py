import os
import re
import time
import hashlib


def main(path):
    fp_arr =  file_search(path)  # 查找文件(文件类型自行填写，不写查所有文件类型)
    du_arr = find_duplicate_file(fp_arr)          # 检查重复
# [fp_arr.remove(l) for j in [i[1:] for i in du_arr] for l in j] # 去重，重复文件只保留第1个即可


def extract_filename(s):
    s = s.split('/')[-1]        
    s = max(s.split('.'), key=len)
    if '_hd_' in s:
        s = s.replace('_hd_', '-')
    if 'caribbeancom ' in s:
        s = s.replace('caribbeancom ','caribbeancom-')    
    if '1080p' in s:
        s = s.replace('1080p','=')    
    if '720p' in s:
        s = s.replace('720p','=') 
    if '2k' in s:
        s = s.replace('2k','=')         
    if '4k' in s:
        s = s.replace('4k','=')  
    if '8k' in s:
        s = s.replace('8k','=')               


    # 正则表达式进行匹配
    pattern = r'([a-zA-Z]{2,}[-_ ]?[0-9]{2,}[-_0-9]{0,})'
    match = re.findall(pattern, s)
    if not match:
        pattern = r'([n][0-9]{4,})'
        match = re.findall(pattern, s)     
        if not match:
            pattern = r'([0-9]{3,}[-_]?[0-9]{0,})'
            match = re.findall(pattern, s)               

    if match:
        temp = match[-1]
        if '_' in temp:
            temp = temp.replace('_','-')
        if 'ppv-' in temp:
            temp = temp.replace('ppv-','')
        if 'fc-' in temp:
            temp = temp.replace('fc-','')      
        if 'fc2-' in temp:
            temp = temp.replace('fc2-','')   
        if temp[-1] == '-':
            temp =  temp[:-1]

        # 把 abc234 修改为 abc-234
        pattern = r'^([a-zA-Z]{3,})([0-9]{3,})$'
        match = re.match(pattern, temp)
        if match:
            temp = match.group(1)+'-'+match.group(2)

        return temp
    else:
        return None
    
def file_search(path='.',repat = r'.*'):
    """
    文件查找：
        文件夹及子文件夹下，所有匹配文件，返回list文件列表，绝对路径形式
    Args:
        path: 文件路径（默认当前路径）
        repat: 文件名正则匹配，不区分大小写（默认匹配所有文件）
        return: 文件列表（绝对路径）
    Returns:
        files_match: 文件列表
    """
    # 获取文件夹，及子文件夹下所有文件，并转为绝对路径
    folders,files = list(),list()
    st = time.time()
    repat = '^'+repat+'$'
    # walk结果形式 [(path:文件夹,[dirlist:该文件夹下的文件夹],[filelist:该文件夹下的文件]),(子文件夹1,[子子文件夹],[]),(子文件夹2,[],[])...]
    # 该遍历会走遍所有子文件夹，返回上述形式的结果信息。
    for record in os.walk(path):  
        fop = record[0]
        folders.append(fop)
        for fip in record[2]:
            fip = os.path.abspath(os.path.join(fop,fip)).replace('\\','/')
            files.append(fip)
    # 逐个检查是否符合要求
    files_match = list()
    for file in files:
        a = re.findall(repat,file.lower())
        if a:
            files_match+=a
    print('找到{0}个文件'.format(len(files_match)))
    # 返回满足要求的
    return files_match


def fastmd5(file_path,split_piece=256,get_front_bytes=8):
    """
    快速计算一个用于区分文件的md5（非全文件计算，是将文件分成s段后，取每段前d字节，合并后计算md5，以加快计算速度）

    Args:
        file_path: 文件路径
        split_piece: 分割块数
        get_front_bytes: 每块取前多少字节
    """
    size = os.path.getsize(file_path) # 取文件大小
    block = size//split_piece # 每块大小 
    h = hashlib.md5()
    # 计算md5
    if size < split_piece*get_front_bytes: 
        # 小于能分割提取大小的直接计算整个文件md5
        with open(file_path, 'rb') as f:
            h.update(f.read())
    else:
        # 否则分割计算
        with open(file_path, 'rb') as f:
            index = 0
            for i in range(split_piece):
                f.seek(index)
                h.update(f.read(get_front_bytes))
                index+=block
    return h.hexdigest()


def find_duplicate_file(fp_arr):
    """
    查找重复文件

    Args:
        fp_arr:文件列表
    """
    # 将文件大小和路径整理到字典中
    d = {}  # 临时词典 {文件大小1:[文件路径1,文件路径2,……], 文件大小2:[文件路径1,文件路径2,……], ……}
    for fp in fp_arr:
        size = os.path.getsize(fp)
        d[size]=d.get(size,list())+[fp]
    # 列出相同大小的文件列表
    l = [] # 临时列表 [[文件路径1,文件路径2,……], [文件路径1,文件路径2,……], ……]
    for k in d:
        if len(d[k])>1:
            l.append(d[k])
    # 核对大小一致的文件，md5是否相同
    ll = [] # 临时列表 [[文件路径1,文件路径2,……], [文件路径1,文件路径2,……], ……]
    for f_arr in l:
        d = {} # 临时词典 {文件大小1:[文件路径1,文件路径2,……], 文件大小2:[文件路径1,文件路径2,……], ……}
        for f in f_arr:
            fmd5 = fastmd5(f)
            d[fmd5]=d.get(fmd5,list())+[f]
        # 找到相同md5的文件
        for k in d: # 相同大小的文件，核对一下md5是否一致
            if len(d[k])>1:
                ll.append(d[k])


    # 方法二：正则提取文件名来判断
    d = {}  # 临时词典 {番号1:[文件路径1,文件路径2,……], 番号2:[文件路径1,文件路径2,……], ……}
    for fp in fp_arr:
        # re提取文件名
        if '.srt' in fp:
            continue
        name = extract_filename(fp)
        # print(name, '===', fp)  # 输出提取的番号
        if name == None or len(name) <= 4:
            continue
        d[name]=d.get(name,list())+[fp]    
    print("#"*30 + " 方法1：番号重复的文件： " + "#"*30)
    for k in d:
        if len(d[k])>1:
            print('*'*120)
            print('key:' + str(k))
            for file in d[k]:
                size_in_bytes = os.path.getsize(file)
                size_in_gb = size_in_bytes / (1024 ** 3)
                print(file, "，", "size:{:.1f} GB".format(size_in_gb))


    print("#"*30 + " 方法2：md5查重的文件： " + "#"*30)
    # 输出第一种方法的重复文件
    for i in ll:
        print('\n'.join(i))
        print('*'*120)



if __name__ == '__main__':
    path = 'D:/'  # 填写要判断的文件夹路径
    main(path)
