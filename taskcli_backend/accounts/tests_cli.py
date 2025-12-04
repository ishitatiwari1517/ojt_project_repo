from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from accounts.models import Task
from io import StringIO
from datetime import date, time

class TaskCLITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.out = StringIO()

    def test_add_task(self):
        call_command(
            'task_cli', 'add',
            '--name', 'Test Task',
            '--due_date', '2023-12-31',
            '--user', 'testuser',
            stdout=self.out
        )
        self.assertIn('Successfully created task "Test Task"', self.out.getvalue())
        self.assertTrue(Task.objects.filter(name='Test Task', user=self.user).exists())

    def test_list_tasks(self):
        Task.objects.create(user=self.user, name='Task 1', due_date=date(2023, 12, 31), due_time=time(12, 0))
        call_command('task_cli', 'list', '--user', 'testuser', stdout=self.out)
        self.assertIn('Task 1', self.out.getvalue())

    def test_complete_task(self):
        task = Task.objects.create(user=self.user, name='Task to Complete', due_date=date(2023, 12, 31), due_time=time(12, 0))
        call_command('task_cli', 'complete', str(task.id), stdout=self.out)
        task.refresh_from_db()
        self.assertTrue(task.completed)
        self.assertIn('Successfully marked task', self.out.getvalue())

    def test_delete_task(self):
        task = Task.objects.create(user=self.user, name='Task to Delete', due_date=date(2023, 12, 31), due_time=time(12, 0))
        call_command('task_cli', 'delete', str(task.id), stdout=self.out)
        self.assertFalse(Task.objects.filter(id=task.id).exists())
        self.assertIn('Successfully deleted task', self.out.getvalue())
