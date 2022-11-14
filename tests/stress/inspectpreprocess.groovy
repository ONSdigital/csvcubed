import org.apache.jmeter.services.FileServer

void runProcessJMeter(String command) {
	def baseDir = FileServer.getFileServer().getBaseDir()
	log.info("This is the baseDir: ${baseDir}")

	def proc = command.execute(null, new File(baseDir))

	def b = new StringBuffer()
	proc.consumeProcessErrorStream(b)

	def statusCode = proc.waitFor()
	if (statusCode != 0) {
		log.error("Error occurred: ${b}")
		throw new Exception("Script failed.")	
	}
	def textOut = proc.text
	log.info("Status code: ${statusCode}")

	log.info("Found the following: ${textOut}");
}

// Assign the number of rows to be tested as either 10
// when running the .jmx files in GUI mode or as 
// whatever value is supplied to the bash script.
def rows = 10
if (args) {
	rows = args[0]
}

runProcessJMeter("python3 inspectpreprocess.py ${rows}")