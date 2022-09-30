import org.apache.jmeter.services.FileServer
def baseDir = FileServer.getFileServer().getBaseDir()
log.info("This is the baseDir: ${baseDir}")


//def proc = "python3 HelloWorld.py".execute()
//def proc = ["python3 HelloWorld.py"].execute()
//println "Found the following: ${proc.text}"
def proc = "python3 test.py 1".execute(null, new File(baseDir))
//def args = 'echo hiya'
//def proc = args.execute()

def b = new StringBuffer()
proc.consumeProcessErrorStream(b)

//def textOut = stream.getText()
def statusCode = proc.waitFor()
if (statusCode != 0) {
	log.error("Error occurred: ${b}")
	throw new Exception("Script failed.")	
}
def textOut = proc.text
log.info("Status code: ${statusCode}")

//proc.waitForOrKill(1000)

log.info("Found the following: ${textOut}");