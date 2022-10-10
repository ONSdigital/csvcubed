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


runProcessJMeter("python3 postprocess.py")