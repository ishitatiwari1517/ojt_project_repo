"""
Task Model for TaskCLI Application
===================================
This module defines the Task model which stores all task-related data.
The same database is shared between the Web App and CLI interface.

Author: TaskCLI Team
"""

from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    """
    Task Model - Represents a single task in the system.
    
    This model is used by both the Web Application and CLI interface,
    ensuring data consistency across both platforms.
    
    Attributes:
        user (ForeignKey): The user who owns this task
        name (str): Task title/name (max 255 chars)
        project (str): Project category for grouping tasks
        priority (str): Task priority - High, Medium, or Low
        due_date (date): When the task is due
        due_time (time): Specific time the task is due
        completed (bool): Whether the task is marked as done
        is_recurring (bool): If task was created as part of a recurring set
        created_at (datetime): Timestamp of task creation (auto-set)
    """
    
    # Priority choices for dropdown/selection
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ]

    # Foreign key to Django's built-in User model
    # CASCADE: If user is deleted, all their tasks are also deleted
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        help_text="The user who owns this task"
    )
    
    # Task details
    name = models.CharField(max_length=255, help_text="Task title")
    project = models.CharField(max_length=255, help_text="Project/category name")
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='Medium',
        help_text="Task priority level"
    )
    
    # Due date and time
    due_date = models.DateField(help_text="Task due date")
    due_time = models.TimeField(help_text="Task due time")
    
    # Status flags
    completed = models.BooleanField(default=False, help_text="Is task completed?")
    is_recurring = models.BooleanField(default=False, help_text="Is this a recurring task?")
    
    # Timestamp (auto-set on creation)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for Task model."""
        ordering = ['due_date', 'due_time']  # Default ordering by due date/time
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        """String representation for admin and debugging."""
        return f"{self.name} ({self.user.username})"
    
    @property
    def is_overdue(self):
        """Check if task is past its due date."""
        from datetime import date
        return not self.completed and self.due_date < date.today()
