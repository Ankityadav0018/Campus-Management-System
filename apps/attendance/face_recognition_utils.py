"""
AI Face Recognition Utilities - DeepFace Edition (dlib-free)
Uses DeepFace + OpenCV — works on Apple Silicon, no dlib required.

Key fixes vs previous version:
  - Camera lock deadlock fixed: capture_and_recognize reuses the open camera
    instead of calling initialize_camera() again while generate_frames() holds it.
  - BGR slice order fixed: frame[top:bottom, left:right] was transposed.
  - Quality threshold lowered (webcam frames are fine at 20+).
  - enforce_detection=False on live frames so partial/angled faces still work.
"""

import cv2
import numpy as np
import pickle
from django.conf import settings
import os
from .models import StudentFace, Student, Attendance
from datetime import datetime
import logging
from threading import Lock
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

# ── Globals ────────────────────────────────────────────────────────────────────
camera = None
camera_lock = Lock()

known_face_encodings = []   # list of np.ndarray shape (128,)
known_face_names     = []
known_face_ids       = []
face_data_lock = Lock()

CONFIG = {
    'frame_width':  640,
    'frame_height': 480,
    'fps':          30,
    'jpeg_quality': 80,
    'frame_skip':   3,
    'resize_factor': 0.5,
    'quality_threshold': 20.0,   # lowered — webcam frames are fine at 20+
    'min_confidence':    0.55,   # cosine-similarity minimum to accept a match
    'model_name':       'Facenet',
    'detector_backend': 'opencv',
    'bulk_recognition_frames': 10,
    'recognition_consensus':   2,
}

# ── Lazy DeepFace import ───────────────────────────────────────────────────────
_deepface = None

def _get_deepface():
    global _deepface
    if _deepface is None:
        from deepface import DeepFace
        _deepface = DeepFace
    return _deepface

# ── OpenCV Haar cascade (dlib-free) ────────────────────────────────────────────
_face_cascade = None

def _get_cascade():
    global _face_cascade
    if (_face_cascade is None):
        path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        _face_cascade = cv2.CascadeClassifier(path)
    return _face_cascade


# ── Camera management ──────────────────────────────────────────────────────────

def initialize_camera(retries=3):
    """Open and return the shared camera, or None on failure."""
    global camera
    with camera_lock:
        if camera is not None and camera.isOpened():
            return camera
        for attempt in range(retries):
            for idx in [0, 1, -1]:
                cam = cv2.VideoCapture(idx)
                if not cam.isOpened():
                    continue
                cam.set(cv2.CAP_PROP_FRAME_WIDTH,  CONFIG['frame_width'])
                cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CONFIG['frame_height'])
                cam.set(cv2.CAP_PROP_FPS,          CONFIG['fps'])
                cam.set(cv2.CAP_PROP_BUFFERSIZE,   1)
                ret, _ = cam.read()
                if ret:
                    camera = cam
                    logger.info(f"Camera initialised at index {idx}")
                    return camera
                cam.release()
            if attempt < retries - 1:
                time.sleep(1)
    logger.error("Failed to initialise camera after all retries")
    return None


def release_camera():
    global camera
    with camera_lock:
        if camera is not None:
            try:
                camera.release()
            except Exception as e:
                logger.error(f"release_camera error: {e}")
            finally:
                camera = None


# ── Image quality ──────────────────────────────────────────────────────────────

def check_image_quality(image):
    """Laplacian-variance blur check. Returns (is_ok, score)."""
    try:
        gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        score = cv2.Laplacian(gray, cv2.CV_64F).var()
        return score >= CONFIG['quality_threshold'], float(score)
    except Exception as e:
        logger.error(f"check_image_quality: {e}")
        return False, 0.0


# ── DeepFace helpers ───────────────────────────────────────────────────────────

def _represent(img, enforce=True):
    """
    Call DeepFace.represent on a file path or numpy array.
    Returns list of result dicts, or [] on failure.
    """
    DeepFace = _get_deepface()
    try:
        return DeepFace.represent(
            img_path=img,
            model_name=CONFIG['model_name'],
            detector_backend=CONFIG['detector_backend'],
            enforce_detection=enforce,
        )
    except Exception as e:
        logger.debug(f"DeepFace.represent failed: {e}")
        return []


def _embedding_from_result(result):
    """Extract a float32 (128,) embedding from a DeepFace result list."""
    if result:
        return np.array(result[0]['embedding'], dtype=np.float32)
    return None


# ── Face encoding for registration ────────────────────────────────────────────

def encode_face_from_image(image_path):
    """
    Encode a face from a saved image file.
    Returns (success, message, embedding, quality_score).
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False, "Could not read image file.", None, 0.0

        ok, quality = check_image_quality(img)
        if not ok:
            return False, (
                f"Image too blurry (score {quality:.1f}, need ≥{CONFIG['quality_threshold']})."
                " Use better lighting or a sharper photo."
            ), None, quality

        result = _represent(image_path, enforce=True)
        if not result:
            return False, "No face detected. Make sure the face is clearly visible.", None, quality

        if len(result) > 1:
            return False, "Multiple faces detected. Please use a photo with only one face.", None, quality

        embedding = _embedding_from_result(result)
        logger.info(f"Face encoded OK — quality={quality:.1f}, shape={embedding.shape}")
        return True, "Face registered successfully!", embedding, quality

    except Exception as e:
        logger.error(f"encode_face_from_image: {e}")
        return False, f"Error processing image: {e}", None, 0.0


def process_and_encode_face(image_file):
    """
    Encode a face from a Django UploadedFile.
    Returns (success, message, embedding).
    """
    temp_dir  = os.path.join(settings.MEDIA_ROOT, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f'tmp_{datetime.now().timestamp()}.jpg')
    try:
        with open(temp_path, 'wb+') as f:
            for chunk in image_file.chunks():
                f.write(chunk)
        ok, msg, enc, _ = encode_face_from_image(temp_path)
        return ok, msg, enc
    except Exception as e:
        logger.error(f"process_and_encode_face: {e}")
        return False, str(e), None
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ── Known-face store ───────────────────────────────────────────────────────────

def load_known_faces():
    """
    Load all registered student embeddings from the DB into memory.
    Returns the number of faces loaded.
    """
    global known_face_encodings, known_face_names, known_face_ids
    with face_data_lock:
        known_face_encodings = []
        known_face_names     = []
        known_face_ids       = []
        loaded = failed = 0
        try:
            for sf in StudentFace.objects.select_related('student').all():
                if not sf.face_encoding:
                    continue
                try:
                    enc = pickle.loads(bytes(sf.face_encoding))
                    enc = np.array(enc, dtype=np.float32)
                    if enc.ndim != 1 or enc.shape[0] == 0:
                        raise ValueError(f"Bad shape {enc.shape}")
                    known_face_encodings.append(enc)
                    known_face_names.append(sf.student.name)
                    known_face_ids.append(sf.student.student_id)
                    loaded += 1
                except Exception as e:
                    logger.error(f"Bad encoding for {sf.student.name}: {e}")
                    failed += 1
        except Exception as e:
            logger.error(f"load_known_faces DB error: {e}")
        logger.info(f"Loaded {loaded} face(s), {failed} failed")
        return loaded


# ── Matching ───────────────────────────────────────────────────────────────────

def _cosine_similarity(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _find_best_match(embedding):
    """
    Return (name, student_id, confidence) for the closest registered face,
    or ("Unknown", None, score) if no match is confident enough.
    """
    with face_data_lock:
        if not known_face_encodings:
            return "Unknown", None, 0.0
        sims     = [_cosine_similarity(embedding, k) for k in known_face_encodings]
        best_idx = int(np.argmax(sims))
        best_sim = sims[best_idx]
        if best_sim >= CONFIG['min_confidence']:
            return known_face_names[best_idx], known_face_ids[best_idx], best_sim
        return "Unknown", None, best_sim


# ── Frame-level detection + recognition ───────────────────────────────────────

def _detect_faces_opencv(frame):
    """
    Haar-cascade face detection.
    Returns list of (top, right, bottom, left) in original-frame coords.
    """
    cascade = _get_cascade()
    gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    dets    = cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50)
    )
    boxes = []
    if len(dets):
        for (x, y, w, h) in dets:
            boxes.append((y, x + w, y + h, x))   # top, right, bottom, left
    return boxes


def _embed_cropped_face(frame, box):
    """
    Crop the face region and get a DeepFace embedding.
    box = (top, right, bottom, left)
    """
    DeepFace = _get_deepface()
    top, right, bottom, left = box
    # Correct numpy slice: rows = top:bottom, cols = left:right
    face_img = frame[top:bottom, left:right]
    if face_img.size == 0:
        return None
    try:
        result = DeepFace.represent(
            img_path=face_img,
            model_name=CONFIG['model_name'],
            detector_backend='skip',       # already cropped
            enforce_detection=False,
        )
        return _embedding_from_result(result)
    except Exception as e:
        logger.debug(f"_embed_cropped_face: {e}")
        return None


def recognize_faces_in_frame(frame):
    """
    Detect and recognise all faces in *frame*.
    Returns list of (name, student_id, (top,right,bottom,left), confidence, is_real).
    """
    if not known_face_encodings:
        return []
    try:
        # Downscale for faster detection
        small  = cv2.resize(frame, (0, 0),
                             fx=CONFIG['resize_factor'],
                             fy=CONFIG['resize_factor'])
        boxes_small = _detect_faces_opencv(small)
        if not boxes_small:
            return []

        scale   = 1.0 / CONFIG['resize_factor']
        results = []
        for (st, sr, sb, sl) in boxes_small:
            # Scale back to original frame coords
            top, right, bottom, left = (
                int(st * scale), int(sr * scale),
                int(sb * scale), int(sl * scale),
            )
            box_orig = (top, right, bottom, left)

            embedding = _embed_cropped_face(frame, box_orig)
            if embedding is None:
                results.append(("Unknown", None, box_orig, 0.0, True))
                continue

            name, sid, conf = _find_best_match(embedding)
            results.append((name, sid, box_orig, conf, True))
        return results
    except Exception as e:
        logger.error(f"recognize_faces_in_frame: {e}")
        return []


def recognize_faces_in_frame_fast(frame):
    return recognize_faces_in_frame(frame)


# ── Drawing ────────────────────────────────────────────────────────────────────

def draw_faces_on_frame(frame, recognized_faces):
    try:
        for name, sid, (top, right, bottom, left), conf, _ in recognized_faces:
            color = (0, 165, 255) if name == "Unknown" else (0, 220, 0)
            label = "Unknown" if name == "Unknown" else f"{name} ({conf*100:.0f}%)"
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, label, (left + 4, bottom - 8),
                        cv2.FONT_HERSHEY_DUPLEX, 0.45, (255, 255, 255), 1)
        info = f"Faces detected: {len(recognized_faces)}"
        cv2.putText(frame, info, (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, info, (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    except Exception as e:
        logger.error(f"draw_faces_on_frame: {e}")
    return frame


# ── Video streaming ────────────────────────────────────────────────────────────

def generate_frames():
    """
    MJPEG generator for Django StreamingHttpResponse.
    The camera lock is held only for the duration of each cam.read() call,
    so capture_and_recognize() can grab frames in between.
    """
    global camera
    camera = initialize_camera()
    if camera is None:
        logger.error("generate_frames: camera unavailable")
        return

    frame_count = 0
    last_faces  = []
    try:
        while True:
            # Hold lock only for the read — release immediately after
            with camera_lock:
                if camera is None or not camera.isOpened():
                    break
                success, frame = camera.read()

            if not success:
                time.sleep(0.05)
                continue

            frame_count += 1
            if frame_count % CONFIG['frame_skip'] == 0:
                try:
                    last_faces = recognize_faces_in_frame(frame)
                except Exception as e:
                    logger.error(f"generate_frames recognition: {e}")

            frame = draw_faces_on_frame(frame, last_faces)

            ret, buf = cv2.imencode(
                '.jpg', frame,
                [cv2.IMWRITE_JPEG_QUALITY, CONFIG['jpeg_quality']]
            )
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n'
                       + buf.tobytes() + b'\r\n')

    except GeneratorExit:
        pass
    except Exception as e:
        logger.error(f"generate_frames error: {e}")
    finally:
        logger.info("Video stream ended")


# ── Attendance capture ─────────────────────────────────────────────────────────

def capture_and_recognize():
    """
    Grab several frames from the (already-open) camera and return
    [(student_id, avg_confidence), …] for all recognised students.

    NOTE: does NOT call initialize_camera() again — the camera may already
    be open by generate_frames().  We just grab the global instance.
    """
    global camera

    # If camera isn't open yet, open it now
    if camera is None or not camera.isOpened():
        camera = initialize_camera()
    if camera is None:
        logger.error("capture_and_recognize: no camera")
        return []

    seen = defaultdict(list)

    for _ in range(10):          # sample 10 frames for better accuracy
        with camera_lock:
            if camera is None or not camera.isOpened():
                break
            ok, frame = camera.read()

        if not ok:
            time.sleep(0.05)
            continue

        for name, sid, loc, conf, is_real in recognize_faces_in_frame(frame):
            if sid and is_real and conf >= CONFIG['min_confidence']:
                seen[sid].append(conf)

        time.sleep(0.08)

    if not seen:
        logger.info("capture_and_recognize: no faces matched")
        return []

    result = [(sid, sum(c) / len(c)) for sid, c in seen.items()]
    result.sort(key=lambda x: x[1], reverse=True)
    logger.info(f"capture_and_recognize: matched {len(result)} student(s)")
    return result


def capture_and_recognize_bulk(num_frames=None):
    """
    Consensus-based bulk recognition.
    Returns [(student_id, avg_confidence, count), …].
    """
    global camera
    if num_frames is None:
        num_frames = CONFIG['bulk_recognition_frames']

    if camera is None or not camera.isOpened():
        camera = initialize_camera()
    if camera is None:
        return []

    data = defaultdict(lambda: {'confidences': [], 'count': 0})

    for i in range(num_frames):
        with camera_lock:
            if camera is None or not camera.isOpened():
                break
            ok, frame = camera.read()
        if not ok:
            continue
        for name, sid, loc, conf, is_real in recognize_faces_in_frame(frame):
            if sid and is_real and conf >= CONFIG['min_confidence']:
                data[sid]['confidences'].append(conf)
                data[sid]['count'] += 1
        if i < num_frames - 1:
            time.sleep(0.05)

    result = []
    for sid, d in data.items():
        if d['count'] >= CONFIG['recognition_consensus']:
            avg = sum(d['confidences']) / len(d['confidences'])
            result.append((sid, avg, d['count']))
    return sorted(result, key=lambda x: (x[2], x[1]), reverse=True)


# ── Mark attendance ────────────────────────────────────────────────────────────

def mark_attendance_for_recognized_faces(recognized_student_ids, faculty,
                                          course, class_date, class_time):
    """
    Upsert Attendance records for every recognised student.
    Returns (marked_count, [(name, confidence, already_marked), …]).
    """
    marked_count    = 0
    student_details = []
    try:
        for item in recognized_student_ids:
            sid, conf = (item[0], item[1]) if isinstance(item, tuple) else (item, 1.0)
            try:
                student = Student.objects.get(student_id=sid)
                _, created = Attendance.objects.update_or_create(
                    student=student,
                    faculty=faculty,
                    course=course,
                    class_date=class_date,
                    class_time=class_time,
                    defaults={'status': 'present', 'mode': 'AI'},
                )
                if created:
                    marked_count += 1
                student_details.append((student.name, conf, not created))
            except Student.DoesNotExist:
                logger.error(f"Student not found: {sid}")
            except Exception as e:
                logger.error(f"Attendance error for {sid}: {e}")
    except Exception as e:
        logger.error(f"mark_attendance_for_recognized_faces: {e}")

    logger.info(f"Marked {marked_count} new attendance record(s)")
    return marked_count, student_details


# ── Misc ───────────────────────────────────────────────────────────────────────

def get_camera_status():
    global camera
    status = {'available': False, 'opened': False,
               'width': 0, 'height': 0, 'fps': 0}
    with camera_lock:
        if camera is not None:
            status['available'] = True
            status['opened']    = camera.isOpened()
            if status['opened']:
                status['width']  = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                status['height'] = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                status['fps']    = int(camera.get(cv2.CAP_PROP_FPS))
    return status


def reset_camera():
    release_camera()
    time.sleep(0.5)
    return initialize_camera()
