"""Run one child and report its Linux maximum RSS, without external time(1)."""
import resource,subprocess,sys
result=subprocess.run(sys.argv[1:])
print('max_rss_kib='+str(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss),flush=True)
raise SystemExit(result.returncode)
