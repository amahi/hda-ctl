#! /usr/bin/ruby
#
# Amahi Home Server
# Copyright (C) 2007-2009 Amahi Team
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License v3
# (29 June 2007), as published in the COPYING file.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# file COPYING for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Amahi
# team at http://www.amahi.org/ under "Contact Us."

#
# interface the real hda-install script
#

require 'fileutils'
ROOT_DIR = "/usr/share/hdactl/web-installer"
require File.join(ROOT_DIR, "config.rb")

PROGRESS_PER_LINE = 3
INSTALLER = "/usr/bin/hda-install -q #{ARGV[0]}"
# INSTALLER = "#{File.dirname(__FILE__)}/test-hda-install"

main_pid = Process.pid

FileUtils.mkdir_p(FILE_BASE)

readme, writeme = IO.pipe
pid = fork {
	$stdout.reopen writeme
	readme.close
	exec(INSTALLER)
}
writeme.close

f = File.new(FILE_STDOUT, 'a')

counter = 0
readme.each do |line|
	counter += PROGRESS_PER_LINE
	# never terminate to 100 based on line count!
	counter = 99 if counter > 99
	counter = 100 if line =~ /Instalation completed/
	f.write(line)
	f.flush
	p = File.new(FILE_PROGRESS, 'w+')
	p.write("#{counter}: #{line}")
	p.close
	if counter == 100
		s = File.new(FILE_STATUS, 'w')
		s.write(STATUSES[:finished])
		s.close
	end
end

f.close

Process.waitpid(pid)
installer_exitstatus = $?.exitstatus
s = File.new(FILE_STATUS, 'w')
if installer_exitstatus.to_i != 0
  s.write(STATUSES[:error])
else
  s.write(STATUSES[:finished])
end
s.close

f = File.new(FILE_STDERR, 'w')
f.write(installer_exitstatus)
f.close
