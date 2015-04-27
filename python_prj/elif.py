#!/usr/bin/env python
# coding=utf-8
import cmd
if user.cmd in('create', 'delete', 'update'):
    action = '%s item' % user.cmd
else:    
    action = 'incalid choice... try again'
