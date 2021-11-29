print("test")
import csv
import time
import os
# for logfile
import my_log
import datetime
# for my_inspect
import cv2


print("\n\033[32m...........program booting...........\033[0m\n")

def main():
    wd = os.getcwd()
    if os.getcwd()[-3:] != "src":
        print("workdir error : cd src/")
        exit()
    download_list = my_log.mylog(file_name = 'out_for_issue/__logfile__/download_list_issue.csv',
                                field_names = ['flag',
                                                'repo_name',
                                                'PR_id',
                                                'number',
                                                'url',
                                                'address',
                                                'img_or_mov'])
    movs_num_list = my_log.mylog(file_name = 'out_for_issue',
                                field_names = ['mov_number',
                                                'mov_url',
                                                'pixels_of_height',
                                                'pixels_of_width',
                                                'volume',
                                                'length_or_numOfSheets',
                                                'extension'],
                                create_file = False)
    
    file_name = './out_for_issue/__logfile__/download_list_issue.csv'
    with open(file_name, mode='r') as f_in:
        reader = csv.reader(f_in)
        l = [row for row in reader]
        len_l = len(l)
    for i in range(1,len_l):
        r = csv_mod_read_row(file_name, i)
        if r != None:
            flag    = r[0]
            repo_name=r[1]
            PR_id   = r[2]
            counter = r[3]
            img_url = r[4]
            address = r[5]
            img_or_mov = r[6]
            print(f"({i:05}/{len_l}){address}")
            if img_or_mov == "mov":
                my_address = myget_name_left(address, f'/mov{counter}')
                movs_num_list.reset_buf()
                movs_num_list.setup_file(f"{my_address}/movs_detail.csv")
                log = movs_num_list
            else :
                # This message say that you need to execute download.py again.
                print(f'$[img_or_mov] is [{img_or_mov}] which is invalid input.')
                flag = "error"

            # Let's try to download
            if flag == "notDone" and not(os.path.exists(f"{wd}/{address}")):
                try:
                    if os.system("curl {} --progress-bar > {}".format(img_url, f"{wd}/{address}")) != 0:
                        raise Exception("os.system error")
                except Exception as e:
                    print(e)
                else:
                    is_success = my_inspect(repo_name,PR_id,counter,img_url,address,img_or_mov,log)
                    if is_success == True:
                        download_list.rewrite(["Done",
                                            r[1],
                                            r[2],
                                            r[3],
                                            r[4],
                                            r[5],
                                            r[6]],
                                            idx=i-1)
                    else:
                        pass

                time_saver(5)

            # already downloaded.
            elif flag == "notDone" and os.path.exists(f"{wd}/{address}"):
                print(f"file already exists, (no.{i}) please check manually.[{address}] ")

            elif flag == "error":
                # you need to execute download.py again.
                pass
            else:
                print(f"   ----->  pass")

        elif r == None:
            print("\033[33m no data. \033[0m")

    print("\n\n\033[32m...........all tasks done!!...........\033[0m\n")




def time_saver(i):
    i = int(i)
    print("[", end='', flush=True)
    for j in range(2*i):
        print("*", end='', flush=True)
        time.sleep(0.5)
    print("]", end='', flush=True)
    for j in range(2*i+2):
        print("\b", end='', flush=True)

def csv_mod_read_row(path, idx):
    with open(path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if reader.line_num - 1 == idx:
                return row
    return None

def my_inspect(repo_name,PR_id,counter,img_url,address,img_or_mov,log):
    for i in range(int(counter)):
        is_exist , temp_url = log.check_log(target=i+1,num1=0)
        if is_exist == -1:
            log.write([i+1])

    if img_or_mov == "img":
        extension = myget_name_right(address, target=f"img{counter}.")
        my_img = cv2.imread(address)
        if my_img == None:
            print("Failed to load image file.")
            log.rewrite([counter,
                        img_url,
                        'download_error',
                        'download_error',
                        'download_error',
                        extension],
                        idx = int(counter)-1)
            return False
        else:
            # 解像度を取得
            pixels_of_height,pixels_of_width = my_img.shape[:2]
            # サイズを取得、単位はバイト
            volume = os.path.getsize(address)
            # logファイルに出力
            log.rewrite([counter,
                        img_url,
                        pixels_of_height,
                        pixels_of_width,
                        volume,
                        extension],
                        idx = int(counter)-1)
            return True

    elif img_or_mov == "mov":
        extension = myget_name_right(address, target=f"mov{counter}.")
        if extension == "gif":
            my_mov = cv2.VideoCapture(address)
            if my_mov == None:
                print("Failed to load image file.")
                pixels_of_height = 'download_error'
                pixels_of_width = 'download_error'
                length_or_numOfSheets = 'download_error'
                volume = 'download_error'
            else:
                # 解像度を取得
                pixels_of_height = str(my_mov.get(cv2.CAP_PROP_FRAME_HEIGHT))
                pixels_of_width = str(my_mov.get(cv2.CAP_PROP_FRAME_WIDTH))
                length_or_numOfSheets = str(my_mov.get(cv2.CAP_PROP_FRAME_COUNT))
                volume = str(os.path.getsize(address))
        elif extension == "mp4" or extension == "mov":
            my_mov = cv2.VideoCapture(address)
            if my_mov == None:
                print("Failed to load image file.")
                pixels_of_height = 'download_error'
                pixels_of_width = 'download_error'
                length_or_numOfSheets = 'download_error'
                volume = 'download_error'
            else:
                # 解像度を取得
                pixels_of_height = str(my_mov.get(cv2.CAP_PROP_FRAME_HEIGHT))
                pixels_of_width = str(my_mov.get(cv2.CAP_PROP_FRAME_WIDTH))
                length_or_numOfSheets = str(my_mov.get(cv2.CAP_PROP_FRAME_COUNT) / my_mov.get(cv2.CAP_PROP_FPS))
                volume = str(os.path.getsize(address))

        # サイズを取得、単位はバイト
        volume = os.path.getsize(address)
        # logファイルに出力
        log.rewrite([counter,
                    img_url,
                    pixels_of_height,
                    pixels_of_width,
                    volume,
                    length_or_numOfSheets,
                    extension],
                    idx = int(counter)-1)
        if pixels_of_height == 'download_error':
            return False
        elif pixels_of_height != 'download_error':
            return True

def myget_name_left(text, target):
    # ${target}より前を抽出したい
    idx = text.find(target)
    t = text[:idx]
    return t
def myget_name_right(text, target):
    # ${target}より後を抽出したい
    idx = text.find(target)
    t = text[idx+len(target):]
    return t
if(__name__=="__main__"):
    main()
