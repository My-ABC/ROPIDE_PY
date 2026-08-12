import rop_parser as parser
import render
import read_rop
import rich
from rich.traceback import install

install()

if __name__ == '__main__':
    # 读取 .rop 文件
    file_data = read_rop.read_rop_file('if-then.rop')
    
    if file_data is None:
        print("读取 .rop 文件失败")
        exit()
    
    # 解析
    res = parser.parseRopInput(
        file_data['input'],
        file_data['gadgets'],
        {
            "leftStartAddress": file_data['leftStartAddress'],
            "rightStartAddress": file_data['rightStartAddress']
        }
    )
    
    # 显示结果
    render.set_mode(True)
    rich.print(render.render_highlighted_code(res['highlightLines']))
    print(f"hexChars: {res['hexChars']}")
    print(f"errorCount: {res['errorCount']}")