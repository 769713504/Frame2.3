from Py_Main.Main import showMainWindow


def run():
    while True:
        try:
            showMainWindow()
            break
        except SystemExit as e:
            s = str(e)
            if s.isdigit():
                exit_code = int(s)
                if exit_code == 6:
                    continue
                elif exit_code == 0:
                    break
                else:
                    print('退出编号: %s' % s)
                    break
            else:
                raise SystemExit('程序运行中断,返回值: %s' % s)


if __name__ == '__main__':
    run()
