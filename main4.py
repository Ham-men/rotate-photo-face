import time
import io
import cv2
import imutils as imutils
from PIL import Image
from analis import analis_eye_main, detect_yawn
# from matplotlib import pyplot as plt
# import fitz  # PyMuPDF
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader

#нахожу 1 лицо.
#сделать чтобы он обрезал 3*4 сам. отдельную функцию.
#алгоритм: сначала вращаем лицо, обрезаем 3*4, удаляем белый фон если будет или наоборот.
#запускаю сразу cute face(). пытаюсь анализировать картинку без многочисленных сохранений

photo='14.jpg'
white_background=photo
#функция обрезать белый фон
def trim_white_background(image, tolerance=255):
    # Конвертация изображения в RGBA (если оно не в этом формате)
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Преобразование изображения в массив пикселей
    pixdata = image.load()

    # Определение границ для обрезки
    width, height = image.size
    left, top, right, bottom = width, height, -1, -1

    # Перебор всех пикселей и определение границ
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixdata[x, y]
            if a != 0 and (r < tolerance and g < tolerance and b < tolerance):
                if x < left: left = x
                if y < top: top = y
                if x > right: right = x
                if y > bottom: bottom = y

    # Обрезка изображения
    image = image.crop((left+15, top+15, right, bottom-15))

    return image

#тут я беру картинку и вращаю ее до вертикального состояния. возможно позже надо будет доработать
def analis_face():
    img2 = plt.imread(photo)
    img3=Image.open(photo)
    img3 = trim_white_background(img3)
    #img3.save('res1.png')
    #time.sleep(2)
    #img3=Image.open('res1.png')
    rotate1=0


    while True:
        # Load the cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Convert image to grayscale
        gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        print("количество лиц = ", len(faces))
        # If at least one face is detected
        if len(faces) > 0:


            while True:
                #анализ глаз
                try:
                    EAR, proverka,pitch_naklon_z, image, ear_1x,ear_1y,ear_2x,ear_2y=analis_eye_main(img2)
                    #анализ рот
                    rot_x, rot_y=detect_yawn(image)

                    #пытаюсь улучшить
                    if(abs(ear_1y-ear_2y)>10):

                        if(ear_1y>ear_2y and rot_y>ear_1y):
                            img2 = imutils.rotate(img2, angle=5)
                            rotate1+=5
                        elif(ear_1y>ear_2y and rot_y<ear_1y):
                            img2 = imutils.rotate(img2, angle=5)
                            rotate1+=5
                        else:
                            img2 = imutils.rotate(img2, angle=-5)
                            rotate1+=-5
                    else:
                        break
                except:
                    #cv2.imshow("except", img2)
                    #он обрезает и анализирует маленький участок. проверить координаты обрезки фото. тут он никогда не найдет фото
                    print("не вижу лицо - поворачиваю")
                    img2 = imutils.rotate(img2, angle=5)
                    rotate1+=5
            print(rotate1)
            img3=img3.rotate(rotate1, expand=True)

            #img3.save('res2.png')

            #перевод в jpg
            #rgb_im = img3.convert('RGB')
            white_background = Image.new("RGB", img3.size, (255, 255, 255))

            # Комбинирование исходного изображения с белым фоном
            white_background.paste(img3, mask=img3.split()[3]) # 3 - альфа-канал

            #удалить низ
            # Save the white_background to a buffer
            buffer = io.BytesIO()
            white_background.save(buffer, format="PNG")
            buffer.seek(0)

            # Now you can use buffer as an input to plt.imread and Image.open
            img2 = plt.imread(buffer)
            buffer.seek(0)  # Reset buffer position to the beginning
            img3 = Image.open(buffer)
            #white_background.save('res3.jpg')
            #img3.save('res3.jpg')
            print("обрезаем лица")
            while 1:
                cv2.imshow("te",img2)
                if cv2.waitKey(1) & 0xff == ord('q'):
                    break
            return img2, img3

        else:
            print("No face detected.")
            img2 = imutils.rotate(img2, angle=5)
            rotate1+=5
        if rotate1>=360:
            break
    return 0

#тут я обрезаю 1 лицо и обрезаю белую рамку
def cut_face():
    img2,img3=analis_face()


    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if gray2.dtype != 'uint8':
        gray2 = gray2.astype('uint8')
    # Detect faces
    faces = face_cascade.detectMultiScale(gray2, 1.1, 4)
    print("кол-во лиц = "+str(len(faces)))
    # Get the coordinates of the first face
    (x, y, w, h) = faces[0]
    # while 1:
    #         cv2.imshow("te",faces[0])
    #         if cv2.waitKey(1) & 0xff == ord('q'):
    #             break
    # Define the new boundaries for cropping
    # здесь получаю координаты 1 головы. надо сделать относительными от самой головы
    crop_top = y - h//2  if y - h//2  > 0 else 0
    crop_bottom = y + h * 2
    crop_left = x - w//2 if x - w//2  > 0 else 0
    crop_right = x + w*1.2

    # Ensure the new boundaries do not exceed the image dimensions
    crop_bottom = crop_bottom if crop_bottom < img3.size[1] else img3.size[1]
    crop_right = crop_right if crop_right < img3.size[0] else img3.size[0]

    # Crop the image to the new boundaries
    #img2.crop((crop_left, crop_top, crop_right, crop_bottom))

    face3 = img3.crop((crop_left, crop_top, crop_right, crop_bottom))
    face3 = trim_white_background(face3)

    face3.save('res4.png')

#перевод из pdf в картинку
def pdfread3():
    # Открытие PDF файла
    with open('pdf11.pdf', 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)

        # Выбор страницы
        page = pdf_reader.pages[0]

        # Извлечение изображений со страницы
        xObject = page['/Resources']['/XObject'].get_object()

        for obj in xObject:
            if xObject[obj]['/Subtype'] == '/Image':
                size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                data = xObject[obj].get_data()  # Используйте get_data() вместо _data

                # Проверка, является ли изображение в формате JPEG
                if xObject[obj]['/Filter'] == '/DCTDecode':
                    file_ext = 'jpg'
                elif xObject[obj]['/Filter'] == '/JPXDecode':
                    file_ext = 'jp2'
                else:
                    file_ext = 'png'

                # Сохранение изображения
                with io.BytesIO(data) as image_stream:
                    img = Image.open(image_stream)
                    img.save(f'res3.{file_ext}')
                    # while 1:
                    #     cv2.imshow("te",img)
                    #     if cv2.waitKey(1) & 0xff == ord('q'):
                    #         break


if __name__ == '__main__':
    #analis_face()
    #time.sleep(2)
    cut_face()
    #pdfread3()
