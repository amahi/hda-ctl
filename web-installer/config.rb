STATUSES = {
  :not_started => '0',
  :running => '1',
  :error => '2',
  :finished => '3',
  :cancelled => '4'
}

LOG_DIR = "/tmp/amahi-web-installer-log"

# FILE_BASE = File.join(LOG_DIR, 'outputs')
FILE_BASE = LOG_DIR
FILE_PROGRESS = File.join(FILE_BASE, "progress")
FILE_PID = File.join(FILE_BASE, "pid")
FILE_STATUS = File.join(FILE_BASE, "status")
FILE_STDOUT = File.join(FILE_BASE, "stdout")
FILE_STDERR = File.join(FILE_BASE, "stderr")