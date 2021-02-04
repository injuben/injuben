import sys
import re
from io import StringIO

UTF_8 = "utf-8"

def str_encode(s):
    if sys.version_info < (3, 0):
        return s.encode(UTF_8)
    else:
        return s

def str_decode(s):
    if sys.version_info < (3, 0):
        return s.decode(UTF_8)
    else:
        return s

ACTION_PER_LINE = 33 # 动作描述每行的最大文字数
DIALOG_PER_LINE = 21 # 台词每行的最大文字数
MORE = str_decode("转下页")   # 跨页台词转下页提示文字
CONT_D = str_decode("继续")  # 跨页台词继续提示文字
LINE_PER_PAGE = 36 # 排版行数
LINE_PER_SCENE_HEADING = 3
LINE_PER_TRANSACTION = 2
LINE_PER_CHARACTER = 2
LINE_PER_DIALOG = 1
LINE_PER_ACTION = 1
FIRST_LINE_MARGIN = 1

CTR_A = chr(1)
CTR_B = chr(2)
CTR_C = chr(3)
CTR_D = chr(4)

def print_raw(line):
    return str_encode(line.replace(CTR_A, "**").replace(CTR_B,"**").replace(CTR_C, "_").replace(CTR_D, "_")).strip() + "\n"

def print_raw_char(line):
    return str_encode(line.replace(CTR_A, "**").replace(CTR_B,"**").replace(CTR_C, "_").replace(CTR_D, "_"))

def print_raw_strip(line):
    return str_encode(line).strip()

def print_page_break():
    return "\n\n===\n\n"

def count_len(c):
    length = 0
    if ord(c) < 32:
        return length
    elif ord(c) < 128:
        if ord(c) == 73 or ord(c) == 74 or ord(c) == 76 or ord(c) == 105 or ord(c) == 106 or ord(c) == 108:
            length = 0.3846  #5/13
        elif ord(c) >= 97 or ord(c) <= 64:
            length = 0.5714  #4/7
        else:
            length = 0.75
    else:
        length = 1
    return length

def count_character(line):
    count = 0
    for c in line.strip():
        count = count + count_len(c)
    return count

def is_title_item(line):
    if( line.startswith("Title:")
     or line.startswith("Author:")
     or line.startswith("Credit:")
     or line.startswith("Source:")
     or line.startswith("Draft date:")
     ):
        return True


def parse(stream, first_line_indent):
    line_count = 0
    current_charater = ""
    in_title_page = True
    title_page_empty_line = 0
    final_string = ""
    is_contact = False
    is_dialog = False
    character_cross_page = ''
    is_new_line_action = True
    is_bold = False
    is_underline = False
    is_firstline_detected = False
    
    content = stream.read()
    lines = re.compile('\r\n|\n|\r').split(content)
   
    total_line = 0
    new_lines = []
    tmp_char = ''
    for line in lines:
        new_line = str_decode(line).replace(":", "：", 1)
        new_line = new_line.strip()
        if( not is_firstline_detected and new_line == ''):
            continue
        else:
            is_firstline_detected = True

        if(
           new_line.startswith("Title：")
        or new_line.startswith("Author：")
        or new_line.startswith("Credit：")
        or new_line.startswith("Source：")
        or new_line.startswith("Draft date：")
        or new_line.startswith("===")
        ):
            is_contact = False
            new_lines.append(line)
            continue

        if(new_line.startswith("Contact：")):
            is_contact = True
            new_lines.append(line)
            continue

        if(is_contact):
            if(new_line.strip() != ''):
                new_lines.append(line)
                continue
            else:
                is_contact = False
                new_lines.append(line)
                continue
            
        dialog_start = str_decode(new_line).find('：')
        if( dialog_start > 0 and dialog_start <= 20):
            new_line =  re.sub(r"\s*（", " (", new_line)
            new_line =  re.sub("）", ")", new_line)
            tmp_char = re.search(r"([^\(\s]*)", new_line.split('：', 1)[0]).group(0)
            if(count_character(tmp_char) <= 10):
                new_lines.append('@' + print_raw_strip(new_line.split('：')[0]))
                dialog = print_raw_strip(new_line.split('：', 1)[1])
                new_lines += re.compile('\n').split(re.sub(r"(\([^\)]+\))", r"\n\1\n", dialog).strip() + '\n')
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    is_contact = False
    for line in new_lines:
        if(line_count >= LINE_PER_PAGE):
            final_string += print_page_break()
            line_count = 0
        # 删除注释
        line = re.sub(r"\[\[.+\]\]", "", str_decode(line))
        line = re.sub("（", "(", str_decode(line))
        line = re.sub("）", ")", str_decode(line))
  
        if(line.strip()):
            total_line += 1
        if(in_title_page):
            if(total_line == 1 and line.strip() and not is_title_item(line)):
                final_string += print_raw("Title: " + line)
                continue
            elif(total_line == 2 and line.strip() and not is_title_item(line)):
                final_string += print_raw("Author: " + line)
                continue
            elif(total_line == 3 and line.strip() and not is_title_item(line)):
                final_string += print_raw("Source: " + line)
                continue

        # 在封面页结束处清空高度
        if (in_title_page):
            if(not len(line.strip())):
                is_contact = False
                title_page_empty_line = title_page_empty_line + 1
                final_string += "\n"
    
            if (title_page_empty_line == 2):
                is_contact = False
                in_title_page = False
   
        if(is_contact):
            final_string += print_raw("Contact: " + line.strip())
            continue

        # 封面页内容、换页符
        if(
        line.startswith("Title:")
        or line.startswith("Author:")
        or line.startswith("Credit:")
        or line.startswith("Source:")
        or line.startswith("Draft date:")
        or line.startswith("===")
        ):
            is_contact = False
            is_new_line_action = True
            final_string += print_raw(line)
   
        elif(line.startswith("Contact:")):
            final_string += print_raw(line)
            is_contact = True
            is_new_line_action = True
            continue

        # 大纲、大纲内容
        elif(line.startswith("#")
        or line.startswith("= ")
        ):
            final_string += print_raw(line)
            is_new_line_action = True
    
        # 场景标题
        elif(line.startswith(".") and not line.startswith("..")):
            if ( LINE_PER_PAGE - line_count <= LINE_PER_SCENE_HEADING):
                final_string += print_page_break()
                line_count = 0
            line_count += LINE_PER_SCENE_HEADING
            final_string += "\n\n\n\n" + print_raw(line) + "\n\n"
            is_dialog = False
            is_new_line_action = True

        # 场景标题
        elif(line.startswith("。") 
            or line.startswith("内 ") 
            or line.startswith("内景 ") 
            or line.startswith("外 ") 
            or line.startswith("外景 ")
            or line.startswith("内外 ")
            or line.startswith("外内 ")
            or line.startswith("内／外 ")
            or line.startswith("内/外 ")
            or line.startswith("外／内 ")
            or line.startswith("外/内 ")
            ):
            line = "." + line.replace('。', '', 1)
            if ( LINE_PER_PAGE - line_count <= LINE_PER_SCENE_HEADING):
                final_string += print_page_break()
                line_count = 0
            line_count += LINE_PER_SCENE_HEADING
            final_string += "\n\n\n\n" + print_raw(line) + "\n\n"
            is_dialog = False
            is_new_line_action = True
    
        # 角色
        elif(line.startswith("@")):
            if ( LINE_PER_PAGE - line_count == 1):
                final_string += print_page_break()
                final_string += "\n\n" + print_raw(line)
                line_count =+ LINE_PER_CHARACTER
            elif ( LINE_PER_PAGE - line_count ==  LINE_PER_CHARACTER or LINE_PER_PAGE - line_count == LINE_PER_CHARACTER + LINE_PER_DIALOG):
                character_cross_page = line
            else:
                line_count += LINE_PER_CHARACTER 
                final_string += "\n\n" + print_raw(line)

            current_charater = re.search(r"\@([^\(\s]*)", line).group(0)
            is_dialog = True
            is_new_line_action = True
    
        # 换场或居中
        elif(line.startswith(">")):
            if ( LINE_PER_PAGE - line_count <= LINE_PER_TRANSACTION):
                final_string += print_page_break()
                line_count = 0
            line_count += LINE_PER_TRANSACTION
            final_string += "\n\n" + print_raw(line) + "\n\n"
            is_dialog = False
            is_new_line_action = True

        # 空行
        elif(not len(line.strip())):
            final_string += "\n\n\n\n"
            is_contact = False
            is_dialog = False
            is_new_line_action = True
            in_title_page = False
    
        # 台词或动作
        else:
            line = re.sub("：", ":", str_decode(line))
            # 台词
            repl_start = CTR_A + '\\2' + CTR_B
            repl_end = CTR_C + '\\2' + CTR_D
            line = re.sub(r"(\*\*([^\*]+)\*\*)", repl_start, line)
            line = re.sub(r"(_([^\*]+)_)", repl_end, line)
            line_char_count = count_character(line)
            is_new_line_action = True
            if is_dialog:
                if character_cross_page:
                    if ((line_char_count <= DIALOG_PER_LINE ) or (line_char_count <= 2 * DIALOG_PER_LINE and LINE_PER_PAGE - line_count == LINE_PER_CHARACTER + LINE_PER_DIALOG)):
                        final_string += "\n\n" + print_raw(character_cross_page)
                        final_string += print_raw(line)
                        final_string += print_page_break()
                        character_cross_page = ''
                        line_count = 0
                        continue
                    else:
                        final_string += print_page_break()
                        final_string += "\n\n" + print_raw(character_cross_page)
                        line_count = 0
                        character_cross_page = ''
                        line_count += LINE_PER_CHARACTER

                if (line_count == 0):
                    if is_bold:
                        final_string += "**"
                    if is_underline:
                        final_string += "_"
                    final_string += "\n\n" + print_raw(current_charater +  " (" + CONT_D + ")" )
                    if is_underline:
                        final_string += "_"
                    if is_bold:
                        final_string += "**"
                    is_bold = False
                    is_underline = False
                    line_count += LINE_PER_CHARACTER
                    
                i = 0
                total = 0
                for c in line.strip():
                    if(c == CTR_A):
                        is_bold = True
                    if(c == CTR_B):
                        is_bold = False
                    if(c == CTR_C):
                        is_underline = True
                    if(c == CTR_D):
                        is_underline = False
                    if(line_count >= LINE_PER_PAGE):
                        if (count_character(line) - total <= ACTION_PER_LINE):
                            final_string += print_raw_char(c)
                            continue
                        else:
                            i = 0
                            line_count = 0
                            if is_bold:
                                final_string += "**"
                            if is_underline:
                                final_string += "_"
                            final_string += "\n" + " (" + MORE + ")" + print_page_break()
                            final_string += "\n\n" + print_raw(current_charater +  " (" + CONT_D + ")" ) 
                            if is_underline:
                                final_string += "_"
                            if is_bold:
                                final_string += "**"
                            line_count += LINE_PER_CHARACTER
                    char_len = count_len(c)
                    final_string += print_raw_char(c)
                    i += char_len
                    if (i >= DIALOG_PER_LINE - 0.5):
                        i = 0
                        line_count += LINE_PER_DIALOG
                    total += 1
                if ( i > 0 ):
                    line_count += LINE_PER_DIALOG
                final_string += "\n"
            else:
                i = 0
                if (line_char_count <= ACTION_PER_LINE  and LINE_PER_PAGE - line_count ==  1):
                    final_string += print_raw(line)
                    final_string += print_page_break()
                    line_count = 0
                    continue
                
                if is_new_line_action :
                    line_count += FIRST_LINE_MARGIN # 起始行
                    is_new_line_action = False

                line = line.strip()
                if first_line_indent:
                    line = " "*6 + line
                for c in line:
                    if(c == CTR_A):
                        is_bold = True
                    if(c == CTR_B):
                        is_bold = False
                    if(c == CTR_C):
                        is_underline = True
                    if(c == CTR_D):
                        is_underline = False
                    if(line_count >= LINE_PER_PAGE):
                        i = 0
                        line_count = 0
                        if is_bold:
                            final_string += "**"
                        if is_underline:
                            final_string += "_"
                        final_string += print_page_break()
                        if is_underline:
                            final_string += "_"
                        if is_bold:
                            final_string += "**"
                    char_len = count_len(c)
                    final_string += print_raw_char(c)
                    i += char_len
                    if (i >= ACTION_PER_LINE):
                        i = 0
                        line_count += LINE_PER_ACTION
                if ( i > 0 ):
                    line_count += LINE_PER_ACTION
                final_string += "\n"
    return StringIO(final_string)
