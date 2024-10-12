import os
from pdf2image import convert_from_path

import PyPDF2

from PyPDF2 import PdfReader

from tkinter import filedialog
from tkinter import messagebox

import cv2

import numpy as np

from change_image import *

from find_staff import get_staff_lines


def pdf_2_image():
    files = filedialog.askopenfilenames(initialdir="/",
                     title = "파일을 선택 해 주세요",
                        filetypes = (("*.pdf","*pdf"),("*.mid","*mid"),))
    #files 변수에 선택 파일 경로 넣기

    if files == '':
        messagebox.showwarning("경고", "파일을 추가 하세요")    # 파일 선택 안했을 때 메세지 출력

    size_w = 3400
    size_h = 4400
    while True:
        # PDF 파일을 이미지로 변환
        pages = convert_from_path(files[0],
                                  poppler_path= os.getcwd() +
                                '\\poppler-0.68.0_x86\\poppler-0.68.0\\bin',
                                  size=(size_w, size_h))  # 3400, 4400

        # 첫 번째 페이지 이미지를 선택
        image = pages[0]

        # 이미지를 메모리에서 직접 읽어오기
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

        threshold, img = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)

        h, w = img.shape

        # 스태프 높이 (h) 값 리스트
        staff_lines = get_staff_lines(w, h, img)

        diff_h = staff_lines[4] - staff_lines[0]

        diff_w = find_diff_w(img, staff_lines)

        c_h, c_w, is_same = resize_img(diff_h, diff_w)

        if is_same is True:
            break

        size_w += c_w
        size_h += c_h

    # file_name 은 경로까지 설정할수가 있다. (사용할 이름까지 적어줘야 한다.)
    file = os.getcwd() + f'\\input\\test'

    for i, page in enumerate(pages):
      page.save(file + str(i) + ".jpg", "JPEG")


def change_pdf_dpi():
    # PDF 파일 열기
    i = 1
    while True:
        files = filedialog.askopenfilenames(initialdir="/",
                                            title="파일을 선택 해 주세요",
                                            filetypes=(("*.pdf", "*pdf"), ("*.mid", "*mid"),))[0]
        pdf_reader = PdfReader(files)
        page_size = pdf_reader.pages[0].mediabox
        # 가로, 세로 크기 추출
        width, height = page_size[2], page_size[3]

        print(width, height)
        key = cv2.waitKey(0) & 0xFF

        # esc 누르면 종료
        if key == 27:
            break

        page = pdf_reader.pages[0]
        page.scale_to(495, 792)  # 595 792

        with open('output_%d.pdf' % i, 'wb') as f:
            pdf_writer = PyPDF2.PdfWriter()
            pdf_writer.add_page(page)
            pdf_writer.write(f)

        i += 1

        if i == 4:
            break


