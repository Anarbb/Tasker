"""Main window for Tasker.

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
import sys
from pathlib import Path
from typing import Optional

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

from cron_manager import CronManager, CronJob
from task_dialog import TaskDialog


class TaskerWindow(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application):
        super().__init__(application=app, title="Tasker")
        self.set_default_size(800, 600)
        
        if hasattr(app, 'css_provider'):
            display = self.get_display()
            Gtk.StyleContext.add_provider_for_display(
                display,
                app.css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        
        self.cron_manager: Optional[CronManager] = None
        self.is_system = False
        self.current_jobs: list[CronJob] = []
        
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)
        self.set_titlebar(header)
        
        crontab_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.pack_start(crontab_box)
        
        self.crontab_switch = Gtk.Switch()
        self.crontab_switch.set_tooltip_text("Toggle between user and system crontab")
        self.crontab_switch.connect("state-set", self._on_crontab_changed)
        crontab_box.append(self.crontab_switch)
        
        system_label = Gtk.Label(label="System")
        crontab_box.append(system_label)
        
        add_button = Gtk.Button(label="Add Task")
        add_button.add_css_class("suggested-action")
        add_button.connect("clicked", self._on_add_task)
        header.pack_end(add_button)
        
        refresh_button = Gtk.Button(icon_name="view-refresh-symbolic")
        refresh_button.set_tooltip_text("Refresh")
        refresh_button.connect("clicked", self._on_refresh)
        header.pack_end(refresh_button)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(main_box)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        main_box.append(scrolled)
        
        self.job_list = Gtk.ListBox()
        self.job_list.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.set_child(self.job_list)
        
        self.status_bar = Gtk.Label()
        self.status_bar.add_css_class("dim-label")
        self.status_bar.set_margin_top(8)
        self.status_bar.set_margin_bottom(8)
        self.status_bar.set_margin_start(12)
        self.status_bar.set_margin_end(12)
        main_box.append(self.status_bar)
        
        self._update_crontab_manager()
        self._refresh_jobs()

    def _on_crontab_changed(self, switch: Gtk.Switch, state: bool) -> bool:
        if state:
            if not self._authenticate_for_system_mode():
                switch.set_active(False)
                return True
        
        self.is_system = state
        self._update_crontab_manager()
        self._refresh_jobs()
        return False
    
    def _authenticate_for_system_mode(self) -> bool:
        """Authenticate for system crontab access using pkexec."""
        import subprocess
        
        try:
            result = subprocess.run(
                ["pkexec", "sudo", "-v"],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            self._show_error("pkexec not found. Please install polkit to use system crontab.")
            return False

    def _update_crontab_manager(self) -> None:
        self.cron_manager = CronManager(is_system=self.is_system)

    def _on_add_task(self, button: Gtk.Button) -> None:
        dialog = TaskDialog(self)
        dialog.connect("response", self._on_dialog_response, None)
        dialog.present()

    def _on_edit_task(self, button: Gtk.Button, job: CronJob) -> None:
        dialog = TaskDialog(self, job=job)
        dialog.connect("response", self._on_dialog_response, job)
        dialog.present()

    def _on_delete_task(self, button: Gtk.Button, job: CronJob) -> None:
        dialog = Gtk.Dialog(
            title="Delete Task?",
            transient_for=self,
            modal=True,
        )
        dialog.set_default_size(400, 150)
        
        content = dialog.get_content_area()
        content.set_spacing(12)
        content.set_margin_top(20)
        content.set_margin_bottom(20)
        content.set_margin_start(20)
        content.set_margin_end(20)
        
        message_label = Gtk.Label(label=f"Are you sure you want to delete this task?\n\n{job}")
        message_label.set_wrap(True)
        message_label.set_xalign(0)
        content.append(message_label)
        
        dialog.add_button("No", Gtk.ResponseType.NO)
        dialog.add_button("Yes", Gtk.ResponseType.YES)
        dialog.set_default_response(Gtk.ResponseType.NO)
        
        dialog.connect("response", self._on_delete_confirm, job)
        dialog.present()

    def _on_delete_confirm(self, dialog: Gtk.Dialog, response_id: int, job: CronJob) -> None:
        dialog.destroy()
        
        if response_id == Gtk.ResponseType.YES:
            try:
                self.cron_manager.delete_job(job)
                self._refresh_jobs()
                self._update_status("Task deleted successfully")
            except RuntimeError as e:
                error_msg = str(e)
                if self.is_system and ("sudo" in error_msg.lower() or "password" in error_msg.lower()):
                    if self._authenticate_for_system_mode():
                        try:
                            self.cron_manager.delete_job(job)
                            self._refresh_jobs()
                            self._update_status("Task deleted successfully")
                        except Exception as retry_error:
                            self._show_error(f"Failed to delete task: {retry_error}")
                    else:
                        self._show_error("Authentication required to delete task")
                else:
                    self._show_error(f"Failed to delete task: {e}")
            except Exception as e:
                self._show_error(f"Failed to delete task: {e}")

    def _on_dialog_response(self, dialog: TaskDialog, response_id: int, old_job: Optional[CronJob]) -> None:
        if response_id == Gtk.ResponseType.ACCEPT:
            new_job = dialog.get_job()
            if not new_job:
                self._show_error("Invalid task: Command is required")
                dialog.destroy()
                return
            
            try:
                if old_job:
                    self.cron_manager.update_job(old_job, new_job)
                    self._update_status("Task updated successfully")
                else:
                    self.cron_manager.add_job(new_job)
                    self._update_status("Task added successfully")
                
                self._refresh_jobs()
            except RuntimeError as e:
                error_msg = str(e)
                if self.is_system and ("sudo" in error_msg.lower() or "password" in error_msg.lower()):
                    if self._authenticate_for_system_mode():
                        try:
                            if old_job:
                                self.cron_manager.update_job(old_job, new_job)
                                self._update_status("Task updated successfully")
                            else:
                                self.cron_manager.add_job(new_job)
                                self._update_status("Task added successfully")
                            self._refresh_jobs()
                        except Exception as retry_error:
                            self._show_error(f"Failed to save task: {retry_error}")
                    else:
                        self._show_error("Authentication required to save task")
                else:
                    self._show_error(f"Failed to save task: {e}")
            except Exception as e:
                self._show_error(f"Failed to save task: {e}")
        
        dialog.destroy()

    def _on_refresh(self, button: Gtk.Button) -> None:
        self._refresh_jobs()

    def _refresh_jobs(self) -> None:
        while child := self.job_list.get_first_child():
            self.job_list.remove(child)
        
        try:
            self.current_jobs = self.cron_manager.get_jobs()
            
            if not self.current_jobs:
                empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
                empty_box.set_margin_top(48)
                empty_box.set_margin_bottom(48)
                
                empty_label = Gtk.Label(label="No scheduled tasks")
                empty_label.add_css_class("dim-label")
                empty_label.add_css_class("title-1")
                empty_box.append(empty_label)
                
                hint_label = Gtk.Label(label="Click 'Add Task' to create your first scheduled task")
                hint_label.add_css_class("dim-label")
                empty_box.append(hint_label)
                
                self.job_list.append(empty_box)
            else:
                for job in self.current_jobs:
                    row = self._create_job_row(job)
                    self.job_list.append(row)
            
            crontab_type = "system" if self.is_system else "user"
            self._update_status(f"Loaded {len(self.current_jobs)} task(s) from {crontab_type} crontab")
            
        except RuntimeError as e:
            error_msg = str(e)
            if self.is_system and ("sudo" in error_msg.lower() or "password" in error_msg.lower()):
                if self._authenticate_for_system_mode():
                    self._refresh_jobs()
                    return
            self._show_error(f"Failed to load tasks: {e}")
        except Exception as e:
            self._show_error(f"Failed to load tasks: {e}")

    def _create_job_row(self, job: CronJob) -> Gtk.ListBoxRow:
        row = Gtk.ListBoxRow()
        
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        row.set_child(box)
        
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info_box.set_hexpand(True)
        info_box.set_halign(Gtk.Align.START)
        box.append(info_box)
        
        schedule_label = Gtk.Label(label=f"Schedule: {job.minute} {job.hour} {job.day_of_month} {job.month} {job.day_of_week}")
        schedule_label.set_xalign(0)
        schedule_label.add_css_class("title-4")
        info_box.append(schedule_label)
        
        command_label = Gtk.Label(label=f"Command: {job.command}")
        command_label.set_xalign(0)
        command_label.add_css_class("dim-label")
        command_label.set_wrap(True)
        info_box.append(command_label)
        
        if job.comment:
            comment_label = Gtk.Label(label=f"Comment: {job.comment}")
            comment_label.set_xalign(0)
            comment_label.add_css_class("dim-label")
            info_box.append(comment_label)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.append(button_box)
        
        edit_button = Gtk.Button(icon_name="document-edit-symbolic")
        edit_button.set_tooltip_text("Edit")
        edit_button.connect("clicked", self._on_edit_task, job)
        button_box.append(edit_button)
        
        delete_button = Gtk.Button(icon_name="edit-delete-symbolic")
        delete_button.set_tooltip_text("Delete")
        delete_button.add_css_class("destructive-action")
        delete_button.connect("clicked", self._on_delete_task, job)
        button_box.append(delete_button)
        
        return row

    def _update_status(self, message: str) -> None:
        self.status_bar.set_text(message)

    def _show_error(self, message: str) -> None:
        dialog = Gtk.Dialog(
            title="Error",
            transient_for=self,
            modal=True,
        )
        dialog.set_default_size(400, 150)
        
        content = dialog.get_content_area()
        content.set_spacing(12)
        content.set_margin_top(20)
        content.set_margin_bottom(20)
        content.set_margin_start(20)
        content.set_margin_end(20)
        
        error_label = Gtk.Label(label=message)
        error_label.set_wrap(True)
        error_label.set_xalign(0)
        error_label.add_css_class("error")
        content.append(error_label)
        
        dialog.add_button("OK", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()


class MyApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="me.arbaoui.tasker")
        GLib.set_application_name("Tasker")
        self._load_css()

    def _load_css(self):
        # Try system path first, then local
        css_paths = [
            Path("/usr/share/tasker/ui.css"),
            Path(__file__).parent / "ui.css",
        ]
        for css_path in css_paths:
            if css_path.exists():
                css_provider = Gtk.CssProvider()
                css_provider.load_from_path(str(css_path))
                self.css_provider = css_provider
                break

    def do_activate(self):
        window = TaskerWindow(self)
        window.present()


def main():
    """Main entry point."""
    app = MyApplication()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)


if __name__ == "__main__":
    main()
