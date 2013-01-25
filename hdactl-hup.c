// Amahi Home Server
// Copyright (C) 2007-2009 Amahi Team
//
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License v3
// (29 June 2007), as published in the COPYING file.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// file COPYING for more details.
// 
// You should have received a copy of the GNU General Public
// License along with this program; if not, write to the Amahi
// team at http://www.amahi.org/ under "Contact Us."

/* signal the hdactl process */
/* exits with 0 if it works, -1 if not */

#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <signal.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>

#define SZ 20

int main (int argc, char *argv[])
{
	int fd = open ("/var/run/hdactl.pid", O_RDONLY);

	if (fd < 0) exit (-1);

	char buf[SZ];

	int rd = read(fd, &buf, SZ-1);

	if (rd < 1) exit (-1);

	buf[SZ-1]='\0';

	int pid = strtol(buf, NULL, 10);

	int ret = 0;

	if (argc > 1 && !strncmp(argv[1], "usr1", 4)) {
		ret = kill(pid, SIGUSR1);
	} else {
		ret = kill(pid, SIGHUP);
		printf("Your HDA services have been restarted.\n");
	}

	return ret;
}
