import peewee
from peewee import *
import sys
import datetime

db = SqliteDatabase('cis110.db')

class Queue(Model):
    name = CharField()
    staffs = CharField(default='')
    students = CharField(default='')
    startTime = DateTimeField(default=datetime.datetime.now())
    endTime = DateTimeField(null=True)

    class Meta:
        database = db

class Student(Model):
    name = CharField()
    pennkey = CharField()
    comment = CharField(default='')
    question = CharField(default='')
    status = CharField(default='WAITING')
    createdTime = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db

class TA(Model):
    name = CharField()
    pennkey = CharField()

    class Meta:
        database = db

db.connect()

db.create_tables([Queue, Student, TA], safe=True)

# Commandline Interface
def processInput(command):
    parts = command.split()
    cmd = parts[0]
    if (cmd == 'addTA'):
        addTACommand(parts)
    elif (cmd == 'addQueue'):
        addQueueCommand(parts)
    elif (cmd == 'taLogin'):
        taLoginCommand(parts)
    elif (cmd == 'taLogout'):
        taLogoutCommand(parts)
    elif (cmd == 'addStudent'):
        addStudentCommand(parts)
    elif (cmd == 'resolveStudent'):
        resolveStudentCommand(parts)
    elif (cmd == 'getNextStudent'):
        getNextStudentForTACommand(parts)
    elif (cmd == 'quit'):
        sys.exit(0)
    else:
        print('Invalid command')

def addTACommand(parts):
    if len(parts) < 4:
        print('Usage: addTA [First] [Last] [PennKey]')
    else:
        ta_name = ' '.join(parts[1:3])
        ta_pk = parts[3]
        addTA(ta_name, ta_pk)
        print('Added {0} as a TA'.format(ta_name))

def addQueueCommand(parts):
    start, end = None, None
    if len(parts) < 2:
        print('Usage: addQueue [Name] Optional [Start Time] [End Time]')
    else:
        name = parts[1]
        if len(parts) > 2:
            start = parts[2]
        if len(parts) == 4:
            end = parts[3]
        addQueue(name, start, end)
        print('Added queue: {0}'.format(name))

def taLoginCommand(parts):
    if len(parts) < 3:
        print('Usage: taLogin [PennKey] [Queue Name]')
    else:
        pk = parts[1]
        q = parts[2]
        taLogin(pk, q)
        print('Logged {0} into {1}'.format(pk, q))

def taLogoutCommand(parts):
    if len(parts) < 3:
        print('Usage: taLogout [PennKey] [Queue Name]')
    else:
        pk = parts[1]
        q = parts[2]
        taLogout(pk, q)
        print('Logged {0} out of {1}'.format(pk, q))

def addStudentCommand(parts):
    if len(parts) < 5:
        print('Usage: addStudent [Queue Name] [First] [Last] [PennKey] Optional [Comment] [Question]')
    else: 
        queues = parts[1].split(',')
        name = ' '.join(parts[2:4])
        pk = parts[4]
        comment, question = None, None
        if (len(parts) > 5):
            comment = parts[5]
        if (len(parts) == 7):
            question = parts[6]
        addStudent(queues, name, pk, comment, question)
        for q in queues:
            print('Added {0} to queue {1}'.format(name, q))

def resolveStudentCommand(parts):
    if len(parts) < 2:
        print('Usage: resolveStudent [PennKey]')
    else:
        pk = parts[1]
        resolveStudent(pk)
        print('Resolved {0}'.format(pk))

def getNextStudentForTACommand(parts):
    if len(parts) < 2:
        print('Usage: getNextStudent [TA PennKey]')
    else:
        ta = parts[1]
        student = getNextStudentForTA(ta)
        if student is not None:
            print('Next student is {0}'.format(student.name))
            return student
        else:
            print('No more student to be helped!')
            return None

# DB Functions

# Add a TA into the system
def addTA(ta_name, ta_pennkey):
    ta = TA.create(name=ta_name, pennkey=ta_pennkey)
    ta.save()
    
# Add a queue into the system
def addQueue(q_name, start=None, end=None):
    q = Queue.create(name=q_name)
    if start is not None:
        q.startTime = start
    if end is not None:
        q.endTime = end
    q.save()
    
# Log a TA into a queue
def taLogin(ta_pennkey, queue_name):
    queue = Queue.get(name=queue_name)
    if (queue.staffs == ''):
        queue.staffs = ta_pennkey
    else:
        staffs = queue.staffs.encode("utf8").split(",")
        staffs += [ta_pennkey]
        staffs_str = ','.join(staffs)
        queue.staffs = staffs_str
    queue.save()

# Log a TA out of a queue
def taLogout(ta_pennkey, queue_name):
    queue = Queue.get(name=queue_name)
    staffs = queue.staffs.encode("utf8").split(",")
    if ta_pennkey in staffs:
        staffs.remove(ta_pennkey)
    staffs_str = ','.join(staffs)
    queue.staffs = staffs_str
    queue.save()

# Add a student to desired queues with their comment and question
def addStudent(queues, s_name, s_pennkey, comment=None, question=None):
    student = Student.create(name=s_name, pennkey=s_pennkey)
    if comment is not None:
        student.comment = comment
    if question is not None:
        student.question = question
    student.save()

    for q_name in queues:
        addStudentToQueue(s_pennkey, q_name)

# Add a student to a single queue    
def addStudentToQueue(pk, q_name):
    queue = Queue.get(name=q_name)
    students = queue.students
    if students == '':
        queue.students = pk
    else:
        students = students.split(",")
        students += [pk]
        queue.students = ','.join(students)
    queue.save()

# Resolve a student after helping them
def resolveStudent(pk):
    student = Student.get(pennkey=pk, status='WAITING')
    student.status = 'RESOLVED'
    student.save()
    queues = Queue.select()
    for queue in queues:
        students = queue.students.split(',')
        if pk in students:
            students.remove(pk)
        queue.students = ','.join(students)
        queue.save()

# Get the student who signed in the earliest
# in all queue signed in by the given TA
def getNextStudentForTA(ta_pennkey):
    activeQueues = Queue.select()
    result = []
    for queue in activeQueues:
        tas = queue.staffs.split(',')
        if ta_pennkey in tas:
            students = queue.students.split(',')
            for pk in students:
                student = Student.get(pennkey=pk)
                result += [student]
    if len(result) > 0:
        result = sorted(result, key=lambda k: k.createdTime)
        return result[0]
    else:
        return None

def main():
    # queue = Queue.get(name='mooore')
    # queue.staffs = ''
    # queue.save();
    # taLogin('dodviet', 'mooore')
    # addStudent(['mooore'], 'some name', 'pk')
    # resolveStudent('pk')
    # print(getNextStudentForTA('dodviet'))
    
    # tas = TA.select()
    # queue = Queue.get(name='mooore')
    # queue.staffs = ''
    # queue.save()
    
    # taLogout('dodviet', 'mooore')
    # for ta in tas:
    #     ta.delete_instance()
    
    while (True):
        command = raw_input('Enter command: ')
        processInput(command)

if __name__ == '__main__':
    main()