#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright © 2018 Christian J. Kellner
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <http://www.gnu.org/licenses/>.
# Authors:
#       Christian J. Kellner <christian@kellner.me>

from __future__ import print_function
import argparse
import gitlab

from datetime import datetime, timedelta


def main():
    parser = argparse.ArgumentParser(description='create issue/merge requests reports')
    parser.add_argument('--site',  default='https://gitlab.freedesktop.org', help='gitlab instance to use')
    parser.add_argument('--project',  default='bolt/bolt', help='project to use')
    args = parser.parse_args()

    gl = gitlab.Gitlab(args.site)
    project = gl.projects.get(args.project)
    now = datetime.now()
    td = timedelta(weeks=1, hours=now.hour, minutes=-now.minute, seconds=now.second)
    lw = now - td
    tstr = lw.isoformat(timespec='minutes')

    print('** Issues: ')
    issues = project.issues.list(updated_after=tstr, sort='asc')
    for issue in issues:
        print('   - #%d %s' % (issue.iid, issue.title))
        print('     %s' % (issue.web_url))
        print('')

    mreqs = project.mergerequests.list(updated_after=tstr, sort='asc')

    print('** Merge Requests: ')

    for mr in mreqs:
        print('   - #%d %s' % (mr.iid, mr.title))
        print('     %s' % (mr.web_url))
        print('')

if __name__ == '__main__':
    main()
