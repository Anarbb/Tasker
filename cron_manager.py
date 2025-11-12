"""Cron manager for reading/writing crontab entries.

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
import re
import subprocess
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CronJob:
    """Single cron job entry."""
    minute: str
    hour: str
    day_of_month: str
    month: str
    day_of_week: str
    command: str
    comment: Optional[str] = None
    original_line: Optional[str] = None  # keep original for matching when editing

    def to_cron_string(self) -> str:
        parts = [self.minute, self.hour, self.day_of_month, self.month, self.day_of_week, self.command]
        if self.comment:
            return " ".join(parts) + f" # {self.comment}"
        return " ".join(parts)

    def __str__(self) -> str:
        schedule = f"{self.minute} {self.hour} {self.day_of_month} {self.month} {self.day_of_week}"
        return f"{schedule} → {self.command}"


class CronManager:
    """Handles crontab operations for user/system crontabs."""

    def __init__(self, is_system: bool = False):
        self.is_system = is_system

    def _run_crontab_command(self, operation: str, content: Optional[str] = None) -> tuple[str, str, int]:
        """Run crontab command. Returns (stdout, stderr, return_code)."""
        if operation == "list":
            if self.is_system:
                cmd = ["sudo", "-n", "crontab", "-l"]
            else:
                cmd = ["crontab", "-l"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout, result.stderr, result.returncode
        elif operation == "write":
            if self.is_system:
                cmd = ["sudo", "-n", "crontab", "-"]
            else:
                cmd = ["crontab", "-"]
            result = subprocess.run(cmd, input=content, capture_output=True, text=True)
            return result.stdout, result.stderr, result.returncode
        return "", "", 1

    def get_jobs(self) -> List[CronJob]:
        """Read all cron jobs from crontab."""
        output, error, return_code = self._run_crontab_command("list")
        
        error_lower = error.lower()
        output_lower = output.lower()
        if return_code != 0 and ("no crontab" in error_lower or "no crontab" in output_lower):
            return []
        
        if return_code != 0:
            error_msg = error.strip() if error.strip() else output.strip()
            if self.is_system and ("password is required" in error_lower or "a password is required" in error_lower):
                raise RuntimeError("sudo: a password is required (credentials expired)")
            raise RuntimeError(f"Failed to read crontab: {error_msg}")

        jobs = []
        for line in output.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            job = self._parse_cron_line(line)
            if job:
                jobs.append(job)
        
        return jobs

    def _parse_cron_line(self, line: str) -> Optional[CronJob]:
        """Parse a crontab line into CronJob. Returns None if invalid."""
        comment_match = re.search(r'\s+#\s+(.+)$', line)
        comment = comment_match.group(1) if comment_match else None
        line_without_comment = re.sub(r'\s+#\s+.+$', '', line)
        
        parts = line_without_comment.split()
        if len(parts) < 6:
            return None
        
        minute, hour, day_of_month, month, day_of_week = parts[:5]
        command = " ".join(parts[5:])
        
        return CronJob(
            minute=minute,
            hour=hour,
            day_of_month=day_of_month,
            month=month,
            day_of_week=day_of_week,
            command=command,
            comment=comment,
            original_line=line
        )

    def add_job(self, job: CronJob) -> None:
        """Add a new cron job."""
        jobs = self.get_jobs()
        jobs.append(job)
        self._write_jobs(jobs)

    def update_job(self, old_job: CronJob, new_job: CronJob) -> None:
        """Update an existing cron job."""
        jobs = self.get_jobs()
        for i, job in enumerate(jobs):
            if (job.original_line == old_job.original_line or
                (job.minute == old_job.minute and
                 job.hour == old_job.hour and
                 job.day_of_month == old_job.day_of_month and
                 job.month == old_job.month and
                 job.day_of_week == old_job.day_of_week and
                 job.command == old_job.command)):
                jobs[i] = new_job
                break
        self._write_jobs(jobs)

    def delete_job(self, job: CronJob) -> None:
        """Delete a cron job."""
        jobs = self.get_jobs()
        jobs = [j for j in jobs if not (
            j.original_line == job.original_line or
            (j.minute == job.minute and
             j.hour == job.hour and
             j.day_of_month == job.day_of_month and
             j.month == job.month and
             j.day_of_week == job.day_of_week and
             j.command == job.command))
        ]
        self._write_jobs(jobs)

    def _write_jobs(self, jobs: List[CronJob]) -> None:
        """Write all jobs to crontab."""
        lines = []
        for job in jobs:
            lines.append(job.to_cron_string())
        
        content = "\n".join(lines)
        if content:
            content += "\n"
        
        stdout, stderr, return_code = self._run_crontab_command("write", content)
        if return_code != 0:
            error_msg = stderr.strip() if stderr.strip() else stdout.strip()
            error_lower = error_msg.lower()
            if self.is_system and ("password is required" in error_lower or "a password is required" in error_lower):
                raise RuntimeError("sudo: a password is required (credentials expired)")
            raise RuntimeError(f"Failed to write crontab: {error_msg}")

