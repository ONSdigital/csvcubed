import org.apache.jmeter.services.FileServer
def baseDir = FileServer.getFileServer().getBaseDir()
log.info("This is the baseDir: ${baseDir}")

def proc = "python3 buildpreprocess.py 100".execute(null, new File(baseDir))

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