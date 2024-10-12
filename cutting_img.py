import cv2
import os


def cutting_img(inputfolder, fn):

    img = cv2.imread('{}/{}'.format(inputfolder, fn))
    cv2.namedWindow('image', flags=cv2.WINDOW_AUTOSIZE)
    x, y = 0, 0

    h, w, n = img.shape

    while True:
        if y >= h:
            y = h
        elif y < 0:
            y = 0

        if x >= w:
            x = w
        elif x < 0:
            x = 0

        cv2.imshow('image', img[y:y + 1000, x:x + 2000])

        key = cv2.waitKey(0) & 0xFF

        cv2.setMouseCallback('image', left_click, img)

        if key == ord('a') or key == ord('A'):  # 'a' 키 이면 좌로 이동
            x -= 500
        elif key == ord('s') or key == ord('S'):  # 's' 키 이면 아래로 이동
            y += 500
        elif key == ord('w') or key == ord('W'):  # 'w' 키 이면 위로 이동
            y -= 500
        elif key == ord('d') or key == ord('D'):  # 'd' 키 이면 오른쪽으로 이동
            x += 500

        elif key == 13:
            cut_img = img[y_1 + y: y_2 + y, x_1 + x: x_2 + x]
            cv2.imwrite(os.getcwd() +
                        f'\\sheet_test\\cut_img.png', cut_img)

        elif key == ord('q') or key == 27:  # 'q' 이거나 'esc' 이면 종료
            break
    cv2.destroyAllWindows()


def left_click(event, x, y, flags, param):
    global x_1, y_1, x_2, y_2

    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, y)
        x_1, y_1 = x, y

    elif event == cv2.EVENT_RBUTTONDOWN:
        print(x, y)
        x_2, y_2 = x, y
