import io
import os
import glob
import re
import googletrans
import six
from google.cloud import translate_v2 as translate
import html
import ntpath

LEFT_BUCKET = '[^'
LEFT_BUCKET_REGEX = '\[\^'

RIGHT_BUCKET = '^]'
RIGHT_BUCKET_REGEX = '\^\]'

ORIGIN_PATH = 'C:/repo/Staxel_Korean/resources/ORIGIN'
EXTRACT_SRC_PATH = 'C:/repo/Staxel_Korean/resources/ja-JP/'
KO_DST_PATH = 'C:/repo/Staxel_Korean/resources/ko-KR/'

"""
ORIGIN_PATH = 'C:\Program Files (x86)\Steam\steamapps\common\Staxel\content\staxel\StaxelTranslations\ja-JP'
KO_DST_PATH = 'C:/repo/Staxel_Korean/resources/extract_others/'
"""


def extract_real_contents_from_origin_file(origin_file, dst_path):
    origin_file_name = ntpath.basename(origin_file)
    print(f'origin file path = {origin_file}')

    with io.open(origin_file, 'r', encoding="UTF-8") as f:
        lines = f.readlines()
        tmp_list = list()

        for line in lines:
            if line.lstrip().startswith('//'):
                continue
            elif line.strip() == '':
                continue
            elif 'language.code=' in line:
                continue
            elif '/[Reference]' in line:
                continue
            elif line.lstrip().startswith('language='):
                continue
            elif line.lstrip().startswith('font='):
                continue

            tmp_list.append(line)

        dst_file_path = os.path.join(dst_path, origin_file_name)
        ret_file_path = dst_file_path
        with io.open(dst_file_path, 'w', encoding="UTF-8") as dst_f:
            dst_f.seek(0)
            dst_f.truncate()
            dst_f.writelines(tmp_list)

    print(f'ret_file_path = {ret_file_path}')
    return ret_file_path


def extract_raw_text_with_key(line):
    key = re.sub('=.*$', '', line)
    key = key.rstrip().lstrip()
    raw_text = re.sub('^.*?=', '', line)
    raw_text = raw_text.rstrip().lstrip()

    print(f'key = {key}')
    return key, raw_text


def extract_plain_text_with_color_info(raw_text):
    ret = raw_text

    print(f'raw_text : {raw_text}')
    list_color_info = list()

    if '^c:pop;' in raw_text:
        raw_text = re.sub('\^c:pop;', RIGHT_BUCKET, raw_text)

        list_colors = re.findall('\^c:.*?;', raw_text)
        raw_text = re.sub('\^c:.*?;', LEFT_BUCKET, raw_text)
        list_contents = re.findall(LEFT_BUCKET_REGEX + '.*?' + RIGHT_BUCKET_REGEX, raw_text)

        cnt = 0
        for content in list_contents:
            content = content.replace(LEFT_BUCKET, '')
            content = content.replace(RIGHT_BUCKET, '')
            list_color_info.append((content, list_colors[cnt]))
            cnt += 1

        for color_info in list_color_info:
            print(f'color_info : {color_info[0]}, {color_info[1]}')

        print('Extracted plain text : ' + ret)
        ret = raw_text

    return ret, list_color_info


def fix_translate_text(translate_raw_text, list_color_info):
    tmp_txt = translate_raw_text
    tmp_color = ''
    if RIGHT_BUCKET in tmp_txt:
        list_color_raw = re.findall(LEFT_BUCKET_REGEX + '.*?' + RIGHT_BUCKET_REGEX, tmp_txt)

        for color_data in list_color_raw:
            origin_data = color_data
            color_data = color_data.replace(LEFT_BUCKET, '')
            color_data = color_data.replace(RIGHT_BUCKET, '')
            for pair_val_color in list_color_info:
                value = pair_val_color[0]
                color = pair_val_color[1]
                tmp_color = color
                if color_data == value:
                    tmp_txt = tmp_txt.replace(origin_data, color + value + '^c:pop;', 1)
                    print(f'fix color string ret : {translate_raw_text} -> {tmp_txt}')
                else:
                    tmp_txt = tmp_txt.replace(RIGHT_BUCKET, '^c:pop;', 1)
                    tmp_txt = tmp_txt.replace(LEFT_BUCKET, color, 1)
                    print(f'fix color string ret : {translate_raw_text} -> {tmp_txt}')

    if RIGHT_BUCKET in tmp_txt or LEFT_BUCKET in tmp_txt:
        print('[WARNING] color info not replaced!')
        tmp_txt = tmp_txt.replace(RIGHT_BUCKET, '^c:pop;')
        tmp_txt = tmp_txt.replace(LEFT_BUCKET, tmp_color)
        print(f'fix color string ret : {translate_raw_text} -> {tmp_txt}')

    return tmp_txt


def translate_text_test(line):
    print(f"Translate TEST: {line} => {line}")
    return line


def translate_text_free(line):
    translator = googletrans.Translator()
    ret_ko_line = translator.translate(line, dest='ko')

    print(f"Translate : {line} => {ret_ko_line.text}")
    return ret_ko_line.text


def translate_text_google_api(text):
    if text == '' or text == 'true':
        return text

    # set GOOGLE_APPLICATION_CREDENTIALS=F:\GOOGLE_APPLICATION_CREDENTIALS\YOUR-CREDENTIAL-ID.json
    translate_client = translate.Client()
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    result = translate_client.translate(text, target_language='ko', source_language='ja')
    print(u"Origin Text: {}".format(result["input"]))
    ret = result["translatedText"]

    # fix &#39; to quote
    if '&#39;' in ret or '&quot;' in ret:
        ret = html.unescape(ret)

    print(u"Translation: {}".format(ret))
    ret = str(ret)

    return ret


def main(is_translate, origin_path, extract_path, ko_dst_path):

    # Remove extract pure data destination path's files
    if extract_path.endswith('/'):
        extract_path = extract_path[:-1]
    files = glob.glob(f'{extract_path}/*')
    for file in files:
        print(f'Remove file : {file}')
        os.remove(file)
    extract_path = extract_path + '/'

    # Remove final destination path's files
    if ko_dst_path.endswith('/'):
        ko_dst_path = ko_dst_path[:-1]
    files = glob.glob(f'{ko_dst_path}/*')
    for file in files:
        print(f'Remove file : {file}')
        os.remove(file)
    ko_dst_path = ko_dst_path + '/'

    # Extract pure data from origin lang path
    for file_path in os.listdir(origin_path):
        origin_file_path = os.path.join(origin_path, file_path)
        extract_real_contents_from_origin_file(origin_file_path, extract_path)

    # Extract color info from pure data and translate lines and replace color info from translate result
    for file_path in os.listdir(extract_path):
        extract_file_path = os.path.join(extract_path, file_path)
        print(f'pure extract file_path : {extract_file_path}')
        with io.open(extract_file_path, 'r', encoding="UTF-8") as f:
            origin_file_name = os.path.splitext(file_path)[0]
            ret_filename = origin_file_name.replace('ja_JP', 'ko_KR.lang')

            lines = f.readlines()
            tmp_list = list()
            tmp_list.append('language.code=ko-KR\n')
            tmp_list.append('language=한국어\n')

            cnt_write = 0
            for line in lines:
                # Split key and value
                text_key, text_raw_line = extract_raw_text_with_key(line)

                # FIX ORIGIN JA TEXT ERROR!
                if 'staxel.village.dialogue.NerdPrimary.line:10016100' == text_key:
                    text_raw_line = text_raw_line.replace('c:1486b0;', '^c:1486b0;')
                elif 'staxel.village.dialogue.Mechanic.line:10015500' == text_key:
                    text_raw_line = text_raw_line.replace('^c:pop;^c:pop;', '^c:pop;')

                if text_raw_line.rstrip() == '':
                    ret_line = f"{text_key}=\n"
                elif 'CharacterTest' in text_key:
                    ret_line = f"{text_key}={text_raw_line}\n"
                else:
                    # Extract color info from pure data
                    plain_text, list_color_info = extract_plain_text_with_color_info(text_raw_line)

                    # Translate line
                    if is_translate is True:
                        trans_text = translate_text_google_api(plain_text)
                        # trans_text = translate_text_free(plain_text)
                    else:
                        trans_text = translate_text_test(plain_text)

                    # Replace color info from translate result
                    fix_text = fix_translate_text(trans_text, list_color_info)

                    ret_line = f"{text_key}={fix_text}\n"

                print(f"Final ret Text = " + ret_line)
                cnt_write += 1
                tmp_list.append(ret_line)

            if cnt_write > 0:
                dst_file_path = os.path.join(ko_dst_path, ret_filename)
                print(f'dst_file_path : {dst_file_path}')
                file = open(dst_file_path, 'w', encoding="UTF-8")
                file.seek(0)
                file.truncate()
                file.writelines(tmp_list)
                file.close()


def fix_results():
    dir_path = KO_DST_PATH
    for file_path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, file_path)):
            file_path = os.path.join(dir_path, file_path)
            print(f"fix_results :: file_path = " + file_path)
            with io.open(file_path, 'r+', encoding="UTF-8") as f:
                lines = f.readlines()
                tmp_list = list()

                for line in lines:
                    if RIGHT_BUCKET in line or LEFT_BUCKET in line:
                        print('[WARNING] color info not replaced!')
                        line = line.replace(RIGHT_BUCKET, '^c:pop;')
                        line = line.replace(LEFT_BUCKET, '^c:1486b0;')
                    tmp_list.append(line)

                f.seek(0)
                f.truncate()
                f.writelines(tmp_list)
                f.close()


def check_files():
    dir_path = KO_DST_PATH
    for file_path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, file_path)):
            file_path = os.path.join(dir_path, file_path)
            with io.open(file_path, 'r', encoding="UTF-8") as f:
                lines = f.readlines()
                for line in lines:
                    if '//[Reference]' not in line:
                        if RIGHT_BUCKET in line or LEFT_BUCKET in line:
                            print(f"ERROR!!!!!! = " + line)


def test_breaker(find_str, line):
    if find_str in line:
        print(f'BREAK : line {line}')
        exit(0)


main(True, ORIGIN_PATH, EXTRACT_SRC_PATH, KO_DST_PATH)
fix_results()
check_files()
