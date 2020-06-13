#!/usr/bin/env ruby

require 'cgi'

cgi  = CGI.new
user = cgi.params['user'][0]
id   = cgi.params['id'][0]

unless(pg_name = ENV[it = 'POSTGRESQL_DATABASE'] || ENV['HTTP_%s' % it])
	require 'sqlite3'
	db = SQLite3::Database.new('data/remote_bookmark.db')
else
	require './pg_compat.rb'
	db = PG.connect(PG.connect_args)
end

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
