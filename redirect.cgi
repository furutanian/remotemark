#!/usr/bin/env ruby

require 'cgi'
require 'sqlite3'

cgi  = CGI.new
user = cgi.params['user'][0]
id   = cgi.params['id'][0]

db = SQLite3::Database.new('data/remote_bookmark.db')

#---------------------------------------------------------------
#
#	redirect page
#
uri = db.execute('select uri from bookmarks where id = %s' % id)
print("Location: %s\n\n" % uri[0])
$stdout.close

#---------------------------------------------------------------
#
#	add history
#
if(db.execute("select id from tracks_%s where id = %s" % [user, id]).size == 0)
	db.execute("insert into tracks_%s (id, history) values(%s, (select max(history) from tracks_%s) + 1)" % [user, id, user])
else
	db.execute("update tracks_%s set history = (select max(history) from tracks_%s) + 1 where id = %s" % [user, user, id])
end

db.close
