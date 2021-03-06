# -*- coding:utf-8 -*-
# !/usr/bin/env python
import os
import argparse as ap
import re
import json
from multiprocessing import Pool as mp


class phoneDict(object):
    def __init__(self, file_path):
        self.phone_dict = self.loadDict(file_path)

    def loadDict(self, file_path):
        fileIn = file(file_path)
        my_dict = json.load(fileIn)
        return my_dict

def _convert_transcription(phone_dict, line, txtfile_path, output_txt_file, failed_txt_file):
    pass_flag = True
    failed_words = ''
    failed_list = []
    content = []
    fid = open(output_txt_file, 'w')
    for word in line:
        if word in phone_dict:
            hasPhone = phone_dict[word]
            if len(hasPhone) > 1:   # if it's polyphone
                pass_flag = False
                failed_words += word
                failed_list.append(' '.join(hasPhone))
                fid.write('<multi>\n')
                content.append('<multi>'+' '.join(hasPhone))
            else:
                fid.write(hasPhone[0]+'\n')
                fid.write('<space>\n')
                content.append(hasPhone[0])
        else:  # failed to transform phone
            pass_flag = False
            failed_words += word
            failed_list.append('#')
            fid.write('<unfound>\n')
            content.append('<unfound>')
    if not pass_flag:
        fid.close()
        os.system('rm '+output_txt_file)
        if not os.path.exists(failed_txt_file):
            os.system('cp '+txtfile_path+' '+failed_txt_file)
            fid2 = open(failed_txt_file, 'w')
            fid2.write(line.encode('utf-8')+'\n')
            fid2.write(' '.join(content).encode('utf-8')+'\n')
            fid2.write(failed_words.encode('utf-8')+'\n')
            fid2.write(','.join(failed_list).encode('utf-8')+'\n')
            fid2.close()
    # if not os.path.exists(output_wav_file):
    #     os.system('cp '+wavfile_path+' '+output_txt_file)


if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument("--output",help="Path to input files", default="output") 
    # parser.add_argument("--wav_dir", default='wav', type=str, help="Directory to store the dataset.")
    parser.add_argument("--txt_dir", default='txt', type=str, help="Directory to store the dataset.")
    parser.add_argument("--dict_file", default='Chinese_phone_dict1.json', type=str, help="Directory to store the dataset.")

    args = vars(parser.parse_args())
    input_txt_dir = args["txt_dir"]  # input txt dir
    # input_wav_dir = args["wav_dir"]  # input wav dir
    dict_file = args["dict_file"]
    output_txt_dir = os.path.join(args["output"], 'phone-txt')  # output phoneme txt dir
    if not os.path.isdir(output_txt_dir):
        os.makedirs(output_txt_dir)
    # output_wav_dir = os.path.join(args["output"], 'phone-wav')
    # if not os.path.isdir(output_wav_dir):
    #     os.makedirs(output_wav_dir)
    failed_txt_dir = os.path.join(args["output"], 'failed-txt')  # output failed to transform txt dir
    if not os.path.isdir(failed_txt_dir):
        os.makedirs(failed_txt_dir)
    # failed_wav_dir = os.path.join(args["output"], 'failed-wav')
    # if not os.path.isdir(failed_wav_dir):
    #     os.makedirs(failed_wav_dir)

    dict_class = phoneDict(dict_file)  # load phone dict
    print("test word: %s : %s " % ('hello',dict_class.txtToDict2("今天。")))  # dictionary test
    input_files = os.listdir(input_txt_dir)
    data_num = 0
    total_num = len(input_files)
    processers = mp(32)
    for index,file_name in enumerate(input_files):
        # break
        # print("Processing: %s" % (file_name))
        lines = open(os.path.join(input_txt_dir, file_name)).readlines()
        # wavfile_path = os.path.join(input_wav_dir, file_name[:-4]+'.wav')
        txtfile_path = os.path.join(input_txt_dir, file_name)
        # output_wav_file = os.path.join(output_wav_dir, file_name[:-4]+'.wav') 
        output_txt_file = os.path.join(output_txt_dir, file_name) 
        failed_txt_file = os.path.join(failed_txt_dir, file_name)
        for line in lines:
            line = line.strip()
            # print(line)
            try:
                line = line.decode('utf-8', 'ignore').strip()
            except:
                print("failed decode %s " % (file_name))
                continue
            processers.apply_async(_convert_transcription,args=(dict_class.phone_dict, line, txtfile_path, output_txt_file, failed_txt_file))
            # _convert_transcription(dict_class.phone_dict, line, txtfile_path, output_txt_file, failed_txt_file)
    processers.close()
    processers.join()
    # update_progress(index/float(total_num))  
    # print("total copy data_num: %d" % (data_num))
