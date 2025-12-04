"""
TaskCLI - Interactive Command Line Interface for Task Management
================================================================
This module provides a full-featured CLI for managing tasks, with both
interactive menu mode and direct command-line arguments.

USAGE:
------
Interactive Mode (Recommended for beginners):
    python manage.py task_cli
    
Direct Commands:
    python manage.py task_cli list --status pending
    python manage.py task_cli add "Task Name" --user email@example.com --priority High
    python manage.py task_cli complete 123
    python manage.py task_cli edit 123 --name "New Name"
    python manage.py task_cli delete 123

FEATURES:
---------
- Login/Signup with same credentials as web app
- Create, edit, delete, complete tasks
- Filter by priority, project, status, recurring
- Colorful terminal UI with emojis
- Full feature parity with web application

Author: TaskCLI Team
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from accounts.models import Task
from datetime import datetime, timedelta
import os
import getpass

# ANSI Color Codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class Command(BaseCommand):
    help = 'Interactive Task CLI - Manage tasks with an easy-to-use menu'
    current_user = None  # Track logged-in user

    def add_arguments(self, parser):
        parser.add_argument('--interactive', '-i', action='store_true', help='Launch interactive mode')
        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # List command
        list_parser = subparsers.add_parser('list', help='List tasks')
        list_parser.add_argument('--user', type=str, help='Filter by username (email)')
        list_parser.add_argument('--priority', type=str, choices=['High', 'Medium', 'Low'], help='Filter by priority')
        list_parser.add_argument('--project', type=str, help='Filter by project name')
        list_parser.add_argument('--status', type=str, choices=['pending', 'completed', 'all'], default='all', help='Filter by status')
        list_parser.add_argument('--recurring', action='store_true', help='Show only recurring tasks')

        # Add command
        add_parser = subparsers.add_parser('add', help='Add a new task')
        add_parser.add_argument('name', type=str, help='Task name')
        add_parser.add_argument('--project', type=str, default='General', help='Project name')
        add_parser.add_argument('--priority', type=str, choices=['High', 'Medium', 'Low'], default='Medium', help='Priority')
        add_parser.add_argument('--due_date', type=str, help='Due date (YYYY-MM-DD)')
        add_parser.add_argument('--due_time', type=str, default='12:00', help='Due time (HH:MM)')
        add_parser.add_argument('--user', type=str, required=True, help='Username (email) to assign task to')
        add_parser.add_argument('--recurrence', type=str, choices=['none', 'daily_7', 'daily_30', 'weekly_4'], default='none', help='Recurrence pattern')

        # Complete command
        complete_parser = subparsers.add_parser('complete', help='Mark task as complete')
        complete_parser.add_argument('task_id', type=int, help='Task ID')

        # Pending command
        pending_parser = subparsers.add_parser('pending', help='Mark task as pending')
        pending_parser.add_argument('task_id', type=int, help='Task ID')

        # Edit command
        edit_parser = subparsers.add_parser('edit', help='Edit a task')
        edit_parser.add_argument('task_id', type=int, help='Task ID')
        edit_parser.add_argument('--name', type=str, help='New task name')
        edit_parser.add_argument('--project', type=str, help='New project name')
        edit_parser.add_argument('--priority', type=str, choices=['High', 'Medium', 'Low'], help='New priority')
        edit_parser.add_argument('--due_date', type=str, help='New due date (YYYY-MM-DD)')
        edit_parser.add_argument('--due_time', type=str, help='New due time (HH:MM)')

        # Delete command
        delete_parser = subparsers.add_parser('delete', help='Delete a task')
        delete_parser.add_argument('task_id', type=int, help='Task ID')

    def handle(self, *args, **options):
        if options.get('interactive') or options.get('command') is None:
            self.interactive_mode()
        else:
            command = options['command']
            if command == 'list':
                self.list_tasks(options)
            elif command == 'add':
                self.add_task(options)
            elif command == 'complete':
                self.complete_task(options['task_id'])
            elif command == 'pending':
                self.pending_task(options['task_id'])
            elif command == 'edit':
                self.edit_task(options)
            elif command == 'delete':
                self.delete_task(options['task_id'])

    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_header(self):
        self.stdout.write(f"\n{Colors.CYAN}{Colors.BOLD}")
        self.stdout.write("╔══════════════════════════════════════════════════╗")
        self.stdout.write("║           🗓️  TASK CLI - Task Manager            ║")
        self.stdout.write("╚══════════════════════════════════════════════════╝")
        self.stdout.write(f"{Colors.END}")
        if self.current_user:
            name = self.current_user.first_name or self.current_user.username
            self.stdout.write(f"{Colors.GREEN}👤 Logged in as: {name}{Colors.END}\n")
        else:
            self.stdout.write(f"{Colors.YELLOW}👤 Not logged in{Colors.END}\n")

    def print_auth_menu(self):
        self.stdout.write(f"\n{Colors.YELLOW}{Colors.BOLD}🔐 WELCOME{Colors.END}\n")
        self.stdout.write(f"{Colors.BLUE}{'─' * 50}{Colors.END}\n")
        menu_items = [
            ("1", "🔑 Login"),
            ("2", "📝 Create New Account"),
            ("3", "👥 Continue as Guest (view all tasks)"),
            ("0", "🚪 Exit"),
        ]
        for num, text in menu_items:
            self.stdout.write(f"  {Colors.GREEN}{num:>2}{Colors.END}. {text}")
        self.stdout.write(f"{Colors.BLUE}{'─' * 50}{Colors.END}\n")

    def print_menu(self):
        self.stdout.write(f"\n{Colors.YELLOW}{Colors.BOLD}📋 MAIN MENU{Colors.END}\n")
        self.stdout.write(f"{Colors.BLUE}{'─' * 50}{Colors.END}\n")
        menu_items = [
            ("1", "📄 View My Tasks"),
            ("2", "⏳ View Pending Tasks"),
            ("3", "✅ View Completed Tasks"),
            ("4", "🔴 View High Priority Tasks"),
            ("5", "➕ Add New Task"),
            ("6", "✔️  Mark Task as Complete"),
            ("7", "⏸️  Mark Task as Pending"),
            ("8", "✏️  Edit Task"),
            ("9", "🗑️  Delete Task"),
            ("10", "🔍 Search/Filter Tasks"),
            ("11", "🔄 Switch User / Logout"),
            ("0", "🚪 Exit"),
        ]
        for num, text in menu_items:
            self.stdout.write(f"  {Colors.GREEN}{num:>2}{Colors.END}. {text}")
        self.stdout.write(f"{Colors.BLUE}{'─' * 50}{Colors.END}\n")

    def get_input(self, prompt, color=Colors.CYAN):
        try:
            return input(f"{color}{prompt}{Colors.END}").strip()
        except (EOFError, KeyboardInterrupt):
            return None

    def get_password(self, prompt):
        try:
            return getpass.getpass(f"{Colors.CYAN}{prompt}{Colors.END}")
        except (EOFError, KeyboardInterrupt):
            return None

    def login(self):
        self.stdout.write(f"\n{Colors.CYAN}{Colors.BOLD}🔑 LOGIN{Colors.END}\n")
        self.stdout.write(f"{Colors.BLUE}{'─' * 40}{Colors.END}\n")
        
        email = self.get_input("Email: ")
        if not email:
            return False
        
        password = self.get_password("Password: ")
        if not password:
            return False
        
        user = authenticate(username=email, password=password)
        if user:
            self.current_user = user
            self.stdout.write(f"\n{Colors.GREEN}✅ Welcome back, {user.first_name or user.username}!{Colors.END}")
            return True
        else:
            self.stdout.write(f"\n{Colors.RED}❌ Invalid email or password.{Colors.END}")
            return False

    def signup(self):
        self.stdout.write(f"\n{Colors.CYAN}{Colors.BOLD}📝 CREATE NEW ACCOUNT{Colors.END}\n")
        self.stdout.write(f"{Colors.BLUE}{'─' * 40}{Colors.END}\n")
        
        name = self.get_input("Your Name: ")
        if not name:
            self.stdout.write(f"{Colors.RED}❌ Name is required.{Colors.END}")
            return False
        
        email = self.get_input("Email: ")
        if not email:
            self.stdout.write(f"{Colors.RED}❌ Email is required.{Colors.END}")
            return False
        
        if User.objects.filter(username=email).exists():
            self.stdout.write(f"\n{Colors.RED}❌ Email already registered. Please login instead.{Colors.END}")
            return False
        
        password = self.get_password("Password (min 6 characters): ")
        if not password or len(password) < 6:
            self.stdout.write(f"\n{Colors.RED}❌ Password must be at least 6 characters.{Colors.END}")
            return False
        
        confirm_password = self.get_password("Confirm Password: ")
        if password != confirm_password:
            self.stdout.write(f"\n{Colors.RED}❌ Passwords do not match.{Colors.END}")
            return False
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=name,
                password=password
            )
            self.current_user = user
            self.stdout.write(f"\n{Colors.GREEN}✅ Account created successfully! Welcome, {name}!{Colors.END}")
            return True
        except Exception as e:
            self.stdout.write(f"\n{Colors.RED}❌ Error creating account: {e}{Colors.END}")
            return False

    def interactive_mode(self):
        self.clear_screen()
        self.print_header()
        
        # Auth menu first
        while not self.current_user:
            self.print_auth_menu()
            choice = self.get_input("Enter your choice: ", Colors.YELLOW)
            
            if choice is None or choice == '0':
                self.stdout.write(f"\n{Colors.GREEN}👋 Goodbye!{Colors.END}\n")
                return
            elif choice == '1':
                if self.login():
                    self.get_input("\nPress Enter to continue...")
                    break
            elif choice == '2':
                if self.signup():
                    self.get_input("\nPress Enter to continue...")
                    break
            elif choice == '3':
                self.stdout.write(f"\n{Colors.YELLOW}📋 Continuing as guest (read-only for all users' tasks){Colors.END}")
                self.get_input("\nPress Enter to continue...")
                break
            else:
                self.stdout.write(f"{Colors.RED}❌ Invalid choice.{Colors.END}")
            
            self.get_input("\nPress Enter to continue...")
            self.clear_screen()
            self.print_header()
        
        self.clear_screen()
        self.print_header()
        
        # Main menu
        while True:
            self.print_menu()
            choice = self.get_input("Enter your choice: ", Colors.YELLOW)
            
            if choice is None or choice == '0':
                self.stdout.write(f"\n{Colors.GREEN}👋 Goodbye! Thanks for using Task CLI!{Colors.END}\n")
                break
            elif choice == '1':
                if self.current_user:
                    self.list_tasks({'user': self.current_user.username, 'status': 'all'})
                else:
                    self.list_tasks({'status': 'all'})
            elif choice == '2':
                opts = {'status': 'pending'}
                if self.current_user:
                    opts['user'] = self.current_user.username
                self.list_tasks(opts)
            elif choice == '3':
                opts = {'status': 'completed'}
                if self.current_user:
                    opts['user'] = self.current_user.username
                self.list_tasks(opts)
            elif choice == '4':
                opts = {'priority': 'High'}
                if self.current_user:
                    opts['user'] = self.current_user.username
                self.list_tasks(opts)
            elif choice == '5':
                if self.current_user:
                    self.interactive_add_task()
                else:
                    self.stdout.write(f"{Colors.RED}❌ Please login to add tasks.{Colors.END}")
            elif choice == '6':
                if self.current_user:
                    self.interactive_complete_task()
                else:
                    self.stdout.write(f"{Colors.RED}❌ Please login to complete tasks.{Colors.END}")
            elif choice == '7':
                if self.current_user:
                    self.interactive_pending_task()
                else:
                    self.stdout.write(f"{Colors.RED}❌ Please login to modify tasks.{Colors.END}")
            elif choice == '8':
                if self.current_user:
                    self.interactive_edit_task()
                else:
                    self.stdout.write(f"{Colors.RED}❌ Please login to edit tasks.{Colors.END}")
            elif choice == '9':
                if self.current_user:
                    self.interactive_delete_task()
                else:
                    self.stdout.write(f"{Colors.RED}❌ Please login to delete tasks.{Colors.END}")
            elif choice == '10':
                self.interactive_filter_tasks()
            elif choice == '11':
                self.current_user = None
                self.clear_screen()
                self.print_header()
                continue
            else:
                self.stdout.write(f"{Colors.RED}❌ Invalid choice. Please try again.{Colors.END}\n")
            
            self.get_input("\nPress Enter to continue...")
            self.clear_screen()
            self.print_header()

    def interactive_add_task(self):
        self.stdout.write(f"\n{Colors.CYAN}{Colors.BOLD}➕ ADD NEW TASK{Colors.END}\n")
        self.stdout.write(f"{Colors.BLUE}{'─' * 40}{Colors.END}\n")
        
        name = self.get_input("Task name: ")
        if not name:
            self.stdout.write(f"{Colors.RED}❌ Task name is required.{Colors.END}")
            return
        
        project = self.get_input("Project name (press Enter for 'General'): ") or "General"
        
        self.stdout.write(f"\n{Colors.YELLOW}Priority:{Colors.END}")
        self.stdout.write("  1. High")
        self.stdout.write("  2. Medium")
        self.stdout.write("  3. Low")
        priority_choice = self.get_input("Select priority (1-3): ") or "2"
        priority_map = {'1': 'High', '2': 'Medium', '3': 'Low'}
        priority = priority_map.get(priority_choice, 'Medium')
        
        due_date = self.get_input(f"Due date (YYYY-MM-DD, default: {datetime.now().strftime('%Y-%m-%d')}): ")
        due_date = due_date or datetime.now().strftime('%Y-%m-%d')
        
        due_time = self.get_input("Due time (HH:MM, default: 12:00): ") or "12:00"
        
        self.stdout.write(f"\n{Colors.YELLOW}Recurrence:{Colors.END}")
        self.stdout.write("  1. None (one-time task)")
        self.stdout.write("  2. Daily for 7 days")
        self.stdout.write("  3. Daily for 30 days")
        self.stdout.write("  4. Weekly for 4 weeks")
        recurrence_choice = self.get_input("Select recurrence (1-4): ") or "1"
        recurrence_map = {'1': 'none', '2': 'daily_7', '3': 'daily_30', '4': 'weekly_4'}
        recurrence = recurrence_map.get(recurrence_choice, 'none')
        
        options = {
            'user': self.current_user.username,
            'name': name,
            'project': project,
            'priority': priority,
            'due_date': due_date,
            'due_time': due_time,
            'recurrence': recurrence
        }
        self.add_task(options)

    def interactive_complete_task(self):
        self.stdout.write(f"\n{Colors.CYAN}{Colors.BOLD}✔️ MARK TASK AS COMPLETE{Colors.END}\n")
        self.list_tasks({'user': self.current_user.username, 'status': 'pending'})
        task_id = self.get_input("\nEnter Task ID to complete: ")
        if task_id:
            try:
                self.complete_task(int(task_id))
            except ValueError:
                self.stdout.write(f"{Colors.RED}❌ Invalid Task ID.{Colors.END}")

    def interactive_pending_task(self):
        self.stdout.write(f"\n{Colors.CYAN}{Colors.BOLD}⏸️ MARK TASK AS PENDING{Colors.END}\n")
        self.list_tasks({'user': self.current_user.username, 'status': 'completed'})
        task_id = self.get_input("\nEnter Task ID to mark as pending: ")
        if task_id:
            try:
                self.pending_task(int(task_id))
            except ValueError:
                self.stdout.write(f"{Colors.RED}❌ Invalid Task ID.{Colors.END}")

    def interactive_edit_task(self):
        self.stdout.write(f"\n{Colors.CYAN}{Colors.BOLD}✏️ EDIT TASK{Colors.END}\n")
        self.list_tasks({'user': self.current_user.username, 'status': 'all'})
        task_id = self.get_input("\nEnter Task ID to edit: ")
        if not task_id:
            return
        
        try:
            task = Task.objects.get(id=int(task_id), user=self.current_user)
        except (ValueError, Task.DoesNotExist):
            self.stdout.write(f"{Colors.RED}❌ Task not found or not yours.{Colors.END}")
            return
        
        self.stdout.write(f"\n{Colors.YELLOW}Current values (press Enter to keep):{Colors.END}")
        self.stdout.write(f"  Name: {task.name}")
        self.stdout.write(f"  Project: {task.project}")
        self.stdout.write(f"  Priority: {task.priority}")
        self.stdout.write(f"  Due Date: {task.due_date}")
        self.stdout.write(f"  Due Time: {task.due_time}\n")
        
        options = {'task_id': int(task_id)}
        
        new_name = self.get_input("New name: ")
        if new_name:
            options['name'] = new_name
        
        new_project = self.get_input("New project: ")
        if new_project:
            options['project'] = new_project
        
        self.stdout.write(f"\n{Colors.YELLOW}New priority (1=High, 2=Medium, 3=Low, Enter to skip):{Colors.END}")
        new_priority = self.get_input("Priority: ")
        if new_priority:
            priority_map = {'1': 'High', '2': 'Medium', '3': 'Low'}
            options['priority'] = priority_map.get(new_priority)
        
        new_date = self.get_input("New due date (YYYY-MM-DD): ")
        if new_date:
            options['due_date'] = new_date
        
        new_time = self.get_input("New due time (HH:MM): ")
        if new_time:
            options['due_time'] = new_time
        
        self.edit_task(options)

    def interactive_delete_task(self):
        self.stdout.write(f"\n{Colors.CYAN}{Colors.BOLD}🗑️ DELETE TASK{Colors.END}\n")
        self.list_tasks({'user': self.current_user.username, 'status': 'all'})
        task_id = self.get_input("\nEnter Task ID to delete: ")
        if task_id:
            confirm = self.get_input(f"{Colors.RED}Are you sure? (yes/no): {Colors.END}")
            if confirm and confirm.lower() in ['yes', 'y']:
                try:
                    # Verify ownership
                    task = Task.objects.get(id=int(task_id), user=self.current_user)
                    self.delete_task(int(task_id))
                except (ValueError, Task.DoesNotExist):
                    self.stdout.write(f"{Colors.RED}❌ Task not found or not yours.{Colors.END}")
            else:
                self.stdout.write(f"{Colors.YELLOW}Deletion cancelled.{Colors.END}")

    def interactive_filter_tasks(self):
        self.stdout.write(f"\n{Colors.CYAN}{Colors.BOLD}🔍 FILTER TASKS{Colors.END}\n")
        self.stdout.write(f"{Colors.BLUE}{'─' * 40}{Colors.END}\n")
        self.stdout.write("  1. By Priority")
        self.stdout.write("  2. By Project")
        self.stdout.write("  3. All Users' Tasks")
        self.stdout.write("  4. Recurring Tasks Only")
        
        choice = self.get_input("\nSelect filter type: ")
        options = {}
        
        if self.current_user:
            options['user'] = self.current_user.username
        
        if choice == '1':
            self.stdout.write("\n  1. High  2. Medium  3. Low")
            p = self.get_input("Select priority: ")
            priority_map = {'1': 'High', '2': 'Medium', '3': 'Low'}
            options['priority'] = priority_map.get(p)
        elif choice == '2':
            options['project'] = self.get_input("Enter project name: ")
        elif choice == '3':
            options.pop('user', None)  # Remove user filter to see all
        elif choice == '4':
            options['recurring'] = True
        
        self.list_tasks(options)

    # Original command methods (updated with colors)
    def list_tasks(self, options):
        tasks = Task.objects.all()
        
        if options.get('user'):
            try:
                user = User.objects.get(username=options['user'])
                tasks = tasks.filter(user=user)
            except User.DoesNotExist:
                self.stdout.write(f"{Colors.RED}❌ User '{options['user']}' not found.{Colors.END}")
                return
        
        if options.get('priority'):
            tasks = tasks.filter(priority=options['priority'])
        if options.get('project'):
            tasks = tasks.filter(project__icontains=options['project'])
        if options.get('status') == 'pending':
            tasks = tasks.filter(completed=False)
        elif options.get('status') == 'completed':
            tasks = tasks.filter(completed=True)
        if options.get('recurring'):
            tasks = tasks.filter(is_recurring=True)
        
        if not tasks:
            self.stdout.write(f"{Colors.YELLOW}⚠️ No tasks found.{Colors.END}")
            return

        self.stdout.write(f"\n{Colors.BOLD}{'ID':<5} {'Name':<22} {'Project':<12} {'Priority':<8} {'Due':<18} {'Status':<8} {'Rec'}{Colors.END}")
        self.stdout.write(f"{Colors.BLUE}{'─' * 85}{Colors.END}")
        
        for task in tasks:
            status_icon = f"{Colors.GREEN}✅" if task.completed else f"{Colors.YELLOW}⏳"
            priority_color = Colors.RED if task.priority == 'High' else (Colors.YELLOW if task.priority == 'Medium' else Colors.GREEN)
            recurring_icon = "🔄" if task.is_recurring else "  "
            
            name = task.name[:19] + "..." if len(task.name) > 22 else task.name
            project = task.project[:9] + "..." if len(task.project) > 12 else task.project
            due = f"{task.due_date} {str(task.due_time)[:5]}"
            
            self.stdout.write(f"{task.id:<5} {name:<22} {project:<12} {priority_color}{task.priority:<8}{Colors.END} {due:<18} {status_icon}{Colors.END}  {recurring_icon}")
        
        self.stdout.write(f"\n{Colors.CYAN}Total: {tasks.count()} task(s){Colors.END}")

    def add_task(self, options):
        try:
            user = User.objects.get(username=options['user'])
        except User.DoesNotExist:
            self.stdout.write(f"{Colors.RED}❌ User '{options['user']}' not found.{Colors.END}")
            return

        due_date_str = options.get('due_date') or datetime.now().strftime('%Y-%m-%d')
        due_time = options.get('due_time') or "12:00"
        recurrence = options.get('recurrence', 'none')

        try:
            start_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            dates_to_create = []

            if recurrence == 'daily_7':
                for i in range(7):
                    dates_to_create.append(start_date + timedelta(days=i))
            elif recurrence == 'daily_30':
                for i in range(30):
                    dates_to_create.append(start_date + timedelta(days=i))
            elif recurrence == 'weekly_4':
                for i in range(4):
                    dates_to_create.append(start_date + timedelta(weeks=i))
            else:
                dates_to_create.append(start_date)

            is_recurring_flag = recurrence != 'none'
            created_ids = []

            for d in dates_to_create:
                task = Task.objects.create(
                    user=user,
                    name=options['name'],
                    project=options['project'],
                    priority=options['priority'],
                    due_date=d,
                    due_time=due_time,
                    completed=False,
                    is_recurring=is_recurring_flag
                )
                created_ids.append(task.id)

            if len(created_ids) == 1:
                self.stdout.write(f"{Colors.GREEN}✅ Task '{options['name']}' created with ID {created_ids[0]}{Colors.END}")
            else:
                self.stdout.write(f"{Colors.GREEN}✅ Created {len(created_ids)} recurring tasks (IDs: {created_ids[0]}-{created_ids[-1]}){Colors.END}")

        except ValueError as e:
            self.stdout.write(f"{Colors.RED}❌ Invalid date format. Use YYYY-MM-DD.{Colors.END}")

    def complete_task(self, task_id):
        try:
            task = Task.objects.get(id=task_id)
            task.completed = True
            task.save()
            self.stdout.write(f"{Colors.GREEN}✅ Task {task_id} ('{task.name}') marked as complete!{Colors.END}")
        except Task.DoesNotExist:
            self.stdout.write(f"{Colors.RED}❌ Task with ID {task_id} not found.{Colors.END}")

    def pending_task(self, task_id):
        try:
            task = Task.objects.get(id=task_id)
            task.completed = False
            task.save()
            self.stdout.write(f"{Colors.YELLOW}⏳ Task {task_id} ('{task.name}') marked as pending.{Colors.END}")
        except Task.DoesNotExist:
            self.stdout.write(f"{Colors.RED}❌ Task with ID {task_id} not found.{Colors.END}")

    def edit_task(self, options):
        try:
            task = Task.objects.get(id=options['task_id'])
            
            if options.get('name'):
                task.name = options['name']
            if options.get('project'):
                task.project = options['project']
            if options.get('priority'):
                task.priority = options['priority']
            if options.get('due_date'):
                task.due_date = options['due_date']
            if options.get('due_time'):
                task.due_time = options['due_time']
            
            task.save()
            self.stdout.write(f"{Colors.GREEN}✅ Task {options['task_id']} updated successfully!{Colors.END}")
        except Task.DoesNotExist:
            self.stdout.write(f"{Colors.RED}❌ Task with ID {options['task_id']} not found.{Colors.END}")
        except Exception as e:
            self.stdout.write(f"{Colors.RED}❌ Error updating task: {e}{Colors.END}")

    def delete_task(self, task_id):
        try:
            task = Task.objects.get(id=task_id)
            task_name = task.name
            task.delete()
            self.stdout.write(f"{Colors.GREEN}✅ Task {task_id} ('{task_name}') deleted.{Colors.END}")
        except Task.DoesNotExist:
            self.stdout.write(f"{Colors.RED}❌ Task with ID {task_id} not found.{Colors.END}")