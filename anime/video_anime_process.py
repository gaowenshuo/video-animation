import os
import ffmpeg
from anime_func import process_image


def anime_video_frame(video_path , output_path , position_seconds , duration_seconds):
    input_video = ffmpeg.input ( video_path , ss=str ( position_seconds ) )
    probe = ffmpeg.probe ( video_path )
    video_stream = next ( (stream for stream in probe[ 'streams' ] if stream[ 'codec_type' ] == 'video') , None )
    frame_rate = eval ( video_stream[ 'r_frame_rate' ] )
    temp_image_path = 'temp.jpg'
    img_output = ffmpeg.output ( input_video , temp_image_path , vframes=1 )
    ffmpeg.run ( img_output , overwrite_output=True )
    anime_image_path = 'temp output.jpg'
    process_image ( temp_image_path )
    input_image = ffmpeg.input ( anime_image_path , loop=1 , t=str ( duration_seconds ) , framerate=frame_rate )
    output_b_video = ffmpeg.output ( input_image , "tmp_b.mp4" , vf='setsar=1/1' )
    ffmpeg.run ( output_b_video , overwrite_output=True )
    input_a_video = ffmpeg.input ( video_path , ss='0' , t=str ( position_seconds ) )
    output_a_video = ffmpeg.output ( input_a_video , 'tmp_a.mp4' , vf='setsar=1/1' )
    ffmpeg.run ( output_a_video , overwrite_output=True )
    input_c_video = ffmpeg.input ( video_path , ss=str ( position_seconds ) )
    output_c_video = ffmpeg.output ( input_c_video , 'tmp_c.mp4' , vf='setsar=1/1' )
    ffmpeg.run ( output_c_video , overwrite_output=True )
    input1 = ffmpeg.input ( 'tmp_a.mp4' )
    input2 = ffmpeg.input ( 'tmp_b.mp4' )
    input3 = ffmpeg.input ( 'tmp_c.mp4' )
    output = ffmpeg.concat ( input1 , input2 , input3 ).output ( output_path )
    ffmpeg.run ( output , overwrite_output=True )
    os.remove ( temp_image_path )
    os.remove ( anime_image_path )
    os.remove ( 'tmp_a.mp4' )
    os.remove ( 'tmp_b.mp4' )
    os.remove ( 'tmp_c.mp4' )


def anime_video_frames(video_path , output_path , position_seconds_list , duration_seconds_list):
    nums = len ( position_seconds_list )
    if nums != len ( duration_seconds_list ):
        print ( "The lists has different lengths" )
        return
    info = ffmpeg.probe ( video_path )
    duration = float ( info[ 'format' ][ 'duration' ] )
    print ( "Video length:" , duration )
    for i in range ( nums ):
        if position_seconds_list[ i ] > duration:
            print ( "Time exceeded" )
            return
    now_addition = 0.0
    for i in range ( nums ):
        if i == 0:
            anime_video_frame ( video_path , output_path , position_seconds_list[ i ] , duration_seconds_list[ i ] )
            now_addition = now_addition + duration_seconds_list[ i ]
        else:
            anime_video_frame ( output_path , output_path , position_seconds_list[ i ] + now_addition ,
                                duration_seconds_list[ i ] )
            now_addition = now_addition + duration_seconds_list[ i ]
    return


if __name__ == '__main__':
    video_path = 'IMG_6302.mp4'
    output_path = 'IMG_6302 output.mp4'
    position_seconds_list = [ 3 , 7.7 ]
    duration_seconds_list = [ 1 , 1 ]
    anime_video_frames ( video_path , output_path , position_seconds_list , duration_seconds_list )
