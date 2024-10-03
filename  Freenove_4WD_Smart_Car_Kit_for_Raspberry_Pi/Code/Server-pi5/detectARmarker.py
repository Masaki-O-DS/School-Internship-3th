# piカメラ画像からopencvでARマーカーを検知するプログラム
import cv2
from cv2 import aruco
from picamera2 import Picamera2, Preview

def main(): 
    picam2 = Picamera2()
    preview_config = picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)})
    picam2.configure(preview_config)
    picam2.start()
    
    detected_markers = []

    # カメラ画像を取得
    frame = picam2.capture_array()
    #cv2.imshow("", frame)

    # 画像を前処理:グレースケール化
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #OpenCVは色コードをBGRで扱っているらしいのでRGBに変換しておく
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # ARマーカー検知
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50) # 4x4bitのARマーカーを検知するモデル指定
    parameters =  aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    # 検知箇所を画像にマーキング
    frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners, ids)
    cv2.imshow("result", cv2.cvtColor(frame_markers, cv2.COLOR_BGR2RGB))

    # キー入力があるまで待機. その後終了.
    cv2.waitKey(0)
    #cv2.imwrite('capture.jpg', frame_markers)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
