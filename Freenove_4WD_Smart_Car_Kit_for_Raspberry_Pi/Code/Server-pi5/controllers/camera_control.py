# controllers/camera_control.py
import cv2
from picamera2 import Picamera2
import time
import logging
import threading
import os
import queue
import zmq
import numpy as np
import json

# ログの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')  # INFOレベルに設定

def send_frame(socket, frame):
    """
    フレームをエンコードして送信する関数
    """
    try:
        # JPEGにエンコード
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            logging.error("Failed to encode frame.")
            return
        # バイナリデータとして送信
        socket.send(buffer.tobytes(), zmq.NOBLOCK)
    except zmq.Again:
        logging.warning("Frame sender socket is not ready to receive frames.")
    except Exception as e:
        logging.error(f"Error sending frame: {e}")

def receive_detection(socket):
    """
    検出結果を受信する関数
    """
    try:
        message = socket.recv_string(flags=zmq.NOBLOCK)
        return message
    except zmq.Again:
        # メッセージがない場合
        return None
    except Exception as e:
        logging.error(f"Error receiving detection: {e}")
        return None

def camera_control(audio_queue):
    """
    カメラから映像を取得し、ARマーカー検出をMac側で行います。
    検出結果に応じて音声を再生します。
    映像をリアルタイムで画面に表示します。
    """
    # ZeroMQコンテキストの作成
    context = zmq.Context()

    # フレーム送信用ソケット（PUSH）
    frame_sender = context.socket(zmq.PUSH)
    frame_sender.connect("tcp://192.168.47.103:5555")  # MacのIPアドレスに置き換えてください

    # 検出結果受信用ソケット（SUB）
    detection_receiver = context.socket(zmq.SUB)
    detection_receiver.connect("tcp://192.168.47.103:5556")  # MacのIPアドレスに置き換えてください
    detection_receiver.setsockopt_string(zmq.SUBSCRIBE, "")  # 全メッセージを購読

    try:
        # Picamera2の初期化
        picam2 = Picamera2()

        # 解像度とフォーマットの設定
        resolution = (320, 240)  # フレームサイズを小さくして処理を高速化
        preview_config = picam2.create_preview_configuration(
            main={"format": 'RGB888', "size": resolution}
        )
        picam2.configure(preview_config)
        picam2.start()
        logging.info("Camera started successfully.")

        # imgフォルダのパスを設定
        script_dir = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(os.path.dirname(script_dir), 'img')
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
            logging.info(f"Image directory created at {img_dir}")

        # 検出済みのマーカーIDを保持するセット
        detected_ids = set()

        # フレーム処理のインターバル設定
        process_every_n_frames = 2  # 2フレームごとに送信
        frame_count = 0

        while True:
            # カメラからフレームをキャプチャ
            frame = picam2.capture_array()

            # キャプチャしたフレームの検証
            if frame is None or frame.size == 0:
                logging.warning("Empty frame captured. Skipping frame processing.")
                continue

            frame_count += 1

            # 必要に応じてフレームを送信
            if frame_count % process_every_n_frames == 0:
                send_frame(frame_sender, frame)

            # 検出結果を受信
            detection = receive_detection(detection_receiver)
            if detection:
                try:
                    # 検出結果の処理（JSON形式を想定）
                    detection_data = json.loads(detection)
                    marker_ids = detection_data.get("marker_ids", [])
                    if marker_ids:
                        new_ids = [marker_id for marker_id in marker_ids if marker_id not in detected_ids]
                        if new_ids:
                            logging.info(f"AR marker(s) detected: {new_ids}")
                            detected_ids.update(new_ids)
                            # 音声再生の指示をキューに送信
                            audio_queue.put("PLAY_AR_SOUND")
                            # 一定時間後に音声停止の指示を送信（例：2秒後）
                            threading.Timer(2.0, lambda: audio_queue.put("STOP_AR_SOUND")).start()
                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding detection data: {e}")
                except Exception as e:
                    logging.error(f"Error processing detection data: {e}")

            # 映像をリアルタイムで表示
            try:
                cv2.imshow("Camera Feed", frame)
                # 'q'キーで終了
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logging.info("Stopping camera feed.")
                    break
            except cv2.error as e:
                logging.error(f"Error displaying frame: {e}")

    except KeyboardInterrupt:
        logging.info("\nExiting camera control thread gracefully.")
    except Exception as e:
        logging.error(f"An unexpected error occurred in camera_control: {e}")
    finally:
        # カメラの停止とOpenCVのウィンドウを閉じる
        if 'picam2' in locals():
            try:
                picam2.stop()
                logging.info("Camera stopped successfully.")
            except Exception as e:
                logging.error(f"Error stopping camera: {e}")
        cv2.destroyAllWindows()
        logging.info("Camera resources have been released.")
        # ソケットのクリーンアップ
        frame_sender.close()
        detection_receiver.close()
        context.term()
