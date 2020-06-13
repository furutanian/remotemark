#===============================================================================
#
#	CLASS: Html
#
require 'pg'	# https://deveiate.org/code/pg/

module PG

	def self.connect_args
		connect_args = {}
		connect_args[:host]		= ENV[it = 'DATABASE_SERVICE_NAME']	|| ENV['HTTP_%s' % it]
		connect_args[:dbname]	= ENV[it = 'POSTGRESQL_DATABASE']	|| ENV['HTTP_%s' % it]
		connect_args[:user]		= ENV[it = 'POSTGRESQL_USER']		|| ENV['HTTP_%s' % it]
		connect_args[:password]	= ENV[it = 'POSTGRESQL_PASSWORD']	|| ENV['HTTP_%s' % it]
		connect_args
	end

	class Connection

		def results_as_hash=(bool)
			Result.results_as_hash = bool
		end

		def execute(sql)
			self.exec(sql)
		end
	end

	class Result

		@@results_as_hash = false

		def self.results_as_hash=(bool)
			@@results_as_hash = bool
		end

		def size
			self.ntuples
		end

		def [](n, m = nil)
			rs = []; (m ? m : 1).times {|i|
				r = @@results_as_hash ? {} : []
				self.tuple(n + i).each {|key, value|
					@@results_as_hash ? r[key] = value : r << value
				} rescue(break)
				rs << r
			}
			m ? rs : rs[0]
		end
	end
end

