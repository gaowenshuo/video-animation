def process_image(content_image_path):
    import os
    from PIL import Image
    import torch
    import kornia as K
    import cv2
    from kornia.contrib import FaceDetector , FaceDetectorResult

    model = torch.hub.load (
        "AK391/animegan2-pytorch:main" ,
        "generator" ,
        pretrained=True ,
        progress=False
    )
    face2paint = torch.hub.load (
        'AK391/animegan2-pytorch:main' , 'face2paint' ,
        size=512 , side_by_side=False
    )
    face2paint_high = torch.hub.load (
        'AK391/animegan2-pytorch:main' , 'face2paint' ,
        size=1024 , side_by_side=False
    )

    content_image = Image.open ( content_image_path )
    device = torch.device ( "cpu" )
    dtype = torch.float32

    # 动漫化处理图片，输入图片：PIL.Image，是否高清：bool
    def process(content_image , high=False):
        w , h = content_image.size
        size = max ( w , h )
        square_image = Image.new ( 'RGB' , (size , size) , (127 , 127 , 127) )
        x = (size - w) // 2
        y = (size - h) // 2
        square_image.paste ( content_image , (x , y) )
        square_image = square_image.resize ( (512 , 512) , Image.BICUBIC )
        if high:
            result_image = face2paint_high ( model , square_image )
        else:
            result_image = face2paint ( model , square_image )
        result_image = result_image.resize ( (size , size) , Image.BICUBIC )
        left = (size - w) // 2
        top = (size - h) // 2
        right = left + w
        bottom = top + h
        result_image = result_image.crop ( (left , top , right , bottom) )
        return result_image

    # 处理原图
    result_image = process ( content_image , True )
    result_image_path = content_image_path[ 0:-4 ] + " output.jpg"
    result_image.save ( result_image_path )
    # 人脸识别
    content_image_whole = cv2.imread ( content_image_path , cv2.IMREAD_COLOR )
    img = K.image_to_tensor ( content_image_whole , keepdim=False ).to ( device )
    img = K.color.bgr_to_rgb ( img.float () )
    face_detection = FaceDetector ().to ( device )
    with torch.no_grad ():
        dets = face_detection ( img )
    dets = [ FaceDetectorResult ( o ) for o in dets[ 0 ] ]
    for b in dets:
        top_left = b.top_left.int ().tolist ()
        bottom_right = b.bottom_right.int ().tolist ()
        score = b.score
        if score < 0.7:
            continue
        print ( top_left , bottom_right )
        x1 , y1 = top_left
        x2 , y2 = bottom_right
        w , h = content_image.size
        if x1 < 0 or y1 < 0 or x2 > w or y2 > h:
            continue
        cropped_img = content_image_whole[ y1:y2 , x1:x2 ]
        cv2.imwrite ( content_image_path[ 0:-4 ] + " face" + '.jpg' , cropped_img )
        face_content_image = Image.open ( content_image_path[ 0:-4 ] + " face" + '.jpg' )
        face_result_image = process ( face_content_image )
        # 模糊处理边缘并粘贴图片
        face_w, face_h = face_result_image.size
        for x in range ( face_w ):
            for y in range ( face_h ):
                b_x , b_y = x + x1 , y + y1
                opacity = 127
                distance = min ( x/face_w , y/face_h , (face_w - x)/face_w , (face_h - y)/face_h )
                opacity = int(min(255, 2550 * distance))
                pixel_a = face_result_image.getpixel ( (x , y) )
                pixel_b = result_image.getpixel ( (b_x , b_y) )
                pixel = ((pixel_a[ 0 ] * opacity + pixel_b[ 0 ] * (255 - opacity)) // 255 ,
                         (pixel_a[ 1 ] * opacity + pixel_b[ 1 ] * (255 - opacity)) // 255 ,
                         (pixel_a[ 2 ] * opacity + pixel_b[ 2 ] * (255 - opacity)) // 255)
                result_image.putpixel ( (b_x , b_y) , pixel )
        os.remove (content_image_path[ 0:-4 ] + " face" + '.jpg')
    result_image_path = content_image_path[ 0:-4 ] + " output.jpg"
    result_image.save ( result_image_path )
    # result_image.show ()