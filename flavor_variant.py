# coding=utf-8

import os
import shutil

root = './app/src'
main_path = root + '/main'
test_path = root + '/test'
android_test_path = root + '/androidTest'
# 默认不是一个新变体
is_new_variant = False


# 获取文件md5
def get_MD5(file_path):
    files_md5 = os.popen('md5 %s' % file_path).read().strip()
    file_md5 = files_md5.replace('MD5 (%s) = ' % file_path, '')
    return file_md5


# 目录复制
def copy_path(path, out):
    for files in os.listdir(path):
        name = os.path.join(path, files)
        back_name = os.path.join(out, files)
        if os.path.isfile(name):
            if os.path.isfile(back_name):
                if get_MD5(name) != get_MD5(back_name):
                    shutil.copy(name, back_name)
            else:
                shutil.copy(name, back_name)
        else:
            if not os.path.isdir(back_name):
                os.makedirs(back_name)
                copy_path(name, back_name)


def list_all_files(rootdir, onlydir=False):
    import os
    _files = []

    # 列出文件夹下所有的目录与文件
    list_file = os.listdir(rootdir)

    for i in range(0, len(list_file)):

        # 构造路径
        path = os.path.join(rootdir, list_file[i])

        # 判断路径是否是一个文件目录或者文件
        # 如果是文件目录，继续递归
        if onlydir:
            if os.path.isdir(path):
                _files.append(path)
        else:
            if os.path.isdir(path):
                _files.extend(list_all_files(path))
            if os.path.isfile(path):
                _files.append(path)
    return _files


def main(file_name, variant_name):
    print("需要移动的文件名称：" + file_name)
    print("需要创建的变体名称：" + variant_name)

    # 加入新变体之前的全部旧变体，用于拷贝旧变体中文件到新变体
    old_variants = list_all_files(root, True)
    # 新变体路径
    new_variant_path = root + '/' + variant_name
    old_variants.remove(main_path)
    old_variants.remove(new_variant_path)
    # 过滤test
    if test_path in old_variants:
        old_variants.remove(test_path)
    if android_test_path in old_variants:
        old_variants.remove(android_test_path)
    print("当前项目中存在的变体(不包含新建):")
    print(old_variants)

    # 列出main中全部文件
    files = list_all_files(main_path)
    # 包含新变体在内的全部变体，用于复制新文件到全部变体
    variants = list_all_files(root, True)
    # 移除main 的包含新变体的全部变体目录
    variants.remove(main_path)
    # 过滤test
    if test_path in variants:
        variants.remove(test_path)
    if android_test_path in variants:
        variants.remove(android_test_path)
    print("当前项目中存在的变体(包含新建):")
    print(variants)

    # 新变体 复制 旧变体 的全部文件
    if is_new_variant:
        if len(old_variants) >= 1:
            # 当前已经存在一个或多个变体需要复制旧变体文件到新变体中去
            if len(old_variants) == 1:
                # 只存在一个变体，直接复制该变体文件到新变体
                copy_path(old_variants[0], new_variant_path)
            else:
                # 多个变体，手动选择
                var_index = 1
                for v in old_variants:
                    print('变体序号' + str(var_index) + "：" + v)
                    var_index += 1
                select_index = input('输入需要拷贝的变体序号，将从该变体复制全部文件到新变体：')
                copy_path(old_variants[int(select_index) - 1], new_variant_path)

    yes_or_no = input('请确认以上信息（Y）：')
    if not (yes_or_no.lower() == 'y') or not (yes_or_no.lower() != 'yes'):
        print("结束运行！")
        return

    # 所有匹配的文件 & 所在目录
    orign_files = []
    dir_paths = []
    index = 1
    for f in files:
        if file_name in f:
            print("文件序号" + str(index) + ": " + f)
            path = f.replace(main_path, '').replace(file_name, '')
            # 源文件路径
            orign_files.append(f)
            dir_paths.append(path)
            index += 1
    # 如果数组数量大于1 要求输入
    if len(orign_files) > 1:
        select_index = input('输入选择的文件序号：')
        orign_file = orign_files[int(select_index) - 1]
        dir_path = dir_paths[int(select_index) - 1]
    else:
        orign_file = orign_files[0]
        dir_path = dir_paths[0]

    for d in variants:
        # flavor对应的文件层级路径
        flavor_path = d + dir_path
        # 如果该层级不存在 则创建
        if not os.path.exists(flavor_path):
            os.makedirs(flavor_path)
        # 复制目标源文件到目标文件夹
        if not os.path.exists(flavor_path + file_name):
            # 复制文件
            shutil.copy(orign_file, flavor_path)

    # 移除源文件
    os.remove(orign_file)
    print()
    print("====================执行完毕====================")


if __name__ == '__main__':
    file = input('输入需要移动到flavor中的文件名，注意大小写与尾缀，务必输入正确完整：')
    variant = input('输入需要创建的变体名，如果已经创建了变体文件夹请输入空：')
    if len(variant) > 0:
        if not os.path.exists(root + "/" + variant):
            # 一个新变体，需要选择一个旧变体复制
            is_new_variant = True
            os.mkdir(root + "/" + variant)
    main(file, variant)
