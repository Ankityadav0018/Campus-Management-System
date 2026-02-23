from django.core.management.base import BaseCommand
import cv2, pickle, numpy as np


class Command(BaseCommand):
    help = 'Test face recognition pipeline end-to-end'

    def handle(self, *args, **options):
        from apps.attendance.models import Student, StudentFace
        from apps.attendance.face_recognition_utils import (
            encode_face_from_image, load_known_faces,
            _find_best_match, _embed_cropped_face, _detect_faces_opencv,
        )

        self.stdout.write('\n=== STEP 1: Camera test ===')
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            self.stdout.write(self.style.ERROR('Camera FAILED to open'))
            return
        for _ in range(15):
            cam.read()
        ret, frame = cam.read()
        cam.release()
        if not ret:
            self.stdout.write(self.style.ERROR('Camera read FAILED'))
            return
        self.stdout.write(self.style.SUCCESS(f'Camera OK — frame shape: {frame.shape}'))
        cv2.imwrite('/tmp/test_face_frame.jpg', frame)

        self.stdout.write('\n=== STEP 2: Face encoding ===')
        ok, msg, emb, quality = encode_face_from_image('/tmp/test_face_frame.jpg')
        self.stdout.write(f'  ok={ok}, quality={quality:.1f}, msg={msg}')
        if not ok:
            self.stdout.write(self.style.ERROR(
                'Face encoding FAILED.\n'
                'Make sure you are sitting in front of the camera when running this test.\n'
                'The camera captured a frame with no face visible.'
            ))
            return
        self.stdout.write(self.style.SUCCESS(f'  Embedding shape: {emb.shape}'))

        self.stdout.write('\n=== STEP 3: Save to DB ===')
        student = Student.objects.first()
        if not student:
            self.stdout.write(self.style.ERROR('No students in DB'))
            return
        StudentFace.objects.all().delete()
        StudentFace.objects.create(student=student, face_encoding=pickle.dumps(emb))
        self.stdout.write(self.style.SUCCESS(f'  Saved face for: {student.name} ({student.student_id})'))

        self.stdout.write('\n=== STEP 4: Load known faces ===')
        count = load_known_faces()
        self.stdout.write(self.style.SUCCESS(f'  Loaded {count} face(s) from DB'))

        self.stdout.write('\n=== STEP 5: Detect faces in frame ===')
        boxes = _detect_faces_opencv(frame)
        self.stdout.write(f'  Detected {len(boxes)} face box(es): {boxes}')
        if not boxes:
            self.stdout.write(self.style.WARNING(
                '  No face boxes detected. The Haar cascade did not find a face.\n'
                '  This is the likely reason attendance is not working.\n'
                '  Try better lighting or position face closer to camera.'
            ))
            return

        self.stdout.write('\n=== STEP 6: Match faces ===')
        for i, box in enumerate(boxes):
            emb2 = _embed_cropped_face(frame, box)
            if emb2 is None:
                self.stdout.write(self.style.ERROR(f'  Box {i}: embedding FAILED'))
                continue
            name, sid, conf = _find_best_match(emb2)
            style = self.style.SUCCESS if sid else self.style.WARNING
            self.stdout.write(style(
                f'  Box {i}: name={name}, student_id={sid}, confidence={conf:.3f}'
            ))

        self.stdout.write('\n=== RESULT ===')
        self.stdout.write(self.style.SUCCESS('Pipeline test complete. Check results above.'))
