#!/usr/bin/env ruby

=begin

	Remote Bookmark
	Copyright (C) 2002-2020 Furutanian

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.

=end

require 'cgi'
require './html.rb'
require './http_info.rb'

@configs = {}; load './remotemark.conf'
proxy_host = @configs[:PROXY_HOST] || nil
proxy_port = @configs[:PROXY_PORT] || nil
proxy_user = @configs[:PROXY_USER] || nil
proxy_pass = @configs[:PROXY_PASS] || nil
if(@configs[:PROXY])
	proxys = @configs[:PROXY].gsub(/.*\/\//, '').gsub(/\/.*/, '').split(/[@:]/) 
	proxys.size > 2 and proxy_user = proxys.shift and proxy_pass = proxys.shift
	proxy_host = proxys.shift and proxy_port = proxys.shift.to_i
end

cgi = CGI.new
user = cgi.params['user'][0] || 'nobody'

unless(pg_name = ENV[it = 'POSTGRESQL_DATABASE'] || ENV['HTTP_%s' % it])
	require 'sqlite3'
	db = SQLite3::Database.new('data/remote_bookmark.db')
	is_exist_table	= 'sqlite_master'
	is_exist_field	= 'name'
	type_autoinc	= 'integer'
else
	require './pg_compat.rb'
	db = PG.connect(PG.connect_args)
	is_exist_table	= 'information_schema.tables'
	is_exist_field	= 'table_name'
	type_autoinc	= 'serial'
end
db.results_as_hash = true

if(db.execute("select * from %s where %s = 'bookmarks'" % [is_exist_table, is_exist_field]).size == 0)
	db.execute("create table bookmarks (id integer, title text, uri text, primary key(id))" % type_autoinc)
	db.execute("create index bookmarks_title on bookmarks (title asc)")
	db.execute("insert into bookmarks (id, title, uri) values(1, 'Yahoo! JAPAN', 'http://www.yahoo.co.jp/')")
end
if(db.execute("select * from %s where %s = 'tracks_%s'" % [is_exist_table, is_exist_field, user]).size == 0)
	db.execute("create table tracks_%s (id %s, history integer, folder integer, primary key(id))" % [user, type_autoinc])
	db.execute("insert into tracks_%s (id, history) values(1, 1)" % user)
	db.execute("create table folders_%s (id %s, label text, exposure integer, position integer, primary key(id))" % [user, type_autoinc])
	db.execute("insert into folders_%s (id, label, exposure) values(1, 'Visited', 99999)" % user)
	db.execute("insert into folders_%s (id, label, exposure) values(2, 'UnVisited', 0)" % user)
end

if(cgi.params['command'][0] == '   set   ')

	#-----------------------------------------------------------
	#
	#	regist site
	#
	if((it = cgi.params['newuri'][0]) != '')
		uri = URI.parse(URI.encode(it))
		id = db.execute("select id from bookmarks where uri = '%s'" % uri.to_s)
		if(id.size == 0)										# new site
			http = HTTP_info.new(uri.host, 80, proxy_host, proxy_port, proxy_user, proxy_pass)
			http.start {|session| session.get(uri.path, uri.query) }
			db.transaction {
				db.execute("insert into bookmarks (uri, title) values('%s', '%s')" % [uri.to_s, http.info['title'].gsub("'", "''")])
				id = db.execute("select id from bookmarks where uri = '%s'" % uri.to_s)
				db.execute("insert into tracks_%s (id, history) values(%s, (select max(history) from tracks_%s) + 1)" % [user, id[0]['id'], user])
			}
		else													# already exist
			if(db.execute("select id from tracks_%s where id = %s" % [user, id[0]['id']]).size == 0)
				db.execute("insert into tracks_%s (id, history) values(%s, (select max(history) from tracks_%s) + 1)" % [user, id[0]['id'], user])
			else
				db.execute("update tracks_%s set history = (select max(history) from tracks_%s) + 1, folder = null where id = %s" % [user, user, id[0]['id']])
			end
		end

	#-----------------------------------------------------------
	#
	#	rename link, folder / make new folder
	#
	elsif((it = cgi.params['newname'][0]) != '')
		if((id = cgi.params['id']).size == 1)					# rename bookmark title
			db.execute("update bookmarks set title = '%s' where id = %s" % [it, id[0]])
		elsif((folder = cgi.params['folder']).size == 1)		# rename folder label
			db.execute("update folders_%s set label = '%s' where id = %s" % [user, it, folder[0]])
		elsif((ids = cgi.params['id']).size > 1)				# make new folder
			db.transaction {
				db.execute("insert into folders_%s (label, exposure) values('%s', 99999)" % [user, it])
				folder_id = db.execute("select id from folders_%s where label = '%s'" % [user, it])
				ids.each {|id|
					db.execute("update tracks_%s set folder = %s where id = %s" % [user, folder_id[0]['id'], id])
				}
			}
		end

	#-----------------------------------------------------------
	#
	#	move link to folder
	#
	elsif((it = cgi.params['folder']).size == 1 and cgi.params['id'].size > 0)
		cgi.params['id'].each {|id|
			db.execute("update tracks_%s set folder = %s where id = %s" % [user, it[0], id])
		}
	end

#---------------------------------------------------------------
#
#	remove link, folder
#
elsif(cgi.params['command'][0] == 'remove')
	cgi.params['id'].each {|id|
		db.transaction {
			db.execute("delete from bookmarks where id = %s" % id)
			db.execute("delete from tracks_%s where id = %s" % [user, id])
		}
	}
	cgi.params['folder'].each {|folder|
		db.transaction {
			db.execute("update tracks_%s set folder = null where folder = %s" % [user, folder])
			db.execute("delete from folders_%s where id = %s" % [user, folder])
		}
	}
end

#---------------------------------------------------------------
#
#	folder expose
#
if(cgi.params['fold'][0] == 'close')
	db.execute("update folders_%s set exposure = 0 where id = %s" % [user, cgi.params['folder'][0]])
elsif(cgi.params['fold'][0] == 'plus')
	db.execute("update folders_%s set exposure = (%s) where id = %s" %
		[user, "select exposure + 3 from folders_%s where id = %s" % [user, it = cgi.params['folder'][0]], it])
elsif(cgi.params['fold'][0] == 'open')
	db.execute("update folders_%s set exposure = 99999 where id = %s" % [user, cgi.params['folder'][0]])
end

#---------------------------------------------------------------
#
#	begin html
#
html = Html.new

javascript = <<EOS
		<SCRIPT LANGUAGE="JavaScript">
			function jump(sel){
				if(sel.options[sel.selectedIndex].value != "") {
					w = window.open("","","");
					w.location = sel.options[sel.selectedIndex].value;
					sel.selectedIndex = 0
				}
			}
		</SCRIPT>
EOS

html.start('Remote Bookmark[%s]' % user, javascript) {

	#-----------------------------------------------------------
	#
	#	net search section
	#
	html.raw("<P align='center'><FONT size='+2'>Search</FONT>")
	html.search_form({'FORM' => " target='_blank'", 'TABLE' => " border='0'", 'A' => " target='_brank'"})

	html.raw("<BR><HR width='800' size='4'><BR>")

	#-----------------------------------------------------------
	#
	#	bookmark section
	#
	html.raw("<P align='center'><FONT size='+2'>Bookmarks</FONT>")
	html.form({'FORM' => " method='POST' action='index.cgi'"}) {
		html.raw("<INPUT type='hidden' name='user' value='#{user}'>")

		#-------------------------------------------------------
		#
		#	panel section
		#
		html.centered_table(4, {'TABLE' => " border='0' valign='middle'", 'IMG' => " src='images/tp.png' width='200' height='1'"}) {

			html.raw("<TR><TD><TD align='right'>uri")
			html.raw("<TD colspan='2' align='center'><INPUT type='text' name='newuri' size='50'>")
			html.raw("<TD align='right'><A href='index.cgi?user=%s'>reload</A>" % user)

			html.raw("<TR><TD><TD align='right'>name")
			html.raw("<TD colspan='2' align='center'><INPUT type='text' name='newname' size='50'>")
			html.raw("<TD align='right'>")
			html.raw("<INPUT type='submit' name='command' value='   set   '>")
			html.raw("<INPUT type='submit' name='command' value='remove'>")
		}

		#-------------------------------------------------------
		#
		#	link section
		#
		def build_links(user, bookmarks, folder)
			yield("<LI type='square'>")
			folder['id'].to_i > 2 and yield("<INPUT type='checkbox' name='folder' value='%s'> " % folder['id'])
			if((exposure = folder['exposure'].to_i) != 0)
				yield("<B>%s</B>" % folder['label'])
			else
				yield("<SELECT name='%s' onchange='jump(this)'>" % folder['id'])
				yield("<OPTION value=''>[%s]" % folder['label'])
				yield("<OPTION disabled>----------------------------------------")
				bookmarks.each {|bookmark|
					yield("<OPTION value='redirect.cgi?user=%s;id=%s'>%s" % [user, bookmark['id'], bookmark['title']])
				}
				yield("</SELECT>")
			end

			exposure !=     0 and yield("<A href='index.cgi?user=%s;folder=%s;fold=close'>x</A>" % [user, folder['id']])
			exposure != 99999 and yield("<A href='index.cgi?user=%s;folder=%s;fold=plus' >+</A>" % [user, folder['id']])
			exposure != 99999 and yield("<A href='index.cgi?user=%s;folder=%s;fold=open' >o</A>" % [user, folder['id']])

			if(exposure != 0)
				yield("<UL>")
					bookmarks[0, exposure].each {|bookmark|
						yield("<LI type='desc'><INPUT type='checkbox' name='id' value='%s'>" % bookmark['id'])
						yield("<A href='redirect.cgi?user=%s;id=%s' target='_blank'>%s</A>" % [user, bookmark['id'], bookmark['title']])
					}
					if(bookmarks[exposure])
						yield("<LI>...and <SELECT name='%s' onchange='jump(this)'>" % folder['id'])
						yield("<OPTION value=''>more")
						yield("<OPTION disabled>--------------------------------")
						bookmarks[exposure, 99999].each {|bookmark|
							yield("<OPTION value='redirect.cgi?user=%s;id=%s'>%s" % [user, bookmark['id'], bookmark['title']])
						}
						yield("</SELECT>")
					end
				yield("</UL>")
			end
		end

		html.centered_table(2, {'TABLE' => " border='0' valign='top'", 'IMG' => " src='images/tp.png' width='400' height='1'"}) {

			html.raw("<TR><TD><TD valign='top'>")				# left pane
			html.ul {
				folders = db.execute("select id, label, exposure from folders_%s where label = 'Visited'" % user)
				bookmarks = db.execute(<<-SQL % [user, user, user, user, user])
					select bookmarks.id, bookmarks.title from bookmarks
					left outer join tracks_%s on bookmarks.id = tracks_%s.id
					where tracks_%s.folder is null and tracks_%s.history is not null
					order by tracks_%s.history desc
				SQL
				build_links(user, bookmarks, folders[0]) {|l| html.raw(l) }
				folders = db.execute("select id, label, exposure from folders_%s where label = 'UnVisited'" % user)
				bookmarks = db.execute(<<-SQL % [user, user, user])
					select bookmarks.id, bookmarks.title from bookmarks
					left outer join tracks_%s on bookmarks.id = tracks_%s.id
					where tracks_%s.history is null
					order by bookmarks.title
				SQL
				build_links(user, bookmarks, folders[0]) {|l| html.raw(l) }
			}

			html.raw("<TD valign='top'>")						# right pane
			html.ul {
				folders = db.execute("select id, label, exposure from folders_%s where id > 2 order by position desc, label" % user)
				folders.each {|folder|
					bookmarks = db.execute(<<-SQL % [user, user, user, folder['id'], user])
						select bookmarks.id, bookmarks.title from bookmarks
						left outer join tracks_%s on bookmarks.id = tracks_%s.id
						where tracks_%s.folder = %s
						order by tracks_%s.history desc
					SQL
					build_links(user, bookmarks, folder) {|l| html.raw(l) }
				}
			}
		}
	}
	html.raw('%s backend.<BR>' % [pg_name ? 'PostgreSQL' : 'SQLite'])
}
