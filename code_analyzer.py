import sys
import os
import glob
import re


class LineChecker:
    INDENTION_PATTERN = r'^[ ]+'
    INLINE_COMMENT_PATTERN = r'.+[ ]*#.*'
    INLINE_COMMENT_SPACES_PATTERN = r'[ ]{2}#.*'

    @classmethod
    def check_length(cls, line: str, line_no: int) -> str | None:
        if len(line) > 79:
            return f'Line {line_no}: S001 Too long'
        return None

    @classmethod
    def check_indentations(cls, line: str, line_no: int) -> str | None:
        result = re.match(cls.INDENTION_PATTERN, line)
        if result and result.span()[1] % 4:
            return f'Line {line_no}: S002 Indentation is not a multiple of four'
        return None

    @classmethod
    def unnecessary_semicolon(cls, line: str, line_no: int) -> str | None:
        message = f'Line {line_no}: S003 Unnecessary semicolon after a statement'
        if ';' not in line:
            return None

        line = line.rstrip()

        if re.match(r'.*#.*;', line):
            return None
        elif line.endswith(';'):
            return message
        elif cls.find_between(line, '"', ';') or cls.find_between(line, "'", ';'):
            return None

        return message

    @classmethod
    def inline_comment_spaces(cls, line: str, line_no: int) -> str | None:
        if "#" in line:
            if re.match(cls.INLINE_COMMENT_PATTERN, line):
                if re.search(cls.INLINE_COMMENT_SPACES_PATTERN, line):
                    return None
                return f'Line {line_no}: S004 Less than two spaces before inline comments'
        return None

    @classmethod
    def todo_found(cls, line: str, line_no: int):
        if "#" not in line:
            return None
        elif "TODO" in line.upper():
            message = f'Line {line_no}: S005 TODO found'
            return message if line.index("#") < line.upper().index('TODO') else None
        return None

    @classmethod
    def test_line(cls, line: str, line_no: int, file_path_description: str) -> int | None:
        if line.strip() == '':
            return 1

        if result := cls.check_length(line, line_no):
            print(file_path_description, result)
        if result := cls.check_indentations(line, line_no):
            print(file_path_description, result)
        if result := cls.unnecessary_semicolon(line, line_no):
            print(file_path_description, result)
        if result := cls.inline_comment_spaces(line, line_no):
            print(file_path_description, result)
        if result := cls.todo_found(line, line_no):
            print(file_path_description, result)
        return 0

    @staticmethod
    def find_between(base_str: str, border_sign: str, sign_between: str) -> bool:
        sign_position = base_str.index(sign_between)
        if base_str.find(border_sign) < sign_position < base_str.find(border_sign, sign_position):
            return True
        return False

    @classmethod
    def check_file(cls, file_path):
        path_to_files = glob.escape(file_path)
        path_to_files = os.path.normpath(path_to_files)
        blank_lines = 0
        msg = True
        try:
            with open(path_to_files, 'r') as file:
                file_path_description = f'{file_path}:'

                for l_no, line in enumerate(file, start=1):
                    l = line.rstrip()
                    b_lines = cls.test_line(l, l_no, file_path_description)

                    if b_lines > 0:
                        blank_lines += b_lines
                    if b_lines == 0:
                        if blank_lines > 2 and not msg:
                            print(file_path_description, f'Line {l_no}: S006 More than two blank lines preceding a code line')
                        blank_lines = 0
                        msg = False
        except FileNotFoundError:
            print(f'File {file_path} not found')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        checker = LineChecker()
        if os.path.isdir(sys.argv[1]):

            for dirpath, _, filenames in os.walk(sys.argv[1]):
                # sort the list by filename
                filenames.sort()
                for filename in filenames:

                    if filename.endswith(".py"):
                        checker.check_file(os.path.join(dirpath, filename))

        elif os.path.isfile(sys.argv[1]):
            checker.check_file(sys.argv[1])

