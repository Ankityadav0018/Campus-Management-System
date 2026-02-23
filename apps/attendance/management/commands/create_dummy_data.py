from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.attendance.models import Student, Attendance
from apps.food.models import FoodItem, FoodStall, FoodOrder, FoodOrderItem
from apps.resources.models import CampusFaculty, Course, Block, CampusClassroom
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create dummy data for training and testing purposes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating dummy data...'))
        
        # Create Blocks
        blocks = []
        block_names = ['Block A', 'Block B', 'Block C', 'Block D', 'Library Block']
        for name in block_names:
            block, created = Block.objects.get_or_create(
                name=name,
                defaults={'description': f'Academic {name}'}
            )
            blocks.append(block)
            if created:
                self.stdout.write(f'Created block: {name}')
        
        # Create Classrooms
        for block in blocks[:4]:  # Only academic blocks
            for room in range(101, 106):
                CampusClassroom.objects.get_or_create(
                    block=block,
                    room_number=str(room),
                    defaults={'capacity': random.choice([30, 40, 50, 60])}
                )
        
        # Create Vendor Users first
        vendor_user, created = User.objects.get_or_create(
            email='vendor@lpu.in',
            defaults={
                'username': 'vendor_lpu',
                'role': 'vendor',
                'is_active': True
            }
        )
        if created:
            vendor_user.set_password('vendor123')
            vendor_user.save()
            self.stdout.write('Created vendor user')
        
        # Create Faculty Users and Profiles
        faculties_data = [
            {'name': 'Dr. Rajesh Kumar', 'email': 'rajesh.kumar@lpu.in', 'faculty_id': 'FAC001', 'dept': 'Computer Science'},
            {'name': 'Prof. Priya Sharma', 'email': 'priya.sharma@lpu.in', 'faculty_id': 'FAC002', 'dept': 'Computer Science'},
            {'name': 'Dr. Amit Patel', 'email': 'amit.patel@lpu.in', 'faculty_id': 'FAC003', 'dept': 'Electronics'},
            {'name': 'Prof. Neha Gupta', 'email': 'neha.gupta@lpu.in', 'faculty_id': 'FAC004', 'dept': 'Mathematics'},
            {'name': 'Dr. Sanjay Singh', 'email': 'sanjay.singh@lpu.in', 'faculty_id': 'FAC005', 'dept': 'Physics'},
        ]
        
        faculties = []
        for fac_data in faculties_data:
            # Create user account
            username = fac_data['email'].split('@')[0].replace('.', '_')
            user, created = User.objects.get_or_create(
                email=fac_data['email'],
                defaults={
                    'username': username,
                    'role': 'faculty',
                    'is_active': True
                }
            )
            if created:
                user.set_password('faculty123')
                user.save()
                self.stdout.write(f'Created faculty user: {fac_data["email"]}')
            
            # Create faculty profile
            faculty, created = CampusFaculty.objects.get_or_create(
                faculty_id=fac_data['faculty_id'],
                defaults={
                    'name': fac_data['name'],
                    'email': fac_data['email'],
                    'user': user
                }
            )
            faculties.append(faculty)
            if created:
                self.stdout.write(f'Created faculty profile: {fac_data["name"]}')
        
        # Create Courses
        courses_data = [
            {'course_id': 'CS101', 'name': 'Introduction to Programming', 'faculty': 0},
            {'course_id': 'CS102', 'name': 'Data Structures', 'faculty': 0},
            {'course_id': 'CS201', 'name': 'Database Management Systems', 'faculty': 1},
            {'course_id': 'CS202', 'name': 'Web Development', 'faculty': 1},
            {'course_id': 'EC101', 'name': 'Digital Electronics', 'faculty': 2},
            {'course_id': 'MA101', 'name': 'Calculus I', 'faculty': 3},
            {'course_id': 'PH101', 'name': 'Physics Fundamentals', 'faculty': 4},
        ]
        
        courses = []
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                course_id=course_data['course_id'],
                defaults={
                    'name': course_data['name'],
                    'assigned_faculty': faculties[course_data['faculty']]
                }
            )
            courses.append(course)
            if created:
                self.stdout.write(f'Created course: {course_data["name"]}')
        
        # Create Student Users and Profiles
        students_data = [
            {'student_id': 'STU2024001', 'name': 'Ankit Kumar', 'email': 'ankit.kumar@lpu.student.in'},
            {'student_id': 'STU2024002', 'name': 'Priya Singh', 'email': 'priya.singh@lpu.student.in'},
            {'student_id': 'STU2024003', 'name': 'Rahul Sharma', 'email': 'rahul.sharma@lpu.student.in'},
            {'student_id': 'STU2024004', 'name': 'Sneha Patel', 'email': 'sneha.patel@lpu.student.in'},
            {'student_id': 'STU2024005', 'name': 'Vikram Gupta', 'email': 'vikram.gupta@lpu.student.in'},
            {'student_id': 'STU2024006', 'name': 'Riya Verma', 'email': 'riya.verma@lpu.student.in'},
            {'student_id': 'STU2024007', 'name': 'Arjun Reddy', 'email': 'arjun.reddy@lpu.student.in'},
            {'student_id': 'STU2024008', 'name': 'Ishita Joshi', 'email': 'ishita.joshi@lpu.student.in'},
            {'student_id': 'STU2024009', 'name': 'Rohan Das', 'email': 'rohan.das@lpu.student.in'},
            {'student_id': 'STU2024010', 'name': 'Kavya Nair', 'email': 'kavya.nair@lpu.student.in'},
            {'student_id': 'STU2024011', 'name': 'Aditya Mishra', 'email': 'aditya.mishra@lpu.student.in'},
            {'student_id': 'STU2024012', 'name': 'Pooja Rao', 'email': 'pooja.rao@lpu.student.in'},
            {'student_id': 'STU2024013', 'name': 'Siddharth Jain', 'email': 'siddharth.jain@lpu.student.in'},
            {'student_id': 'STU2024014', 'name': 'Anjali Desai', 'email': 'anjali.desai@lpu.student.in'},
            {'student_id': 'STU2024015', 'name': 'Karan Mehta', 'email': 'karan.mehta@lpu.student.in'},
        ]
        
        students = []
        for std_data in students_data:
            # Create user account
            user, created = User.objects.get_or_create(
                email=std_data['email'],
                defaults={
                    'username': std_data['email'].split('@')[0],
                    'role': 'student',
                    'is_active': True
                }
            )
            if created:
                user.set_password('student123')
                user.save()
                self.stdout.write(f'Created student user: {std_data["email"]}')
            
            # Create student profile
            student, created = Student.objects.get_or_create(
                student_id=std_data['student_id'],
                defaults={
                    'name': std_data['name'],
                    'email': std_data['email']
                }
            )
            students.append(student)
            if created:
                self.stdout.write(f'Created student profile: {std_data["name"]}')
        
        # Create Attendance Records (last 30 days)
        time_slots = ['09:00', '10:00', '11:00', '13:00', '14:00', '15:00']
        for i in range(30):
            date = datetime.now().date() - timedelta(days=i)
            
            # Random 2-3 classes per day
            for _ in range(random.randint(2, 3)):
                course = random.choice(courses)
                time_slot = random.choice(time_slots)
                
                # Mark attendance for random students
                for student in random.sample(students, random.randint(10, 15)):
                    Attendance.objects.get_or_create(
                        student=student,
                        faculty=course.assigned_faculty,
                        course=course,
                        class_date=date,
                        class_time=time_slot,
                        defaults={
                            'status': random.choices(['present', 'absent'], weights=[85, 15])[0],
                            'mode': 'manual'
                        }
                    )
        
        self.stdout.write(self.style.SUCCESS('Created attendance records for last 30 days'))
        
        # Create Food Stalls
        stalls_data = [
            {'name': 'North Indian Delight', 'description': 'Authentic North Indian cuisine'},
            {'name': 'South Indian Corner', 'description': 'Traditional South Indian dishes'},
            {'name': 'Chinese Wok', 'description': 'Indo-Chinese favorites'},
            {'name': 'Beverages & Snacks', 'description': 'Quick bites and drinks'},
            {'name': 'Fast Food Junction', 'description': 'Popular fast food items'},
        ]
        
        stalls = []
        for stall_data in stalls_data:
            stall, created = FoodStall.objects.get_or_create(
                name=stall_data['name'],
                vendor=vendor_user,
                defaults={
                    'description': stall_data['description'],
                    'is_active': True
                }
            )
            stalls.append(stall)
            if created:
                self.stdout.write(f'Created stall: {stall_data["name"]}')
        
        # Create Food Items
        food_items_data = [
            # North Indian
            {'name': 'Paneer Butter Masala', 'price': 120, 'category': 'lunch', 'stall': 0},
            {'name': 'Dal Makhani with Rice', 'price': 100, 'category': 'lunch', 'stall': 0},
            {'name': 'Roti (2 pcs)', 'price': 20, 'category': 'snacks', 'stall': 0},
            {'name': 'Rajma Chawal', 'price': 90, 'category': 'lunch', 'stall': 0},
            
            # South Indian
            {'name': 'Masala Dosa', 'price': 60, 'category': 'breakfast', 'stall': 1},
            {'name': 'Idli Sambhar (4 pcs)', 'price': 50, 'category': 'breakfast', 'stall': 1},
            {'name': 'Uttapam', 'price': 70, 'category': 'breakfast', 'stall': 1},
            {'name': 'Medu Vada (3 pcs)', 'price': 45, 'category': 'snacks', 'stall': 1},
            
            # Chinese
            {'name': 'Veg Fried Rice', 'price': 110, 'category': 'lunch', 'stall': 2},
            {'name': 'Chilli Paneer', 'price': 130, 'category': 'dinner', 'stall': 2},
            {'name': 'Veg Noodles', 'price': 100, 'category': 'lunch', 'stall': 2},
            {'name': 'Spring Rolls (4 pcs)', 'price': 80, 'category': 'snacks', 'stall': 2},
            
            # Beverages & Snacks
            {'name': 'Cold Coffee', 'price': 60, 'category': 'beverages', 'stall': 3},
            {'name': 'Chai (Tea)', 'price': 20, 'category': 'beverages', 'stall': 3},
            {'name': 'Samosa (2 pcs)', 'price': 30, 'category': 'snacks', 'stall': 3},
            {'name': 'Sandwich', 'price': 50, 'category': 'snacks', 'stall': 3},
            {'name': 'Fresh Juice', 'price': 40, 'category': 'beverages', 'stall': 3},
            
            # Fast Food
            {'name': 'Veg Burger', 'price': 70, 'category': 'snacks', 'stall': 4},
            {'name': 'French Fries', 'price': 50, 'category': 'snacks', 'stall': 4},
            {'name': 'Pizza Slice', 'price': 80, 'category': 'dinner', 'stall': 4},
            {'name': 'Pasta', 'price': 90, 'category': 'lunch', 'stall': 4},
        ]
        
        food_items = []
        for item_data in food_items_data:
            item, created = FoodItem.objects.get_or_create(
                name=item_data['name'],
                stall=stalls[item_data['stall']],
                defaults={
                    'description': f'Delicious {item_data["name"]}',
                    'price': item_data['price'],
                    'category': item_data['category'],
                    'available': True
                }
            )
            food_items.append(item)
            if created:
                self.stdout.write(f'Created food item: {item_data["name"]}')
        
        # Create Food Orders for students (last 15 days)
        for i in range(15):
            order_date = datetime.now() - timedelta(days=i)
            
            # Random 5-10 orders per day
            for _ in range(random.randint(5, 10)):
                student = random.choice(students)
                food_item = random.choice(food_items)
                quantity = random.randint(1, 3)
                
                order, created = FoodOrder.objects.get_or_create(
                    student=student,
                    stall=food_item.stall,
                    time_slot=order_date,
                    pickup_time_slot=f"{random.choice(['12:00', '13:00', '14:00', '18:00', '19:00'])} - {random.choice(['12:30', '13:30', '14:30', '18:30', '19:30'])}",
                    defaults={
                        'total_price': food_item.price * quantity,
                        'status': random.choice(['pending', 'completed', 'completed', 'completed'])
                    }
                )
                
                if created:
                    # Add order items
                    FoodOrderItem.objects.create(
                        order=order,
                        food_item=food_item,
                        quantity=quantity,
                        price_at_order=food_item.price
                    )
        
        self.stdout.write(self.style.SUCCESS('Created food orders for last 15 days'))
        
        # Print Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('DUMMY DATA CREATION SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'✓ Blocks: {Block.objects.count()}')
        self.stdout.write(f'✓ Classrooms: {CampusClassroom.objects.count()}')
        self.stdout.write(f'✓ Faculty: {CampusFaculty.objects.count()}')
        self.stdout.write(f'✓ Courses: {Course.objects.count()}')
        self.stdout.write(f'✓ Students: {Student.objects.count()}')
        self.stdout.write(f'✓ Attendance Records: {Attendance.objects.count()}')
        self.stdout.write(f'✓ Food Stalls: {FoodStall.objects.count()}')
        self.stdout.write(f'✓ Food Items: {FoodItem.objects.count()}')
        self.stdout.write(f'✓ Food Orders: {FoodOrder.objects.count()}')
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('LOGIN CREDENTIALS'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write('Faculty Login:')
        self.stdout.write('  Email: rajesh.kumar@lpu.in')
        self.stdout.write('  Password: faculty123')
        self.stdout.write('\nStudent Login:')
        self.stdout.write('  Email: ankit.kumar@lpu.student.in')
        self.stdout.write('  Password: student123')
        self.stdout.write('\nVendor Login:')
        self.stdout.write('  Email: vendor@lpu.in')
        self.stdout.write('  Password: vendor123')
        self.stdout.write(self.style.SUCCESS('='*50))
