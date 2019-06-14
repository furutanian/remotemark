#===============================================================================
#
#	CLASS: Http_info
#
require 'kconv'
require 'net/http'

class HTTP_info < Net::HTTP

	attr_reader :info

	#-----------------------------------------------------------
	#
	#	constructor
	#
	def initialize(address, port = nil)
		super(address, port)
		@info = {}
	end

	#-----------------------------------------------------------
	#
	#	get with extract some info
	#
	def get(path, header = nil)
		begin
			response = super(path, header)
			if(response['content-type'] =~ /text\/html/i)
				@info['title'] = response.body =~ /<title>(.+)<\/title>/i ? $1.toutf8 : '--- no title ---'
				if(response.body =~ /<meta name=(['"]*)description\1.*content=(['"]*)(.*)\2>/i)
					@info['description'] = $3.toutf8
				end
			else
				@info['title'] = "--- #{response['content-type']} ---"
			end
		rescue
			@info['title'] = '--- connect failed ---'
		end
		response
	end
end
