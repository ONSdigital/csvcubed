# def run_command_in_temp_dir(context, command: str) -> Tuple[int, str]:
#     tmp_dir_path = get_context_temp_dir_path(context)

#     Path(tmp_dir_path / "buffer").mkdir()
#     stdout_path = Path(tmp_dir_path / "buffer" / "stdout")
#     stderr_path = Path(tmp_dir_path / "buffer" / "stderr")

#     with open(stdout_path, "w") as stdout_file, open(stderr_path, "w") as stderr_file:

#         process = subprocess.Popen(
#             command,
#             shell=True,
#             cwd=tmp_dir_path.resolve(),
#             stdout=stdout_file,
#             stderr=stderr_file,
#         )

#     status_code = process.wait()

#     with open(stdout_path) as stdout_file, open(stderr_path) as stderr_file:
#         response = stdout_file.read() + stderr_file.read()

#     return status_code, response

command = "csvcubed build sweden_at_eurovision_no_missing.csv".strip()

import subprocess

test = subprocess.Popen(command, stdout=subprocess.PIPE)
# test = subprocess.Popen(["ping","-W","2","-c", "1", "192.168.1.70"], stdout=subprocess.PIPE)
# output = test.communicate()[0]
# jmeter -n –t stress.jmx -l testresults.jtl
