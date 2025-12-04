from django.core.management.base import BaseCommand, CommandError
from accounts.models import Task
from django.contrib.auth.models import User
from django.utils import timezone
import argparse
from datetime import datetime

class Command(BaseCommand):
    help = 'Manage tasks via CLI'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='subcommand', required=True)

        # List command
        list_parser = subparsers.add_parser('list', help='List tasks')
        list_parser.add_argument('--user', type=str, help='Username to list tasks for')

        # Add command
        add_parser = subparsers.add_parser('add', help='Add a new task')
        add_parser.add_argument('--name', type=str, required=True, help='Task name')
        add_parser.add_argument('--project', type=str, default='General', help='Project name')
        add_parser.add_argument('--priority', type=str, choices=['High', 'Medium', 'Low'], default='Medium', help='Task priority')
        add_parser.add_argument('--due_date', type=str, required=True, help='Due date (YYYY-MM-DD)')
        add_parser.add_argument('--due_time', type=str, default='23:59', help='Due time (HH:MM)')
        add_parser.add_argument('--user', type=str, help='Username to assign task to')

        # Complete command
        complete_parser = subparsers.add_parser('complete', help='Mark task as complete')
        complete_parser.add_argument('task_id', type=int, help='ID of the task to complete')

        # Delete command
        delete_parser = subparsers.add_parser('delete', help='Delete a task')
        delete_parser.add_argument('task_id', type=int, help='ID of the task to delete')

    def handle(self, *args, **options):
        subcommand = options['subcommand']

        if subcommand == 'list':
            self.list_tasks(options)
        elif subcommand == 'add':
            self.add_task(options)
        elif subcommand == 'complete':
            self.complete_task(options)
        elif subcommand == 'delete':
            self.delete_task(options)

    def get_user(self, username):
        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'User "{username}" does not exist')
        
        user = User.objects.first()
        if not user:
            raise CommandError('No users found in the database. Please create a user first.')
        
        if not username:
             self.stdout.write(self.style.WARNING(f'No user specified, defaulting to "{user.username}"'))
        
        return user

    def list_tasks(self, options):
        user = self.get_user(options['user'])
        tasks = Task.objects.filter(user=user).order_by('due_date', 'due_time')
        
        if not tasks:
            self.stdout.write(self.style.WARNING(f'No tasks found for user "{user.username}"'))
            return

        self.stdout.write(self.style.SUCCESS(f'Tasks for {user.username}:'))
        self.stdout.write(f"{'ID':<5} {'Name':<30} {'Project':<15} {'Priority':<10} {'Due Date':<12} {'Status'}")
        self.stdout.write("-" * 85)
        
        for task in tasks:
            status = "Done" if task.completed else "Pending"
            self.stdout.write(f"{task.id:<5} {task.name[:28]:<30} {task.project[:13]:<15} {task.priority:<10} {str(task.due_date):<12} {status}")

    def add_task(self, options):
        user = self.get_user(options['user'])
        
        try:
            due_date = datetime.strptime(options['due_date'], '%Y-%m-%d').date()
            due_time = datetime.strptime(options['due_time'], '%H:%M').time()
        except ValueError:
            raise CommandError('Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time.')

        task = Task.objects.create(
            user=user,
            name=options['name'],
            project=options['project'],
            priority=options['priority'],
            due_date=due_date,
            due_time=due_time
        )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created task "{task.name}" (ID: {task.id})'))

    def complete_task(self, options):
        try:
            task = Task.objects.get(pk=options['task_id'])
            task.completed = True
            task.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully marked task "{task.name}" (ID: {task.id}) as complete'))
        except Task.DoesNotExist:
            raise CommandError(f'Task with ID {options["task_id"]} does not exist')

    def delete_task(self, options):
        try:
            task = Task.objects.get(pk=options['task_id'])
            task_name = task.name
            task.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted task "{task_name}" (ID: {options["task_id"]})'))
        except Task.DoesNotExist:
            raise CommandError(f'Task with ID {options["task_id"]} does not exist')
