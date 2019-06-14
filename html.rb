#===============================================================================
#
#	CLASS: Html
#
class Html

	#-----------------------------------------------------------
	#
	#	start(header and footer)
	#
	def start(title = 'No Title', script = '')
		start = Time.new
		@indent = Array.new
		print(<<-HTML)
Content-Type: text/html

<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN'>
<HTML>
	<HEAD>
		<TITLE>#{title}</TITLE>
		<META http-equiv='Content-Type' content='text/html; charset=utf-8'>
#{script}	</HEAD>
	<BODY>
		HTML
		@indent.push("\t")
			@indent.push("\t")
				yield
			@indent.pop
		@indent.pop
		finish = Time.new
		print("#{indent}%.3fmsec<BR>\n" % [(finish.to_f - start.to_f) * 1000])
		print(<<-HTML)
	</BODY>
</HTML>
		HTML
	end

	def indent
		@indent.join
	end

	#-----------------------------------------------------------
	#
	#	form
	#
	def form(tagOpt = {})
		print("#{indent}<FORM#{tagOpt['FORM']}>\n")
		@indent.push("\t")
			yield
		@indent.pop
		print("#{indent}</FORM>\n")
	end

	#-----------------------------------------------------------
	#
	#	ul
	#
	def ul(tagOpt = {})
		print("#{indent}<UL#{tagOpt['UL']}>\n")
		@indent.push("\t")
			yield
		@indent.pop
		print("#{indent}</UL>\n")
	end

	#-----------------------------------------------------------
	#
	#	select
	#
	def select(tagOpt = {})
		print("#{indent}<SELECT#{tagOpt['SELECT']}>\n")
		@indent.push("\t")
			yield
		@indent.pop
		print("#{indent}</SELECT>\n")
	end

	#-----------------------------------------------------------
	#
	#	centered table
	#
	def centered_table(num, tagOpt = {})
		print("#{indent}<TABLE#{tagOpt['TABLE']}>\n")
		@indent.push("\t")
			print("#{indent}<TR>\n")
			@indent.push("\t")
				print("#{indent}<TD width='50%'>\n")
				@indent.push("\t")
					(1..num).each {
						print("#{indent}<TD><IMG#{tagOpt['IMG']}>\n")
					}
				@indent.pop
				print("#{indent}<TD width='50%'>\n")
				@indent.push("\t")
					yield
				@indent.pop
			@indent.pop
		@indent.pop
		print("#{indent}</TABLE>\n")
	end

	#-----------------------------------------------------------
	#
	#	raw
	#
	def raw(html)
		print("#{indent}#{html}\n")
	end

	#-----------------------------------------------------------
	#
	#	search form
	#
	def search_form(tagOpt = {})
		print(<<-HTML)
		<TABLE#{tagOpt['TABLE']}>
		<TR>
			<TD width='50%'>
			<TD><IMG src='images/tp.png' alt='' width='384' height='1'><BR>
			<TD><IMG src='images/tp.png' alt='' width='384' height='1'><BR>
			<TD width='50%'>
		<TR>
			<TD>
			<TD valign='top'>
				<FORM action='http://www.bing.com/search'#{tagOpt['FORM']}>
				<TABLE#{tagOpt['TABLE']}>
				<TR>
					<TD><IMG src='images/tp.png' alt='' width='144' height='1'><BR>
					<TD><IMG src='images/tp.png' alt='' width='240' height='1'><BR>
				<TR>
					<TD align='center' height='64'>
						<A href='http://jp.msn.com/'#{tagOpt['A']}><IMG src='images/bing.gif' alt='bing'></A>
					<TD>
						<INPUT type='text' name='q' size='18'>
						<INPUT type='submit' name='go' value='Search'>
						<INPUT type='reset' value='Clear'>
						<INPUT type='hidden' name='qs' value='ns'>
						<INPUT type='hidden' name='form' value='QBLH'>
						<INPUT type='hidden' name='cp' value='utf-8'> 
				<TR>
					<TD colspan='2' align='center'>
						<INPUT type='radio' id='nofilt' name='filt' value='all'>
						<LABEL for='nofilt'>All Lang.</LABEL>
						<INPUT type='radio' id='langfilt' name='filt' value='lf' checked>
						<LABEL for='langfilt'>Japanese</LABEL>
				</TABLE>
				</FORM>
			<TD valign='top'>
				<FORM action='http://www.google.com/search'#{tagOpt['FORM']}>
				<TABLE#{tagOpt['TABLE']}>
				<TR>
					<TD><IMG src='images/tp.png' alt='' width='144' height='1'><BR>
					<TD><IMG src='images/tp.png' alt='' width='240' height='1'><BR>
				<TR>
					<TD align='center' height='64'>
						<A href='http://www.google.co.jp/'#{tagOpt['A']}><IMG src='images/google.gif' alt='google'></A>
					<TD>
						<INPUT type='text' name='q' size='18'>
						<INPUT type='submit' name='btnG' value='Search'>
						<INPUT type='reset' value='Clear'>
						<INPUT type='hidden' name='ie' value='utf-8'>
						<INPUT type='hidden' name='hl' value='ja'>
						<INPUT type='hidden' name='num' value='50'>
				<TR>
					<TD colspan='2' align='center'>
						<INPUT id='gr1' type='radio' name='lr' value=''><LABEL for='gr1'>All Lang.</LABEL>
						<INPUT id='gr2' type='radio' name='lr' value='lang_ja' checked><LABEL for='gr2'>Japanese</LABEL>
				</TABLE>
				</FORM>
		</TABLE>
		HTML
	end
end
