from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Task
from datetime import date, timedelta

class TaskRecurrenceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')

    def test_add_recurring_task_daily_week(self):
        response = self.client.post('/add-task/', {
            'name': 'Daily Task',
            'project': 'Test',
            'priority': 'High',
            'due_date': '2023-10-01',
            'due_time': '10:00',
            'recurrence': 'daily_7'
        })
        self.assertEqual(response.status_code, 302) # Redirects
        tasks = Task.objects.filter(user=self.user)
        self.assertEqual(tasks.count(), 7)
        self.assertTrue(all(t.is_recurring for t in tasks))
        dates = sorted([t.due_date for t in tasks])
        expected_dates = [date(2023, 10, 1) + timedelta(days=i) for i in range(7)]
        self.assertEqual(dates, expected_dates)

    def test_add_recurring_task_weekly_month(self):
        response = self.client.post('/add-task/', {
            'name': 'Weekly Task',
            'project': 'Test',
            'priority': 'Medium',
            'due_date': '2023-10-01',
            'due_time': '10:00',
            'recurrence': 'weekly_4'
        })
        self.assertEqual(response.status_code, 302)
        tasks = Task.objects.filter(user=self.user)
        self.assertEqual(tasks.count(), 4)
        self.assertTrue(all(t.is_recurring for t in tasks))
        dates = sorted([t.due_date for t in tasks])
        expected_dates = [date(2023, 10, 1) + timedelta(weeks=i) for i in range(4)]
        self.assertEqual(dates, expected_dates)
