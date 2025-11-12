"""Dialog for adding/editing cron tasks.

Copyright (C) 2024  Anas Arbaoui

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from typing import Optional

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from cron_manager import CronJob


class TaskDialog(Gtk.Dialog):
    def __init__(self, parent: Gtk.Window, job: Optional[CronJob] = None):
        title = "Edit Task" if job else "Add Task"
        super().__init__(title=title, transient_for=parent, modal=True)
        
        self.job = job
        self.result_job = None
        self.schedule_type = "daily"
        
        self.set_default_size(550, 500)
        
        content = self.get_content_area()
        content.set_spacing(16)
        content.set_margin_top(20)
        content.set_margin_bottom(20)
        content.set_margin_start(20)
        content.set_margin_end(20)
        
        name_label = Gtk.Label(label="Task Name")
        name_label.add_css_class("title-4")
        name_label.set_xalign(0)
        content.append(name_label)
        
        self.comment_entry = Gtk.Entry()
        self.comment_entry.set_placeholder_text("e.g., Daily backup, Weekly cleanup, etc.")
        self.comment_entry.set_tooltip_text("Give your task a descriptive name")
        content.append(self.comment_entry)
        
        schedule_header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        schedule_header_box.set_hexpand(True)
        content.append(schedule_header_box)
        
        schedule_label = Gtk.Label(label="When should this task run?")
        schedule_label.add_css_class("title-4")
        schedule_label.set_xalign(0)
        schedule_label.set_hexpand(True)
        schedule_header_box.append(schedule_label)
        
        advanced_label = Gtk.Label(label="Advanced")
        advanced_label.set_xalign(1)
        schedule_header_box.append(advanced_label)
        
        self.advanced_switch = Gtk.Switch()
        self.advanced_switch.set_valign(Gtk.Align.CENTER)
        self.advanced_switch.connect("state-set", self._on_advanced_toggled)
        schedule_header_box.append(self.advanced_switch)
        
        self.schedule_stack = Gtk.Stack()
        self.schedule_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        content.append(self.schedule_stack)
        
        simple_box = self._create_simple_schedule_box()
        self.schedule_stack.add_named(simple_box, "simple")
        
        advanced_box = self._create_advanced_schedule_box()
        self.schedule_stack.add_named(advanced_box, "advanced")
        
        self.schedule_stack.set_visible_child_name("simple")
        
        self.preview_label = Gtk.Label()
        self.preview_label.add_css_class("dim-label")
        self.preview_label.set_wrap(True)
        self.preview_label.set_xalign(0)
        self.preview_label.set_margin_top(8)
        content.append(self.preview_label)
        
        command_label = Gtk.Label(label="What should this task do?")
        command_label.add_css_class("title-4")
        command_label.set_xalign(0)
        command_label.set_margin_top(12)
        content.append(command_label)
        
        command_help = Gtk.Label(label="Enter the command or script to run")
        command_help.add_css_class("dim-label")
        command_help.set_xalign(0)
        command_help.set_margin_bottom(8)
        content.append(command_help)
        
        self.command_entry = Gtk.Entry()
        self.command_entry.set_placeholder_text("e.g., /usr/bin/backup.sh or /usr/bin/python3 /path/to/script.py")
        self.command_entry.set_tooltip_text("Enter the full path to a script or command to execute")
        self.command_entry.connect("changed", self._on_command_changed)
        content.append(self.command_entry)
        
        if job:
            if job.comment:
                self.comment_entry.set_text(job.comment)
            self.command_entry.set_text(job.command)
            self._detect_schedule_type(job)
            self._populate_from_job(job)
        
        self._update_preview()
        
        cancel_button = self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        
        save_button = self.add_button("Save", Gtk.ResponseType.ACCEPT)
        save_button.add_css_class("suggested-action")
        
        self.set_default_response(Gtk.ResponseType.ACCEPT)

    def _create_simple_schedule_box(self) -> Gtk.Box:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        type_label = Gtk.Label(label="Frequency:")
        type_label.set_xalign(0)
        box.append(type_label)
        
        self.schedule_type_combo = Gtk.ComboBoxText()
        self.schedule_type_combo.append_text("Every hour")
        self.schedule_type_combo.append_text("Daily")
        self.schedule_type_combo.append_text("Weekly")
        self.schedule_type_combo.append_text("Monthly")
        self.schedule_type_combo.set_active(1)
        self.schedule_type_combo.connect("changed", self._on_schedule_type_combo_changed)
        box.append(self.schedule_type_combo)
        
        self.time_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.time_box.set_margin_top(8)
        self.time_box.set_visible(True)
        box.append(self.time_box)
        
        time_label = Gtk.Label(label="Time:")
        time_label.set_xalign(0)
        self.time_box.append(time_label)
        
        hour_label = Gtk.Label(label="Hour:")
        self.time_box.append(hour_label)
        
        self.hour_spinner = Gtk.SpinButton()
        self.hour_spinner.set_adjustment(Gtk.Adjustment(value=0, lower=0, upper=23, step_increment=1))
        self.hour_spinner.set_numeric(True)
        self.hour_spinner.set_value(0)
        self.hour_spinner.connect("value-changed", self._on_time_changed)
        self.time_box.append(self.hour_spinner)
        
        minute_label = Gtk.Label(label="Minute:")
        self.time_box.append(minute_label)
        
        self.minute_spinner = Gtk.SpinButton()
        self.minute_spinner.set_adjustment(Gtk.Adjustment(value=0, lower=0, upper=59, step_increment=1))
        self.minute_spinner.set_numeric(True)
        self.minute_spinner.set_value(0)
        self.minute_spinner.connect("value-changed", self._on_time_changed)
        self.time_box.append(self.minute_spinner)
        
        self.weekday_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.weekday_box.set_margin_top(8)
        self.weekday_box.set_visible(False)
        box.append(self.weekday_box)
        
        weekday_label = Gtk.Label(label="Day of week:")
        self.weekday_box.append(weekday_label)
        
        self.weekday_combo = Gtk.ComboBoxText()
        self.weekday_combo.append_text("Sunday")
        self.weekday_combo.append_text("Monday")
        self.weekday_combo.append_text("Tuesday")
        self.weekday_combo.append_text("Wednesday")
        self.weekday_combo.append_text("Thursday")
        self.weekday_combo.append_text("Friday")
        self.weekday_combo.append_text("Saturday")
        self.weekday_combo.set_active(0)
        self.weekday_combo.connect("changed", self._on_time_changed)
        self.weekday_box.append(self.weekday_combo)
        
        return box

    def _create_advanced_schedule_box(self) -> Gtk.Box:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        help_label = Gtk.Label(label="Enter cron schedule fields manually (use * for any value)")
        help_label.add_css_class("dim-label")
        help_label.set_wrap(True)
        help_label.set_xalign(0)
        box.append(help_label)
        
        schedule_grid = Gtk.Grid()
        schedule_grid.set_column_spacing(12)
        schedule_grid.set_row_spacing(8)
        box.append(schedule_grid)
        
        minute_label = Gtk.Label(label="Minute (0-59):")
        minute_label.set_xalign(0)
        schedule_grid.attach(minute_label, 0, 0, 1, 1)
        self.minute_entry = Gtk.Entry()
        self.minute_entry.set_placeholder_text("*")
        self.minute_entry.connect("changed", self._on_cron_field_changed)
        schedule_grid.attach(self.minute_entry, 1, 0, 1, 1)
        
        hour_label = Gtk.Label(label="Hour (0-23):")
        hour_label.set_xalign(0)
        schedule_grid.attach(hour_label, 0, 1, 1, 1)
        self.hour_entry = Gtk.Entry()
        self.hour_entry.set_placeholder_text("*")
        self.hour_entry.connect("changed", self._on_cron_field_changed)
        schedule_grid.attach(self.hour_entry, 1, 1, 1, 1)
        
        dom_label = Gtk.Label(label="Day of Month (1-31):")
        dom_label.set_xalign(0)
        schedule_grid.attach(dom_label, 0, 2, 1, 1)
        self.dom_entry = Gtk.Entry()
        self.dom_entry.set_placeholder_text("*")
        self.dom_entry.connect("changed", self._on_cron_field_changed)
        schedule_grid.attach(self.dom_entry, 1, 2, 1, 1)
        
        month_label = Gtk.Label(label="Month (1-12):")
        month_label.set_xalign(0)
        schedule_grid.attach(month_label, 0, 3, 1, 1)
        self.month_entry = Gtk.Entry()
        self.month_entry.set_placeholder_text("*")
        self.month_entry.connect("changed", self._on_cron_field_changed)
        schedule_grid.attach(self.month_entry, 1, 3, 1, 1)
        
        dow_label = Gtk.Label(label="Day of Week (0-7, 0/7=Sun):")
        dow_label.set_xalign(0)
        schedule_grid.attach(dow_label, 0, 4, 1, 1)
        self.dow_entry = Gtk.Entry()
        self.dow_entry.set_placeholder_text("*")
        self.dow_entry.connect("changed", self._on_cron_field_changed)
        schedule_grid.attach(self.dow_entry, 1, 4, 1, 1)
        
        return box

    def _on_advanced_toggled(self, switch: Gtk.Switch, state: bool) -> bool:
        if state:
            self.schedule_stack.set_visible_child_name("advanced")
        else:
            self.schedule_stack.set_visible_child_name("simple")
        self._update_preview()
        return False

    def _on_schedule_type_combo_changed(self, combo: Gtk.ComboBoxText) -> None:
        active = combo.get_active()
        schedule_types = ["hourly", "daily", "weekly", "monthly"]
        self.schedule_type = schedule_types[active]
        self._on_schedule_type_changed(self.schedule_type)
    
    def _on_schedule_type_changed(self, schedule_type: str) -> None:
        self.schedule_type = schedule_type
        
        if schedule_type in ["daily", "weekly"]:
            self.time_box.set_visible(True)
        else:
            self.time_box.set_visible(False)
        
        if schedule_type == "weekly":
            self.weekday_box.set_visible(True)
        else:
            self.weekday_box.set_visible(False)
        
        self._update_preview()

    def _on_time_changed(self, widget) -> None:
        self._update_preview()

    def _on_cron_field_changed(self, widget) -> None:
        self._update_preview()

    def _on_command_changed(self, widget) -> None:
        self._update_preview()

    def _update_preview(self) -> None:
        if self.schedule_stack.get_visible_child_name() == "simple":
            preview = self._get_simple_preview()
        else:
            preview = self._get_advanced_preview()
        
        self.preview_label.set_text(preview)

    def _get_simple_preview(self) -> str:
        if self.schedule_type == "hourly":
            return "This task will run every hour at minute 0"
        elif self.schedule_type == "daily":
            hour = int(self.hour_spinner.get_value())
            minute = int(self.minute_spinner.get_value())
            return f"This task will run daily at {hour:02d}:{minute:02d}"
        elif self.schedule_type == "weekly":
            hour = int(self.hour_spinner.get_value())
            minute = int(self.minute_spinner.get_value())
            weekday_idx = self.weekday_combo.get_active()
            weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            return f"This task will run every {weekdays[weekday_idx]} at {hour:02d}:{minute:02d}"
        elif self.schedule_type == "monthly":
            return "This task will run on the 1st day of every month at 00:00"
        return ""

    def _get_advanced_preview(self) -> str:
        minute = self.minute_entry.get_text().strip() or "*"
        hour = self.hour_entry.get_text().strip() or "*"
        dom = self.dom_entry.get_text().strip() or "*"
        month = self.month_entry.get_text().strip() or "*"
        dow = self.dow_entry.get_text().strip() or "*"
        
        schedule = f"{minute} {hour} {dom} {month} {dow}"
        return f"Schedule: {schedule}"

    def _detect_schedule_type(self, job: CronJob) -> None:
        if (job.minute == "0" and job.hour == "*" and 
            job.day_of_month == "*" and job.month == "*" and job.day_of_week == "*"):
            self.schedule_type = "hourly"
            self.schedule_type_combo.set_active(0)
        elif (job.minute != "*" and job.hour != "*" and 
              job.day_of_month == "*" and job.month == "*" and job.day_of_week == "*"):
            self.schedule_type = "daily"
            self.schedule_type_combo.set_active(1)
            try:
                self.hour_spinner.set_value(int(job.hour))
                self.minute_spinner.set_value(int(job.minute))
            except ValueError:
                pass
        elif (job.minute != "*" and job.hour != "*" and 
              job.day_of_month == "*" and job.month == "*" and job.day_of_week != "*"):
            self.schedule_type = "weekly"
            self.schedule_type_combo.set_active(2)
            try:
                self.hour_spinner.set_value(int(job.hour))
                self.minute_spinner.set_value(int(job.minute))
                dow = int(job.day_of_week)
                if dow == 7:
                    dow = 0
                self.weekday_combo.set_active(dow)
            except ValueError:
                pass
        elif (job.minute != "*" and job.hour != "*" and 
              job.day_of_month == "1" and job.month == "*" and job.day_of_week == "*"):
            self.schedule_type = "monthly"
            self.schedule_type_combo.set_active(3)

    def _populate_from_job(self, job: CronJob) -> None:
        if hasattr(self, 'minute_entry'):
            self.minute_entry.set_text(job.minute)
            self.hour_entry.set_text(job.hour)
            self.dom_entry.set_text(job.day_of_month)
            self.month_entry.set_text(job.month)
            self.dow_entry.set_text(job.day_of_week)

    def get_job(self) -> Optional[CronJob]:
        command = self.command_entry.get_text().strip()
        if not command:
            return None
        
        comment = self.comment_entry.get_text().strip() or None
        
        if self.schedule_stack.get_visible_child_name() == "simple":
            minute, hour, dom, month, dow = self._get_simple_schedule()
        else:
            minute = self.minute_entry.get_text().strip() or "*"
            hour = self.hour_entry.get_text().strip() or "*"
            dom = self.dom_entry.get_text().strip() or "*"
            month = self.month_entry.get_text().strip() or "*"
            dow = self.dow_entry.get_text().strip() or "*"
        
        return CronJob(
            minute=minute,
            hour=hour,
            day_of_month=dom,
            month=month,
            day_of_week=dow,
            command=command,
            comment=comment
        )

    def _get_simple_schedule(self) -> tuple[str, str, str, str, str]:
        if self.schedule_type == "hourly":
            return ("0", "*", "*", "*", "*")
        elif self.schedule_type == "daily":
            hour = str(int(self.hour_spinner.get_value()))
            minute = str(int(self.minute_spinner.get_value()))
            return (minute, hour, "*", "*", "*")
        elif self.schedule_type == "weekly":
            hour = str(int(self.hour_spinner.get_value()))
            minute = str(int(self.minute_spinner.get_value()))
            dow = str(self.weekday_combo.get_active())
            return (minute, hour, "*", "*", dow)
        elif self.schedule_type == "monthly":
            return ("0", "0", "1", "*", "*")
        return ("*", "*", "*", "*", "*")
