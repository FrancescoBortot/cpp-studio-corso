"""Apply child limits before exec, without preexec_fn in a threaded server."""
import os,resource,sys
cpu=int(sys.argv[1]);max_file=8*1024*1024
resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu))
resource.setrlimit(resource.RLIMIT_FSIZE,(max_file,max_file))
os.execv(sys.argv[2],sys.argv[2:])
